"""Press-release EPS parsing and the comparison with stored EPS (Data AE-02, LB-03, VL-08).

The Apple files are REAL excerpts (tests/fixtures/README_universe.md). Rows built in a test are
SYNTHETIC and say so.
"""

from datetime import UTC, date, datetime
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text

from earnings import pressrelease as pr
from earnings.clients.edgar import RawResponse, SourceError

FX = Path(__file__).parent / "fixtures"
TABLE = (FX / "aapl_press_release_table.html").read_bytes()
INDEX = (FX / "aapl_8k_index.json").read_bytes()
AAPL = "0000320193"
ACC = "0000320193-25-000007"


@pytest.mark.req("AE-02-AC1")
@pytest.mark.code("src/earnings/pressrelease.py")
def test_the_real_apple_release_gives_the_gaap_diluted_eps_of_the_quarter():
    found = pr.parse_diluted_eps(pr.html_rows(TABLE))
    assert found is not None and found.value == Decimal("2.40")  # Q1 of fiscal 2025
    assert "Diluted" in found.row
    assert pr.exhibit_names(INDEX) == ["a8-kex991q1202512282024.htm"]


@pytest.mark.req("AE-02-AC1")
@pytest.mark.code("src/earnings/pressrelease.py")
def test_adjusted_rows_negatives_and_cut_tables_are_handled():
    adjusted_first = [  # SYNTHETIC rows
        ["Adjusted diluted earnings per share", "$", "3.10"],
        ["Diluted earnings per share", "$", "(0.25)", "$", "0.40"],
    ]
    found = pr.parse_diluted_eps(adjusted_first)
    assert found is not None and found.value == Decimal("-0.25")  # GAAP row, loss
    cut = [["Net income per diluted share"], ["$", "1.07", "$", "0.96"]]
    assert pr.parse_diluted_eps(cut).value == Decimal("1.07")
    share_counts = [  # SYNTHETIC rows shaped like the share-count block of a real release
        ["Weighted average shares outstanding:"],
        ["Basic", "175.2"],
        ["Diluted", "177.7"],
    ]
    assert pr.parse_diluted_eps(share_counts) is None
    named = [["Earnings per share:"], ["Diluted weighted average shares outstanding", "167.6"]]
    assert pr.parse_diluted_eps(named) is None  # a share count that says "diluted"
    wordy = [["Weighted-average shares used in computing diluted earnings per share", "122.6"]]
    assert pr.parse_diluted_eps(wordy) is None  # names per share, but counts shares
    per_share = [["Earnings per share:"], ["Diluted", "$", "1.38"]]
    assert pr.parse_diluted_eps(per_share).value == Decimal("1.38")
    assert pr.parse_diluted_eps([["Basic earnings per share", "1.00"]]) is None
    assert pr.parse_diluted_eps([["Non-GAAP diluted earnings per share", "1.00"]]) is None


@pytest.mark.req("AE-02-AC1")
@pytest.mark.code("src/earnings/pressrelease.py")
def test_agreement_is_within_half_a_percent_of_the_stored_value():
    d = Decimal
    assert pr.agrees(d("2.40"), d("2.40"))
    assert pr.agrees(d("2.401"), d("2.40"))  # 0.04%
    assert pr.agrees(d("2.41"), d("2.40"))
    assert not pr.agrees(d("2.42"), d("2.40"))  # 0.83%: outside
    assert not pr.agrees(d("0.20"), d("0.10"))
    assert pr.agrees(d("-1.00"), d("-1.00")) and not pr.agrees(d("1.00"), d("-1.00"))


class _Client:
    """SYNTHETIC stand-in for the EDGAR client that serves the real Apple fixture bytes."""

    def __init__(self, pages):
        self.pages, self.calls = pages, []

    def get(self, url):
        self.calls.append(url)
        if url not in self.pages:
            raise SourceError("EDGAR returned status 404")
        return RawResponse("sec-edgar", url, 200, "text/html", self.pages[url], datetime.now(UTC))


@pytest.mark.req("AE-02-AC1", "IG-10-AC1")
@pytest.mark.code("src/earnings/pressrelease.py")
def test_a_filing_is_fetched_once_stored_and_then_read_from_the_stored_copy(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    acc = pr.accession_path(ACC)
    pages = {
        pr.INDEX_URL.format(cik=int(AAPL), acc=acc): INDEX,
        pr.FILE_URL.format(cik=int(AAPL), acc=acc, name="a8-kex991q1202512282024.htm"): TABLE,
    }
    client = _Client(pages)
    found, why = pr.press_release_eps(engine, client, AAPL, ACC)
    assert why is None and found.value == Decimal("2.40") and len(client.calls) == 2
    again, _ = pr.press_release_eps(engine, client, AAPL, ACC)  # from the stored copy
    assert again.value == Decimal("2.40") and len(client.calls) == 2
    missing, why = pr.press_release_eps(engine, _Client({}), AAPL, "0000320193-24-000001")
    assert missing is None and why == "filing index not found"


@pytest.mark.req("AE-02-AC1", "TH-12-AC1")
@pytest.mark.code("src/earnings/pressrelease.py")
def test_events_are_compared_and_the_summary_counts_every_outcome(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Apple Inc.')"), {"c": AAPL})
        for end, value, derived in (("2024-12-28", "2.40", False), ("2024-09-28", "0.97", True)):
            conn.execute(
                text(
                    "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
                    "eps_diluted, derived, accession, filed_at) VALUES "
                    "(:c, :s, :e, 'quarter', :v, :d, 'a', '2025-01-31')"
                ),
                {"c": AAPL, "s": date.fromisoformat(end).replace(day=1), "e": end, "v": value,
                 "d": derived},
            )  # fmt: skip
    acc = pr.accession_path(ACC)
    pages = {
        pr.INDEX_URL.format(cik=int(AAPL), acc=acc): INDEX,
        pr.FILE_URL.format(cik=int(AAPL), acc=acc, name="a8-kex991q1202512282024.htm"): TABLE,
    }
    events = [  # SYNTHETIC event rows pointing at the real filing
        {"company_id": AAPL, "period_end": date(2024, 12, 28), "accession": ACC},
        {"company_id": AAPL, "period_end": date(2024, 9, 28), "accession": ACC},  # stored 0.97
        {"company_id": AAPL, "period_end": date(2023, 12, 30), "accession": ACC},  # nothing stored
        {"company_id": AAPL, "period_end": date(2024, 12, 28), "accession": "0000320193-99-000001"},
    ]
    records = pr.compare_events(engine, _Client(pages), events)
    assert [r["result"] for r in records] == ["agree", "differ", "no stored EPS", "not parsed"]
    assert records[1]["derived"] == "True" and "relative difference" in records[1]["note"]
    result = pr.summary(records)
    assert result["sampled"] == 4 and result["agree_of_parsed"] == 0.5
    assert result["agree_of_sampled"] == 0.25
