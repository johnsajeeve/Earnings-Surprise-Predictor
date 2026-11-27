"""Tests for the deployment and operations requirements (deployment-and-operations-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that calls
not_tested() is a placeholder for code that does not exist yet. It is skipped and reported as
NOT TESTED, never as passed. Replace the call with a real check when the code is built
(Deterministic_audit.md, Phase D).

The checks that read the repository skip as NEEDS REPO inside the CI test container. They run in
a full checkout.
"""

import shutil
import subprocess

import pytest

from requirement_support import ROOT, not_tested, repo_path

_CI_COMMANDS = (
    "python3 docs/tools/check_requirements.py",
    "python3 audits/generate_traceability.py",
    "git diff --exit-code -- audits",
    "python3 scripts/check_requirement_refs.py",
    "python3 scripts/check_commit_refs.py",
)


@pytest.mark.req("DP-07")
@pytest.mark.code(
    ".github/workflows/ci.yml",
    "docs/tools/check_requirements.py",
    "scripts/check_requirement_refs.py",
    "scripts/check_commit_refs.py",
)
def test_dp_07_ci_runs_the_requirement_consistency_checks():
    ci = repo_path(".github/workflows/ci.yml").read_text(encoding="utf-8")
    assert "Requirements consistency (DO-03, DO-05)" in ci
    for command in _CI_COMMANDS:
        assert command in ci, command


@pytest.mark.req("DP-10-AC1")
@pytest.mark.code(".gitignore")
def test_dp_10_ac1_no_private_file_is_tracked_by_git():
    repo_path(".git")
    git = shutil.which("git")
    if git is None:
        not_tested("NEEDS REPO", "git is not installed in this environment")
    listing = subprocess.run(
        [git, "-C", str(ROOT), "ls-files"], capture_output=True, text=True, check=True
    ).stdout.splitlines()
    private_suffixes = (".pkl", ".joblib", ".parquet", ".pt", ".onnx", ".ubj")
    private_folders = ("docs/source/", "data/", "models/")
    for path in listing:
        assert path != ".env", path
        assert not path.startswith(private_folders), path
        assert not path.endswith(private_suffixes), path


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.


@pytest.mark.req("DP-01-AC2")
def test_dp_01_ac2_timed_run_is_recorded():
    """DP-01-AC2: Timed run is recorded."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-02-AC1")
def test_dp_02_ac1_the_100_company_pipeline_finishes_with_no():
    """DP-02-AC1: The 100-company pipeline finishes with no out-of-memory kill."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-02-AC2")
def test_dp_02_ac2_peak_memory_table_exists():
    """DP-02-AC2: Peak memory table exists."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-03-AC1")
def test_dp_03_ac1_api_image_has_none_of_the_model():
    """DP-03-AC1: API image has none of the model packages and is under the size recorded at
    the last build.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-04-AC1")
def test_dp_04_ac1_restore_record_shows_matching_counts():
    """DP-04-AC1: Restore record shows matching counts."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-05-AC1")
def test_dp_05_ac1_each_step_has_a_dated_run_record():
    """DP-05-AC1: Each step has a dated run record."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-06-AC1")
def test_dp_06_ac1_secret_scan_passes_project_wide_sp_06():
    """DP-06-AC1: Secret scan passes (Project-Wide SP-06)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-06-AC2")
def test_dp_06_ac2_image_history_contains_no_secret_value():
    """DP-06-AC2: Image history contains no secret value."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-07-AC1")
def test_dp_07_ac1_a_planted_duplicate_id_a_stale_generated():
    """DP-07-AC1: A planted duplicate ID, a stale generated file, a test with an unknown
    reference and a code commit with no requirement ID each fail the job.
    """
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-08-AC1")
def test_dp_08_ac1_modelversion_has_a_commit_field():
    """DP-08-AC1: ModelVersion has a commit field."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-08-AC2")
def test_dp_08_ac2_tags_exist_for_finished_milestones():
    """DP-08-AC2: Tags exist for finished milestones."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-09-AC1")
def test_dp_09_ac1_log_schema_test_project_wide_sp_05():
    """DP-09-AC1: Log schema test (Project-Wide SP-05)."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-11-AC1")
def test_dp_11_ac1_adr_0003_exists_and_is_accepted():
    """DP-11-AC1: ADR 0003 exists and is accepted."""
    not_tested("BLOCKED", "waits for open decision D-15")


@pytest.mark.req("DP-12-AC1")
def test_dp_12_ac1_budget_alert_exists_before_any_resource_is():
    """DP-12-AC1: Budget alert exists before any resource is listed."""
    not_tested("BLOCKED", "waits for open decision D-15")


@pytest.mark.req("DP-13-AC1")
def test_dp_13_ac1_the_demo_bundle_manifest_lists_each_source():
    """DP-13-AC1: The demo bundle manifest lists each source and its licence with no
    personal-use source.
    """
    not_tested("BLOCKED", "waits for open decision D-18")


@pytest.mark.req("DP-14-AC1")
def test_dp_14_ac1_rollback_is_timed_once():
    """DP-14-AC1: Rollback is timed once."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-14-AC2")
def test_dp_14_ac2_service_scales_to_zero_in_a_test():
    """DP-14-AC2: Service scales to zero in a test."""
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("DP-15-AC1")
def test_dp_15_ac1_adr_0003_names_how_the_worker_runs():
    """DP-15-AC1: ADR 0003 names how the worker runs."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("DP-16-AC1")
def test_dp_16_ac1_placeholder():
    """DP-16-AC1: Every hosted component has a row with its host, limits, source page, date and
    datasets.
    """
    not_tested("NOT IMPLEMENTED", "no deployment profile exists yet")


@pytest.mark.req("DP-17-AC1")
def test_dp_17_ac1_placeholder():
    """DP-17-AC1: A terms record with a date exists for every host in the deployment profile."""
    not_tested("NOT IMPLEMENTED", "no host has been chosen")


@pytest.mark.req("DP-18-AC1")
def test_dp_18_ac1_placeholder():
    """DP-18-AC1: An export that would include a dataset that may not be deployed fails."""
    not_tested("NOT IMPLEMENTED", "the export is not built")


@pytest.mark.req("DP-19-AC1")
def test_dp_19_ac1_placeholder():
    """DP-19-AC1: A scan of each image to be deployed finds none of them."""
    not_tested("NOT IMPLEMENTED", "no image is built for deployment")


@pytest.mark.req("DP-20-AC1")
def test_dp_20_ac1_placeholder():
    """DP-20-AC1: With the setting on, the prediction endpoints return the unavailable state
    and health reports it.
    """
    not_tested("NOT IMPLEMENTED", "there is no prediction endpoint yet")
