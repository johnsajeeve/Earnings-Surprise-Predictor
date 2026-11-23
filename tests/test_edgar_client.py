"""EDGAR client, rate limits, raw payload storage and parsing (Ingestion IG-07, IG-08, IG-10,
IG-12; Data SR-07; Database DB-11; Project-Wide SP-06).

No test here calls the network. The recorded response is a real, trimmed EDGAR payload whose
origin is stated inside the fixture file. Fakes and rows written to the test database are synthetic.
"""

import json
import logging
import socket
from pathlib import Path

import pytest
import redis
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from db_support import table_hash
from earnings import consensus
from earnings.clients import edgar
from earnings.clients.edgar import EdgarClient, MissingContactError, SourceError
from earnings.config import get_settings
from earnings.limits import RedisSlidingWindowLimiter, SlidingWindowLimiter
from earnings.parsing import parse_diluted_eps
from earnings.rawstore import latest_payload, store_payload

FIXTURE = Path(__file__).parent / "fixtures" / "edgar_companyfacts_aapl_trimmed.json"
CONTACT = "Synthetic Test Client synthetic-contact@example.invalid"
URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK0000320193.json"


class FakeResponse:
    def __init__(self, status_code=200, content=b"{}"):
        self.status_code, self.content = status_code, content
        self.headers = {"Content-Type": "application/json"}


class FakeSession:
    """SYNTHETIC stand-in for a requests session. Records every call."""

    def __init__(self, response=None):
        self.calls, self._response = [], response or FakeResponse()

    def get(self, url, *, headers, timeout):
        self.calls.append((url, dict(headers)))
        return self._response


class FakeClock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now

    def sleep(self, seconds):
        self.now += seconds


@pytest.fixture
def no_external_network(monkeypatch):
    """Refuse every name lookup except the stack's own services."""
    real = socket.getaddrinfo

    def guarded(host, *args, **kwargs):
        if host not in ("db", "redis", "localhost", "127.0.0.1"):
            raise OSError(f"network disabled in this test: {host}")
        return real(host, *args, **kwargs)

    monkeypatch.setattr(socket, "getaddrinfo", guarded)


@pytest.mark.req("IG-08-AC1")
@pytest.mark.code("src/earnings/clients/edgar.py")
@pytest.mark.parametrize("unset", ["", "   "])
def test_with_the_contact_unset_the_client_raises_and_sends_nothing(unset):
    session = FakeSession()
    with pytest.raises(MissingContactError):
        EdgarClient(unset, session=session).get(URL)
    assert session.calls == []


@pytest.mark.req("IG-08")
@pytest.mark.code("src/earnings/clients/edgar.py")
def test_the_contact_is_sent_as_the_user_agent_and_never_logged_or_shown(caplog):
    session = FakeSession()
    client = EdgarClient(CONTACT, session=session)
    with caplog.at_level(logging.DEBUG):
        raw = client.get(URL)
    assert session.calls == [(URL, {"User-Agent": CONTACT})]
    assert CONTACT not in caplog.text and CONTACT not in repr(client) and CONTACT not in repr(raw)
    failing = EdgarClient(CONTACT, session=FakeSession(FakeResponse(503)))
    with pytest.raises(SourceError) as error:
        failing.get(URL)
    assert CONTACT not in str(error.value)


@pytest.mark.req("IG-08", "SP-06")
@pytest.mark.code("src/earnings/clients/edgar.py")
@pytest.mark.parametrize(
    "bad", ["https://example.com/x", "https://sec.gov.evil.example/x", "http://localhost/x"]
)
def test_the_contact_goes_only_to_sec_gov_hosts(bad):
    session = FakeSession()
    with pytest.raises(ValueError):
        EdgarClient(CONTACT, session=session).get(bad)
    assert session.calls == []
    EdgarClient(CONTACT, session=session).get("https://www.sec.gov/files/company_tickers.json")
    assert len(session.calls) == 1


@pytest.mark.req("SR-07-AC1")
@pytest.mark.code("src/earnings/clients/edgar.py", "src/earnings/consensus.py")
def test_a_request_log_line_is_written_for_each_source_call(caplog, test_db):
    from datetime import timedelta

    from earnings.db import get_engine

    with caplog.at_level(logging.INFO):
        EdgarClient(CONTACT, session=FakeSession(FakeResponse(200, b"abc"))).get(URL)
        consensus.capture_all(
            get_engine("worker"),
            [("AAPL", "0000320193", "SYNTHETIC test row")],
            fetch=lambda _t: {"mean": 1.0, "payload": {}},
            now=consensus.CAPTURE_START + timedelta(days=1),
        )
    text_ = caplog.text
    assert "edgar GET /api/xbrl/companyfacts/CIK0000320193.json -> 200, 3 bytes" in text_
    assert "yfinance fetch AAPL" in text_ and CONTACT not in text_


@pytest.mark.req("IG-07")
@pytest.mark.code("src/earnings/limits.py", "src/earnings/clients/edgar.py")
def test_edgar_requests_never_exceed_the_limit_in_any_second_with_a_mocked_clock():
    clock = FakeClock()
    limiter = SlidingWindowLimiter(edgar.MAX_REQUESTS_PER_SECOND, 1.0, clock, clock.sleep)
    stamps = []
    for _ in range(100):
        limiter.acquire()  # waits when the window is full, never raises
        stamps.append(clock.now)
    assert edgar.MAX_REQUESTS_PER_SECOND <= 10  # the SEC limit
    for start in stamps:
        assert sum(1 for s in stamps if start <= s < start + 1.0) <= edgar.MAX_REQUESTS_PER_SECOND


@pytest.mark.req("IG-07")
@pytest.mark.code("src/earnings/limits.py", "src/earnings/tasks.py")
def test_two_worker_processes_together_stay_under_the_limit_through_redis():
    clock = FakeClock()
    client = redis.Redis.from_url(get_settings().celery_broker_url, decode_responses=True)
    key = "ratelimit:test:synthetic"
    client.delete(key)
    try:
        # Two limiters on one key stand for two worker processes.
        first, second = (
            RedisSlidingWindowLimiter(client, key, 8, 1.0, clock, clock.sleep) for _ in range(2)
        )
        stamps = []
        for i in range(60):
            (first if i % 2 == 0 else second).acquire()
            stamps.append(clock.now)
        for start in stamps:
            assert sum(1 for s in stamps if start <= s < start + 1.0) <= 8
    finally:
        client.delete(key)


@pytest.mark.req("IG-12", "IG-10")
@pytest.mark.code("tests/fixtures/edgar_companyfacts_aapl_trimmed.json", "src/earnings/parsing.py")
def test_the_recorded_edgar_response_states_its_origin_and_parses_with_no_network(
    no_external_network,
):
    document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    assert document["_origin"].startswith("REAL response")
    facts = parse_diluted_eps(FIXTURE.read_bytes())
    assert len(facts) == 6
    first = facts[0]
    assert (first["end"], first["value"], first["form"]) == ("2012-09-29", 6.31, "10-K")
    assert all({"end", "value", "filed", "accession"} <= set(f) for f in facts)


@pytest.mark.req("IG-10", "DB-11")
@pytest.mark.code("src/earnings/rawstore.py", "src/earnings/parsing.py")
def test_a_payload_is_stored_as_received_and_parsed_from_the_database_offline(
    test_db, no_external_network
):
    from earnings.db import get_engine

    body = FIXTURE.read_bytes()
    session = FakeSession(FakeResponse(200, body))
    raw = EdgarClient(CONTACT, session=session).get(URL)
    engine = get_engine("worker")
    assert store_payload(engine, raw) is True
    assert store_payload(engine, raw) is False  # the same content again adds nothing
    stored = latest_payload(get_engine("api"), "sec-edgar", URL)
    assert stored == body  # as received, byte for byte
    assert len(parse_diluted_eps(stored)) == 6  # parsed from the database, network off
    with get_engine("api").connect() as conn:
        count, digest = conn.execute(text("SELECT count(*), max(sha256) FROM raw_payload")).one()
    assert (count, digest) == (1, raw.sha256)


@pytest.mark.req("DB-11")
@pytest.mark.code("src/earnings/migrations/versions")
def test_raw_payloads_are_insert_only_and_the_length_is_checked(test_db):
    from earnings.db import get_engine

    raw = EdgarClient(CONTACT, session=FakeSession(FakeResponse(200, b"abc"))).get(URL)
    engine = get_engine("worker")
    store_payload(engine, raw)
    for statement, error in (
        ("UPDATE raw_payload SET url = 'x'", "InsufficientPrivilege"),
        ("DELETE FROM raw_payload", "InsufficientPrivilege"),
        (
            "INSERT INTO raw_payload (source, url, retrieved_at, sha256, byte_length, body) "
            "VALUES ('s', 'u', now(), repeat('a', 64), 99, 'abc')",
            "CheckViolation",
        ),
    ):
        with pytest.raises(DBAPIError) as err:
            with engine.begin() as conn:
                conn.execute(text(statement))
        assert type(err.value.orig).__name__ == error


@pytest.mark.req("IG-01")
@pytest.mark.code("src/earnings/rawstore.py", "src/earnings/tasks.py")
def test_fetching_the_same_payload_twice_leaves_an_identical_table_hash(test_db, monkeypatch):
    from earnings import tasks
    from earnings.db import get_engine

    session = FakeSession(FakeResponse(200, FIXTURE.read_bytes()))
    monkeypatch.setattr(tasks, "edgar_client", lambda: EdgarClient(CONTACT, session=session))

    def state():
        with get_engine("api").connect() as conn:
            return table_hash(conn, "raw_payload", ["source", "url", "sha256", "byte_length"])

    first_result = tasks.fetch_company_facts.apply(args=["320193"]).get()
    first = state()
    second_result = tasks.fetch_company_facts.apply(args=["320193"]).get()
    assert (first_result["stored"], second_result["stored"]) == (True, False)
    assert state() == first
