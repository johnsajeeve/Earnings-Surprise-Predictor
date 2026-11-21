"""Tests for the API and serving requirements (api-and-serving-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that calls
not_tested() is a placeholder for code that does not exist yet. It is skipped and reported as
NOT TESTED, never as passed. Replace the call with a real check when the code is built
(Deterministic_audit.md, Phase D).
"""

import ast

import pytest

from requirement_support import ROOT, not_tested

_MODEL_PACKAGES = {"torch", "transformers", "spacy", "xgboost", "shap", "sklearn", "lightgbm"}


@pytest.mark.req("SV-01-AC1")
@pytest.mark.code("src/earnings/api/main.py", "src/earnings/api/middleware.py")
def test_sv_01_ac1_the_api_code_imports_no_model_package():
    imported = set()
    for path in (ROOT / "src" / "earnings" / "api").rglob("*.py"):
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Import):
                imported |= {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.module:
                imported.add(node.module.split(".")[0])
    assert not imported & _MODEL_PACKAGES, imported & _MODEL_PACKAGES


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("SV-01-AC2")
def test_sv_01_ac2_a_request_makes_no_model_call():
    """SV-01-AC2: A request makes no model call."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-02-AC1")
def test_sv_02_ac1_a_static_check_finds_no_database_call():
    """SV-02-AC1: A static check finds no database call in a route."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-03-AC1")
def test_sv_03_ac1_fixture_company_with_a_renamed_ticker_resolves():
    """SV-03-AC1: Fixture company with a renamed ticker resolves to one company."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-03-AC2")
def test_sv_03_ac2_t0_and_t1_are_returned_as_two():
    """SV-03-AC2: T0 and T1 are returned as two labelled items."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-04-AC1")
def test_sv_04_ac1_contract_test_checks_the_envelope_and_the():
    """SV-04-AC1: Contract test checks the envelope and the as-of times on each prediction
    endpoint.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-05-AC1")
def test_sv_05_ac1_fixture_with_each_invalid_input_returns_the():
    """SV-05-AC1: Fixture with each invalid input returns the expected status and message."""
    not_tested("BLOCKED", "waits for open decision D-43")


@pytest.mark.req("SV-06-AC1")
def test_sv_06_ac1_two_identical_requests_give_one_job():
    """SV-06-AC1: Two identical requests give one job."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-06-AC2")
def test_sv_06_ac2_status_never_moves_backwards():
    """SV-06-AC2: Status never moves backwards."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-06-AC3")
def test_sv_06_ac3_a_queue_failure_leaves_a_failed_row():
    """SV-06-AC3: A queue failure leaves a failed row."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-06-AC4")
def test_sv_06_ac4_an_unknown_identifier_returns_404():
    """SV-06-AC4: An unknown identifier returns 404."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-07-AC1")
def test_sv_07_ac1_fixture_with_an_unreleased_event_shows_pending():
    """SV-07-AC1: Fixture with an unreleased event shows Pending."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-07-AC2")
def test_sv_07_ac2_unknown_model_name_returns_422():
    """SV-07-AC2: Unknown model name returns 422."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-08-AC1")
def test_sv_08_ac1_altered_artefact_makes_the_prediction_endpoint_return():
    """SV-08-AC1: Altered artefact makes the prediction endpoint return 503 with the Section
    12 message.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-08-AC2")
def test_sv_08_ac2_the_error_log_line_exists():
    """SV-08-AC2: The error log line exists."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-09-AC1")
def test_sv_09_ac1_load_test_report_states_the_95th_percentile():
    """SV-09-AC1: Load test report states the 95th percentile against 500 ms."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("SV-10-AC1")
def test_sv_10_ac1_load_fixture_over_the_limit_gets_429():
    """SV-10-AC1: Load fixture over the limit gets 429 with the header."""
    not_tested("BLOCKED", "waits for open decision D-43")


@pytest.mark.req("SV-10-AC2")
def test_sv_10_ac2_redis_stopped_requests_pass_and_a_warning():
    """SV-10-AC2: Redis stopped: requests pass and a warning is logged."""
    not_tested("BLOCKED", "waits for open decision D-43")


@pytest.mark.req("SV-11-AC1")
def test_sv_11_ac1_scrape_output_contains_route_templates_and_no():
    """SV-11-AC1: Scrape output contains route templates and no ticker values."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-12-AC1")
def test_sv_12_ac1_health_response_lists_the_date_for_a():
    """SV-12-AC1: Health response lists the date for a test ticker and the artefact status."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-12-AC2")
def test_sv_12_ac2_secret_scan_of_the_response_passes():
    """SV-12-AC2: Secret scan of the response passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-13-AC1")
def test_sv_13_ac1_oversized_body_is_refused():
    """SV-13-AC1: Oversized body is refused."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-13-AC2")
def test_sv_13_ac2_a_cross_origin_test_request_from_an():
    """SV-13-AC2: A cross-origin test request from an arbitrary origin is refused."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-14-AC1")
def test_sv_14_ac1_injected_failure_fixtures_return_the_message_and():
    """SV-14-AC1: Injected failure fixtures return the message and are logged."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-15-AC1")
def test_sv_15_ac1_request_without_a_token_returns_401():
    """SV-15-AC1: Request without a token returns 401."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-15-AC2")
def test_sv_15_ac2_expired_tampered_and_none_tokens_return_401():
    """SV-15-AC2: Expired, tampered and "none" tokens return 401."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-16-AC1")
def test_sv_16_ac1_secret_scan_passes():
    """SV-16-AC1: Secret scan passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SV-16-AC2")
def test_sv_16_ac2_logs_contain_no_token():
    """SV-16-AC2: Logs contain no token."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")
