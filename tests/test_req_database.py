"""Tests for the database requirements (database-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that calls
not_tested() is a placeholder for code that does not exist yet. It is skipped and reported as
NOT TESTED, never as passed. Replace the call with a real check when the code is built
(Deterministic_audit.md, Phase D).
"""

import ast

import pytest

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
@pytest.mark.req("DB-01-AC2")
def test_db_01_ac2_the_extension_list_matches_the_migrations():
    """DB-01-AC2: The extension list matches the migrations."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-02-AC1")
def test_db_02_ac1_each_role_is_tested_for_one_allowed():
    """DB-02-AC1: Each role is tested for one allowed and one forbidden statement."""
    not_tested("BLOCKED", "waits for open decision D-38")


@pytest.mark.req("DB-03-AC1")
def test_db_03_ac1_a_load_fixture_with_more_clients_than():
    """DB-03-AC1: A load fixture with more clients than the pool does not exhaust connections."""
    not_tested("BLOCKED", "waits for open decision D-38")


@pytest.mark.req("DB-03-AC2")
def test_db_03_ac2_a_long_query_is_cancelled():
    """DB-03-AC2: A long query is cancelled."""
    not_tested("BLOCKED", "waits for open decision D-38")


@pytest.mark.req("DB-04-AC1")
def test_db_04_ac1_join_on_company_id_across_ten_known():
    """DB-04-AC1: Join on `company_id` across ten known ticker changes gives one history
    (Data IM-03).
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-05-AC1")
def test_db_05_ac1_inserting_a_duplicate_of_each_fails():
    """DB-05-AC1: Inserting a duplicate of each fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-06-AC1")
def test_db_06_ac1_insert_of_an_out_of_range_probability():
    """DB-06-AC1: Insert of an out-of-range probability fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-07-AC1")
def test_db_07_ac1_schema_query_finds_no_timestamp_without_zone():
    """DB-07-AC1: Schema query finds no timestamp-without-zone column."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-08-AC1")
def test_db_08_ac1_the_worker_role_s_update_on_each():
    """DB-08-AC1: The worker role's UPDATE on each such table fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-09-AC1")
def test_db_09_ac1_a_planted_version_dated_d_or_later():
    """DB-09-AC1: A planted version dated D or later is not returned."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-09-AC2")
def test_db_09_ac2_a_test_finds_no_direct_read_of():
    """DB-09-AC2: A test finds no direct read of a versioned table in the feature code."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-10-AC1")
def test_db_10_ac1_an_overlapping_membership_insert_fails():
    """DB-10-AC1: An overlapping membership insert fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-10-AC2")
def test_db_10_ac2_a_date_on_a_boundary_resolves_to():
    """DB-10-AC2: A date on a boundary resolves to exactly one period."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-11-AC1")
def test_db_11_ac1_rebuild_from_stored_payloads_gives_identical_table():
    """DB-11-AC1: Rebuild from stored payloads gives identical table hashes (Data DV-08)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


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


@pytest.mark.req("DB-16-AC1")
def test_db_16_ac1_the_test_configuration_refuses_to_start_against():
    """DB-16-AC1: The test configuration refuses to start against the project database name."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DB-17-AC1")
def test_db_17_ac1_section_11_matches_the_migrated_schema():
    """DB-17-AC1: Section 11 matches the migrated schema."""
    not_tested("BLOCKED", "waits for open decision D-38")
