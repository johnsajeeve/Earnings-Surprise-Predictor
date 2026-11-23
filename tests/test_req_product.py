"""Tests for the product requirements (product-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that calls
not_tested() is a placeholder for code that does not exist yet. It is skipped and reported as
NOT TESTED, never as passed. Replace the call with a real check when the code is built
(Deterministic_audit.md, Phase D).
"""

import re

import pytest

from requirement_support import not_tested

_LOG_LINE = re.compile(
    r"^request_id=[0-9a-f]{32} method=GET path=/no-such-path-\d status=404 latency_ms=\d+\.\d$"
)


@pytest.mark.req("NFR-11-AC1")
@pytest.mark.code("src/earnings/api/middleware.py")
def test_nfr_11_ac1_every_request_is_logged_with_id_latency_and_status(request_log):
    from fastapi.testclient import TestClient

    from earnings.api import main

    client = TestClient(main.app)
    returned_ids = [client.get(f"/no-such-path-{n}").headers["X-Request-ID"] for n in range(3)]
    assert len(request_log) == 3
    for line, request_id in zip(request_log, returned_ids, strict=True):
        assert _LOG_LINE.match(line), line
        assert line.startswith(f"request_id={request_id} ")


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("API-03-AC1")
def test_api_03_ac1_contract_test_checks_the_shape_for_404():
    """API-03-AC1: Contract test checks the shape for 404, 422, 401, 429 and 503."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("API-04-AC1")
def test_api_04_ac1_contract_test_on_each_prediction_endpoint():
    """API-04-AC1: Contract test on each prediction endpoint."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("API-05-AC1")
def test_api_05_ac1_request_for_500_rows_returns_100_with():
    """API-05-AC1: Request for 500 rows returns 100 with a next-page link."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("API-06-AC1")
def test_api_06_ac1_request_without_a_token_returns_401():
    """API-06-AC1: Request without a token returns 401."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("API-07-AC1")
def test_api_07_ac1_load_test_exceeding_the_limit_returns_429():
    """API-07-AC1: Load test exceeding the limit returns 429 with the header present."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-01-AC1")
def test_ep_01_ac1_get_v1_predictions_ticker_latest_prediction_top():
    """EP-01-AC1: GET /v1/predictions/{ticker}: Latest prediction, top three features,
    evidence base, input as-of times and sector context.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-02-AC1")
def test_ep_02_ac1_get_v1_predictions_ticker_sector_peer_list():
    """EP-02-AC1: GET /v1/predictions/{ticker}/sector: Peer list and statistics behind the
    sector context and realised score.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-03-AC1")
def test_ep_03_ac1_get_v1_predictions_ticker_explanation_explanation_with():
    """EP-03-AC1: GET /v1/predictions/{ticker}/explanation: Explanation with citations and
    verification status.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-04-AC1")
def test_ep_04_ac1_post_v1_predictions_ticker_explanation_jobs_starts():
    """EP-04-AC1: POST /v1/predictions/{ticker}/explanation/jobs: Starts an explanation job
    and returns the job identifier.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-05-AC1")
def test_ep_05_ac1_get_v1_jobs_job_id_status_of():
    """EP-05-AC1: GET /v1/jobs/{job_id}: Status of an explanation job."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-06-AC1")
def test_ep_06_ac1_get_v1_predictions_ticker_history_from_to():
    """EP-06-AC1: GET /v1/predictions/{ticker}/history?from=&to=&page=: Past predictions
    with outcomes and realised sector scores.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-07-AC1")
def test_ep_07_ac1_get_v1_evaluation_metrics_model_full_tabular():
    """EP-07-AC1: GET /v1/evaluation/metrics?model=full|tabular|majority|previous|consensus:
    Test-set metrics for a model version.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-08-AC1")
def test_ep_08_ac1_get_health_service_data_freshness_and_ingestion():
    """EP-08-AC1: GET /health: Service, data freshness and ingestion status."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-09-AC1")
def test_ep_09_ac1_get_metrics_service_metrics_for_scraping():
    """EP-09-AC1: GET /metrics: Service metrics for scraping."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EP-10-AC1")
def test_ep_10_ac1_get_v1_universe_tickers_in_the_universe():
    """EP-10-AC1: GET /v1/universe: Tickers in the universe with company names, for ticker
    autocomplete. Could.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-01-AC1")
def test_er_01_ac1_user_sees_no_transcript_available_for_this():
    """ER-01-AC1: User sees "No transcript available for this ticker." """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-01-AC2")
def test_er_01_ac2_system_logs_the_request_no_prediction_stored():
    """ER-01-AC2: System: Logs the request; no prediction stored."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-02-AC1")
def test_er_02_ac1_user_sees_ticker_not_in_universe_404():
    """ER-02-AC1: User sees "Ticker not in universe." (404)"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-02-AC2")
def test_er_02_ac2_system_logs_the_request():
    """ER-02-AC2: System: Logs the request."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-03-AC1")
def test_er_03_ac1_user_sees_invalid_ticker_format_422():
    """ER-03-AC1: User sees "Invalid ticker format." (422)"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-03-AC2")
def test_er_03_ac2_system_rejects_before_lookup():
    """ER-03-AC2: System: Rejects before lookup."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-04-AC1")
def test_er_04_ac1_user_sees_data_refresh_failed_on_date():
    """ER-04-AC1: User sees "Data refresh failed on <date>. Showing the last stored result."
    beside the stored prediction.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-04-AC2")
def test_er_04_ac2_system_retries_up_to_three_times_then():
    """ER-04-AC2: System: Retries up to three times, then dead-letters the task (PL-02);
    marks the run failed (PL-01); /health shows ingestion degraded; stores no partial event.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-05-AC1")
def test_er_05_ac1_user_sees_too_many_requests_try_again():
    """ER-05-AC1: User sees "Too many requests. Try again shortly." (429)"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-05-AC2")
def test_er_05_ac2_system_returns_retry_after_header():
    """ER-05-AC2: System: Returns Retry-After header."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-06-AC1")
def test_er_06_ac1_user_sees_prediction_with_limited_history_label():
    """ER-06-AC1: User sees Prediction with "Limited history" label."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-06-AC2")
def test_er_06_ac2_system_marks_trailing_features_as_unavailable():
    """ER-06-AC2: System: Marks trailing features as unavailable."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-07-AC1")
def test_er_07_ac1_user_sees_q_a_analysis_unavailable_for():
    """ER-07-AC1: User sees "Q&A analysis unavailable for this call." """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-07-AC2")
def test_er_07_ac2_system_stores_q_a_features_as_unavailable():
    """ER-07-AC2: System: Stores Q&A features as unavailable."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-08-AC1")
def test_er_08_ac1_user_sees_insufficient_peers_in_the_sector():
    """ER-08-AC1: User sees "Insufficient peers" in the sector section."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-08-AC2")
def test_er_08_ac2_system_stores_sector_features_as_unavailable_srs():
    """ER-08-AC2: System: Stores sector features as unavailable (SRS-06)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-09-AC1")
def test_er_09_ac1_user_sees_sector_comparison_unavailable():
    """ER-09-AC1: User sees "Sector comparison unavailable." """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-09-AC2")
def test_er_09_ac2_system_sector_features_switched_off_srs_14():
    """ER-09-AC2: System: Sector features switched off (SRS-14)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-10-AC1")
def test_er_10_ac1_user_sees_pending():
    """ER-10-AC1: User sees "Pending." """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-10-AC2")
def test_er_10_ac2_system_no_value_computed_srs_09():
    """ER-10-AC2: System: No value computed (SRS-09)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-11-AC1")
def test_er_11_ac1_user_sees_explanation_marked_partially_verified():
    """ER-11-AC1: User sees Explanation marked "partially verified"."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-11-AC2")
def test_er_11_ac2_system_logs_the_failure_with_prediction_identifier():
    """ER-11-AC2: System: Logs the failure with prediction identifier."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-12-AC1")
def test_er_12_ac1_user_sees_explanation_could_not_be_generated():
    """ER-12-AC1: User sees "Explanation could not be generated." """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-12-AC2")
def test_er_12_ac2_system_stores_the_failure_reason_and_returns():
    """ER-12-AC2: System: Stores the failure reason and returns it with the status."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-13-AC1")
def test_er_13_ac1_user_sees_service_temporarily_unavailable_503():
    """ER-13-AC1: User sees "Service temporarily unavailable." (503)"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-13-AC2")
def test_er_13_ac2_system_refuses_to_serve_logs_an_error():
    """ER-13-AC2: System: Refuses to serve; logs an error line with the request identifier
    and the artefact identifier, and sets the artefact check in /health to failed (SV-08).
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-14-AC1")
def test_er_14_ac1_user_sees_service_temporarily_unavailable_503():
    """ER-14-AC1: User sees "Service temporarily unavailable." (503)"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ER-14-AC2")
def test_er_14_ac2_system_logs_the_request_identifier_returns_no():
    """ER-14-AC2: System: Logs the request identifier; returns no partial result."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EX-01-AC1")
def test_ex_01_ac1_a_claim_with_no_link_is_rejected():
    """EX-01-AC1: A claim with no link is rejected before the explanation is stored."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EX-02-AC1")
def test_ex_02_ac1_every_stored_claim_has_a_label_and():
    """EX-02-AC1: Every stored claim has a label and a reason."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EX-03-AC1")
def test_ex_03_ac1_rank_agreement_test_on_the_evaluation_sample():
    """EX-03-AC1: Rank-agreement test on the evaluation sample."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("EX-04-AC1")
def test_ex_04_ac1_fixture_with_no_matching_sentence_returns_the():
    """EX-04-AC1: Fixture with no matching sentence returns the no-evidence message."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EX-05-AC1")
def test_ex_05_ac1_agreement_statistic_exists_for_the_sample():
    """EX-05-AC1: Agreement statistic exists for the sample."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("FR-01-AC1")
def test_fr_01_ac1_given_a_ticker_with_a_stored_transcript():
    """FR-01-AC1: Given a ticker with a stored transcript and feature vector, when the user
    submits the ticker, then the prediction card shows the class, the three class
    probabilities summing to 1.00 within rounding, a confidence value, and three features.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-01-AC2")
def test_fr_01_ac2_given_the_same_ticker_submitted_twice_without():
    """FR-01-AC2: Given the same ticker submitted twice without new data, then the same
    prediction is returned both times.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-01-AC3")
def test_fr_01_ac3_given_a_ticker_with_no_earlier_transcript():
    """FR-01-AC3: Given a ticker with no earlier transcript (a cold-start ticker), then the
    card shows "No transcript available for this ticker" and no class.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-02-AC1")
def test_fr_02_ac1_given_any_event_in_the_database_when():
    """FR-02-AC1: Given any event in the database, when its record is read, then all three
    date fields are present and non-null, or the event is marked incomplete. The label route
    is stored beside them.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-02-AC2")
def test_fr_02_ac2_given_a_transcript_dated_after_its_announcement():
    """FR-02-AC2: Given a transcript dated after its announcement by more than the window in
    Data TX-02, then the event is flagged for review and excluded from training.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-03-AC1")
def test_fr_03_ac1_given_the_training_pipeline_runs_when_any():
    """FR-03-AC1: Given the training pipeline runs, when any training row has a date after
    31 December 2021, then the pipeline fails with an error naming the row.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-03-AC2")
def test_fr_03_ac2_given_the_test_suite_runs_then_a():
    """FR-03-AC2: Given the test suite runs, then a test confirms the split boundaries
    against the feature matrix.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-04-AC1")
def test_fr_04_ac1_given_a_prediction_when_the_explanation_is():
    """FR-04-AC1: Given a prediction, when the explanation is requested, then three features
    are returned in descending absolute SHAP value.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-04-AC2")
def test_fr_04_ac2_given_a_feature_with_a_positive_shap():
    """FR-04-AC2: Given a feature with a positive SHAP value for miss, then its direction is
    labelled "toward miss".
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-05-AC1")
def test_fr_05_ac1_given_an_explanation_citing_a_sentence_when():
    """FR-05-AC1: Given an explanation citing a sentence, when the source transcript is
    checked, then the sentence is present verbatim, or the citation is removed and the
    explanation is marked "partially verified".
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-05-AC2")
def test_fr_05_ac2_given_a_citation_that_cannot_be_found():
    """FR-05-AC2: Given a citation that cannot be found, then the failure is logged with the
    prediction identifier.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-06-AC1")
def test_fr_06_ac1_given_the_evaluation_page_loads_then_every():
    """FR-06-AC1: Given the evaluation page loads, then every model shown has accuracy,
    weighted F1, three-class AUC (one-against-rest, macro average), binary AUC (beat against
    miss, in-line excluded), Brier score and precision at top 20%, computed on the same
    rows. The consensus-revision baseline, where it exists, is shown in its own table on the
    prospective set, with the full and tabular models re-scored on those same rows.
    Accuracy, weighted F1 and binary AUC follow the SAE-FiRE definitions so that tables line
    up with the literature.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-06-AC2")
def test_fr_06_ac2_given_any_headline_metric_then_tr_01():
    """FR-06-AC2: Given any headline metric, then TR-01 (confidence intervals) and TR-02
    (variants tried) apply.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-06-AC3")
def test_fr_06_ac3_given_the_full_model_does_not_outperform():
    """FR-06-AC3: Given the full model does not outperform a baseline, then the page states
    this without hiding either result.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-07-AC1")
def test_fr_07_ac1_given_a_data_source_returns_an_error():
    """FR-07-AC1: Given a data source returns an error during ingestion, then the task
    retries and is then dead-lettered (PL-02), the run record shows the failure (PL-01), no
    partial event is stored (DB-13), and /health reports the ingestion status without
    changing its HTTP status. Predictions already stored are still served, with the warning
    "Data refresh failed on <date>. Showing the last stored result." in the response
    envelope (API-04).
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-07-AC2")
def test_fr_07_ac2_given_postgresql_is_unavailable_then_every_data():
    """FR-07-AC2: Given PostgreSQL is unavailable, then every data endpoint returns 503
    "Service temporarily unavailable." with no partial result. Given Redis is unavailable,
    then only the explanation job endpoint returns 503, and other endpoints are unaffected.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-07-AC3")
def test_fr_07_ac3_given_a_ticker_with_too_little_history():
    """FR-07-AC3: Given a ticker with too little history for a trailing feature (fewer than
    five earlier calls at T0 for the sentiment surprise, or fewer than four prior SUE values
    for the surprise trend), then the prediction is returned with the label "Limited
    history" and that feature is marked as unavailable.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-08-AC1")
def test_fr_08_ac1_given_any_prediction_or_explanation_is_shown():
    """FR-08-AC1: Given any prediction or explanation is shown, then the notice appears in
    the same view, not behind a link.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-09-AC1")
def test_fr_09_ac1_given_a_ticker_and_a_range_covering():
    """FR-09-AC1: Given a ticker and a range covering four events, then four rows are
    returned, each showing the prediction date, class, confidence and realised outcome.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-09-AC2")
def test_fr_09_ac2_given_a_prediction_whose_outcome_is_not():
    """FR-09-AC2: Given a prediction whose outcome is not yet known, then the outcome field
    shows "Pending".
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-10-AC1")
def test_fr_10_ac1_given_the_evaluation_page_then_a_calibration():
    """FR-10-AC1: Given the evaluation page, then a calibration plot and the precision at
    top 20% value are displayed for the test set.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-10-AC2")
def test_fr_10_ac2_given_the_evaluation_page_then_calibration_by():
    """FR-10-AC2: Given the evaluation page, then calibration by confidence decile is shown
    as TR-05 requires.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-11-AC1")
def test_fr_11_ac1_given_a_prediction_is_stored_then_both():
    """FR-11-AC1: Given a prediction is stored, then both version identifiers are present
    and match a registered model artefact.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-12-AC1")
def test_fr_12_ac1_srs_01_to_srs_14_pass():
    """FR-12-AC1: SRS-01 to SRS-14 pass."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-13-AC1")
def test_fr_13_ac1_given_the_same_transcript_is_ingested_twice():
    """FR-13-AC1: Given the same transcript is ingested twice, then exactly one transcript
    row exists for it.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-13-AC2")
def test_fr_13_ac2_given_an_ingestion_job_fails_halfway_and():
    """FR-13-AC2: Given an ingestion job fails halfway and is re-run, then the final row
    count equals the count of a clean run.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-14-AC1")
def test_fr_14_ac1_given_a_new_consensus_estimate_arrives_for():
    """FR-14-AC1: Given a new consensus estimate arrives for an event, then a new snapshot
    row is added with its capture timestamp and the earlier snapshot is unchanged.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-14-AC2")
def test_fr_14_ac2_given_a_prediction_for_an_event_announced():
    """FR-14-AC2: Given a prediction for an event announced on date D, then any snapshot
    captured on or after D is excluded from its inputs.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-15-AC1")
def test_fr_15_ac1_given_a_transcript_with_a_recognised_q():
    """FR-15-AC1: Given a transcript with a recognised Q&A marker, then prepared and Q&A
    sections are stored separately.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-15-AC2")
def test_fr_15_ac2_given_no_q_a_marker_is_found():
    """FR-15-AC2: Given no Q&A marker is found, then the event is flagged "Segmentation
    failed" and the Q&A features are stored as unavailable, not as zero.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-16-AC1")
def test_fr_16_ac1_given_a_transcript_is_already_scored_with():
    """FR-16-AC1: Given a transcript is already scored with the current FinBERT version,
    when the batch runs, then no sentence is rescored.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-16-AC2")
def test_fr_16_ac2_given_the_finbert_version_changes_then_every():
    """FR-16-AC2: Given the FinBERT version changes, then every affected transcript is
    rescored and the old scores are retained with their version.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-17-AC1")
def test_fr_17_ac1_given_a_fixture_transcript_with_a_known():
    """FR-17-AC1: Given a fixture transcript with a known hedge-word count, then the
    uncertainty score equals hedge count divided by word count to four decimal places.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-17-AC2")
def test_fr_17_ac2_given_a_transcript_with_zero_words_then():
    """FR-17-AC2: Given a transcript with zero words, then the feature is stored as
    unavailable and no division is attempted.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-18-AC1")
def test_fr_18_ac1_given_four_prior_quarters_of_scores_then():
    """FR-18-AC1: Given four prior quarters of scores, then the z-score equals (current
    minus the mean of the four) divided by their standard deviation.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-18-AC2")
def test_fr_18_ac2_given_the_standard_deviation_of_the_four():
    """FR-18-AC2: Given the standard deviation of the four prior quarters is zero, then the
    feature is stored as unavailable, not as infinity.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-18-AC3")
def test_fr_18_ac3_given_the_call_being_scored_and_fewer():
    """FR-18-AC3: Given the call being scored and fewer than four calls before it, then the
    prediction carries the "Limited history" label (FR-07). At T0 the call being scored is
    the most recent earlier call.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-19-AC1")
def test_fr_19_ac1_given_an_explanation_request_then_the_api():
    """FR-19-AC1: Given an explanation request, then the API returns a job identifier within
    500 ms and the job status is pending.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-19-AC2")
def test_fr_19_ac2_given_the_job_completes_then_the_status():
    """FR-19-AC2: Given the job completes, then the status changes to complete and the
    explanation is retrievable by identifier.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-19-AC3")
def test_fr_19_ac3_given_the_job_fails_then_the_failure():
    """FR-19-AC3: Given the job fails, then the failure reason is stored and returned with
    the status.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-20-AC1")
def test_fr_20_ac1_given_a_ticker_not_in_the_universe():
    """FR-20-AC1: Given a ticker not in the universe for any date in the dataset, then the
    response is 404 with the message "Ticker not in universe".
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-20-AC2")
def test_fr_20_ac2_given_a_ticker_with_characters_outside_letters():
    """FR-20-AC2: Given a ticker with characters outside letters, digits, dot or hyphen, or
    longer than ten characters, then the response is 422 with the message "Invalid ticker
    format".
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-21-AC1")
def test_fr_21_ac1_given_any_prediction_card_then_all_four():
    """FR-21-AC1: Given any prediction card, then all four values are shown and match the
    ModelVersion record of the model that produced it.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-22-AC1")
def test_fr_22_ac1_given_a_t0_prediction_for_an_event():
    """FR-22-AC1: Given a T0 prediction for an event with cutoff C (the earlier of the call
    time and the 8-K Item 2.02 acceptance time), then every stored as-of timestamp is before
    C. A test fails the build if any is not. A T1 prediction is labelled "post-call" and
    records its own transcript time, which is after C. Every other input of a T1 prediction
    is still before C.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-22-AC2")
def test_fr_22_ac2_given_the_prediction_card_then_the_timestamps():
    """FR-22-AC2: Given the prediction card, then the timestamps are visible in the same
    view or one click away.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-23-AC1")
def test_fr_23_ac1_given_the_evaluation_page_then_the_thresholds():
    """FR-23-AC1: Given the evaluation page, then the thresholds shown equal the frozen
    values recorded under Data VL-06.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-24-AC1")
def test_fr_24_ac1_given_the_feature_set_version_then_every():
    """FR-24-AC1: Given the feature-set version, then every feature in the table is listed
    with its source tag and as-of rule, or is listed as dropped with a decision-log
    reference.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-24-AC2")
def test_fr_24_ac2_given_a_fixture_event_then_each_computed():
    """FR-24-AC2: Given a fixture event, then each computed feature equals a hand-calculated
    value.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-25-AC1")
def test_fr_25_ac1_given_the_evaluation_report_then_it_contains():
    """FR-25-AC1: Given the evaluation report, then it contains a per-quarter series of a
    sentiment-only metric with the pretraining cutoff marked, and the result is stated
    either way. If no labelled quarter lies before the cutoff, the report says the check
    cannot show a jump and gives the reason (Modelling and Evaluation MD-20).
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-26-AC1")
def test_fr_26_ac1_given_the_evaluation_page_then_it_shows():
    """FR-26-AC1: Given the evaluation page, then it shows mean absolute SHAP value for
    every feature.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-26-AC2")
def test_fr_26_ac2_given_at_least_four_named_features_then():
    """FR-26-AC2: Given at least four named features, then their expected directions are
    recorded before the test set is read, and the observed direction is shown beside each.
    Mismatches are reported, not hidden.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-27-AC1")
def test_fr_27_ac1_given_the_benchmark_then_the_tabular_only():
    """FR-27-AC1: Given the benchmark, then the tabular-only and text-augmented baselines
    are run with the same features and split rules as the main model, where the benchmark
    supplies the inputs. Features it cannot supply are listed and left out of both models,
    and if it supplies no tabular input only the text model is reported and the report says
    so. Accuracy, weighted F1 and binary AUC are reported with intervals.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-27-AC2")
def test_fr_27_ac2_given_the_report_then_the_benchmark_s():
    """FR-27-AC2: Given the report, then the benchmark's label definition, licence (CC BY-
    NC-ND for transcripts; the repository is Apache-2.0) and the note that its label uses
    post-call forecasts are stated beside every number.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-27-AC3")
def test_fr_27_ac3_given_any_comparison_with_sae_fire_auc():
    """FR-27-AC3: Given any comparison with SAE-FiRE (AUC 0.620), then it is labelled as
    indicative, because the label, period and universe differ.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-27-AC4")
def test_fr_27_ac4_given_the_public_demo_then_no_benchmark():
    """FR-27-AC4: Given the public demo, then no benchmark data is shown or redistributed
    (Data SR-03).
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("FR-28-AC1")
def test_fr_28_ac1_given_a_first_visit_then_the_notice():
    """FR-28-AC1: Given a first visit, then the notice is shown before the first prediction."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-28-AC2")
def test_fr_28_ac2_given_any_screen_then_the_notice_can():
    """FR-28-AC2: Given any screen, then the notice can be reopened from that screen."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-29-AC1")
def test_fr_29_ac1_given_the_evaluation_page_then_the_t1():
    """FR-29-AC1: Given the evaluation page, then the T1 result is in its own table labelled
    "post-call nowcast, not a forecast", with the same metrics, intervals and rows as the T0
    table.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("FR-29-AC2")
def test_fr_29_ac2_given_any_headline_claim_then_it_names():
    """FR-29-AC2: Given any headline claim, then it names T0 or T1."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ML-01-AC1")
def test_ml_01_ac1_two_runs_with_the_same_seed_and():
    """ML-01-AC1: Two runs with the same seed and snapshot produce identical predictions,
    and the metrics match to two decimal places.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ML-02-AC1")
def test_ml_02_ac1_access_log_shows_test_rows_read_only():
    """ML-02-AC1: Access log shows test rows read only in the final evaluation job."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ML-03-AC1")
def test_ml_03_ac1_altered_artefact_fails_to_load_with_a():
    """ML-03-AC1: Altered artefact fails to load with a checksum error."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ML-04-AC1")
def test_ml_04_ac1_explainer_and_model_share_the_artefact_identifier():
    """ML-04-AC1: Explainer and model share the artefact identifier."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ML-05-AC1")
def test_ml_05_ac1_registration_fails_if_the_report_file_is():
    """ML-05-AC1: Registration fails if the report file is missing."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ML-06-AC1")
def test_ml_06_ac1_promotion_step_checks_that_the_comparison_report():
    """ML-06-AC1: Promotion step checks that the comparison report and the sign-off record
    both exist for the new version.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MR-01-AC1")
def test_mr_01_ac1_every_registered_version_has_an_entry():
    """MR-01-AC1: Every registered version has an entry."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MR-02-AC1")
def test_mr_02_ac1_model_card_exists_for_every_served_version():
    """MR-02-AC1: Model card exists for every served version."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MR-04-AC1")
def test_mr_04_ac1_rolling_outcome_table_exists():
    """MR-04-AC1: Rolling outcome table exists."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MR-05-AC1")
def test_mr_05_ac1_drift_report_runs_on_the_schedule():
    """MR-05-AC1: Drift report runs on the schedule."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("MR-06-AC1")
def test_mr_06_ac1_rank_change_flag_fires_on_a_planted():
    """MR-06-AC1: Rank-change flag fires on a planted change."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("NFR-01-AC1")
def test_nfr_01_ac1_under_500_ms():
    """NFR-01-AC1: Under 500 ms"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("NFR-02-AC1")
def test_nfr_02_ac1_under_10_s_or_returned_as_pending():
    """NFR-02-AC1: Under 10 s, or returned as pending"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("NFR-03-AC1")
def test_nfr_03_ac1_check_runs_every_24_hours():
    """NFR-03-AC1: Check runs every 24 hours"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("NFR-07-AC1")
def test_nfr_07_ac1_automated_check_passes():
    """NFR-07-AC1: Automated check passes"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("NFR-08-AC1")
def test_nfr_08_ac1_no_horizontal_scrolling_on_prediction_card():
    """NFR-08-AC1: No horizontal scrolling on prediction card"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("NFR-09-AC1")
def test_nfr_09_ac1_completes_within_24_hours():
    """NFR-09-AC1: Completes within 24 hours"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("NFR-12-AC1")
def test_nfr_12_ac1_available_at_metrics():
    """NFR-12-AC1: Available at /metrics"""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("NFR-13-AC1")
def test_nfr_13_ac1_five_minutes():
    """NFR-13-AC1: Five minutes"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("PL-03-AC1")
def test_pl_03_ac1_health_response_lists_the_date_for_a():
    """PL-03-AC1: Health response lists the date for a test ticker."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("PL-04-AC1")
def test_pl_04_ac1_fixture_with_insufficient_eps_history_is_rejected():
    """PL-04-AC1: Fixture with insufficient EPS history is rejected with the logged reason."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


EXPECTED_SCHEMA = {
    "alembic_version": ["version_num"],
    "company": ["company_id", "name"],
    "dead_letter": [
        "dead_letter_id", "task_name", "args_hash", "error_class", "failed_at", "attempt_count",
        "run_id",
    ],
    "estimate_snapshot": [
        "snapshot_id", "company_id", "event_id", "mean_estimate", "low_estimate", "high_estimate",
        "std_estimate", "estimate_count", "eps_basis", "period_label", "source", "source_version",
        "captured_at", "raw_payload",
    ],
    "index_membership": [
        "index_membership_id", "company_id", "valid_from", "valid_to", "removal_reason",
    ],
    "ingestion_run": [
        "run_id", "job_name", "source", "started_at", "ended_at", "status", "rows_read",
        "rows_written", "error_class", "task_id",
    ],
    "raw_payload": [
        "payload_id", "source", "url", "retrieved_at", "sha256", "content_type", "byte_length",
        "body",
    ],
    "ticker_history": ["ticker_history_id", "company_id", "ticker", "valid_from", "valid_to"],
}  # fmt: skip


def _schema_snapshot(database):
    """{table: [columns in order]} plus the index names, read as the superuser."""
    import os

    import psycopg

    with psycopg.connect(
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"], dbname=database,
    ) as conn:  # fmt: skip
        rows = conn.execute(
            "SELECT table_name, column_name FROM information_schema.columns "
            "WHERE table_schema = 'public' ORDER BY table_name, ordinal_position"
        ).fetchall()
    out = {}
    for table, column in rows:
        out.setdefault(table, []).append(column)
    return out


@pytest.mark.req("PL-05-AC1")
@pytest.mark.code("src/earnings/migrate.py", "src/earnings/migrations/versions")
def test_pl_05_ac1_migration_history_matches_the_deployed_schema_on():
    """PL-05-AC1: Migration history matches the deployed schema on a clean database."""
    from sqlalchemy import create_engine, inspect
    from sqlalchemy.pool import NullPool

    from db_support import assert_test_database, project_database
    from earnings import migrate

    name = assert_test_database(project_database() + "_pl05_test")
    migrate.drop_database(name)
    try:
        migrate.bootstrap(name)
        migrate.upgrade(name)
        engine = create_engine(migrate.migrator_url(name), poolclass=NullPool)
        with engine.connect() as conn:
            head = conn.exec_driver_sql("SELECT version_num FROM alembic_version").scalar()
            tables = set(inspect(conn).get_table_names())
            columns = [c["name"] for c in inspect(conn).get_columns("company")]
        engine.dispose()
        assert head == migrate.head_revision()
        # The expected schema at head. A new migration adds its table here in the same change.
        assert tables == {
            "alembic_version",
            "company",
            "estimate_snapshot",
            "ingestion_run",
            "dead_letter",
            "raw_payload",
            "ticker_history",
            "index_membership",
        }
        assert columns == ["company_id", "name"]
        # Every column of every table, in order, and the same schema as the deployed database.
        built = _schema_snapshot(name)
        assert built == EXPECTED_SCHEMA
        assert _schema_snapshot(project_database()) == built
        migrate.downgrade(name, "base")  # the history is reversible
        engine = create_engine(migrate.migrator_url(name), poolclass=NullPool)
        with engine.connect() as conn:
            assert set(inspect(conn).get_table_names()) <= {"alembic_version"}
        engine.dispose()
    finally:
        migrate.drop_database(name)


@pytest.mark.req("PL-06-AC1")
def test_pl_06_ac1_hash_of_raw_text_is_identical_before():
    """PL-06-AC1: Hash of raw text is identical before and after cleaning."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-01-AC1")
def test_scr_01_ac1_input_field_submit_autocomplete_if_ui_01():
    """SCR-01-AC1: Input field, submit. Autocomplete if UI-01 is built (EP-10)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-02-AC1")
def test_scr_02_ac1_class_probabilities_confidence_evidence_base_input_as():
    """SCR-02-AC1: Class, probabilities, confidence, evidence base, input as-of times,
    sector context (SRS-11), not-investment-advice notice, link to explanation.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-03-AC1")
def test_scr_03_ac1_horizontal_bars_for_top_three_shap_features():
    """SCR-03-AC1: Horizontal bars for top three SHAP features, coloured by direction, with
    a data table alternative.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-04-AC1")
def test_scr_04_ac1_each_claim_its_faithfulness_label_the_cited():
    """SCR-04-AC1: Each claim, its faithfulness label, the cited sentence and its
    verification status.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-05-AC1")
def test_scr_05_ac1_date_class_confidence_realised_outcome_realised_sector():
    """SCR-05-AC1: Date, class, confidence, realised outcome, realised sector score, pending
    state, pagination.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-06-AC1")
def test_scr_06_ac1_baseline_comparison_table_with_confidence_intervals_calibrat():
    """SCR-06-AC1: Baseline comparison table with confidence intervals, calibration plot,
    precision at top 20%, global SHAP, label definition, limitations notice.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SCR-07-AC1")
def test_scr_07_ac1_peer_list_and_statistics_srs_12():
    """SCR-07-AC1: Peer list and statistics (SRS-12)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SM-01-AC1")
def test_sm_01_ac1_f1_and_auc_difference_reported_with_95():
    """SM-01-AC1: F1 and AUC difference reported with 95% bootstrap intervals."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-01-AC2")
def test_sm_01_ac2_no_pass_mark_a_negative_result_is():
    """SM-01-AC2: No pass mark: a negative result is valid (Proposal 7)."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-01-AC3")
def test_sm_01_ac3_counter_metric_brier_score_reported_beside_it():
    """SM-01-AC3: Counter-metric: Brier score reported beside it"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-02-AC1")
def test_sm_02_ac1_reported_beside_the_sae_fire_xgboost_baseline():
    """SM-02-AC1: Reported beside the SAE-FiRE XGBoost baseline (0.620 on calls) as a
    reference point, not a pass mark.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-02-AC2")
def test_sm_02_ac2_the_label_period_and_universe_differ_so():
    """SM-02-AC2: The label, period and universe differ, so the comparison is indicative
    only (FR-27).
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-02-AC3")
def test_sm_02_ac3_the_three_class_auc_is_not_compared():
    """SM-02-AC3: The three-class AUC is not compared with it."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-02-AC4")
def test_sm_02_ac4_counter_metric_share_of_events_excluded_as():
    """SM-02-AC4: Counter-metric: Share of events excluded as in-line"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-03-AC1")
def test_sm_03_ac1_reported_no_target_until_baseline_known():
    """SM-03-AC1: Reported; no target until baseline known"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-03-AC2")
def test_sm_03_ac2_counter_metric_coverage_share_of_events_receiving():
    """SM-03-AC2: Counter-metric: Coverage: share of events receiving a prediction"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-04-AC1")
def test_sm_04_ac1_at_least_90_of_predictions_have_a():
    """SM-04-AC1: At least 90% of predictions have a numeric sector context (proposed)"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-04-AC2")
def test_sm_04_ac2_counter_metric_share_showing_insufficient_peers_by():
    """SM-04-AC2: Counter-metric: Share showing "Insufficient peers", by year and sector"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-05-AC1")
def test_sm_05_ac1_100_verified_or_flagged():
    """SM-05-AC1: 100% verified or flagged"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-05-AC2")
def test_sm_05_ac2_counter_metric_explanation_length():
    """SM-05-AC2: Counter-metric: Explanation length"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-06-AC1")
def test_sm_06_ac1_reported_on_held_out_sample():
    """SM-06-AC1: Reported on held-out sample"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-06-AC2")
def test_sm_06_ac2_counter_metric_number_of_features_discussed_per():
    """SM-06-AC2: Counter-metric: Number of features discussed per explanation"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-07-AC1")
def test_sm_07_ac1_reported_per_explanation():
    """SM-07-AC1: Reported per explanation"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-07-AC2")
def test_sm_07_ac2_counter_metric_human_agreement_with_automated_labels():
    """SM-07-AC2: Counter-metric: Human agreement with automated labels (EX-05)"""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SM-08-AC1")
def test_sm_08_ac1_all_complete_j1_without_help():
    """SM-08-AC1: All complete J1 without help"""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SM-08-AC2")
def test_sm_08_ac2_counter_metric_time_to_complete_j2():
    """SM-08-AC2: Counter-metric: Time to complete J2"""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SRS-01-AC1")
def test_srs_01_ac1_data_vl_11_a_company_reclassified_in():
    """SRS-01-AC1: Data VL-11: a company reclassified in 2023 shows its old sector before
    the change date.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-02-AC1")
def test_srs_02_ac1_a_test_date_in_2015_resolves_to():
    """SRS-02-AC1: A test date in 2015 resolves to the structure in force then, and the
    stored version matches it.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-03-AC1")
def test_srs_03_ac1_unit_test_on_a_fixed_date_with():
    """SRS-03-AC1: Unit test on a fixed date with a known peer set passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-03-AC2")
def test_srs_03_ac2_a_company_removed_from_the_index_before():
    """SRS-03-AC2: A company removed from the index before D is not a peer."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-04-AC1")
def test_srs_04_ac1_test_a_peer_announcing_on_d_is():
    """SRS-04-AC1: Test: a peer announcing on D is excluded; a peer with two events in the
    window contributes only the later one; a peer whose last event is 101 days before D is
    excluded.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-05-AC1")
def test_srs_05_ac1_test_a_peer_event_with_5_prior():
    """SRS-05-AC1: Test: a peer event with 5 prior seasonal differences (or two estimates,
    under a consensus label) is excluded and counted.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-06-AC1")
def test_srs_06_ac1_fixture_with_four_eligible_peers_returns_insufficient():
    """SRS-06-AC1: Fixture with four eligible peers returns "Insufficient peers" and
    unavailable features.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-07-AC1")
def test_srs_07_ac1_test_with_a_planted_extreme_peer_sue():
    """SRS-07-AC1: Test with a planted extreme peer SUE shows it is clipped."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-07-AC2")
def test_srs_07_ac2_clip_limits_match_the_frozen_record():
    """SRS-07-AC2: Clip limits match the frozen record."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-08-AC1")
def test_srs_08_ac1_data_vl_03_peer_set_replay_matches():
    """SRS-08-AC1: Data VL-03 peer-set replay matches for 30 predictions."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-08-AC2")
def test_srs_08_ac2_a_planted_peer_event_dated_d_does():
    """SRS-08-AC2: A planted peer event dated D does not change the feature."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-09-AC1")
def test_srs_09_ac1_feature_matrix_schema_test_no_column_is():
    """SRS-09-AC1: Feature-matrix schema test: no column is derived from the event's own SUE."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-09-AC2")
def test_srs_09_ac2_before_the_announcement_the_api_returns_pending():
    """SRS-09-AC2: Before the announcement, the API returns "Pending" for the realised score."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-10-AC1")
def test_srs_10_ac1_recomputing_the_statistics_from_the_stored_peer():
    """SRS-10-AC1: Recomputing the statistics from the stored peer list reproduces the
    stored values.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-11-AC1")
def test_srs_11_ac1_ui_test_covers_all_three_states():
    """SRS-11-AC1: UI test covers all three states."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-12-AC1")
def test_srs_12_ac1_the_view_lists_exactly_the_peers_stored():
    """SRS-12-AC1: The view lists exactly the peers stored under SRS-10."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SRS-13-AC1")
def test_srs_13_ac1_coverage_table_exists_in_the_evaluation_report():
    """SRS-13-AC1: Coverage table exists in the evaluation report."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SRS-14-AC1")
def test_srs_14_ac1_configuration_test_with_sector_history_missing_no():
    """SRS-14-AC1: Configuration test: with sector history missing, no sector column is
    produced and the card shows "Sector comparison unavailable".
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TR-01-AC1")
def test_tr_01_ac1_every_headline_metric_on_the_evaluation_page():
    """TR-01-AC1: Every headline metric on the evaluation page has a 95% interval."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TR-02-AC1")
def test_tr_02_ac1_the_evaluation_page_states_the_variant_count():
    """TR-02-AC1: The evaluation page states the variant count and the adjustment."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TR-04-AC1")
def test_tr_04_ac1_per_year_table_exists_and_a_per():
    """TR-04-AC1: Per-year table exists, and a per-sector table where sector history exists."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TR-05-AC1")
def test_tr_05_ac1_decile_calibration_plot_exists():
    """TR-05-AC1: Decile calibration plot exists."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("TR-06-AC1")
def test_tr_06_ac1_both_appear_in_the_fr_06_table():
    """TR-06-AC1: Both appear in the FR-06 table on the same rows."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UI-01-AC1")
def test_ui_01_ac1_typing_two_letters_shows_matching_tickers():
    """UI-01-AC1: Typing two letters shows matching tickers."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UI-02-AC1")
def test_ui_02_ac1_automated_accessibility_check_finds_no_chart_without():
    """UI-02-AC1: Automated accessibility check finds no chart without an alternative."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UI-03-AC1")
def test_ui_03_ac1_each_citation_in_the_view_has_a():
    """UI-03-AC1: Each citation in the view has a visible status."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UI-04-AC1")
def test_ui_04_ac1_view_lists_every_peer_used_in_the():
    """UI-04-AC1: View lists every peer used in the calculation."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UI-05-AC1")
def test_ui_05_ac1_keyboard_only_walkthrough_completes_journey_j1():
    """UI-05-AC1: Keyboard-only walkthrough completes Journey J1."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")
