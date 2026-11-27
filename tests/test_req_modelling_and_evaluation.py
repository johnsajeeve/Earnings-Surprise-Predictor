"""Tests for the modelling and evaluation requirements (modelling-and-evaluation-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that
calls not_tested() is a placeholder for code that does not exist yet. It is skipped and
reported as NOT TESTED, never as passed. Replace the call with a real check when the
code is built (Deterministic_audit.md, Phase D).
"""

import pytest

from requirement_support import not_tested


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("MD-01-AC1")
def test_md_01_ac1_fixture_prediction_has_three_probabilities_summing_to():
    """MD-01-AC1: Fixture prediction has three probabilities summing to 1.00."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-01-AC2")
def test_md_01_ac2_the_class_order_in_the_record_matches():
    """MD-01-AC2: The class order in the record matches the output columns."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-02-AC1")
def test_md_02_ac1_report_lists_the_three_models_with_the():
    """MD-02-AC1: Report lists the three models with the feature-set version and prediction
    point of each.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-03-AC1")
def test_md_03_ac1_split_test_confirms_boundaries_by_announcement_date():
    """MD-03-AC1: Split test confirms boundaries by announcement date."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-03-AC2")
def test_md_03_ac2_date_tests_pass_for_all_features():
    """MD-03-AC2: Date tests pass for all features."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-04-AC1")
def test_md_04_ac1_weights_are_stored_with_the_run():
    """MD-04-AC1: Weights are stored with the run."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-04-AC2")
def test_md_04_ac2_changing_2022_data_leaves_the_weights_unchanged():
    """MD-04-AC2: Changing 2022 data leaves the weights unchanged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-05-AC1")
def test_md_05_ac1_search_file_is_dated_before_the_run():
    """MD-05-AC1: Search file is dated before the run."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-05-AC2")
def test_md_05_ac2_every_model_has_the_same_trial_count():
    """MD-05-AC2: Every model has the same trial count."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-05-AC3")
def test_md_05_ac3_test_rows_are_not_read():
    """MD-05-AC3: Test rows are not read."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-06-AC1")
def test_md_06_ac1_a_fixture_with_a_missing_value_trains():
    """MD-06-AC1: A fixture with a missing value trains and predicts."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-07-AC1")
def test_md_07_ac1_two_runs_give_identical_predictions_and_matching():
    """MD-07-AC1: Two runs give identical predictions and matching metrics (Product ML-01)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-08-AC1")
def test_md_08_ac1_registration_fails_without_the_report():
    """MD-08-AC1: Registration fails without the report."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-08-AC2")
def test_md_08_ac2_access_log_shows_one_test_read():
    """MD-08-AC2: Access log shows one test read."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-09-AC1")
def test_md_09_ac1_altered_artefact_fails_to_load():
    """MD-09-AC1: Altered artefact fails to load."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-09-AC2")
def test_md_09_ac2_repository_contains_no_artefact():
    """MD-09-AC2: Repository contains no artefact."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-10-AC1")
def test_md_10_ac1_fixture_confidence_equals_the_largest_calibrated_probability():
    """MD-10-AC1: Fixture confidence equals the largest calibrated probability."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-11-AC1")
def test_md_11_ac1_calibration_parameters_are_in_the_modelversion_record():
    """MD-11-AC1: Calibration parameters are in the ModelVersion record."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-11-AC2")
def test_md_11_ac2_both_brier_scores_appear_in_the_report():
    """MD-11-AC2: Both Brier scores appear in the report."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-12-AC1")
def test_md_12_ac1_fixture_prediction_s_shap_values_plus_base():
    """MD-12-AC1: Fixture prediction's SHAP values plus base value equal the predicted
    class's raw score to 1e-4.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-12-AC2")
def test_md_12_ac2_a_shape_test_passes():
    """MD-12-AC2: A shape test passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-13-AC1")
def test_md_13_ac1_fixtures_for_each_of_the_three_predicted():
    """MD-13-AC1: Fixtures for each of the three predicted classes give the expected label."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-14-AC1")
def test_md_14_ac1_evaluation_page_lists_every_feature_with_its():
    """MD-14-AC1: Evaluation page lists every feature with its mean absolute value."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-15-AC1")
def test_md_15_ac1_hand_calculated_fixture_matches_each_metric():
    """MD-15-AC1: Hand-calculated fixture matches each metric."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-16-AC1")
def test_md_16_ac1_evaluation_report_has_the_per_class_table():
    """MD-16-AC1: Evaluation report has the per-class table."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-17-AC1")
def test_md_17_ac1_interval_code_run_twice_gives_identical_bounds():
    """MD-17-AC1: Interval code run twice gives identical bounds."""
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-18-AC1")
def test_md_18_ac1_both_appear_in_the_fr_06_table():
    """MD-18-AC1: Both appear in the FR-06 table with the exclusion count."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-19-AC1")
def test_md_19_ac1_report_states_the_count_and_the_method():
    """MD-19-AC1: Report states the count and the method, and both are dated before the test
    read.
    """
    not_tested("BLOCKED", "waits for open decision D-42")


@pytest.mark.req("MD-20-AC1")
def test_md_20_ac1_per_quarter_series_exists_with_the_cutoff():
    """MD-20-AC1: Per-quarter series exists with the cutoff marked."""
    not_tested("BLOCKED", "waits for open decision D-22")


@pytest.mark.req("MD-20-AC2")
def test_md_20_ac2_if_no_labelled_quarter_lies_before_the():
    """MD-20-AC2: If no labelled quarter lies before the cutoff, the report says the check
    cannot show a jump and gives the reason.
    """
    not_tested("BLOCKED", "waits for open decision D-22")


@pytest.mark.req("MD-21-AC1")
def test_md_21_ac1_number_on_the_page_equals_the_stored():
    """MD-21-AC1: Number on the page equals the stored row."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-22-AC1")
def test_md_22_ac1_event_with_features_gets_one_stored_prediction():
    """MD-22-AC1: Event with features gets one stored prediction per point."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-22-AC2")
def test_md_22_ac2_a_second_run_adds_none():
    """MD-22-AC2: A second run adds none."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-23-AC1")
def test_md_23_ac1_altered_artefact_makes_the_endpoint_return_503():
    """MD-23-AC1: Altered artefact makes the endpoint return 503 with the Section 12 message."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MD-24-AC1")
def test_md_24_ac1_placeholder():
    """MD-24-AC1: The card has sections for direct use, out-of-scope use, and limitations each
    with a recommendation.
    """
    not_tested("NOT IMPLEMENTED", "no model card exists yet (Wave 3.5)")


@pytest.mark.req("MD-25-AC1")
def test_md_25_ac1_placeholder():
    """MD-25-AC1: The report has all three breakdowns with counts, and no rate for a group
    under 30 events.
    """
    not_tested("NOT IMPLEMENTED", "no evaluation report exists yet (Wave 3.4)")


@pytest.mark.req("MD-26-AC1")
def test_md_26_ac1_placeholder():
    """MD-26-AC1: A figure missing any of these fails the report check."""
    not_tested("NOT IMPLEMENTED", "no accuracy figure is produced yet (Wave 3.4)")


@pytest.mark.req("MD-27-AC1")
def test_md_27_ac1_placeholder():
    """MD-27-AC1: The report has a not-measured section with at least the coverage and
    survivorship gaps.
    """
    not_tested("NOT IMPLEMENTED", "no evaluation report exists yet (Wave 3.4)")
