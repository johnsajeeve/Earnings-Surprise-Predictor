"""Storage rules: append-only tables, the as-of read, validity periods, payload hashes
(Database DB-08, DB-09, DB-10; Data SR-04).

Rows written here are synthetic and say so.
"""

from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import psycopg
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from db_support import find_direct_reads
from earnings import consensus
from earnings.clients.edgar import RawResponse
from earnings.rawstore import store_payload, verify_hashes
from earnings.schema import APPEND_ONLY_TABLES, AS_OF_FUNCTIONS

ROOT = Path(__file__).resolve().parents[1]
D1, D3 = consensus.CAPTURE_START + timedelta(hours=1), consensus.CAPTURE_START + timedelta(days=2)


def _admin(database):
    import os

    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=database,
        autocommit=True,
    )


def _error(engine, statement, params=None):
    try:
        with engine.begin() as conn:
            conn.execute(text(statement), params or {})
        return None
    except DBAPIError as exc:
        return type(exc.orig).__name__


def _company(engine, company_id, name="SYNTHETIC test row"):
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO company VALUES (:c, :n) ON CONFLICT DO NOTHING"),
            {"c": company_id, "n": name},
        )


def _snapshot(engine, captured_at, mean=1.0, company="0000320193", period="0q"):
    _company(engine, company)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, source, "
                "source_version, captured_at, raw_payload) VALUES (:c, :m, :p, 'synthetic-test', "
                "'x', :t, '{}')"
            ),
            {"c": company, "m": mean, "p": period, "t": captured_at},
        )


@pytest.mark.req("DB-08-AC1")
@pytest.mark.code("src/earnings/schema.py", "src/earnings/migrations/versions")
@pytest.mark.parametrize("table", APPEND_ONLY_TABLES)
def test_the_worker_role_cannot_update_or_delete_an_append_only_table(test_db, table):
    from earnings.db import get_engine

    engine = get_engine("worker")
    column = {"estimate_snapshot": "source", "raw_payload": "source", "dead_letter": "task_name"}[
        table
    ]
    assert _error(engine, f"UPDATE {table} SET {column} = 'x'") == "InsufficientPrivilege"
    assert _error(engine, f"DELETE FROM {table}") == "InsufficientPrivilege"


@pytest.mark.req("DB-08")
@pytest.mark.code("src/earnings/schema.py", "src/earnings/migrations/versions")
def test_the_append_only_registry_matches_the_privileges_in_the_database(test_db_name):
    with _admin(test_db_name) as conn:
        rows = conn.execute(
            "SELECT t.table_name, has_table_privilege('earnings_worker', "
            "quote_ident(t.table_name), 'UPDATE') FROM information_schema.tables t "
            "WHERE t.table_schema = 'public' AND t.table_type = 'BASE TABLE'"
        ).fetchall()
    without_update = {name for name, can_update in rows if not can_update}
    # The migration history is the migrator's alone, so it is also closed to the worker.
    assert without_update == set(APPEND_ONLY_TABLES) | {"alembic_version"}


@pytest.mark.req("DB-09-AC1")
@pytest.mark.code("src/earnings/migrations/versions", "src/earnings/schema.py")
def test_a_planted_version_dated_d_or_later_is_not_returned(test_db):
    from earnings.db import get_engine

    assert AS_OF_FUNCTIONS["estimate_snapshot"] == "estimate_snapshot_as_of"
    worker, api = get_engine("worker"), get_engine("api")
    _snapshot(worker, D1, mean=1.0)
    _snapshot(worker, D3, mean=9.0)  # the planted version: stamped exactly at D
    _snapshot(worker, D3 + timedelta(days=1), mean=8.0)  # and one a day after D

    def as_of(moment):
        with api.connect() as conn:
            return [
                float(r[0])
                for r in conn.execute(
                    text("SELECT mean_estimate FROM estimate_snapshot_as_of('0000320193', :d)"),
                    {"d": moment},
                )
            ]

    assert as_of(D3) == [1.0]  # strictly before D: the row at D itself is not known yet
    assert as_of(D3 + timedelta(microseconds=1)) == [9.0]  # one microsecond later it is
    assert as_of(D1) == []  # nothing before the first capture


@pytest.mark.req("DB-09")
@pytest.mark.code("src/earnings/migrations/versions")
def test_the_as_of_read_returns_one_latest_row_per_source_and_period(test_db):
    from earnings.db import get_engine

    worker, api = get_engine("worker"), get_engine("api")
    _snapshot(worker, D1, mean=1.0, period="0q")
    _snapshot(worker, D1 + timedelta(days=1), mean=2.0, period="0q")
    _snapshot(worker, D1, mean=5.0, period="+1q")
    with api.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT period_label, mean_estimate FROM estimate_snapshot_as_of('0000320193', :d)"
            ),
            {"d": D3},
        ).all()
    assert {p: float(m) for p, m in rows} == {"+1q": 5.0, "0q": 2.0}  # one row per period


@pytest.mark.req("DB-09-AC2")
@pytest.mark.code("src/earnings", "tests/db_support.py")
def test_no_feature_code_reads_a_versioned_table_directly():
    tables = list(AS_OF_FUNCTIONS)
    features = ROOT / "src" / "earnings" / "features"
    offenders = {
        str(p.relative_to(ROOT)): find_direct_reads(p.read_text("utf-8"), tables)
        for p in (features.rglob("*.py") if features.exists() else [])
    }
    assert {k: v for k, v in offenders.items() if v} == {}
    # The detector itself finds a direct read and ignores a read through the function.
    assert find_direct_reads("SELECT * FROM estimate_snapshot WHERE a", tables) == [
        "estimate_snapshot"
    ]
    assert find_direct_reads("SELECT * FROM estimate_snapshot_as_of('x', now())", tables) == []


def _tickers(engine):
    _company(engine, "0000000001")
    _company(engine, "0000000002")
    return engine


@pytest.mark.req("DB-10-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_an_overlapping_membership_insert_fails(test_db):
    from earnings.db import get_engine

    engine = _tickers(get_engine("worker"))
    insert = "INSERT INTO index_membership (company_id, valid_from, valid_to) VALUES (:c, :f, :t)"
    for args in (
        {"c": "0000000001", "f": date(2020, 1, 1), "t": date(2021, 1, 1)},
        {"c": "0000000001", "f": date(2021, 1, 1), "t": None},  # starts where the last ends: fine
    ):
        assert _error(engine, insert, args) is None
    overlap = {"c": "0000000001", "f": date(2020, 6, 1), "t": date(2020, 7, 1)}
    assert _error(engine, insert, overlap) == "ExclusionViolation"
    other = {"c": "0000000002", "f": date(2020, 6, 1), "t": date(2020, 7, 1)}
    assert _error(engine, insert, other) is None  # another company is not affected
    backwards = {"c": "0000000002", "f": date(2022, 1, 1), "t": date(2021, 1, 1)}
    assert _error(engine, insert, backwards) == "CheckViolation"


@pytest.mark.req("DB-10-AC2")
@pytest.mark.code("src/earnings/migrations/versions")
def test_a_date_on_a_boundary_resolves_to_exactly_one_period(test_db):
    from earnings.db import get_engine

    engine = _tickers(get_engine("worker"))
    insert = (
        "INSERT INTO ticker_history (company_id, ticker, valid_from, valid_to) "
        "VALUES (:c, :t, :f, :to)"
    )
    for args in (
        {"c": "0000000001", "t": "OLD", "f": date(2015, 1, 1), "to": date(2020, 1, 1)},
        {"c": "0000000001", "t": "NEW", "f": date(2020, 1, 1), "to": None},
    ):
        assert _error(engine, insert, args) is None
    with get_engine("api").connect() as conn:

        def company_on(ticker, day):
            return conn.execute(
                text("SELECT company_for_ticker(:t, :d)"), {"t": ticker, "d": day}
            ).scalar_one()

        assert company_on("OLD", date(2019, 12, 31)) == "0000000001"
        assert company_on("OLD", date(2020, 1, 1)) is None  # the end date is not in the period
        assert company_on("NEW", date(2020, 1, 1)) == "0000000001"  # and the next period starts
        assert company_on("NEW", date(2019, 12, 31)) is None


@pytest.mark.req("DB-10")
@pytest.mark.code("src/earnings/migrations/versions")
def test_two_share_classes_can_coexist_but_a_ticker_belongs_to_one_company(test_db):
    from earnings.db import get_engine

    engine = _tickers(get_engine("worker"))
    insert = (
        "INSERT INTO ticker_history (company_id, ticker, valid_from) VALUES (:c, :t, '2020-01-01')"
    )
    assert _error(engine, insert, {"c": "0000000001", "t": "AAA"}) is None
    assert _error(engine, insert, {"c": "0000000001", "t": "AAB"}) is None  # two classes, one firm
    assert _error(engine, insert, {"c": "0000000002", "t": "AAA"}) == "ExclusionViolation"
    assert _error(engine, insert, {"c": "0000000001", "t": "AAA"}) == "ExclusionViolation"


@pytest.mark.req("SR-04-AC1")
@pytest.mark.code("src/earnings/rawstore.py")
def test_the_hash_of_each_stored_raw_payload_matches_the_hash_recorded(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    for n in range(3):
        raw = RawResponse(
            "synthetic", f"https://example.invalid/{n}", 200, "text/plain",
            f"payload {n}".encode(), datetime.now(UTC),
        )  # fmt: skip
        assert store_payload(engine, raw)
    assert verify_hashes(get_engine("api")) == []
    # Tamper with one body, keeping its length, as only the superuser could.
    with _admin(test_db) as conn:
        conn.execute("UPDATE raw_payload SET body = 'PAYLOAD 1'::bytea WHERE url LIKE '%/1'")
    bad = verify_hashes(get_engine("api"))
    assert len(bad) == 1
