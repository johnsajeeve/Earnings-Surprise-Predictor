"""Tests for the explanation agent requirements (explanation-agent-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that
calls not_tested() is a placeholder for code that does not exist yet. It is skipped and
reported as NOT TESTED, never as passed. Replace the call with a real check when the
code is built (Deterministic_audit.md, Phase D).
"""

import pytest

from requirement_support import not_tested


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("AG-01-AC1")
def test_ag_01_ac1_trace_of_a_run_shows_the_order():
    """AG-01-AC1: Trace of a run shows the order and exactly one generation call."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-02-AC1")
def test_ag_02_ac1_the_agent_s_role_fails_an_update():
    """AG-02-AC1: The agent's role fails an UPDATE on Prediction and FeatureVector."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-03-AC1")
def test_ag_03_ac1_fixture_with_tied_shap_values_gives_the():
    """AG-03-AC1: Fixture with tied SHAP values gives the same three every run."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-03-AC2")
def test_ag_03_ac2_a_null_feature_is_reported_as_missing():
    """AG-03-AC2: A NULL feature is reported as missing."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-04-AC1")
def test_ag_04_ac1_every_registry_feature_has_an_entry():
    """AG-04-AC1: Every registry feature has an entry."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-04-AC2")
def test_ag_04_ac2_a_feature_without_one_is_rejected_at():
    """AG-04-AC2: A feature without one is rejected at start-up."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-05-AC1")
def test_ag_05_ac1_a_static_check_finds_no_string_built():
    """AG-05-AC1: A static check finds no string-built query."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-05-AC2")
def test_ag_05_ac2_a_feature_name_containing_sql_characters_returns():
    """AG-05-AC2: A feature name containing SQL characters returns no rows and raises no error."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-06-AC1")
def test_ag_06_ac1_fixture_transcript_returns_the_expected_sentence_ids():
    """AG-06-AC1: Fixture transcript returns the expected sentence ids in order for each
    text feature.
    """
    not_tested("BLOCKED", "waits for open decision D-37")


@pytest.mark.req("AG-07-AC1")
def test_ag_07_ac1_a_planted_sentence_from_a_transcript_dated():
    """AG-07-AC1: A planted sentence from a transcript dated after the cutoff is never returned."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-07-AC2")
def test_ag_07_ac2_the_call_date_is_present_beside_each():
    """AG-07-AC2: The call date is present beside each quote."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-08-AC1")
def test_ag_08_ac1_fixture_with_no_matching_sentences_returns_the():
    """AG-08-AC1: Fixture with no matching sentences returns the message and makes no
    generation call.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-09-AC1")
def test_ag_09_ac1_prompt_file_has_a_version():
    """AG-09-AC1: Prompt file has a version."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-09-AC2")
def test_ag_09_ac2_a_test_shows_the_data_blocks_are():
    """AG-09-AC2: A test shows the data blocks are delimited."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-10-AC1")
def test_ag_10_ac1_malformed_output_fixture_fails_with_a_stored():
    """AG-10-AC1: Malformed output fixture fails with a stored reason."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-10-AC2")
def test_ag_10_ac2_a_valid_fixture_is_accepted():
    """AG-10-AC2: A valid fixture is accepted."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-11-AC1")
def test_ag_11_ac1_an_id_that_does_not_exist_is():
    """AG-11-AC1: An id that does not exist is rejected."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-11-AC2")
def test_ag_11_ac2_the_displayed_text_equals_the_stored_text():
    """AG-11-AC2: The displayed text equals the stored text byte for byte."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-12-AC1")
def test_ag_12_ac1_text_scan_of_20_fixture_outputs_finds():
    """AG-12-AC1: Text scan of 20 fixture outputs finds none of the banned phrases."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-12-AC2")
def test_ag_12_ac2_disclaimer_present():
    """AG-12-AC2: Disclaimer present."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-13-AC1")
def test_ag_13_ac1_configuration_with_an_alias_is_rejected():
    """AG-13-AC1: Configuration with an alias is rejected."""
    not_tested("BLOCKED", "waits for open decision D-37")


@pytest.mark.req("AG-13-AC2")
def test_ag_13_ac2_stored_explanation_has_all_settings():
    """AG-13-AC2: Stored explanation has all settings."""
    not_tested("BLOCKED", "waits for open decision D-37")


@pytest.mark.req("AG-14-AC1")
def test_ag_14_ac1_fixture_explanations_with_a_wrong_feature_a():
    """AG-14-AC1: Fixture explanations with a wrong feature, a wrong sign, a made-up id and
    a wrong number are each caught.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-15-AC1")
def test_ag_15_ac1_fixtures_cover_partial_and_total_failure():
    """AG-15-AC1: Fixtures cover partial and total failure."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-16-AC1")
def test_ag_16_ac1_a_fixture_output_containing_html_and_a():
    """AG-16-AC1: A fixture output containing HTML and a link renders as text."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-17-AC1")
def test_ag_17_ac1_all_planted_cases_are_stopped():
    """AG-17-AC1: All planted cases are stopped."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-18-AC1")
def test_ag_18_ac1_request_log_fixture_shows_the_fields_sent():
    """AG-18-AC1: Request log fixture shows the fields sent."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-18-AC2")
def test_ag_18_ac2_register_entry_exists_before_the_first_call():
    """AG-18-AC2: Register entry exists before the first call."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-19-AC1")
def test_ag_19_ac1_a_repository_scan_finds_no_fixture_over():
    """AG-19-AC1: A repository scan finds no fixture over the excerpt limit recorded in the
    source register (Data SR-11) and every fixture file states its origin.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-20-AC1")
def test_ag_20_ac1_with_the_cap_set_to_zero_a():
    """AG-20-AC1: With the cap set to zero, a job makes no provider call and fails with that
    reason.
    """
    not_tested("BLOCKED", "waits for open decision D-27")


@pytest.mark.req("AG-21-AC1")
def test_ag_21_ac1_two_requests_give_the_same_stored_explanation():
    """AG-21-AC1: Two requests give the same stored explanation and one provider call."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-22-AC1")
def test_ag_22_ac1_injected_429_and_timeout_fixtures_behave_as():
    """AG-22-AC1: Injected 429 and timeout fixtures behave as described."""
    not_tested("BLOCKED", "waits for open decision D-37")


@pytest.mark.req("AG-23-AC1")
def test_ag_23_ac1_prompt_version_in_the_evaluation_record_is():
    """AG-23-AC1: Prompt version in the evaluation record is dated before the run."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-23-AC2")
def test_ag_23_ac2_regression_report_names_event_ids_and_years():
    """AG-23-AC2: Regression report names event ids and years."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AG-24-AC1")
def test_ag_24_ac1_protocol_file_exists_and_is_dated_before():
    """AG-24-AC1: Protocol file exists and is dated before the run."""
    not_tested("BLOCKED", "waits for open decision D-06, D-37")


@pytest.mark.req("AG-25-AC1")
def test_ag_25_ac1_results_table_has_all_three_values_per():
    """AG-25-AC1: Results table has all three values per metric and the counter-metrics."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("AG-26-AC1")
def test_ag_26_ac1_migration_exists_and_the_fields_are_populated():
    """AG-26-AC1: Migration exists and the fields are populated in a run."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")
