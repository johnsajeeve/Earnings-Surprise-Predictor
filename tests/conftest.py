"""Pytest configuration shared by all tests."""

import ipaddress
import logging
import os
import socket

import pytest

from db_support import assert_test_database, test_database_name
from requirement_support import KINDS


class ExternalNetworkBlocked(AssertionError):
    """A test tried to reach a host outside the local stack (Ingestion IG-12)."""


_connect = socket.socket.connect
# Libraries that do not use Python sockets (yfinance's curl) are sent to a closed local port.
_DEAD_PROXY = "http://127.0.0.1:9"
_LOCAL_NAMES = "localhost,127.0.0.1,::1,db,redis,api,worker"


def _guarded_connect(sock, address):
    if isinstance(address, tuple):
        info = ipaddress.ip_address(socket.gethostbyname(address[0]) if ":" not in address[0]
                                    else address[0].split("%")[0])  # fmt: skip
        if not (info.is_private or info.is_loopback):
            raise ExternalNetworkBlocked(f"a test tried to connect to {address[0]}")
    return _connect(sock, address)


def pytest_configure(config):
    socket.socket.connect = _guarded_connect
    for name in ("HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"):
        os.environ[name] = _DEAD_PROXY
    os.environ["NO_PROXY"] = os.environ["no_proxy"] = _LOCAL_NAMES
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


@pytest.fixture(scope="session")
def test_db_name():
    """A clean, fully migrated test database (Database DB-16, Product PL-05).

    Built from nothing every session, by the same code that migrates the project database.
    The rows tests write to it are synthetic.
    """
    from earnings import migrate

    name = assert_test_database(test_database_name())
    migrate.drop_database(name)
    migrate.bootstrap(name)
    migrate.upgrade(name)
    yield name
    migrate.drop_database(name)


@pytest.fixture
def test_db(test_db_name, monkeypatch):
    """Point the application at the test database for one test and empty the company table."""
    from earnings import migrate
    from earnings.config import get_settings
    from earnings.db import get_engine

    def close_pools():
        # Close the pools before forgetting them. A pool that is only forgotten keeps its server
        # connections, which the connection-limit check (DB-03) then counts.
        if get_engine.cache_info().currsize:
            for role in ("api", "worker"):
                get_engine(role).dispose()
        get_engine.cache_clear()

    monkeypatch.setenv("POSTGRES_DB", test_db_name)
    close_pools()  # before the settings change, so the pools of the old database are closed
    get_settings.cache_clear()
    migrate.truncate_all(test_db_name)
    yield test_db_name
    close_pools()
    get_settings.cache_clear()
