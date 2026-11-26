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

from requirement_support import ROOT, not_tested, repo_path, source_register


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
@pytest.mark.code("docs/adr")
def test_sc_07_ac1_an_adr_records_the_label_route():
    needed = ("label route", "time-series", "status:", "accepted", "supervisor")
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


def _matrix():
    """The test matrix tool, loaded from a full checkout (the CI test image has no copy)."""
    repo_path("scripts/test_matrix.py")
    repo_path("audits/acceptance_index.md")
    sys.path.insert(0, str(ROOT / "scripts"))
    import test_matrix

    return test_matrix


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py")
def test_do_03_a_check_fingerprint_ignores_spacing_but_not_wording():
    tool = _matrix()
    assert tool.fingerprint("Given a ticker,   then  X.") == tool.fingerprint(
        "Given a ticker, then X."
    )
    assert tool.fingerprint("then X.") != tool.fingerprint("then Y.")


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py")
def test_do_03_the_lock_flags_a_changed_new_and_removed_check():
    tool = _matrix()
    locked = {"FR-01-AC1": "aaa", "FR-01-AC2": "bbb", "FR-01-AC3": "ccc"}
    current = {"FR-01-AC1": "aaa", "FR-01-AC2": "CHANGED", "FR-01-AC4": "ddd"}
    problems = tool.lock_problems(current, locked)
    assert len(problems) == 3
    assert any("FR-01-AC2" in p and "wording changed" in p for p in problems)
    assert any("FR-01-AC4" in p and "new check" in p for p in problems)
    assert any("FR-01-AC3" in p and "removed or renumbered" in p for p in problems)
    assert tool.lock_problems(current, current) == []


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py", "tests/requirement_checks.lock")
def test_do_03_every_check_matches_the_text_its_tests_were_reviewed_against():
    tool = _matrix()
    assert tool.lock_problems(tool.current_fingerprints(), tool.read_lock()) == []


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py")
def test_do_03_junit_outcomes_map_to_pass_fail_blocked_and_not_tested():
    tool = _matrix()
    xml = """<testsuites><testsuite>
      <testcase classname="tests.test_a" name="test_pass"/>
      <testcase classname="tests.test_a" name="test_fail"><failure message="boom"/></testcase>
      <testcase classname="tests.test_a" name="test_stub">
        <skipped type="pytest.skip" message="NOT IMPLEMENTED: not built"/></testcase>
      <testcase classname="tests.test_a" name="test_wait">
        <skipped type="pytest.skip" message="BLOCKED: waits for D-37"/></testcase>
      <testcase classname="tests.test_a" name="test_known">
        <skipped type="pytest.xfail" message="NOT SATISFIED: x"/></testcase>
      <testcase classname="tests.test_a" name="test_cases[one]"/>
      <testcase classname="tests.test_a" name="test_cases[two]"><failure message="x"/></testcase>
    </testsuite></testsuites>"""
    got = tool.parse_junit(xml)
    assert got["tests/test_a.py::test_pass"] == ["PASS"]
    assert got["tests/test_a.py::test_fail"] == ["FAIL"]
    assert got["tests/test_a.py::test_stub"] == ["NOT TESTED"]
    assert got["tests/test_a.py::test_wait"] == ["BLOCKED"]
    assert got["tests/test_a.py::test_known"] == ["FAIL (known, requirement not met yet)"]
    assert tool.strongest(got["tests/test_a.py::test_cases"]) == "FAIL"
    assert tool.strongest(["PASS", "NOT TESTED"]) == "PASS"
    assert tool.strongest([]) == "NOT TESTED"


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py")
def test_do_03_coverage_contexts_map_each_test_to_the_files_it_executed():
    tool = _matrix()
    data = {
        "files": {
            "src/earnings/api/main.py": {"contexts": {"10": ["test_a.test_one"], "11": [""]}},
            "src/earnings/config.py": {"contexts": {"3": ["test_a.test_one", "test_a.test_two"]}},
        }
    }
    got = tool.parse_coverage(data)
    assert got["tests/test_a.py::test_one"] == [
        "src/earnings/api/main.py",
        "src/earnings/config.py",
    ]
    assert got["tests/test_a.py::test_two"] == ["src/earnings/config.py"]


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py", "audits/test_matrix.json", "audits/test_matrix.md")
def test_do_03_the_committed_matrix_is_what_the_markers_produce_now():
    tool = _matrix()
    matrix = tool.build_matrix()
    assert repo_path("audits/test_matrix.json").read_text(encoding="utf-8") == tool.render_json(
        matrix
    )
    assert repo_path("audits/test_matrix.md").read_text(encoding="utf-8") == tool.render_markdown(
        matrix
    )


@pytest.mark.req("DO-03")
@pytest.mark.code("scripts/test_matrix.py")
def test_do_03_the_matrix_can_be_walked_in_both_directions():
    matrix = _matrix().build_matrix()
    for rid, entry in matrix["requirements"].items():
        for check in entry["checks"]:
            for test in check["tests"]:
                assert check["ref"] in matrix["tests"][test]["requirements"]
        for test in entry["id_level_tests"]:
            assert rid in matrix["tests"][test]["requirements"]
    for key, test in matrix["tests"].items():
        for ref in test["requirements"]:
            rid = ref.split("-AC")[0]
            entry = matrix["requirements"][rid]
            linked = {t for c in entry["checks"] if c["ref"] == ref for t in c["tests"]}
            assert key in linked | set(entry["id_level_tests"]), (key, ref)
        for path in test["code"]:
            assert key in matrix["code"][path]["tests"]
            assert set(test["requirements"]) <= set(matrix["code"][path]["requirements"])
    for path, entry in matrix["code"].items():
        for key in entry["tests"]:
            assert path in matrix["tests"][key]["code"]


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


# Each registered task and the test that runs it twice and compares state (EQ-07). A new task
# that is not listed here fails the test below, so no task can be added without one.
RUN_TWICE_TESTS = {
    "earnings.check_new_filings": (
        "test_the_filing_check_run_twice_stores_one_copy_and_finds_nothing_new"
    ),
    "earnings.check_new_transcripts": "test_the_transcript_check_run_twice_changes_no_data",
    "earnings.run_data_gates": "test_the_data_gates_run_twice_leave_the_same_rows",
    "earnings.ping": None,  # holds no state
    "earnings.load_companies": "test_eq_07_load_companies_twice_leaves_the_same_rows",
    "earnings.capture_consensus": ("test_the_capture_task_run_twice_in_a_day_leaves_the_same_rows"),
    "earnings.capture_catch_up": (
        "test_the_catch_up_task_retries_when_the_database_is_still_starting"
    ),
    "earnings.fetch_company_facts": (
        "test_fetching_the_same_payload_twice_leaves_an_identical_table_hash"
    ),
}


@pytest.mark.req("EQ-07-AC1")
@pytest.mark.code("src/earnings/tasks.py", "tests/test_ingestion_framework.py")
def test_eq_07_ac1_every_registered_task_has_a_run_twice_test():
    """EQ-07-AC1: Test runs each task twice and compares state."""
    import importlib

    from earnings import tasks  # noqa: F401  (importing registers the tasks)
    from earnings.celery_app import celery_app

    registered = {n for n in celery_app.tasks if n.startswith("earnings.")}
    assert registered == set(RUN_TWICE_TESTS), "a task has no run-twice test (or one was removed)"
    sources = {
        name: importlib.import_module(name).__dict__
        for name in (
            "test_req_project_wide",
            "test_ingestion_framework",
            "test_edgar_client",
            "test_consensus_capture",
            "test_gaps",
        )
    }
    for task, test in RUN_TWICE_TESTS.items():
        if test is not None:
            assert any(test in namespace for namespace in sources.values()), (task, test)


@pytest.mark.req("EQ-07")
@pytest.mark.code("src/earnings/tasks.py", "src/earnings/db.py")
def test_eq_07_load_companies_twice_leaves_the_same_rows(test_db):
    """First task only (load_companies). Each later task adds its own run-twice test."""
    from sqlalchemy import text

    from earnings.db import get_engine
    from earnings.tasks import load_companies

    synthetic = [["320193", "SYNTHETIC one"], ["789019", "SYNTHETIC two"]]

    def snapshot():
        with get_engine("api").connect() as conn:
            return conn.execute(text("SELECT company_id, name FROM company ORDER BY 1")).all()

    assert load_companies(synthetic) == 2
    first = snapshot()
    assert load_companies(synthetic) == 2
    assert snapshot() == first == [("0000320193", "SYNTHETIC one"), ("0000789019", "SYNTHETIC two")]


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
@pytest.mark.code("src/earnings/source_register.csv")
def test_or_02_ac1_source_register_shows_zero_cost_for_every():
    """OR-02-AC1: Source register shows zero cost for every primary-route source."""
    primary = [r for r in source_register() if r["route"] == "primary"]
    assert primary and all(float(r["cost_usd_per_month"]) == 0 for r in primary)


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
