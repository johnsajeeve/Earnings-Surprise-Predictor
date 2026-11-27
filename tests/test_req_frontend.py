"""Tests for the frontend requirements (frontend-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that
calls not_tested() is a placeholder for code that does not exist yet. It is skipped and
reported as NOT TESTED, never as passed. Replace the call with a real check when the
code is built (Deterministic_audit.md, Phase D).
"""

import pytest

from requirement_support import not_tested


# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.
@pytest.mark.req("UX-01-AC1")
def test_ux_01_ac1_the_dashboard_s_container_has_no_database():
    """UX-01-AC1: The dashboard's container has no database credentials."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-01-AC2")
def test_ux_01_ac2_a_search_finds_no_database_import():
    """UX-01-AC2: A search finds no database import."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-02-AC1")
def test_ux_02_ac1_one_test_per_error_state_er_01():
    """UX-02-AC1: One test per error state ER-01 to ER-14."""
    not_tested("BLOCKED", "waits for open decision D-39")


@pytest.mark.req("UX-03-AC1")
def test_ux_03_ac1_stubbed_job_that_completes_after_6_seconds():
    """UX-03-AC1: Stubbed job that completes after 6 seconds shows the three states."""
    not_tested("BLOCKED", "waits for open decision D-39")


@pytest.mark.req("UX-04-AC1")
def test_ux_04_ac1_ui_test_on_complete_and_partially_verified():
    """UX-04-AC1: UI test on complete and partially verified fixtures."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-05-AC1")
def test_ux_05_ac1_fixture_with_two_warnings_shows_both():
    """UX-05-AC1: Fixture with two warnings shows both."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-06-AC1")
def test_ux_06_ac1_fixture_with_both_shows_two_labelled_cards():
    """UX-06-AC1: Fixture with both shows two labelled cards."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-07-AC1")
def test_ux_07_ac1_fixture_where_the_full_model_loses_to():
    """UX-07-AC1: Fixture where the full model loses to the baseline shows the statement."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-08-AC1")
def test_ux_08_ac1_configuration_test():
    """UX-08-AC1: Configuration test."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-08-AC2")
def test_ux_08_ac2_page_source_lists_no_external_script():
    """UX-08-AC2: Page source lists no external script."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")


@pytest.mark.req("UX-09-AC1")
def test_ux_09_ac1_a_page_test_finds_no_transcript_text():
    """UX-09-AC1: A page test finds no transcript text beyond the cited sentences and none
    over the limit.
    """
    not_tested("BLOCKED", "waits for open decision D-18")


@pytest.mark.req("UX-10-AC1")
def test_ux_10_ac1_task_script_is_on_file_and_dated():
    """UX-10-AC1: Task script is on file and dated before the first session."""
    not_tested("NEEDS PERSON", "needs a sign-off, review or approval by a person")


@pytest.mark.req("UX-11-AC1")
def test_ux_11_ac1_service_starts_from_the_readme_command_and():
    """UX-11-AC1: Service starts from the README command and its health check passes."""
    not_tested("BLOCKED", "waits for open decision D-28")


@pytest.mark.req("UX-12-AC1")
def test_ux_12_ac1_placeholder():
    """UX-12-AC1: A fixture company with missing data and a removed company each show their
    notes on the card.
    """
    not_tested("NOT IMPLEMENTED", "the dashboard is not built (Wave 6)")


@pytest.mark.req("UX-13-AC1")
def test_ux_13_ac1_placeholder():
    """UX-13-AC1: The link is on the prediction card and the page it opens asks for no personal
    data.
    """
    not_tested("NOT IMPLEMENTED", "the dashboard is not built (Wave 6)")
