"""Helpers shared by the requirement tests (Project-Wide DO-03, Deterministic_audit.md Phase D).

A test exercises one acceptance check of one requirement and says so with
@pytest.mark.req("ID-ACn"). It can also say which project files it exercises with
@pytest.mark.code("src/earnings/..."). scripts/requirement_tests.py reads both markers and
prints the requirement, test and code relationship.

A test that cannot run yet calls not_tested(). It is skipped and counted as NOT TESTED, never as
passed. Skipping is only for code that does not exist yet, a decision that is still open, or a
check that needs a person or a measurement. A missing running stack is not a reason to skip:
the integration tests fail in that case, so a blocked environment is not hidden.
"""

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]

# The reasons a test may be skipped. The summary printed by conftest.py counts each one.
KINDS = (
    "NOT IMPLEMENTED",  # the code this check exercises is not built yet
    "BLOCKED",  # a value or decision it needs is still open (audits/pending_values.md)
    "NEEDS PERSON",  # a sign-off, approval or review by a person
    "NEEDS MEASUREMENT",  # a measured run on real data or hardware
    "NEEDS REPO",  # a file that exists in a full checkout but not in this environment
)


def not_tested(kind: str, why: str) -> None:
    """Skip the test and record why. Never a pass."""
    assert kind in KINDS, f"unknown kind {kind!r}"
    pytest.skip(f"{kind}: {why}")


def repo_path(relative: str) -> Path:
    """A file in the repository. Skips as NEEDS REPO where it is not available.

    The CI test job runs inside the application image, which holds src/ and scripts/ but not
    docs/, audits/, .github/ or docker-compose.yml. Those tests run in a full checkout.
    """
    path = ROOT / relative
    if not path.exists():
        not_tested("NEEDS REPO", f"{relative} is not in this environment")
    return path
