"""Licence requirements (docs/requirements/licensing-requirements.md, LC-01 to LC-11).

Four of them are not met today. Their tests are strict expected failures: each states the gap, and
each turns into a failure of the suite the day the gap closes, so the mark cannot be left behind.
"""

import csv
import re
from datetime import date, timedelta
from pathlib import Path

import pytest

from earnings import licensing as lic
from requirement_support import repo_path

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def _fixture_sources():
    with (FIXTURES / "fixture_sources.csv").open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


@pytest.mark.req("LC-01-AC1")
@pytest.mark.code("src/earnings/licensing.py", "src/earnings/third_party_register.csv")
def test_every_locked_package_and_container_image_has_a_licence_row():
    lock = repo_path("requirements.lock").read_text("utf-8")

    def by_name(kind):  # "redis" is both a Python package and a container image
        return {r["component"].lower(): r for r in lic.third_party() if r["kind"] == kind}

    rows, image_rows = by_name("python-package"), by_name("container-image")
    packages = lic.locked_packages(lock)
    assert len(packages) > 50  # the lock was read
    missing = [p for p in packages if p.lower() not in rows]
    wrong_version = [p for p, v in packages.items()
                     if p.lower() in rows and rows[p.lower()]["version"] != v]  # fmt: skip
    assert missing == [] and wrong_version == []
    compose = repo_path("docker-compose.yml").read_text("utf-8")
    dockerfile = repo_path("Dockerfile").read_text("utf-8")
    images = re.findall(r"^\s+image:\s*([a-z0-9./_-]+):(\S+)", compose, re.M)
    images += re.findall(r"^FROM\s+([a-z0-9./_-]+):(\S+)", dockerfile, re.M)
    assert {n for n, _ in images} >= {"postgres", "redis", "python"}
    for name, version in images:
        assert image_rows[name]["version"] == version, f"image {name} {version} has no row"
    for r in lic.third_party():
        assert all(r[k] for k in ("version", "licence", "licence_class", "evidence", "checked_on"))
    assert all(r["licence_class"] and r["licence"] for r in lic.datasets())


@pytest.mark.req("LC-02-AC1")
@pytest.mark.code("src/earnings/licensing.py")
def test_every_row_uses_a_listed_class_and_only_two_data_classes_may_be_deployed():
    for r in [*lic.datasets(), *lic.third_party()]:
        assert r["licence_class"] in lic.CLASSES, r
    assert lic.DEPLOYABLE_DATA == {"permissive", "public-information"}
    assert "share-alike" not in lic.DEPLOYABLE_DATA  # open, but not permissive


@pytest.mark.req("LC-03-AC1")
@pytest.mark.code("src/earnings/source_register.csv")
@pytest.mark.xfail(
    strict=True,
    reason="NOT MET: transcripts (unclear), prices and consensus (Yahoo terms), Finnhub "
    "(personal use) and Wikipedia (share-alike). Decision D-49",
)
def test_every_dataset_the_project_imports_may_be_deployed():
    assert lic.not_deployable_datasets() == {}


@pytest.mark.req("LC-03-AC1")
@pytest.mark.code("src/earnings/licensing.py", "src/earnings/source_register.csv")
def test_the_gap_in_dataset_licences_is_exactly_the_one_recorded():
    # pins today's gap, so a new source that may not be deployed cannot arrive unnoticed
    assert lic.not_deployable_datasets() == {
        "transcripts_hf": "unclear",
        "consensus_yfinance": "restricted",
        "prices_yfinance": "restricted",
        "consensus_finnhub": "restricted",
        "removal_names_reasons": "share-alike",
    }


@pytest.mark.req("LC-04-AC1", "SR-03", "DP-13")
@pytest.mark.code("src/earnings/licensing.py")
def test_a_bundle_with_a_dataset_that_may_not_be_deployed_is_refused():
    assert lic.bundle_violations(["eps_actuals", "index_membership"]) == []
    for bad in ("prices_yfinance", "transcripts_hf", "removal_names_reasons", "not_registered"):
        found = lic.bundle_violations(["eps_actuals", bad])
        assert len(found) == 1 and found[0].startswith(bad)
    assert lic.main(["x", "bundle", "eps_actuals"]) == 0
    assert lic.main(["x", "bundle", "prices_yfinance"]) == 1


@pytest.mark.req("LC-05-AC1")
@pytest.mark.code("src/earnings/licensing.py")
def test_the_committed_notices_are_the_ones_the_registers_produce():
    committed = repo_path("docs/THIRD_PARTY_NOTICES.md").read_text("utf-8")
    assert committed == lic.notices()
    assert "SEC EDGAR" in committed and "CC BY-SA 4.0" in committed and "redis 7.4.12" in committed


@pytest.mark.req("LC-06-AC1")
@pytest.mark.code("tests/fixtures/fixture_sources.csv")
def test_every_committed_fixture_says_which_dataset_it_comes_from():
    listed = {r["file"] for r in _fixture_sources()}
    present = {p.name for p in FIXTURES.iterdir() if p.is_file()}
    assert present - listed == {"README_universe.md", "fixture_sources.csv"}
    known = {r["dataset_id"] for r in lic.datasets()}
    assert {r["dataset_id"] for r in _fixture_sources()} <= known


@pytest.mark.req("LC-06-AC1", "DP-10")
@pytest.mark.code("tests/fixtures/fixture_sources.csv")
@pytest.mark.xfail(
    strict=True,
    reason="NOT MET: real transcript and Yahoo price excerpts, and Wikipedia text, are committed "
    "to the public repository. Decision D-49 (e)",
)
def test_no_committed_fixture_holds_real_data_from_a_source_that_may_not_be_deployed():
    barred = lic.not_deployable_datasets()
    held = [r["file"] for r in _fixture_sources()
            if r["content"] == "real" and r["dataset_id"] in barred]  # fmt: skip
    assert held == []


@pytest.mark.req("LC-07-AC1", "SR-01")
@pytest.mark.code("src/earnings/licensing.py", "src/earnings/clients")
def test_every_source_name_in_the_code_has_a_register_row():
    names = set()
    for path in (ROOT / "src" / "earnings").rglob("*.py"):
        names |= set(re.findall(r'^[A-Z_]*SOURCE = "([^"]+)"', path.read_text("utf-8"), re.M))
    assert len(names) >= 6  # the source constants were found
    assert names - set(lic.SOURCE_DATASETS) == set()
    known = {r["dataset_id"] for r in lic.datasets()}
    assert {d for rows in lic.SOURCE_DATASETS.values() for d in rows} <= known


@pytest.mark.req("LC-08-AC1")
@pytest.mark.code("src/earnings/licensing.py", "src/earnings/schedule.py")
def test_every_scheduled_job_declares_what_it_collects_and_a_barred_source_is_found():
    from earnings.schedule import JOBS

    assert set(JOBS) == set(lic.JOB_DATASETS)  # a new job must say what it collects
    assert lic.jobs_on_barred_sources(["data-gates", "check-8k"]) == []
    assert lic.jobs_on_barred_sources(["capture-consensus"]) == ["capture-consensus"]


@pytest.mark.req("LC-08-AC1")
@pytest.mark.code("src/earnings/schedule.py")
@pytest.mark.xfail(
    strict=True,
    reason="NOT MET: the daily consensus capture collects through yfinance. Decision D-49 (b)",
)
def test_no_scheduled_job_collects_from_a_source_whose_terms_bar_automation():
    from earnings.schedule import JOBS

    assert lic.jobs_on_barred_sources(list(JOBS)) == []


@pytest.mark.req("LC-09-AC1", "FE-05")
@pytest.mark.code("src/earnings/third_party_register.csv")
def test_every_model_row_names_the_licence_of_its_training_data():
    models = [r for r in lic.third_party() if r["kind"] == "model"]
    assert models and all(r["training_data_licence"].strip() for r in models)


@pytest.mark.req("LC-10-AC1")
@pytest.mark.code("src/earnings/licensing.py")
def test_a_licence_check_older_than_ninety_days_is_listed_as_stale():
    today = date(2027, 3, 1)  # SYNTHETIC rows
    rows = [
        {"component": "edge", "checked_on": str(today - timedelta(days=90))},
        {"component": "old", "checked_on": str(today - timedelta(days=91))},
        {"component": "blank", "checked_on": ""},
    ]
    assert lic.stale_rows(rows, today, "checked_on") == ["old", "blank"]


@pytest.mark.req("LC-11-AC1")
@pytest.mark.code("src/earnings/third_party_register.csv")
@pytest.mark.xfail(
    strict=True,
    reason="NOT MET: Redis 7.4 is source-available, and the Python base image's licences are not "
    "established. Decision D-49 (d)",
)
def test_every_library_and_image_in_use_may_be_used_in_a_deployed_system():
    assert lic.software_exceptions() == {}


@pytest.mark.req("LC-11-AC1")
@pytest.mark.code("src/earnings/licensing.py", "src/earnings/third_party_register.csv")
def test_the_software_exceptions_are_exactly_the_ones_recorded():
    assert lic.software_exceptions() == {"redis": "source-available", "python": "unclear"}
