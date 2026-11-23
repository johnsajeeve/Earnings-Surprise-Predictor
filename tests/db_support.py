"""Test database helpers (Database DB-16): tests never touch the project database.

Synthetic rows are written only to the test database, and every fixture says it is synthetic
(Project-Wide SC-04).
"""

import os


def project_database() -> str:
    return os.environ["POSTGRES_DB"]


def test_database_name() -> str:
    """The test database is the project database name with the suffix _test."""
    return project_database() + "_test"


def assert_test_database(name: str) -> str:
    """Refuse to run against the project database. Returns the name when it is a test database."""
    if name == project_database() or not name.endswith("_test"):
        raise RuntimeError(f"refusing to use {name!r}: tests need a database ending in _test")
    return name
