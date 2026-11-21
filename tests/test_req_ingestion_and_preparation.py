"""Tests for the ingestion and preparation requirements (ingestion-and-preparation-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that
calls not_tested() is a placeholder for code that does not exist yet. It is skipped and
reported as NOT TESTED, never as passed. Replace the call with a real check when the
code is built (Deterministic_audit.md, Phase D).
"""

import pytest

from requirement_support import not_tested


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("IG-01-AC1")
def test_ig_01_ac1_running_the_same_task_twice_gives_an():
    """IG-01-AC1: Running the same task twice gives an identical table hash."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-01-AC2")
def test_ig_01_ac2_killing_a_worker_mid_task_and_restarting():
    """IG-01-AC2: Killing a worker mid-task and restarting gives the row count of a clean run."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-02-AC1")
def test_ig_02_ac1_an_injected_failure_produces_three_retries_and():
    """IG-02-AC1: An injected failure produces three retries and one dead-letter row."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-03-AC1")
def test_ig_03_ac1_each_run_produces_a_queryable_row():
    """IG-03-AC1: Each run produces a queryable row."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-03-AC2")
def test_ig_03_ac2_a_forced_error_gives_status_failed():
    """IG-03-AC2: A forced error gives status failed."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-04-AC1")
def test_ig_04_ac1_the_longest_task_in_the_100_company():
    """IG-04-AC1: The longest task in the 100-company run finishes inside the timeout, and
    the setting is recorded.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IG-05-AC1")
def test_ig_05_ac1_the_schedule_file_lists_each_job_with():
    """IG-05-AC1: The schedule file lists each job with its time."""
    not_tested("BLOCKED", "waits for open decision D-45")


@pytest.mark.req("IG-05-AC2")
def test_ig_05_ac2_a_job_missing_from_the_file_does():
    """IG-05-AC2: A job missing from the file does not run."""
    not_tested("BLOCKED", "waits for open decision D-45")


@pytest.mark.req("IG-06-AC1")
def test_ig_06_ac1_simulated_4_day_gap_is_reported_and():
    """IG-06-AC1: Simulated 4-day gap is reported and the affected events carry the flag."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-07-AC1")
def test_ig_07_ac1_test_with_a_mocked_clock_shows_no():
    """IG-07-AC1: Test with a mocked clock shows no more than 10 EDGAR requests in any
    second and no more than 25 Alpha Vantage requests in a day.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-08-AC1")
def test_ig_08_ac1_with_the_variable_unset_the_client_raises():
    """IG-08-AC1: With the variable unset, the client raises an error and sends nothing."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-09-AC1")
def test_ig_09_ac1_backfill_of_the_100_company_subset_uses():
    """IG-09-AC1: Backfill of the 100-company subset uses the bulk files, and the request
    count is recorded.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IG-10-AC1")
def test_ig_10_ac1_parsing_runs_from_stored_payloads_with_the():
    """IG-10-AC1: Parsing runs from stored payloads with the network disabled."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-11-AC1")
def test_ig_11_ac1_load_report_shows_the_revision_and_the():
    """IG-11-AC1: Load report shows the revision and the number of empty rows rejected."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-12-AC1")
def test_ig_12_ac1_tests_pass_with_the_network_disabled():
    """IG-12-AC1: Tests pass with the network disabled."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-12-AC2")
def test_ig_12_ac2_fixtures_state_their_origin():
    """IG-12-AC2: Fixtures state their origin."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-13-AC1")
def test_ig_13_ac1_ten_known_renames_give_one_continuous_history():
    """IG-13-AC1: Ten known renames give one continuous history."""
    not_tested("BLOCKED", "waits for open decision D-32")


@pytest.mark.req("IG-13-AC2")
def test_ig_13_ac2_every_name_match_appears_in_the_review():
    """IG-13-AC2: Every name match appears in the review list."""
    not_tested("BLOCKED", "waits for open decision D-32")


@pytest.mark.req("IG-14-AC1")
def test_ig_14_ac1_unlinked_fixture_is_rejected_with_a_reason():
    """IG-14-AC1: Unlinked fixture is rejected with a reason."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-14-AC2")
def test_ig_14_ac2_duplicate_fixture_follows_tx_05():
    """IG-14-AC2: Duplicate fixture follows TX-05."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-15-AC1")
def test_ig_15_ac1_fixture_with_a_call_before_the_filing():
    """IG-15-AC1: Fixture with a call before the filing and one after both give the earlier
    time as the cutoff.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-16-AC1")
def test_ig_16_ac1_spike_result_is_in_data_section_12():
    """IG-16-AC1: Spike result is in Data Section 12."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IG-17-AC1")
def test_ig_17_ac1_hash_of_raw_text_is_identical_before():
    """IG-17-AC1: Hash of raw text is identical before and after cleaning."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-17-AC2")
def test_ig_17_ac2_rule_list_has_a_version():
    """IG-17-AC2: Rule list has a version."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-18-AC1")
def test_ig_18_ac1_on_50_hand_labelled_calls_at_least():
    """IG-18-AC1: On 50 hand-labelled calls at least 95% of boundaries are correct."""
    not_tested("BLOCKED", "waits for open decision D-45")


@pytest.mark.req("IG-18-AC2")
def test_ig_18_ac2_a_call_with_no_marker_is_flagged():
    """IG-18-AC2: A call with no marker is flagged."""
    not_tested("BLOCKED", "waits for open decision D-45")


@pytest.mark.req("IG-19-AC1")
def test_ig_19_ac1_re_running_any_stage_leaves_table_hashes():
    """IG-19-AC1: Re-running any stage leaves table hashes unchanged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-19-AC2")
def test_ig_19_ac2_the_label_stage_run_without_a_freeze():
    """IG-19-AC2: The label stage run without a freeze record fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-20-AC1")
def test_ig_20_ac1_a_planted_record_dated_after_its_cutoff():
    """IG-20-AC1: A planted record dated after its cutoff makes the test fail."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IG-21-AC1")
def test_ig_21_ac1_the_same_job_runs_for_5_and():
    """IG-21-AC1: The same job runs for 5 and for 100 companies from a list file."""
    not_tested("BLOCKED", "waits for open decision D-28")


@pytest.mark.req("IG-22-AC1")
def test_ig_22_ac1_report_exists_after_a_run_and_matches():
    """IG-22-AC1: Report exists after a run and matches a hand count on 5 companies."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")
