"""Pytest configuration shared by all tests."""

import logging

import pytest

from requirement_support import KINDS


def pytest_configure(config):
    # A marker names the requirement check a test exercises, for example
    # req("FR-01-AC2") or req("SP-06"). References are validated by
    # scripts/check_requirement_refs.py against audits/acceptance_index.md.
    config.addinivalue_line(
        "markers",
        "req(*references): requirement checks this test exercises (see audits/acceptance_index.md)",
    )
    # The project files a test exercises. scripts/requirement_tests.py checks that they exist.
    config.addinivalue_line(
        "markers",
        "code(*paths): project files this test exercises, relative to the repository root",
    )


def pytest_collection_modifyitems(config, items):
    """A test with no requirement is an extra test. Refuse to run the suite with one."""
    orphans = [item.nodeid for item in items if item.get_closest_marker("req") is None]
    if orphans:
        raise pytest.UsageError("tests with no @pytest.mark.req(...): " + ", ".join(orphans))


def pytest_terminal_summary(terminalreporter):
    """Say how many requirement tests did not run, and why, so a skip is never read as a pass."""
    counts = dict.fromkeys(KINDS, 0)
    for report in terminalreporter.stats.get("skipped", []):
        longrepr = report.longrepr
        reason = longrepr[2] if isinstance(longrepr, tuple) else str(longrepr)
        for kind in KINDS:
            if kind in reason:
                counts[kind] += 1
                break
    total = sum(counts.values())
    if total:
        terminalreporter.write_sep("-", "requirement checks that did NOT run (not a pass)")
        for kind, number in counts.items():
            if number:
                terminalreporter.write_line(f"{kind}: {number}")
        terminalreporter.write_line(f"total not tested: {total}")


@pytest.fixture
def request_log():
    """Messages written by the API's request logger (earnings.request) during a test."""
    # Import first: the middleware sets up the logger only if it has no handler yet.
    import earnings.api.middleware  # noqa: F401

    messages: list[str] = []

    class _Collect(logging.Handler):
        def emit(self, record: logging.LogRecord) -> None:
            messages.append(record.getMessage())

    handler = _Collect()
    logger = logging.getLogger("earnings.request")
    logger.addHandler(handler)
    yield messages
    logger.removeHandler(handler)
