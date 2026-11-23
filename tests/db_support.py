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


def table_hash(conn, table: str, columns: list[str]) -> str:
    """A hash of the chosen columns of a table in a fixed order, to compare table state."""
    cols = ", ".join(columns)
    row = conn.exec_driver_sql(
        f"SELECT md5(coalesce(string_agg(t::text, '|' ORDER BY t::text), '')) "
        f"FROM (SELECT {cols} FROM {table}) t"
    ).scalar()
    return str(row)


def find_direct_reads(source: str, tables: list[str]) -> list[str]:
    """Names of versioned tables that a piece of source code reads directly (FROM or JOIN)."""
    import re

    found = []
    for table in tables:
        if re.search(rf"\b(from|join)\s+{table}\b", source, re.IGNORECASE):
            found.append(table)
    return found
