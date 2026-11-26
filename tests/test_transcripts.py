"""Transcripts: cleaning, sections, roles, linking, loading, review sheet
(Ingestion IG-11, IG-14, IG-17, IG-18; Data TX-01, TX-02, TX-05, TX-06;
Product FR-13, PL-06, ER-07).

The excerpts in tests/fixtures/hf_transcript_excerpts.json are REAL rows of the Hugging Face set,
cut to short excerpts (README_universe.md). Rows built by hand in tests are SYNTHETIC and say so.
"""

import json
from datetime import UTC, date, datetime
from pathlib import Path

import pytest
from sqlalchemy import text

from earnings import financials as fin
from earnings import transcripts as tr
from earnings.clients import huggingface as hf
from earnings.clients.edgar import RawResponse
from earnings.rawstore import store_payload

FX = Path(__file__).parent / "fixtures"
EXCERPTS = json.loads((FX / "hf_transcript_excerpts.json").read_text("utf-8"))
ROWS = {r["case"]: r for r in EXCERPTS["rows"]}
AAPL = "0000320193"
SUBMISSIONS = (FX / "aapl_submissions_8k_sample.json").read_bytes()


def _turns(*speakers_texts):
    return [{"speaker": s, "text": t} for s, t in speakers_texts]


@pytest.mark.req("IG-17-AC1", "PL-06-AC1")
@pytest.mark.code("src/earnings/transcripts.py")
def test_the_raw_text_hash_is_identical_before_and_after_cleaning():
    raw = ROWS["winter_call"]["content"]
    before = tr.sha256_text(raw)
    cleaned = tr.clean_text(raw)
    assert tr.sha256_text(raw) == before  # the raw string is not changed
    assert cleaned != "" and tr.CLEANING_RULES_VERSION == "1"


@pytest.mark.req("IG-17-AC2")
@pytest.mark.code("src/earnings/transcripts.py")
def test_the_cleaning_rules_have_a_version_and_only_touch_characters_and_spaces():
    messy = "Hello​  world ’s“quote”\x07\r\n\r\n\r\n\r\nNext\tline  "
    assert tr.clean_text(messy) == 'Hello world \'s"quote"\n\nNext line'
    words = "We will now begin the question-and-answer session. [Operator Instructions]"
    assert tr.clean_text(words) == words  # no words are removed, the stage direction is kept
    assert tr.CLEANING_RULES_VERSION == "1"


@pytest.mark.req("IG-18")
@pytest.mark.code("src/earnings/transcripts.py")
def test_the_boundary_is_the_first_operator_turn_after_two_other_turns_that_mentions_a_question():
    real = ROWS["boundary_after_four_turns"]
    turns = tr.parse_source_row(json.dumps(real).encode()).turns
    assert tr.find_boundary(turns) == real["expected_boundary"]
    # SYNTHETIC cases of the rule
    opening = _turns(
        ("Operator", "A question-and-answer session will follow the formal presentation."),
        ("Ann", "Welcome."), ("Bob", "Results."),
        ("Operator", "We will now begin the question-and-answer session."), ("Carl", "Hi."),
    )  # fmt: skip
    assert tr.find_boundary(opening) == 3  # the opening mention at turn 0 is not the boundary
    early = _turns(("Ann", "Welcome."), ("Operator", "Our first question is from Carl."))
    assert tr.find_boundary(early) is None  # only one turn before it
    instructions = _turns(
        ("Ann", "a"), ("Bob", "b"), ("Operator", "[Operator Instructions] Go ahead.")
    )
    assert tr.find_boundary(instructions) == 2
    assert tr.find_boundary(_turns(("Ann", "a"), ("Bob", "b"), ("Cara", "c"))) is None


@pytest.mark.req("ER-07-AC1", "IG-18-AC2")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_call_with_no_boundary_is_flagged_and_has_no_question_section_or_roles():
    row = ROWS["no_operator_turn"]
    src = tr.parse_source_row(json.dumps(row).encode())
    turns = [{"speaker": t["speaker"], "text": t["text"]} for t in src.turns]
    assert tr.find_boundary(turns) is None
    labelled = tr.label_turns(turns, None)
    assert {t["section"] for t in labelled} == {"prepared"}
    assert {t["role"] for t in labelled} <= {
        "unknown",
        "operator",
    }  # no analyst or management guess


@pytest.mark.req("TX-06-AC1")
@pytest.mark.code("src/earnings/transcripts.py")
def test_every_turn_keeps_its_speaker_and_gets_a_section_and_a_role():
    row = ROWS["boundary_after_four_turns"]
    turns = [{"speaker": t["speaker"], "text": t["text"]} for t in row["structured_content"]]
    boundary = tr.find_boundary(turns)
    labelled = tr.label_turns(turns, boundary)
    assert all(t["speaker"] and t["section"] in ("prepared", "qa") and t["role"] for t in labelled)
    assert labelled[0]["role"] == "operator" and labelled[1]["role"] == "management"
    assert all(t["section"] == "prepared" for t in labelled[:boundary])
    assert all(t["section"] == "qa" for t in labelled[boundary:])
    first_analyst = next(t for t in labelled[boundary:] if not tr.is_operator(t["speaker"]))
    assert first_analyst["role"] == "analyst"  # first spoke after the boundary
    # SYNTHETIC: a management speaker who answers in the Q&A stays management
    synth = tr.label_turns(
        _turns(
            ("Op", "x"),
            ("Ann", "a"),
            ("Bob", "b"),
            ("Operator", "question"),
            ("Dee", "q"),
            ("Ann", "answer"),
        ),
        3,
    )
    assert [t["role"] for t in synth[3:]] == ["operator", "analyst", "management"]


@pytest.mark.req("IG-14-AC1")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_call_is_linked_to_the_release_filed_within_three_days_or_rejected_with_a_reason():
    releases = fin.parse_earnings_releases([SUBMISSIONS])
    linked = tr.link_release(date(2026, 7, 30), releases)
    assert linked is not None and linked.filed == date(2026, 7, 30)
    assert tr.link_release(date(2026, 7, 31), releases).filed == date(2026, 7, 30)  # one day after
    assert tr.link_release(date(2026, 8, 20), releases) is None  # no release near this call
    assert tr.link_release(date(2026, 8, 2), releases).filed == date(2026, 7, 30)  # 3 days: inside
    assert tr.link_release(date(2026, 8, 3), releases) is None  # 4 days: outside
    # SYNTHETIC tie: one day before and one day after; the earlier acceptance time wins
    early = fin.Release("a-1", date(2026, 3, 9), datetime(2026, 3, 9, 21, tzinfo=UTC), "2.02")
    late = fin.Release("a-2", date(2026, 3, 11), datetime(2026, 3, 11, 21, tzinfo=UTC), "2.02")
    assert tr.link_release(date(2026, 3, 10), [late, early]).accession == "a-1"
    row = tr.SourceRow("AAPL", 2026, 3, "2026-08-20 17:00:00", "text", _turns(("A", "x")))
    assert "no earnings release" in tr.prepare(row, AAPL, releases)
    assert (
        tr.prepare(tr.SourceRow("AAPL", 2026, 3, "2026-07-30 17:00:00", "  ", []), AAPL, releases)
        == "empty text"
    )


@pytest.mark.req("TX-02-AC1")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_call_before_the_release_is_noted_and_one_far_after_it_is_a_violation():
    releases = fin.parse_earnings_releases([SUBMISSIONS])
    release = next(r for r in releases if r.filed == date(2026, 7, 30))  # a Thursday
    assert tr.date_check(date(2026, 7, 30), release) is None
    assert tr.date_check(date(2026, 7, 31), release) is None  # one trading day after
    assert "trading days after" in tr.date_check(
        date(2026, 8, 4), release
    )  # Tuesday: 3 trading days
    assert "before the release" in tr.date_check(date(2026, 7, 29), release)
    assert tr.trading_days_between(date(2026, 7, 31), date(2026, 8, 3)) == 1  # over the weekend


def _setup(engine, rows, extra_tickers=()):
    """SYNTHETIC company and ticker, the real Apple release list, and a small parquet of rows."""
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Apple Inc.')"), {"c": AAPL})
        conn.execute(
            text(
                "INSERT INTO ticker_history (company_id, ticker, valid_from) "
                "VALUES (:c, 'AAPL', '2000-01-01')"
            ),
            {"c": AAPL},
        )
    store_payload(engine, RawResponse(
        "sec-edgar", fin.SUBMISSIONS_URL.format(cik=AAPL), 200, "application/json", SUBMISSIONS,
        datetime.now(UTC),
    ))  # fmt: skip
    return rows


def _parquet(path, rows):
    import pyarrow as pa
    import pyarrow.parquet as pq

    cols = [
        "symbol",
        "company_name",
        "company_id",
        "year",
        "quarter",
        "date",
        "content",
        "structured_content",
    ]
    table = pa.Table.from_pylist([{c: r.get(c) for c in cols} for r in rows])
    pq.write_table(table, path)
    return path


def _aapl(case, stamp, **over):
    row = {**ROWS[case], "symbol": "AAPL", "date": stamp, **over}
    return row


@pytest.mark.req("FR-13-AC1", "IG-11-AC1", "TX-05-AC1", "IG-14-AC2")
@pytest.mark.code("src/earnings/transcripts.py", "src/earnings/migrations/versions")
def test_loading_is_idempotent_counts_empty_rows_and_keeps_the_earliest_call_of_a_release(
    test_db, tmp_path, monkeypatch
):
    from earnings.db import get_engine

    worker = get_engine("worker")
    releases = fin.parse_earnings_releases([SUBMISSIONS])
    monkeypatch.setattr(
        tr, "LAST_CALL_DATE", date(2026, 12, 31)
    )  # the Apple release fixture is 2025+
    day = max(r.filed for r in releases)
    good = ROWS["boundary_after_four_turns"]
    rows = [
        {**good, "symbol": "AAPL", "date": f"{day} 17:00:00", "year": 2026, "quarter": 3},
        {**good, "symbol": "AAPL", "date": f"{day} 21:00:00", "year": 2026, "quarter": 3},
        {**good, "symbol": "AAPL", "date": f"{day} 17:00:00", "year": 2026, "quarter": 3},
        {**good, "symbol": "AAPL", "date": "2026-04-28 17:00:00", "year": 2026, "quarter": 2,
         "content": "", "structured_content": []},  # empty text
        {**good, "symbol": "ZZZZ", "date": f"{day} 17:00:00"},  # another company
    ]  # fmt: skip
    _setup(worker, rows)
    parquet = _parquet(tmp_path / "t.parquet", rows)
    monkeypatch.setattr(
        hf, "manifest", lambda path, downloaded: {"revision": hf.REVISION, "bytes": 1}
    )
    report = tr.load_transcripts(worker, parquet, [AAPL], tmp_path / "out")
    assert report["revision"] == hf.REVISION
    assert report["rejected"] == {"empty text": 1}  # counted, and listed in the notes file
    assert report["other_companies"] == 1
    assert report["loaded"] + report["duplicates"] == 3  # the same row twice is one row, not two
    with get_engine("api").connect() as conn:
        counts = conn.execute(
            text("SELECT status, count(*) FROM transcript GROUP BY 1 ORDER BY 1")
        ).all()
        kept = conn.execute(
            text("SELECT call_at FROM transcript WHERE status = 'kept'")
        ).scalar_one()
    assert dict(counts) == {"duplicate": 1, "kept": 1}
    assert kept.hour in (21, 22, 20, 17, 16)  # the earliest call of the two is the one kept
    assert "empty text" in (tmp_path / "out" / "transcript_load_notes.csv").read_text("utf-8")
    again = tr.load_transcripts(worker, parquet, [AAPL], tmp_path / "out")
    with get_engine("api").connect() as conn:
        after = conn.execute(text("SELECT count(*) FROM transcript")).scalar_one()
    assert after == 2 and again["loaded"] == report["loaded"]


@pytest.mark.req("FR-13-AC2")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_load_that_fails_halfway_and_is_run_again_gives_the_row_count_of_a_clean_run(
    test_db, tmp_path, monkeypatch
):
    from earnings.db import get_engine

    worker = get_engine("worker")
    releases = fin.parse_earnings_releases([SUBMISSIONS])
    monkeypatch.setattr(
        tr, "LAST_CALL_DATE", date(2026, 12, 31)
    )  # the Apple release fixture is 2025+
    days = sorted({r.filed for r in releases})[-3:]
    good = ROWS["boundary_after_four_turns"]
    rows = [
        {**good, "symbol": "AAPL", "date": f"{d} 17:00:00", "year": 2024, "quarter": 1}
        for d in days
    ]
    _setup(worker, rows)
    parquet = _parquet(tmp_path / "t.parquet", rows)
    monkeypatch.setattr(
        hf, "manifest", lambda path, downloaded: {"revision": hf.REVISION, "bytes": 1}
    )
    real_insert, calls = tr._insert, []

    def failing(conn, p, status):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("injected failure halfway")
        return real_insert(conn, p, status)

    monkeypatch.setattr(tr, "_insert", failing)
    with pytest.raises(RuntimeError):
        tr.load_transcripts(worker, parquet, [AAPL])
    with get_engine("api").connect() as conn:
        assert (
            conn.execute(text("SELECT count(*) FROM transcript")).scalar_one() == 0
        )  # nothing partial
    monkeypatch.setattr(tr, "_insert", real_insert)
    tr.load_transcripts(worker, parquet, [AAPL])
    with get_engine("api").connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM transcript")).scalar_one() == len(days)


@pytest.mark.req("TX-01-AC1", "PL-06")
@pytest.mark.code("src/earnings/migrations/versions")
def test_a_transcript_row_needs_a_company_a_call_date_and_its_raw_text_with_a_hash(test_db):
    from sqlalchemy.exc import DBAPIError

    from earnings.db import get_engine

    worker = get_engine("worker")
    with worker.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Apple Inc.')"), {"c": AAPL})
    base = (
        "INSERT INTO transcript (company_id, ticker, call_date, source, source_ref, "
        "release_accession, release_accepted_at, raw_text, raw_hash, cleaned_text, "
        "cleaning_rules_version, turns, segmentation_status, boundary_turn) "
        "VALUES ({c}, 'AAPL', {d}, 's', {r}, 'a', now(), {raw}, {h}, 'x', '1', '[]', "
        "'failed', NULL)"
    )
    good = dict(c="'0000320193'", d="'2024-01-01'", r="'r1'", raw="'text'", h=f"'{'a' * 64}'")
    with worker.begin() as conn:
        conn.execute(text(base.format(**good)))
    for bad, name in (
        ({**good, "c": "NULL", "r": "'r2'"}, "NotNullViolation"),
        ({**good, "d": "NULL", "r": "'r3'"}, "NotNullViolation"),
        ({**good, "raw": "''", "r": "'r4'"}, "CheckViolation"),
        ({**good, "h": "'abc'", "r": "'r5'"}, "CheckViolation"),
    ):
        with pytest.raises(DBAPIError) as err:
            with worker.begin() as conn:
                conn.execute(text(base.format(**bad)))
        assert type(err.value.orig).__name__ == name


@pytest.mark.req("IG-18")
@pytest.mark.code("src/earnings/transcripts.py")
def test_the_review_sheet_draws_the_same_calls_every_time_and_shows_the_boundary(test_db, tmp_path):
    from earnings.db import get_engine

    worker = get_engine("worker")
    with worker.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Apple Inc.')"), {"c": AAPL})
        for i in range(8):  # SYNTHETIC kept transcripts
            conn.execute(
                text("INSERT INTO transcript (company_id, ticker, call_date, source, source_ref, "
                     "release_accession, release_accepted_at, raw_text, raw_hash, cleaned_text, "
                     "cleaning_rules_version, turns, segmentation_status, boundary_turn) VALUES "
                     "(:c, 'AAPL', :d, 's', :r, :a, now(), 'text', :h, 'x', '1', "
                     "CAST(:t AS jsonb), 'ok', 1)"),
                {"c": AAPL, "d": date(2020, 1, 1 + i), "r": f"r{i}", "a": f"a{i}", "h": "a" * 64,
                 "t": json.dumps([{"speaker": "Ann", "text": "prepared"},
                                  {"speaker": "Operator", "text": "question"}])},
            )  # fmt: skip
    first = tr.review_sheet(worker, 5, tmp_path / "s1.md", tmp_path / "i1.csv")
    second = tr.review_sheet(worker, 5, tmp_path / "s2.md", tmp_path / "i2.csv")
    assert first == second and len(set(first)) == 5  # fixed seed, no repeats
    sheet = (tmp_path / "s1.md").read_text("utf-8")
    assert sheet.count("BOUNDARY >>") == 5 and sheet.count("Verdict ->") == 5


@pytest.mark.req("IG-11")
@pytest.mark.code("src/earnings/clients/huggingface.py")
def test_the_download_is_refused_when_the_size_or_checksum_does_not_match(tmp_path, monkeypatch):
    from earnings.clients.edgar import SourceError

    class Response:
        status_code = 200

        def __init__(self, body):
            self.body = body

        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False

        def iter_content(self, n):
            yield self.body

    class Session:
        def __init__(self, body):
            self.body = body

        def get(self, url, **kw):
            assert url == hf.URL and "stream" in kw
            return Response(self.body)

    dest = tmp_path / "part-0.parquet"
    with pytest.raises(SourceError):
        hf.download(dest, Session(b"SYNTHETIC wrong bytes"))
    assert not dest.exists() and not dest.with_suffix(".part").exists()
    body = b"SYNTHETIC pretend file"
    import hashlib

    monkeypatch.setattr(hf, "EXPECTED_BYTES", len(body))
    monkeypatch.setattr(hf, "EXPECTED_SHA256", hashlib.sha256(body).hexdigest())
    info = hf.download(dest, Session(body))
    assert info["downloaded_now"] is True and dest.read_bytes() == body
    assert hf.download(dest, Session(b"never used"))["downloaded_now"] is False  # already there


def _fixture_row(case, symbol, stamp):
    return {**ROWS[case], "symbol": symbol, "date": stamp, "year": 2026, "quarter": 3}


@pytest.mark.req("FR-15-AC1", "FR-15-AC2", "ER-07-AC2", "TX-06-AC1")
@pytest.mark.code("src/earnings/transcripts.py")
def test_sections_are_stored_apart_and_a_call_without_a_boundary_has_no_question_section(
    test_db, tmp_path, monkeypatch
):
    from earnings.db import get_engine

    worker = get_engine("worker")
    monkeypatch.setattr(tr, "LAST_CALL_DATE", date(2026, 12, 31))
    monkeypatch.setattr(hf, "manifest", lambda path, downloaded: {"revision": hf.REVISION})
    d1, d2 = sorted({r.filed for r in fin.parse_earnings_releases([SUBMISSIONS])})[-2:]
    rows = [
        _fixture_row("boundary_after_four_turns", "AAPL", f"{d1} 17:00:00"),
        _fixture_row("no_operator_turn", "AAPL", f"{d2} 17:00:00"),
    ]
    _setup(worker, rows)
    tr.load_transcripts(worker, _parquet(tmp_path / "t.parquet", rows), [AAPL])
    with get_engine("api").connect() as conn:
        status = {
            r[0]: r[1:]
            for r in conn.execute(
                text("SELECT call_date, segmentation_status, boundary_turn FROM transcript")
            )
        }
        kinds = {
            (r[0], r[1])
            for r in conn.execute(
                text(
                    "SELECT t.call_date, s.kind FROM transcript_section s "
                    "JOIN transcript t USING (transcript_id)"
                )
            )
        }
        turns = conn.execute(text("SELECT turns FROM transcript")).scalars().all()
    assert status[d1] == ("ok", 4) and status[d2] == ("failed", None)
    assert (d1, "prepared") in kinds and (d1, "qa") in kinds  # stored separately
    assert (d2, "qa") not in kinds  # unavailable, not an empty or zero section
    assert all(t["speaker"] and t["role"] and t["section"] for ts in turns for t in ts)


@pytest.mark.req("TX-01-AC2")
@pytest.mark.code("src/earnings/transcripts.py")
def test_rows_without_a_ticker_or_a_valid_call_date_are_rejected_and_listed(
    test_db, tmp_path, monkeypatch
):
    from earnings.db import get_engine

    worker = get_engine("worker")
    monkeypatch.setattr(hf, "manifest", lambda path, downloaded: {"revision": hf.REVISION})
    day = max(r.filed for r in fin.parse_earnings_releases([SUBMISSIONS]))
    rows = [
        _fixture_row("boundary_after_four_turns", None, f"{day} 17:00:00"),  # SYNTHETIC defects
        _fixture_row("boundary_after_four_turns", "AAPL", "not a date"),
        _fixture_row("boundary_after_four_turns", "AAPL", ""),
    ]
    _setup(worker, rows)
    report = tr.load_transcripts(
        worker, _parquet(tmp_path / "t.parquet", rows), [AAPL], tmp_path / "out"
    )
    assert report["rejected"] == {"missing ticker": 1, "missing or invalid call date": 2}
    assert report["loaded"] == 0
    notes = (tmp_path / "out" / "transcript_load_notes.csv").read_text("utf-8")
    assert "missing ticker" in notes and "missing or invalid call date" in notes


@pytest.mark.req("IG-10-AC1")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_stored_payload_is_parsed_with_the_network_disabled(test_db, monkeypatch):
    import socket

    from earnings.db import get_engine

    worker = get_engine("worker")
    row = {**ROWS["winter_call"], "symbol": "AAPL"}
    raw = tr.row_payload(row)
    store_payload(worker, raw)
    with worker.connect() as conn:  # read the database first, then cut the network
        body = conn.execute(
            text("SELECT body FROM raw_payload WHERE source = :s"), {"s": hf.SOURCE}
        ).scalar_one()

    def refuse(*a, **k):
        raise AssertionError("network used")

    monkeypatch.setattr(socket.socket, "connect", refuse)
    parsed = tr.parse_source_row(bytes(body))
    assert parsed.symbol == "AAPL" and len(parsed.turns) == len(row["structured_content"])


@pytest.mark.req("IG-12-AC2")
def test_the_transcript_fixture_states_its_origin_and_which_rows_are_real():
    assert EXCERPTS["source"] == "kurry/sp500_earnings_transcripts"
    assert EXCERPTS["revision"] == hf.REVISION
    assert "REAL rows" in EXCERPTS["note"]


@pytest.mark.req("TX-02")
@pytest.mark.code("src/earnings/transcripts.py", "src/earnings/calendar.py")
def test_one_trading_day_is_counted_with_exchange_holidays():
    # SYNTHETIC release on Friday 12 January 2024; Monday 15 January was an exchange holiday
    release = fin.Release("a", date(2024, 1, 12), datetime(2024, 1, 12, 13, tzinfo=UTC), "2.02")
    assert tr.trading_days_between(date(2024, 1, 12), date(2024, 1, 16)) == 1
    assert tr.date_check(date(2024, 1, 16), release) is None
    assert "2 trading days after" in tr.date_check(date(2024, 1, 17), release)
