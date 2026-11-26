"""Tests for the ingestion and preparation requirements (ingestion-and-preparation-requirements.md).

Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that
calls not_tested() is a placeholder for code that does not exist yet. It is skipped and
reported as NOT TESTED, never as passed. Replace the call with a real check when the
code is built (Deterministic_audit.md, Phase D).
"""

import pytest

from requirement_support import not_tested, repo_path

# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to
# not_tested() with a real check when the code this test exercises is built.


@pytest.mark.req("IG-16-AC1")
@pytest.mark.code("docs/requirements/data-requirements.md")
def test_ig_16_ac1_the_spike_result_is_in_data_section_12():
    """IG-16-AC1: Spike result is in Data Section 12."""
    section = repo_path("docs/requirements/data-requirements.md").read_text("utf-8")
    section = section[section.index("## 12. Week-One Experiments") : section.index("## 13.")]
    paragraph = section[section.index("**Call time against 8-K acceptance time (IG-16)") :]
    paragraph = paragraph.split("\n\n")[0]
    assert (
        "50-event sample" in paragraph and "median" in paragraph and "acceptance time" in paragraph
    )


@pytest.mark.req("IG-04-AC1")
def test_ig_04_ac1_the_longest_task_in_the_100_company_run():
    """IG-04-AC1: The longest task in the 100-company run finishes inside the timeout, and the
    setting is recorded.
    """
    not_tested("NEEDS MEASUREMENT", "needs a measured run on real data or hardware")


@pytest.mark.req("IG-07-AC1")
def test_ig_07_ac1_test_with_a_mocked_clock_shows_no_more():
    """IG-07-AC1: Test with a mocked clock shows no more than 10 EDGAR requests in any second and
    no more than 25 Alpha Vantage requests in a day.
    """
    not_tested("NOT IMPLEMENTED", "the Alpha Vantage client and its counter wait for a key (C-45)")


@pytest.mark.req("IG-09-AC1")
def test_ig_09_ac1_backfill_of_the_100_company_subset_uses_the_bulk():
    """IG-09-AC1: Backfill of the 100-company subset uses the bulk files, and the request count
    is recorded.
    """
    not_tested(
        "NOT IMPLEMENTED",
        "bulk files not used: 117 requests for 100 companies is far below the limit (Wave 1.4)",
    )


@pytest.mark.req("IG-18-AC1")
def test_ig_18_ac1_on_50_hand_labelled_calls_at_least():
    """IG-18-AC1: On 50 hand-labelled calls at least 95% of boundaries are correct."""
    not_tested("NEEDS PERSON", "the 50 calls are labelled by hand")


@pytest.mark.req("IG-19-AC2")
def test_ig_19_ac2_the_label_stage_run_without_a_freeze():
    """IG-19-AC2: The label stage run without a freeze record fails."""
    not_tested("NOT IMPLEMENTED", "the code this check exercises is not built yet")
