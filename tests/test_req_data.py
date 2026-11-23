"""Tests for the data requirements (data-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that
calls not_tested() is a placeholder for code that does not exist yet. It is skipped and
reported as NOT TESTED, never as passed. Replace the call with a real check when the
code is built (Deterministic_audit.md, Phase D).
"""

import re

import pytest

from requirement_support import not_tested, source_register


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("AE-01-AC1")
def test_ae_01_ac1_every_event_has_a_document_identifier_an():
    """AE-01-AC1: Every event has a document identifier, an announcement date and an EPS
    filing date.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AE-02-AC1")
def test_ae_02_ac1_at_least_98_agreement_on_a_sample():
    """AE-02-AC1: At least 98% agreement on a sample of 200 events."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("AE-03-AC1")
def test_ae_03_ac1_basis_field_is_populated_and_has_one():
    """AE-03-AC1: Basis field is populated and has one value per dataset."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AE-03-AC2")
def test_ae_03_ac2_test_in_vl_07():
    """AE-03-AC2: Test in VL-07."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AE-04-AC1")
def test_ae_04_ac1_after_a_simulated_correction_the_first_reported():
    """AE-04-AC1: After a simulated correction, the first-reported value is unchanged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-01-AC1")
def test_ce_01_ac1_zero_rows_where_capture_time_is_on():
    """CE-01-AC1: Zero rows where capture time is on or after announcement."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-02-AC1")
def test_ce_02_ac1_test_vl_01_passes():
    """CE-02-AC1: Test VL-01 passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-02-AC2")
def test_ce_02_ac2_sr_08_test_passes():
    """CE-02-AC2: SR-08 test passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-03-AC1")
def test_ce_03_ac1_basis_test_vl_07_passes():
    """CE-03-AC1: Basis test VL-07 passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-04-AC1")
def test_ce_04_ac1_exclusion_count_is_reported_per_year():
    """CE-04-AC1: Exclusion count is reported per year."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-05-AC1")
def test_ce_05_ac1_dataset_version_has_a_label_route_value():
    """CE-05-AC1: Dataset version has a label_route value."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-05-AC2")
def test_ce_05_ac2_a_test_fails_if_events_with_different():
    """CE-05-AC2: A test fails if events with different routes are in one training set."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-06-AC1")
def test_ce_06_ac1_test_a_planted_forecast_dated_d_or():
    """CE-06-AC1: Test: a planted forecast dated D or later is excluded."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-06-AC2")
def test_ce_06_ac2_report_shows_the_age_distribution_of_consensus():
    """CE-06-AC2: Report shows the age distribution of consensus values."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-01-AC1")
def test_dv_01_ac1_quarantine_count_is_reported_per_run():
    """DV-01-AC1: Quarantine count is reported per run."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-02-AC1")
def test_dv_02_ac1_the_three_date_fields_have_zero_nulls():
    """DV-02-AC1: The three date fields have zero nulls."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-02-AC2")
def test_dv_02_ac2_other_fields_are_within_the_thresholds_in():
    """DV-02-AC2: Other fields are within the thresholds in Section 11."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-03-AC1")
def test_dv_03_ac1_uniqueness_check_passes_on_every_load():
    """DV-03-AC1: Uniqueness check passes on every load."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-04-AC1")
def test_dv_04_ac1_flagged_rows_have_a_reviewer_note_before():
    """DV-04-AC1: Flagged rows have a reviewer note before the dataset is signed off."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("DV-05-AC1")
def test_dv_05_ac1_date_order_test_on_every_load_reports():
    """DV-05-AC1: Date-order test on every load reports zero violations."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-06-AC1")
def test_dv_06_ac1_mapping_test_passes_on_five_known_non():
    """DV-06-AC1: Mapping test passes on five known non-calendar companies."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-07-AC1")
def test_dv_07_ac1_test_covers_a_pre_open_and_an():
    """DV-07-AC1: Test covers a pre-open and an after-close release, both mapped correctly."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-08-AC1")
def test_dv_08_ac1_table_hashes_match_between_two_runs():
    """DV-08-AC1: Table hashes match between two runs."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FD-01-AC1")
def test_fd_01_ac1_every_row_has_a_filing_date():
    """FD-01-AC1: Every row has a filing date."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FD-01-AC2")
def test_fd_01_ac2_a_sample_of_20_values_matches_the():
    """FD-01-AC2: A sample of 20 values matches the filing."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FD-02-AC1")
def test_fd_02_ac1_test_with_a_planted_filing_dated_d():
    """FD-02-AC1: Test with a planted filing dated D or later shows it is excluded."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FD-03-AC1")
def test_fd_03_ac1_after_a_simulated_restatement_a_prediction_before():
    """FD-03-AC1: After a simulated restatement, a prediction before the restatement date is
    unchanged.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FD-04-AC1")
def test_fd_04_ac1_mapping_test_passes_on_the_five_non():
    """FD-04-AC1: Mapping test passes on the five non-calendar companies used in DV-06."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("GS-01-AC1")
def test_gs_01_ac1_sign_off_exists_before_the_dataset_is():
    """GS-01-AC1: Sign-off exists before the dataset is used in training."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("GS-02-AC1")
def test_gs_02_ac1_data_card_exists_for_every_dataset_version():
    """GS-02-AC1: Data card exists for every dataset version."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("IM-01-AC1")
def test_im_01_ac1_at_sampled_year_ends_company_count_matches():
    """IM-01-AC1: At sampled year-ends, company count matches the published count within 5,
    and differences are explained.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IM-02-AC1")
def test_im_02_ac1_each_year_in_the_period_has_at():
    """IM-02-AC1: Each year in the period has at least one such company."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IM-02-AC2")
def test_im_02_ac2_each_record_has_a_removal_date_and():
    """IM-02-AC2: Each record has a removal date and reason."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IM-03-AC1")
def test_im_03_ac1_join_on_the_permanent_identifier_produces_one():
    """IM-03-AC1: Join on the permanent identifier produces one continuous history for ten
    known renames.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-01-AC1")
def test_lb_01_ac1_fixture_company_with_a_hand_calculated_sue():
    """LB-01-AC1: Fixture company with a hand-calculated SUE matches to four decimal places."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-02-AC1")
def test_lb_02_ac1_exclusion_count_reported_per_year():
    """LB-02-AC1: Exclusion count reported per year."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-02-AC2")
def test_lb_02_ac2_zero_variance_fixture_returns_unavailable():
    """LB-02-AC2: Zero-variance fixture returns unavailable."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-03-AC1")
def test_lb_03_ac1_derived_values_are_flagged():
    """LB-03-AC1: Derived values are flagged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-03-AC2")
def test_lb_03_ac2_sample_comparison_is_reported_with_differences_above():
    """LB-03-AC2: Sample comparison is reported, with differences above 1% listed."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-04-AC1")
def test_lb_04_ac1_test_with_a_planted_restatement_filed_after():
    """LB-04-AC1: Test with a planted restatement filed after D shows the original value is used."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-05-AC1")
def test_lb_05_ac1_test_on_a_company_with_a_split():
    """LB-05-AC1: Test on a company with a split inside the window gives the same SUE as the
    unsplit series.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-06-AC1")
def test_lb_06_ac1_frozen_threshold_record_exists():
    """LB-06-AC1: Frozen threshold record exists."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("LB-06-AC2")
def test_lb_06_ac2_class_shares_table_exists():
    """LB-06-AC2: Class shares table exists."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("LB-07-AC1")
def test_lb_07_ac1_prospective_table_has_both_labels_per_event():
    """LB-07-AC1: Prospective table has both labels per event."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-07-AC2")
def test_lb_07_ac2_thresholds_are_recorded():
    """LB-07-AC2: Thresholds are recorded."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("LB-08-AC1")
def test_lb_08_ac1_report_exists_with_all_three_measures_and():
    """LB-08-AC1: Report exists with all three measures and the event count."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("PX-01-AC1")
def test_px_01_ac1_20_sampled_announcement_day_closes_match_a():
    """PX-01-AC1: 20 sampled announcement-day closes match a second source."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("PX-02-AC1")
def test_px_02_ac1_test_with_a_planted_future_price_shows():
    """PX-02-AC1: Test with a planted future price shows it is excluded."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("PX-03-AC1")
def test_px_03_ac1_series_type_check_fails_any_series_containing():
    """PX-03-AC1: Series-type check fails any series containing both."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SEC-01-AC1")
def test_sec_01_ac1_test_vl_11_a_company_reclassified_in():
    """SEC-01-AC1: Test VL-11: a company reclassified in 2023 shows its old sector before
    the change date.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SEC-02-AC1")
def test_sec_02_ac1_unit_test_on_a_fixed_date_with():
    """SEC-02-AC1: Unit test on a fixed date with a known peer set passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-01-AC1")
@pytest.mark.code("src/earnings/source_register.csv")
def test_sr_01_ac1_register_has_one_row_per_dataset_each():
    """SR-01-AC1: Register has one row per dataset, each with a licence and a dated access check."""
    rows = source_register()
    assert rows, "the register is empty"
    ids = [r["dataset_id"] for r in rows]
    assert len(ids) == len(set(ids)), "a dataset appears twice"
    for r in rows:
        for field in ("dataset", "source", "licence", "access_route"):
            assert r[field].strip(), f"{r['dataset_id']}: {field} is empty"
        for field in ("licence_checked_on", "access_checked_on"):
            assert re.fullmatch(r"\d{4}-\d{2}-\d{2}", r[field]), f"{r['dataset_id']}: {field}"


@pytest.mark.req("SR-02-AC1")
def test_sr_02_ac1_every_feature_column_carries_a_source_tag():
    """SR-02-AC1: Every feature column carries a source tag."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-02-AC2")
def test_sr_02_ac2_an_untagged_column_fails_the_build():
    """SR-02-AC2: An untagged column fails the build."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-03-AC1")
def test_sr_03_ac1_demo_bundle_manifest_lists_each_source_and():
    """SR-03-AC1: Demo bundle manifest lists each source and its licence."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-03-AC2")
def test_sr_03_ac2_any_personal_use_source_fails_the_check():
    """SR-03-AC2: Any personal-use source fails the check."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-04-AC1")
def test_sr_04_ac1_hash_of_each_stored_raw_file_matches():
    """SR-04-AC1: Hash of each stored raw file matches the hash recorded at retrieval."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-05-AC1")
def test_sr_05_ac1_written_answer_or_dated_refusal_on_file():
    """SR-05-AC1: Written answer or dated refusal on file, or a decision log entry that no
    request was made.
    """
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SR-06-AC1")
@pytest.mark.xfail(
    strict=True, reason="NOT SATISFIED: announcement_times has no documented fallback source"
)
@pytest.mark.code("src/earnings/source_register.csv")
def test_sr_06_ac1_register_lists_a_fallback_per_dataset_and():
    """SR-06-AC1: Register lists a fallback per dataset and records the test result for it."""
    gaps = []
    for r in source_register():
        if r["route"] != "primary":
            continue
        has_fallback = r["fallback"].strip() not in ("", "none documented")
        has_result = r["fallback_test_result"].startswith(("passed", "failed", "not tested"))
        if not (has_fallback and has_result):
            gaps.append(r["dataset_id"])
    assert not gaps, f"no fallback or no recorded test result: {gaps}"


@pytest.mark.req("SR-07-AC1")
def test_sr_07_ac1_request_log_exists():
    """SR-07-AC1: Request log exists."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-07-AC2")
def test_sr_07_ac2_no_scraped_source_appears_in_the_demo():
    """SR-07-AC2: No scraped source appears in the demo bundle."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-08-AC1")
def test_sr_08_ac1_test_rejects_any_row_for_a_snapshot():
    """SR-08-AC1: Test rejects any row for a snapshot source whose capture time is missing
    or earlier than the start date.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SR-09-AC1")
@pytest.mark.code("src/earnings/source_register.csv")
def test_sr_09_ac1_source_register_has_a_cost_column_and():
    """SR-09-AC1: Source register has a cost column, and every primary-route entry shows zero."""
    rows = source_register()
    assert "cost_usd_per_month" in rows[0]
    primary = [r for r in rows if r["route"] == "primary"]
    assert primary, "no primary-route entry"
    assert all(float(r["cost_usd_per_month"]) == 0 for r in primary)


@pytest.mark.req("SR-10-AC1")
def test_sr_10_ac1_job_log_shows_a_successful_daily_run():
    """SR-10-AC1: Job log shows a successful daily run."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SR-10-AC2")
def test_sr_10_ac2_a_gap_of_more_than_3_consecutive():
    """SR-10-AC2: A gap of more than 3 consecutive days is reported and the affected events
    are flagged.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SR-11-AC1")
def test_sr_11_ac1_a_test_fails_any_displayed_excerpt_longer():
    """SR-11-AC1: A test fails any displayed excerpt longer than the recorded limit."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-01-AC1")
def test_th_01_ac1_at_least_90():
    """TH-01-AC1: At least 90%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-02-AC1")
def test_th_02_ac1_at_least_95():
    """TH-02-AC1: At least 95%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-03-AC1")
def test_th_03_ac1_at_least_98_within_0_5():
    """TH-03-AC1: At least 98% within 0.5%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-04-AC1")
def test_th_04_ac1_3():
    """TH-04-AC1: 3"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-05-AC1")
def test_th_05_ac1_within_5_of_published_count():
    """TH-05-AC1: Within 5 of published count"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-06-AC1")
def test_th_06_ac1_to_be_set_after_the_first_comparison():
    """TH-06-AC1: To be set after the first comparison run"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-07-AC1")
def test_th_07_ac1_10():
    """TH-07-AC1: 10%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-08-AC1")
def test_th_08_ac1_at_most_2():
    """TH-08-AC1: At most 2%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-09-AC1")
def test_th_09_ac1_4_weeks_20_tickers_daily():
    """TH-09-AC1: 4 weeks, 20 tickers, daily"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-10-AC1")
def test_th_10_ac1_28_of_30_events_agree_within_1():
    """TH-10-AC1: 28 of 30 events agree within 1 cent or 1%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-11-AC1")
def test_th_11_ac1_at_least_6_prior_seasonal_differences_8():
    """TH-11-AC1: At least 6 prior seasonal differences, 8-difference window"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-12-AC1")
def test_th_12_ac1_differences_above_1_listed():
    """TH-12-AC1: Differences above 1% listed"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-13-AC1")
def test_th_13_ac1_reported_no_pass_mark():
    """TH-13-AC1: Reported; no pass mark"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TH-14-AC1")
@pytest.mark.code("src/earnings/source_register.csv")
def test_th_14_ac1_zero():
    """TH-14-AC1: Zero"""
    primary = [r for r in source_register() if r["route"] == "primary"]
    assert sum(float(r["cost_usd_per_month"]) for r in primary) == 0


@pytest.mark.req("TH-15-AC1")
def test_th_15_ac1_0():
    """TH-15-AC1: 0%"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TX-01-AC1")
def test_tx_01_ac1_100_of_rows_have_all_three_fields():
    """TX-01-AC1: 100% of rows have all three fields."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TX-01-AC2")
def test_tx_01_ac2_rows_missing_one_are_rejected_and_logged():
    """TX-01-AC2: Rows missing one are rejected and logged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TX-02-AC1")
def test_tx_02_ac1_violations_are_zero_or_each_violation_is():
    """TX-02-AC1: Violations are zero, or each violation is listed with a reason."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TX-03-AC1")
def test_tx_03_ac1_on_a_hand_labelled_sample_of_50():
    """TX-03-AC1: On a hand-labelled sample of 50 transcripts, at least 95% of boundaries
    are correct.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("TX-04-AC1")
def test_tx_04_ac1_coverage_report_lists_every_missing_company_and():
    """TX-04-AC1: Coverage report lists every missing company and quarter."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("TX-05-AC1")
def test_tx_05_ac1_given_two_transcripts_for_one_event_the():
    """TX-05-AC1: Given two transcripts for one event, the earlier is kept."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TX-05-AC2")
def test_tx_05_ac2_dv_03_passes():
    """TX-05-AC2: DV-03 passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TX-06-AC1")
def test_tx_06_ac1_sample_of_20_transcripts_has_labels_on():
    """TX-06-AC1: Sample of 20 transcripts has labels on every turn."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("TX-07-AC1")
def test_tx_07_ac1_coverage_table_by_year_survivor_status_and():
    """TX-07-AC1: Coverage table by year, survivor status and, where sector history exists,
    sector exists.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-01-AC1")
def test_vl_01_ac1_the_pipeline_excludes_it():
    """VL-01-AC1: The pipeline excludes it."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("VL-01-AC2")
def test_vl_01_ac2_any_leaked_row_fails_the_build():
    """VL-01-AC2: Any leaked row fails the build."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("VL-02-AC1")
def test_vl_02_ac1_rebuilt_vectors_match_stored_vectors():
    """VL-02-AC1: Rebuilt vectors match stored vectors."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("VL-02-AC2")
def test_vl_02_ac2_any_mismatch_is_a_leak_and_fails():
    """VL-02-AC2: Any mismatch is a leak and fails the build."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("VL-03-AC1")
def test_vl_03_ac1_recomputed_values_match_stored_values():
    """VL-03-AC1: Recomputed values match stored values."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("VL-04-AC1")
def test_vl_04_ac1_counts_and_date_ranges_match_the_definitions():
    """VL-04-AC1: Counts and date ranges match the definitions."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("VL-05-AC1")
def test_vl_05_ac1_a_persistent_gap_above_a_threshold_set():
    """VL-05-AC1: A persistent gap above a threshold set in Section 11 is investigated and
    recorded.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-05-AC2")
def test_vl_05_ac2_th_06_is_set_from_the_first():
    """VL-05-AC2: TH-06 is set from the first comparison run and recorded in the decision
    log before the validation set is read.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-06-AC1")
def test_vl_06_ac1_no_class_is_below_10_in_any():
    """VL-06-AC1: No class is below 10% in any year (proposed threshold), or each year below
    it is listed with its shares.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-06-AC2")
def test_vl_06_ac2_any_change_after_the_freeze_is_logged():
    """VL-06-AC2: Any change after the freeze is logged."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-07-AC1")
def test_vl_07_ac1_zero_mismatches_or_every_mismatch_is_corrected():
    """VL-07-AC1: Zero mismatches, or every mismatch is corrected and logged."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-08-AC1")
def test_vl_08_ac1_20_of_20_stored_eps_values_match():
    """VL-08-AC1: 20 of 20 stored EPS values match the record and 20 of 20 classes match the
    hand calculation, or each miss is investigated.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-09-AC1")
def test_vl_09_ac1_error_rate_at_or_below_2():
    """VL-09-AC1: Error rate at or below 2%."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("VL-10-AC1")
def test_vl_10_ac1_results_are_recorded():
    """VL-10-AC1: Results are recorded."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-10-AC2")
def test_vl_10_ac2_any_change_to_a_past_dated_value():
    """VL-10-AC2: Any change to a past-dated value rules out that source for backfill."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-10-AC3")
def test_vl_10_ac3_this_test_is_the_only_way_to():
    """VL-10-AC3: This test is the only way to establish whether yfinance, FMP or Alpha
    Vantage's estimates endpoint change past-dated values.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-10-AC4")
def test_vl_10_ac4_alpha_vantage_s_documentation_was_read_on():
    """VL-10-AC4: Alpha Vantage's documentation was read on 14 November 2026 and does not say."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-10-AC5")
def test_vl_10_ac5_fmp_s_pages_could_not_be_read():
    """VL-10-AC5: FMP's pages could not be read (HTTP 403)."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-11-AC1")
def test_vl_11_ac1_every_sampled_company_shows_the_sector_that():
    """VL-11-AC1: Every sampled company shows the sector that applied on its event date."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-12-AC1")
def test_vl_12_ac1_at_least_28_of_30_estimates_agree():
    """VL-12-AC1: At least 28 of 30 estimates agree within 1 cent or 1%, and none is a value
    revised after the announcement.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("VL-12-AC2")
def test_vl_12_ac2_otherwise_the_source_cannot_build_the_label():
    """VL-12-AC2: Otherwise the source cannot build the label."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")
