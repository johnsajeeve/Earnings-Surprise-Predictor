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


@pytest.mark.req("AE-02-AC1")
def test_ae_02_ac1_at_least_98_agreement_on_a_sample():
    """AE-02-AC1: At least 98% agreement on a sample of 200 events."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("AE-03-AC2")
def test_ae_03_ac2_test_in_vl_07():
    """AE-03-AC2: Test in VL-07."""
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


@pytest.mark.req("CE-06-AC1")
def test_ce_06_ac1_test_a_planted_forecast_dated_d_or():
    """CE-06-AC1: Test: a planted forecast dated D or later is excluded."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("CE-06-AC2")
def test_ce_06_ac2_report_shows_the_age_distribution_of_consensus():
    """CE-06-AC2: Report shows the age distribution of consensus values."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-02-AC2")
def test_dv_02_ac2_other_fields_are_within_the_thresholds_in():
    """DV-02-AC2: Other fields are within the thresholds in Section 11."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DV-04-AC1")
def test_dv_04_ac1_flagged_rows_have_a_reviewer_note_before():
    """DV-04-AC1: Flagged rows have a reviewer note before the dataset is signed off."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("FD-01-AC2")
def test_fd_01_ac2_a_sample_of_20_values_matches_the():
    """FD-01-AC2: A sample of 20 values matches the filing."""
    not_tested("NEEDS MEASUREMENT", "a hand check of 20 values against the filings (Wave 1.7)")


@pytest.mark.req("GS-01-AC1")
def test_gs_01_ac1_sign_off_exists_before_the_dataset_is():
    """GS-01-AC1: Sign-off exists before the dataset is used in training."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


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


@pytest.mark.req("SR-01")
@pytest.mark.code("src/earnings/source_register.csv", "src/earnings/clients/edgar.py")
def test_every_source_the_code_fetches_from_has_a_register_row():
    from earnings import consensus
    from earnings.clients import edgar

    text_ = " ".join(r["source"].lower() + " " + r["dataset"].lower() for r in source_register())
    assert "sec edgar" in text_ and edgar.SOURCE == "sec-edgar"
    assert consensus.SOURCE in text_
    assert "hugging face" in text_  # the transcripts are read from it from Wave 1.5


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
        # "not tested" and "failed" do not meet SR-06: the fallback must pass the same tests, or
        # the scope is narrowed and that is recorded (found by the Phase 0 audit).
        has_result = r["fallback_test_result"].startswith(("passed", "scope narrowed"))
        if not (has_fallback and has_result):
            gaps.append(r["dataset_id"])
    assert not gaps, f"no fallback or no recorded test result: {gaps}"


@pytest.mark.req("SR-07-AC2")
def test_sr_07_ac2_no_scraped_source_appears_in_the_demo():
    """SR-07-AC2: No scraped source appears in the demo bundle."""
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


@pytest.mark.req("IM-02-AC2")
def test_im_02_ac2_each_removed_company_record_has_its_date_and_reason():
    """IM-02-AC2: Each record has a removal date and reason."""
    not_tested(
        "NOT IMPLEMENTED",
        "no last trading date is stored; one removed company has no reason (audit, 26 Nov)",
    )
