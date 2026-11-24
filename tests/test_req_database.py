"""Tests for the database requirements (database-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that calls
not_tested() is a placeholder for code that does not exist yet. It is skipped and reported as
NOT TESTED, never as passed. Replace the call with a real check when the code is built
(Deterministic_audit.md, Phase D).
"""

import ast
import re
import threading
import time

import psycopg
import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError, IntegrityError

from db_support import assert_test_database, project_database
from requirement_support import ROOT, not_tested

_OTHER_DATABASES = {"sqlite3", "pymongo", "mysql", "duckdb", "lmdb", "shelve", "dbm", "tinydb"}


@pytest.mark.req("DB-01-AC1")
@pytest.mark.code("src/earnings/db.py", "src/earnings/config.py")
def test_db_01_ac1_the_code_uses_no_database_other_than_postgresql():
    imported = set()
    for path in (ROOT / "src" / "earnings").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
    assert not imported & _OTHER_DATABASES, imported & _OTHER_DATABASES


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
def _app_url(role, database):
    from earnings.config import get_settings

    return get_settings().database_url_for(role, database)


def _admin(database):
    import os

    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"],
        user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        dbname=database,
        autocommit=True,
    )


@pytest.mark.req("DB-01-AC2")
@pytest.mark.code("src/earnings/migrations/versions", "src/earnings/migrate.py")
def test_db_01_ac2_the_extension_list_matches_the_migrations(test_db_name):
    created = set()
    for path in (ROOT / "src" / "earnings" / "migrations" / "versions").glob("*.py"):
        created |= set(
            re.findall(r"CREATE EXTENSION (?:IF NOT EXISTS )?(\w+)", path.read_text("utf-8"), re.I)
        )
    with _admin(test_db_name) as conn:
        installed = {row[0] for row in conn.execute("SELECT extname FROM pg_extension")}
    assert installed == created | {"plpgsql"}


def _try(role, database, statement, params=None):
    """Run one statement as a role. Returns None on success or the database error class name."""
    from sqlalchemy import create_engine
    from sqlalchemy.pool import NullPool

    engine = create_engine(_app_url(role, database), poolclass=NullPool)
    try:
        with engine.begin() as conn:
            conn.execute(text(statement), params or {})
        return None
    except DBAPIError as exc:
        return type(exc.orig).__name__
    finally:
        engine.dispose()


@pytest.mark.req("DB-02")
@pytest.mark.code("src/earnings/migrate.py", "src/earnings/config.py")
def test_db_02_migrator_worker_and_api_roles_allowed_and_forbidden(test_db):
    insert = "INSERT INTO company (company_id, name) VALUES ('0000000001', 'SYNTHETIC test row')"
    # api: reads, never writes
    assert _try("api", test_db, "SELECT count(*) FROM company") is None
    assert _try("api", test_db, insert) == "InsufficientPrivilege"
    # worker: writes rows, cannot delete them or change the schema
    assert _try("worker", test_db, insert) is None
    assert _try("worker", test_db, "DELETE FROM company") == "InsufficientPrivilege"
    assert _try("worker", test_db, "CREATE TABLE x (a int)") == "InsufficientPrivilege"
    # migrator: changes the schema
    assert _try("migrator", test_db, "CREATE TABLE scratch_probe (a int)") is None
    assert _try("migrator", test_db, "DROP TABLE scratch_probe") is None
    with _admin(test_db) as conn:
        rows = conn.execute(
            "SELECT rolname, rolsuper FROM pg_roles WHERE rolname LIKE 'earnings\\_%'"
        ).fetchall()
    assert {r[0] for r in rows} >= {"earnings_migrator", "earnings_worker", "earnings_api"}
    assert not any(r[1] for r in rows), "an application role is a superuser"


@pytest.mark.req("DB-02-AC1")
@pytest.mark.xfail(
    strict=True,
    reason="NOT SATISFIED: the explanation agent role is created with the explanation tables",
)
@pytest.mark.code("src/earnings/migrate.py")
def test_db_02_ac1_each_role_is_tested_for_one_allowed():
    """DB-02-AC1: Each role is tested for one allowed and one forbidden statement."""
    with _admin("postgres") as conn:
        names = {r[0] for r in conn.execute("SELECT rolname FROM pg_roles")}
    assert {"earnings_migrator", "earnings_worker", "earnings_api", "earnings_agent"} <= names


@pytest.mark.req("DB-03-AC1")
@pytest.mark.code("src/earnings/db.py", "src/earnings/config.py")
def test_db_03_ac1_a_load_fixture_with_more_clients_than(test_db):
    """DB-03-AC1: A load fixture with more clients than the pool does not exhaust connections."""
    from earnings.db import MAX_OVERFLOW, POOL_SIZE, get_engine

    clients, failures = 30, []
    peak_server, peak_pool = [0], [0]
    engine = get_engine("api")  # 5 connections plus 5 overflow, so 30 clients must queue
    done = threading.Event()

    def one_client():
        try:
            with engine.connect() as conn:
                conn.execute(text("SELECT pg_sleep(0.2)"))
        except Exception as exc:  # noqa: BLE001  record any failure for the assertion below
            failures.append(type(exc).__name__)

    def watch():
        with _admin("postgres") as conn:
            while not done.is_set():
                n = conn.execute(
                    "SELECT count(*) FROM pg_stat_activity "
                    "WHERE usename = 'earnings_api' AND datname = %s",
                    (test_db,),
                ).fetchone()[0]
                peak_server[0] = max(peak_server[0], n)
                peak_pool[0] = max(peak_pool[0], engine.pool.checkedout())
                time.sleep(0.02)

    threads = [threading.Thread(target=one_client) for _ in range(clients)]
    watcher = threading.Thread(target=watch)
    watcher.start()
    for th in threads:
        th.start()
    for th in threads:
        th.join()
    done.set()
    watcher.join()
    assert failures == []
    assert 0 < peak_pool[0] <= POOL_SIZE + MAX_OVERFLOW  # the pool never lends more than 10
    # The server may briefly show one or two more while closed overflow connections linger.
    assert 0 < peak_server[0] <= POOL_SIZE + MAX_OVERFLOW + 2, f"peak connections {peak_server[0]}"


@pytest.mark.req("DB-03")
@pytest.mark.code("src/earnings/db.py", "src/earnings/migrate.py")
def test_the_pool_and_time_out_values_are_the_ones_approved_in_decision_c_44():
    from earnings import migrate
    from earnings.db import MAX_OVERFLOW, POOL_SIZE, POOL_TIMEOUT_SECONDS, get_engine

    assert (POOL_SIZE, MAX_OVERFLOW, POOL_TIMEOUT_SECONDS) == (5, 5, 10)
    assert get_engine("api").pool._pre_ping is True
    assert migrate.STATEMENT_TIMEOUT_SECONDS == {"migrator": 300, "worker": 120, "api": 10}
    assert (migrate.LOCK_TIMEOUT_SECONDS, migrate.IDLE_IN_TRANSACTION_TIMEOUT_SECONDS) == (5, 60)


@pytest.mark.req("DB-02")
@pytest.mark.code("src/earnings/migrate.py")
def test_the_application_roles_cannot_connect_to_the_postgres_database(test_db):
    # The refusal comes at connection time, so it is an OperationalError about permission.
    for role in ("worker", "api"):
        assert _try(role, test_db, "SELECT 1") is None  # their own database works
        assert _try(role, "postgres", "SELECT 1") == "OperationalError"


@pytest.mark.req("DB-03-AC2")
@pytest.mark.code("src/earnings/migrate.py")
def test_db_03_ac2_a_long_query_is_cancelled(test_db):
    started = time.monotonic()
    assert _try("api", test_db, "SELECT pg_sleep(30)") == "QueryCanceled"
    assert time.monotonic() - started < 15  # the api role's limit is 10 seconds
    with _admin(test_db) as conn:
        cfg = {
            r[0]: r[1]
            for r in (
                x[0].split("=", 1)
                for x in conn.execute(
                    "SELECT unnest(rolconfig) FROM pg_roles WHERE rolname = 'earnings_worker'"
                ).fetchall()
            )
        }
    assert cfg["statement_timeout"] == "120s"
    assert cfg["lock_timeout"] == "5s"
    assert cfg["idle_in_transaction_session_timeout"] == "60s"


@pytest.mark.req("DB-05-AC1")
def test_db_05_ac1_inserting_a_duplicate_of_each_fails():
    """DB-05-AC1: Inserting a duplicate of each fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-06-AC1")
def test_db_06_ac1_insert_of_an_out_of_range_probability():
    """DB-06-AC1: Insert of an out-of-range probability fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-07-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_db_07_ac1_schema_query_finds_no_timestamp_without_zone(test_db_name):
    # Guards every later table too: the company table has no time column yet.
    with _admin(test_db_name) as conn:
        bad = conn.execute(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' AND data_type = 'timestamp without time zone'"
        ).fetchall()
    assert bad == []


@pytest.mark.req("DB-12-AC1")
def test_db_12_ac1_insert_of_a_featurevector_without_a_feature():
    """DB-12-AC1: Insert of a FeatureVector without a feature-set version fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-13-AC1")
def test_db_13_ac1_fault_injected_mid_event_leaves_no_rows():
    """DB-13-AC1: Fault injected mid-event leaves no rows for that event."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-13-AC2")
def test_db_13_ac2_re_running_a_stage_leaves_the_row():
    """DB-13-AC2: Re-running a stage leaves the row count unchanged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-14-AC1")
def test_db_14_ac1_explain_output_for_each_named_query_is():
    """DB-14-AC1: `EXPLAIN` output for each named query is stored and shows an index scan on
    the loaded 100-company data.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-15-AC1")
def test_db_15_ac1_size_report_exists():
    """DB-15-AC1: Size report exists."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DB-16")
@pytest.mark.code("src/earnings/migrate.py")
def test_the_functions_that_drop_or_empty_a_database_refuse_a_project_database_name():
    from earnings import migrate

    for name in (project_database(), "postgres", "production"):
        with pytest.raises(RuntimeError):
            migrate.drop_database(name)
        with pytest.raises(RuntimeError):
            migrate.truncate_all(name)


@pytest.mark.req("DB-02")
@pytest.mark.code("docker-compose.yml")
def test_the_worker_service_does_not_receive_the_superuser_password():
    import yaml

    from requirement_support import repo_path

    compose = yaml.safe_load(repo_path("docker-compose.yml").read_text("utf-8"))["services"]
    for forbidden in ("POSTGRES_PASSWORD", "POSTGRES_USER"):
        assert forbidden not in compose["worker"]["environment"]
    assert (
        "POSTGRES_PASSWORD" in compose["migrate"]["environment"]
    )  # only the migration step needs it


@pytest.mark.req("DB-16-AC1")
@pytest.mark.code("tests/db_support.py", "tests/conftest.py")
def test_db_16_ac1_the_test_configuration_refuses_to_start_against():
    """DB-16-AC1: The test configuration refuses to start against the project database name."""
    with pytest.raises(RuntimeError):
        assert_test_database(project_database())
    with pytest.raises(RuntimeError):
        assert_test_database("production")
    assert assert_test_database(project_database() + "_test").endswith("_test")


@pytest.mark.req("DB-04")
@pytest.mark.code("src/earnings/identifiers.py", "src/earnings/migrations/versions")
def test_db_04_company_id_is_one_canonical_cik_form(test_db):
    from earnings.identifiers import canonical_cik

    assert canonical_cik("320193") == "0000320193"
    assert canonical_cik(320193) == "0000320193"
    for bad in ("", "abc", "12345678901", "-5", "AAPL"):
        with pytest.raises(ValueError):
            canonical_cik(bad)
    # The database refuses a company_id that is not in the canonical form, such as a ticker.
    assert _try("migrator", test_db, "INSERT INTO company VALUES ('AAPL', 'x')") == "CheckViolation"
    assert (
        _try("migrator", test_db, "INSERT INTO company VALUES ('320193', 'x')") == "CheckViolation"
    )


@pytest.mark.req("DB-04")
@pytest.mark.code("src/earnings/migrations/versions")
def test_no_table_uses_a_ticker_as_its_key(test_db_name):
    """The ticker is an attribute of ticker_history, never a primary key or a lone unique key."""
    with _admin(test_db_name) as conn:
        keys = conn.execute(
            "SELECT t.relname, a.attname FROM pg_index i JOIN pg_class t ON t.oid = i.indrelid "
            "JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = ANY (i.indkey) "
            "WHERE i.indisunique AND t.relnamespace = 'public'::regnamespace AND "
            "a.attname = 'ticker' AND i.indnatts = 1 AND NOT i.indisexclusion"
        ).fetchall()
    assert keys == []  # no unique or primary key made of a ticker column alone


@pytest.mark.req("DB-05")
@pytest.mark.code("src/earnings/migrations/versions")
def test_db_05_company_duplicate_is_refused_by_the_database(test_db):
    """First case of DB-05 only (company). The other keys arrive with their tables."""
    from earnings.db import get_engine

    sql = text("INSERT INTO company (company_id, name) VALUES ('0000320193', 'SYNTHETIC test row')")
    with get_engine("worker").begin() as conn:
        conn.execute(sql)
    with pytest.raises(IntegrityError):
        with get_engine("worker").begin() as conn:
            conn.execute(sql)


@pytest.mark.req("DB-17-AC1")
def test_db_17_ac1_section_11_matches_the_migrated_schema():
    """DB-17-AC1: Section 11 matches the migrated schema."""
    not_tested("BLOCKED", "waits for open decision D-38")
