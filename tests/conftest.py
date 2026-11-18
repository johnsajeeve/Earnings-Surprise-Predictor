"""Pytest configuration shared by all tests."""


def pytest_configure(config):
    # A marker names the requirement check a test exercises, for example
    # req("FR-01-AC2") or req("SP-06"). References are validated by
    # scripts/check_requirement_refs.py against audits/acceptance_index.md.
    config.addinivalue_line(
        "markers",
        "req(*references): requirement checks this test exercises (see audits/acceptance_index.md)",
    )
