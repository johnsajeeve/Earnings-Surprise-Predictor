"""Tests for the project wide requirements (project-wide-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that calls
not_tested() is a placeholder for code that does not exist yet. It is skipped and reported as
NOT TESTED, never as passed. Replace the call with a real check when the code is built
(Deterministic_audit.md, Phase D).

The checks that read the repository (docs, CI, compose) skip as NEEDS REPO inside the CI test
container, which holds only src/ and scripts/. They run in a full checkout.
"""

import subprocess
import sys

import pytest

from requirement_support import ROOT, not_tested, repo_path


def _ci() -> str:
    return repo_path(".github/workflows/ci.yml").read_text(encoding="utf-8")


def _adr_texts() -> list[str]:
    folder = repo_path("docs/adr")
    return [p.read_text(encoding="utf-8").lower() for p in sorted(folder.glob("*.md"))]


@pytest.mark.req("SC-01-AC1")
@pytest.mark.code("docs/adr/0001-celery-redis-task-queue.md", "src/earnings/celery_app.py")
def test_sc_01_ac1_adr_records_celery_with_redis_as_accepted():
    adr = repo_path("docs/adr/0001-celery-redis-task-queue.md").read_text(encoding="utf-8")
    assert "Celery with Redis" in adr
    assert "Status: **Accepted**" in adr


@pytest.mark.req("SC-02-AC1")
@pytest.mark.code("docs/adr/0002-streamlit-frontend.md")
def test_sc_02_ac1_adr_records_streamlit_as_accepted():
    adr = repo_path("docs/adr/0002-streamlit-frontend.md").read_text(encoding="utf-8")
    assert "Use Streamlit" in adr
    assert "Status: **Accepted**" in adr


@pytest.mark.req("SC-02-AC2")
@pytest.mark.code("requirements.txt", "requirements-pending.txt")
def test_sc_02_ac2_only_one_frontend_framework_is_in_the_repository():
    assert not (ROOT / "package.json").exists()
    for name in ("requirements.txt", "requirements-pending.txt"):
        text = repo_path(name).read_text(encoding="utf-8").lower()
        assert "react" not in text


@pytest.mark.req("SC-06-AC1")
@pytest.mark.xfail(
    strict=True, reason="NOT SATISFIED: no ADR records plain SQL retrieval and the licence check"
)
@pytest.mark.code("docs/adr")
def test_sc_06_ac1_an_adr_records_plain_sql_retrieval_with_the_licence_check():
    needed = ("plain sql", "retrieval", "licence")
    assert any(all(word in text for word in needed) for text in _adr_texts())


@pytest.mark.req("SC-07-AC1")
@pytest.mark.xfail(strict=True, reason="NOT SATISFIED: no ADR records the label route yet")
@pytest.mark.code("docs/adr")
def test_sc_07_ac1_an_adr_records_the_label_route():
    needed = ("label route", "time-series")
    assert any(all(word in text for word in needed) for text in _adr_texts())


@pytest.mark.req("EQ-01")
@pytest.mark.code(".github/workflows/ci.yml")
def test_eq_01_ci_runs_the_tests_on_every_pull_request():
    ci = _ci()
    assert "pull_request:" in ci
    assert "python -m pytest" in ci


@pytest.mark.req("EQ-02")
@pytest.mark.code(".github/workflows/ci.yml", "pyproject.toml")
def test_eq_02_ci_runs_lint_format_and_type_checks():
    ci = _ci()
    for command in ("ruff check .", "ruff format --check .", "mypy"):
        assert command in ci


@pytest.mark.req("EQ-04-AC2")
@pytest.mark.code("scripts/check_pins.py")
def test_eq_04_ac2_an_unpinned_dependency_fails_the_pin_check(tmp_path):
    script = repo_path("scripts/check_pins.py")
    unpinned = tmp_path / "unpinned.txt"
    unpinned.write_text("requests>=2.0\n", encoding="utf-8")
    pinned = tmp_path / "pinned.txt"
    pinned.write_text("requests==2.34.2\n", encoding="utf-8")
    bad = subprocess.run([sys.executable, str(script), str(unpinned)], capture_output=True)
    good = subprocess.run([sys.executable, str(script), str(pinned)], capture_output=True)
    assert bad.returncode == 1
    assert good.returncode == 0


@pytest.mark.req("EQ-04")
@pytest.mark.code("requirements.txt", "requirements.lock", "Dockerfile", "scripts/check_pins.py")
def test_eq_04_the_dependency_files_in_the_repository_are_pinned():
    script = repo_path("scripts/check_pins.py")
    files = [repo_path("requirements.txt"), repo_path("requirements.lock")]
    for name in ("requirements-pending.txt", "requirements-dev.txt"):
        if (ROOT / name).exists():
            files.append(ROOT / name)
    result = subprocess.run(
        [sys.executable, str(script), *map(str, files)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.req("EQ-04")
@pytest.mark.code("Dockerfile", "docker-compose.yml")
def test_eq_04_images_are_pinned_to_exact_tags():
    dockerfile = repo_path("Dockerfile").read_text(encoding="utf-8")
    first_from = next(line for line in dockerfile.splitlines() if line.startswith("FROM "))
    assert first_from.split(":")[-1][0].isdigit(), first_from
    compose = repo_path("docker-compose.yml").read_text(encoding="utf-8")
    images = [line.split("image:")[1].strip() for line in compose.splitlines() if "image:" in line]
    assert images
    for image in images:
        assert ":" in image and not image.endswith(":latest"), image
        assert image.split(":")[-1][0].isdigit(), image


@pytest.mark.req("EQ-08-AC1")
@pytest.mark.code(".github/workflows/ci.yml", "requirements.lock")
def test_eq_08_ac1_a_vulnerability_scan_job_runs_on_every_pull_request():
    ci = _ci()
    assert "pull_request:" in ci
    assert "pip-audit" in ci


@pytest.mark.req("SP-06-AC1")
@pytest.mark.code(".github/workflows/ci.yml")
def test_sp_06_ac1_a_secret_scanner_runs_in_continuous_integration():
    assert "gitleaks" in _ci()


@pytest.mark.req("DO-05-AC1")
@pytest.mark.code("docs/tools/check_requirements.py", "docs/requirements")
def test_do_05_ac1_the_id_checker_reports_no_duplicate_definition():
    script = repo_path("docs/tools/check_requirements.py")
    result = subprocess.run(
        [sys.executable, str(script)], capture_output=True, text=True, cwd=str(ROOT)
    )
    assert result.returncode == 0, result.stdout + result.stderr


@pytest.mark.req("SP-05-AC1")
@pytest.mark.code("src/earnings/api/middleware.py")
def test_sp_05_ac1_the_request_log_holds_only_the_allowed_fields(request_log):
    from fastapi.testclient import TestClient

    from earnings.api import main

    client = TestClient(main.app)
    client.get("/no-such-path?token=query-secret-1", headers={"Authorization": "Bearer hdr-2"})
    assert len(request_log) == 1
    line = request_log[0]
    fields = {part.split("=")[0] for part in line.split() if "=" in part}
    assert fields == {"request_id", "method", "path", "status", "latency_ms"}
    assert "query-secret-1" not in line
    assert "hdr-2" not in line
    assert "testclient" not in line


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("AI-01-AC1")
def test_ai_01_ac1_all_three_fields_are_non_null_on():
    """AI-01-AC1: All three fields are non-null on every stored explanation."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("AI-02-AC1")
def test_ai_02_ac1_regression_report_exists_for_each_change():
    """AI-02-AC1: Regression report exists for each change."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("AI-03-AC1")
def test_ai_03_ac1_results_table_shows_three_values_per_metric():
    """AI-03-AC1: Results table shows three values per metric."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("ASM-01-AC1")
def test_asm_01_ac1_traceability_matrix_do_03_has_no_requirement():
    """ASM-01-AC1: Traceability matrix (DO-03) has no requirement without a link."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-02-AC1")
def test_asm_02_ac1_claim_checklist_is_complete_before_submission():
    """ASM-02-AC1: Claim checklist is complete before submission."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-03-AC1")
def test_asm_03_ac1_novelty_register_has_an_entry_for_each():
    """ASM-03-AC1: Novelty register has an entry for each claim."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-03-AC2")
def test_asm_03_ac2_unverified_claims_in_the_planning_notes_are():
    """ASM-03-AC2: Unverified claims in the planning notes are marked."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-04-AC1")
def test_asm_04_ac1_summary_is_reviewed_at_ss_03():
    """ASM-04-AC1: Summary is reviewed at SS-03."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-05-AC1")
def test_asm_05_ac1_change_entry_exists_ss_04():
    """ASM-05-AC1: Change entry exists (SS-04)."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-05-AC2")
def test_asm_05_ac2_the_methodology_section_cites_it():
    """ASM-05-AC2: The methodology section cites it."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-06-AC1")
def test_asm_06_ac1_methodology_section_and_results_tables_name_the():
    """ASM-06-AC1: Methodology section and results tables name the route."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ASM-06-AC2")
def test_asm_06_ac2_claim_checklist_asm_02_has_a_label():
    """ASM-06-AC2: Claim checklist (ASM-02) has a label-route column."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("DO-01-AC1")
def test_do_01_ac1_timed_run_recorded():
    """DO-01-AC1: Timed run recorded."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DO-02-AC1")
def test_do_02_ac1_adr_list_is_complete_before_week_6():
    """DO-02-AC1: ADR list is complete before Week 6."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DO-03-AC1")
def test_do_03_ac1_no_requirement_without_evidence_at_submission():
    """DO-03-AC1: No requirement without evidence at submission."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DO-04-AC1")
def test_do_04_ac1_each_step_has_a_dated_run_record():
    """DO-04-AC1: Each step has a dated run record."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("EQ-01-AC1")
def test_eq_01_ac1_merge_is_blocked_by_a_planted_failing():
    """EQ-01-AC1: Merge is blocked by a planted failing test."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EQ-02-AC1")
def test_eq_02_ac1_a_planted_style_error_fails_the_job():
    """EQ-02-AC1: A planted style error fails the job."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EQ-03-AC1")
def test_eq_03_ac1_branch_protection_is_on_in_the_repository():
    """EQ-03-AC1: Branch protection is on in the repository settings."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("EQ-04-AC1")
def test_eq_04_ac1_build_succeeds_on_a_fresh_clone_in():
    """EQ-04-AC1: Build succeeds on a fresh clone in a clean environment."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EQ-05-AC1")
def test_eq_05_ac1_load_test_report_exists():
    """EQ-05-AC1: Load test report exists."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("EQ-06-AC1")
def test_eq_06_ac1_three_scripted_tests_pass():
    """EQ-06-AC1: Three scripted tests pass."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EQ-07-AC1")
def test_eq_07_ac1_test_runs_each_task_twice_and_compares():
    """EQ-07-AC1: Test runs each task twice and compares state."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("EQ-09-AC1")
def test_eq_09_ac1_coverage_report_in_continuous_integration():
    """EQ-09-AC1: Coverage report in continuous integration."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ET-01-AC1")
def test_et_01_ac1_approval_reference_on_file():
    """ET-01-AC1: Approval reference on file."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ET-02-AC1")
def test_et_02_ac1_documents_on_file():
    """ET-02-AC1: Documents on file."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ET-02-AC2")
def test_et_02_ac2_retention_date_recorded():
    """ET-02-AC2: Retention date recorded."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("ET-03-AC1")
def test_et_03_ac1_register_is_complete_before_the_demo():
    """ET-03-AC1: Register is complete before the demo."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ET-04-AC1")
def test_et_04_ac1_text_scan_of_all_alert_templates():
    """ET-04-AC1: Text scan of all alert templates."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ET-04-AC2")
def test_et_04_ac2_disclaimer_test_passes():
    """ET-04-AC2: Disclaimer test passes."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("ET-05-AC1")
def test_et_05_ac1_written_confirmation_of_the_tier_and_declaration():
    """ET-05-AC1: Written confirmation of the tier and declaration format from the unit lead
    for each assessed item.
    """
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("OR-01-AC1")
def test_or_01_ac1_restore_test_log_exists():
    """OR-01-AC1: Restore test log exists."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("OR-02-AC1")
def test_or_02_ac1_source_register_shows_zero_cost_for_every():
    """OR-02-AC1: Source register shows zero cost for every primary-route source."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("OR-02-AC2")
def test_or_02_ac2_budget_alert_exists_before_any_spend():
    """OR-02-AC2: Budget alert exists before any spend."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("OR-03-AC1")
def test_or_03_ac1_demo_service_account_has_no_write_rights():
    """OR-03-AC1: Demo service account has no write rights on the evaluation schema."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("PD-01-AC1")
def test_pd_01_ac1_capacity_check_is_recorded_at_each_milestone():
    """PD-01-AC1: Capacity check is recorded at each milestone."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("PD-02-AC1")
def test_pd_02_ac1_drop_order_is_dated_and_approved_at():
    """PD-02-AC1: Drop order is dated and approved at SS-03."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("PD-03-AC1")
def test_pd_03_ac1_milestone_checklist_signed_off():
    """PD-03-AC1: Milestone checklist signed off."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("PD-04-AC1")
def test_pd_04_ac1_decision_log_entry_exists_for_each_slip():
    """PD-04-AC1: Decision log entry exists for each slip."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("PD-05-AC1")
def test_pd_05_ac1_dated_review_entries():
    """PD-05-AC1: Dated review entries."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("PD-06-AC1")
def test_pd_06_ac1_dated_drop_order_list_approved_at_ss():
    """PD-06-AC1: Dated drop-order list approved at SS-03."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SC-01-AC2")
def test_sc_01_ac2_deployment_diagram_matches_the_adr():
    """SC-01-AC2: Deployment diagram matches the ADR."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SC-03-AC1")
def test_sc_03_ac1_review_checklist_includes_the_five_items():
    """SC-03-AC1: Review checklist includes the five items."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SC-04-AC1")
def test_sc_04_ac1_reported_tables_state_their_data_source():
    """SC-04-AC1: Reported tables state their data source."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SC-04-AC2")
def test_sc_04_ac2_the_evaluation_job_refuses_synthetic_input():
    """SC-04-AC2: The evaluation job refuses synthetic input."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SC-05-AC1")
def test_sc_05_ac1_no_rouge_or_bertscore_threshold_exists_in():
    """SC-05-AC1: No ROUGE or BERTScore threshold exists in the evaluation harness."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SC-07-AC2")
def test_sc_07_ac2_a_test_fails_if_events_with_different():
    """SC-07-AC2: A test fails if events with different label routes are in one training set
    (Data CE-05).
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SP-01-AC1")
def test_sp_01_ac1_loader_test_with_a_pickle_file_fails():
    """SP-01-AC1: Loader test with a pickle file fails as expected."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SP-02-AC1")
def test_sp_02_ac1_review_checklist_is_signed_off_before_release():
    """SP-02-AC1: Review checklist is signed off before release."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SP-03-AC1")
def test_sp_03_ac1_test_set_of_20_transcript_excerpts_containing():
    """SP-03-AC1: Test set of 20 transcript excerpts containing planted instructions: agent
    behaviour does not change.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SP-04-AC1")
def test_sp_04_ac1_register_entry_exists_for_each_provider():
    """SP-04-AC1: Register entry exists for each provider."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SP-05-AC2")
def test_sp_05_ac2_retention_job_runs():
    """SP-05-AC2: Retention job runs."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SP-06-AC2")
def test_sp_06_ac2_a_planted_key_fails_the_job():
    """SP-06-AC2: A planted key fails the job."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("SS-01-AC1")
def test_ss_01_ac1_action_list_exists_for_each_meeting():
    """SS-01-AC1: Action list exists for each meeting."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SS-02-AC1")
def test_ss_02_ac1_each_item_is_closed_or_has_a():
    """SS-02-AC1: Each item is closed or has a date."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SS-02-AC2")
def test_ss_02_ac2_no_requirement_document_holds_its_own_open():
    """SS-02-AC2: No requirement document holds its own open-decision list."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("SS-03-AC1")
def test_ss_03_ac1_sign_off_record_on_file():
    """SS-03-AC1: Sign-off record on file."""
    not_tested("BLOCKED", "waits for open decision D-40, D-46")


@pytest.mark.req("SS-04-AC1")
def test_ss_04_ac1_change_log_is_complete():
    """SS-04-AC1: Change log is complete."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")
