"""EPS history, fundamentals, derived quarters, earnings-release times (Data AE-03, AE-04, FD-01 to
FD-03, LB-03; Ingestion IG-09, IG-15; Database DB-11).

The Apple fixtures are real, trimmed data (README_universe.md). Companies, rows and payloads that
tests build by hand are SYNTHETIC and say so.
"""

import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import psycopg
import pytest
from sqlalchemy import text

from db_support import table_hash
from earnings import backfill
from earnings import financials as fin
from earnings.clients.edgar import RawResponse
from earnings.rawstore import store_payload

FX = Path(__file__).parent / "fixtures"
AAPL = "0000320193"
FACTS = (FX / "aapl_companyfacts_2012_2015.json").read_bytes()


def _admin(database):
    import os

    return psycopg.connect(
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"], dbname=database, autocommit=True,
    )  # fmt: skip


def _store(engine, cik=AAPL, body=FACTS):
    raw = RawResponse(
        "sec-edgar", fin.FACTS_URL.format(cik=cik), 200, "application/json", body, datetime.now(UTC)
    )
    store_payload(engine, raw)


def _loaded(test_db):
    from earnings.db import get_engine

    worker = get_engine("worker")
    with worker.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Apple Inc.')"), {"c": AAPL})
    _store(worker)
    return worker, fin.load_financials(worker, AAPL)


def _eps_on(api, as_of, fn="eps_history_as_of"):
    with api.connect() as conn:
        rows = conn.execute(
            text(
                f"SELECT eps_diluted, filed_at FROM {fn}(:c, :d) "
                "WHERE period_end = '2013-12-28' AND NOT derived"
            ),
            {"c": AAPL, "d": as_of},
        ).all()
    return [(float(v), f) for v, f in rows]


def _facts_doc(tag, rows, unit="USD/shares"):
    return json.dumps({"facts": {"us-gaap": {tag: {"units": {unit: rows}}}}}).encode()


def _row(start, end, val, filed, accn, form="10-Q", fy=2020, fp="Q1"):
    return {"start": start, "end": end, "val": val, "filed": filed, "accn": accn, "form": form,
            "fy": fy, "fp": fp}  # fmt: skip


@pytest.mark.req("AE-04-AC1", "FD-03-AC1")
@pytest.mark.code("src/earnings/financials.py", "src/earnings/migrations/versions")
def test_first_filed_value_survives_a_restatement_and_the_as_of_read_follows_the_filing_date(
    test_db,
):
    """REAL Apple data: Q1 of fiscal 2014 was first filed at 14.50 and restated to 2.07 after the
    7-for-1 split of June 2014 (filed with the 10-K of 2014-10-27)."""
    from earnings.db import get_engine

    _loaded(test_db)
    api = get_engine("api")
    assert _eps_on(api, date(2014, 6, 1)) == [(14.5, date(2014, 1, 28))]  # before the restatement
    assert _eps_on(api, date(2014, 10, 27)) == [
        (14.5, date(2014, 1, 28))
    ]  # filed on D: not visible
    assert _eps_on(api, date(2014, 10, 28)) == [(2.07, date(2014, 10, 27))]  # the restated value
    # the first-filed value is always the earliest version, whatever later filings say
    assert _eps_on(api, date(2016, 1, 1), "eps_history_first_filed") == [(14.5, date(2014, 1, 28))]


@pytest.mark.req("AE-04")
@pytest.mark.code("src/earnings/migrations/versions")
def test_a_simulated_correction_is_a_new_row_and_leaves_the_first_value(test_db):
    """SYNTHETIC correction row added by the superuser, since the worker cannot update."""
    from earnings.db import get_engine

    worker, _ = _loaded(test_db)
    api = get_engine("api")
    with _admin(test_db) as conn:
        conn.execute(
            "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
            "eps_diluted, form, accession, filed_at) VALUES (%s, '2013-09-29', '2013-12-28', "
            "'quarter', 99.99, '10-K/A', 'SYNTHETIC-CORRECTION', '2030-01-01')",
            (AAPL,),
        )
    assert _eps_on(api, date(2029, 1, 1)) == [(2.07, date(2015, 10, 28))]  # unchanged before it
    assert _eps_on(api, date(2031, 1, 1))[0][0] == 99.99  # the correction is a later version
    assert _eps_on(api, date(2031, 1, 1), "eps_history_first_filed")[0][0] == 14.5
    with pytest.raises(Exception) as err:  # and the worker cannot rewrite history
        with worker.begin() as conn:
            conn.execute(text("UPDATE eps_history SET eps_diluted = 1"))
    assert "InsufficientPrivilege" in type(err.value.orig).__name__


@pytest.mark.req("FD-02-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_a_filing_dated_d_or_later_is_not_visible_to_a_prediction_at_d(test_db):
    from earnings.db import get_engine

    worker, _ = _loaded(test_db)
    d = date(2031, 3, 1)
    with worker.begin() as conn:  # SYNTHETIC fundamentals rows
        for filed, revenue in (
            (d - timedelta(days=1), 100),
            (d, 200),
            (d + timedelta(days=1), 300),
        ):
            conn.execute(
                text(
                    "INSERT INTO fundamentals_filing (company_id, period_start, period_end, "
                    "revenue, "
                    "accession, filed_at) VALUES (:c, '2030-10-01', '2030-12-31', :r, :a, :f)"
                ),
                {"c": AAPL, "r": revenue, "a": f"SYNTHETIC-{revenue}", "f": filed},
            )
    with get_engine("api").connect() as conn:
        seen = conn.execute(
            text(
                "SELECT revenue FROM fundamentals_filing_as_of(:c, :d) "
                "WHERE period_end = '2030-12-31'"
            ),
            {"c": AAPL, "d": d},
        ).scalar_one()
    assert seen == 100  # the versions filed on D and after D are not visible


@pytest.mark.req("FD-01-AC1", "AE-03-AC1")
@pytest.mark.code("src/earnings/financials.py")
def test_every_row_has_a_filing_date_and_the_eps_basis_is_one_value(test_db):
    from earnings.db import get_engine

    _, counts = _loaded(test_db)
    assert counts["eps"] > 50 and counts["fundamentals"] > 30
    with get_engine("api").connect() as conn:
        assert (
            conn.execute(
                text("SELECT count(*) FROM eps_history WHERE filed_at IS NULL")
            ).scalar_one()
            == 0
        )
        assert (
            conn.execute(
                text(
                    "SELECT count(*) FROM fundamentals_filing "
                    "WHERE filed_at IS NULL OR accession = ''"
                )
            ).scalar_one()
            == 0
        )
        assert [r[0] for r in conn.execute(text("SELECT DISTINCT basis FROM eps_history"))] == [
            "gaap"
        ]
        tags = {
            r[0] for r in conn.execute(text("SELECT DISTINCT revenue_tag FROM fundamentals_filing"))
        }
    assert "SalesRevenueNet" in tags  # Apple's tag in these years; derived rows say "derived"


@pytest.mark.req("FD-01")
@pytest.mark.code("src/earnings/financials.py")
def test_stored_filing_dates_are_the_ones_in_the_payload_and_the_same_period_keeps_every_version(
    test_db,
):
    """Not just NOT NULL: the dates and the versions are compared with the payload itself."""
    from earnings.db import get_engine

    _loaded(test_db)
    payload = {
        (f.start, f.end, f.accession): f.filed
        for f in fin.extract_facts(FACTS, fin.EPS_TAG)
        if f.kind
    }
    with get_engine("api").connect() as conn:
        rows = conn.execute(
            text(
                "SELECT period_start, period_end, accession, filed_at "
                "FROM eps_history WHERE NOT derived"
            )
        ).all()
    assert {(s, e, a): f for s, e, a, f in rows} == payload  # every fact, with its own filing date
    versions = {}
    for s, e, _, f in rows:
        versions.setdefault((s, e), set()).add(f)
    assert any(len(v) > 1 for v in versions.values())  # a period reported in several filings


@pytest.mark.req("FD-03")
@pytest.mark.code("src/earnings/migrations/versions")
def test_the_same_filing_cannot_be_stored_twice_but_a_later_filing_adds_a_version(test_db):
    from sqlalchemy.exc import IntegrityError

    from earnings.db import get_engine

    worker, _ = _loaded(test_db)
    insert = text(
        "INSERT INTO fundamentals_filing (company_id, period_start, period_end, revenue, derived, "
        "accession, filed_at) VALUES (:c, '2030-01-01', '2030-03-31', :r, :d, :a, :f)"
    )
    row = {"c": AAPL, "r": 1, "d": False, "a": "SYNTHETIC-A", "f": date(2030, 5, 1)}
    with worker.begin() as conn:
        conn.execute(insert, row)
        conn.execute(insert, {**row, "a": "SYNTHETIC-B", "f": date(2030, 6, 1)})  # a later filing
        conn.execute(insert, {**row, "d": True})  # a derived row of the same filing is separate
    with pytest.raises(IntegrityError):
        with worker.begin() as conn:
            conn.execute(insert, row)  # the same company, period, flag and filing again
    with get_engine("api").connect() as conn:
        count = conn.execute(
            text("SELECT count(*) FROM fundamentals_filing WHERE period_start = '2030-01-01'")
        ).scalar_one()
    assert count == 3


@pytest.mark.req("DB-11-AC1")
@pytest.mark.code("src/earnings/financials.py", "src/earnings/rawstore.py")
def test_rebuilding_the_tables_from_the_stored_payload_gives_identical_hashes(test_db):
    from earnings.db import get_engine

    worker, _ = _loaded(test_db)
    api = get_engine("api")
    cols_eps = [
        "company_id",
        "period_start",
        "period_end",
        "eps_diluted",
        "derived",
        "accession",
        "filed_at",
    ]
    cols_fund = [
        "company_id",
        "period_start",
        "period_end",
        "revenue",
        "gross_profit",
        "operating_income",
        "accession",
        "filed_at",
    ]

    def state():
        with api.connect() as conn:
            return (table_hash(conn, "eps_history", cols_eps),
                    table_hash(conn, "fundamentals_filing", cols_fund))  # fmt: skip

    before = state()
    with _admin(test_db) as conn:  # drop the derived tables, as a rebuild would
        conn.execute("TRUNCATE eps_history, fundamentals_filing")
    assert state() != before
    fin.load_financials(worker, AAPL)
    assert state() == before


@pytest.mark.req("LB-03-AC1")
@pytest.mark.code("src/earnings/financials.py")
def test_a_quarter_not_reported_on_its_own_is_the_difference_of_cumulative_figures():
    """SYNTHETIC filing pattern (many companies tag only year-to-date amounts in 10-Qs)."""
    s = "2020-01-01"
    body = _facts_doc("EarningsPerShareDiluted", [
        _row(s, "2020-03-31", 1.0, "2020-04-30", "a1", fp="Q1"),
        _row(s, "2020-06-30", 2.5, "2020-07-30", "a2", fp="Q2"),
        _row(s, "2020-09-30", 4.5, "2020-10-30", "a3", fp="Q3"),
        _row(s, "2020-12-31", 7.0, "2021-02-15", "a4", form="10-K", fp="FY"),
    ])  # fmt: skip
    got = {(r.period_end, r.eps): r for r in fin.eps_rows(body) if r.derived}
    assert {(e.isoformat(), float(v)) for e, v in got} == {
        ("2020-06-30", 1.5), ("2020-09-30", 2.0), ("2020-12-31", 2.5)  # Q2, Q3 and Q4
    }  # fmt: skip
    q4 = next(r for r in got.values() if r.period_end == date(2020, 12, 31))
    assert (q4.period_start, q4.fiscal_period, q4.filed) == (
        date(2020, 10, 1),
        "Q4",
        date(2021, 2, 15),
    )


@pytest.mark.req("LB-03")
@pytest.mark.code("src/earnings/financials.py")
def test_the_fourth_quarter_uses_the_nine_month_figure_so_a_split_does_not_break_it():
    """SYNTHETIC: a 4-for-1 split between Q1 and Q3. Q1 is first filed before the split, the nine
    months and the year after it, so year minus the nine months is the true fourth quarter."""
    s = "2020-01-01"
    body = _facts_doc("EarningsPerShareDiluted", [
        _row(s, "2020-03-31", 8.0, "2020-04-30", "a1", fp="Q1"),    # pre-split value
        _row("2020-04-01", "2020-06-30", 2.0, "2020-07-30", "a2", fp="Q2"),
        _row("2020-07-01", "2020-09-30", 2.0, "2020-10-30", "a3", fp="Q3"),
        _row(s, "2020-09-30", 6.0, "2020-10-30", "a3", fp="Q3"),     # nine months, post-split
        _row(s, "2020-12-31", 8.0, "2021-02-15", "a4", form="10-K", fp="FY"),  # year, post-split
    ])  # fmt: skip
    q4 = next(r for r in fin.eps_rows(body) if r.derived and r.period_end == date(2020, 12, 31))
    assert q4.eps == Decimal("2.0")  # not 8 - (8 + 2 + 2) = -4


@pytest.mark.req("LB-03")
@pytest.mark.code("src/earnings/financials.py")
def test_a_year_is_not_derived_when_the_fourth_quarter_is_reported_or_quarters_do_not_line_up():
    """SYNTHETIC. A company that reports Q4 itself, and a year whose quarters have a hole."""
    s = "2020-01-01"
    reported = _facts_doc("EarningsPerShareDiluted", [
        _row(s, "2020-03-31", 1.0, "2020-04-30", "a1"),
        _row("2020-04-01", "2020-06-30", 1.0, "2020-07-30", "a2"),
        _row("2020-07-01", "2020-09-30", 1.0, "2020-10-30", "a3"),
        _row("2020-10-01", "2020-12-31", 1.0, "2021-02-15", "a4", form="10-K"),
        _row(s, "2020-12-31", 4.0, "2021-02-15", "a4", form="10-K", fp="FY"),
    ])  # fmt: skip
    assert [r for r in fin.eps_rows(reported) if r.derived] == []
    hole = _facts_doc("EarningsPerShareDiluted", [
        _row(s, "2020-03-31", 1.0, "2020-04-30", "a1"),
        _row("2020-07-01", "2020-09-30", 1.0, "2020-10-30", "a3"),
        _row(s, "2020-12-31", 4.0, "2021-02-15", "a4", form="10-K", fp="FY"),
    ])  # fmt: skip
    assert [r for r in fin.eps_rows(hole) if r.derived] == []


@pytest.mark.req("FD-01")
@pytest.mark.code("src/earnings/financials.py")
def test_revenue_uses_the_first_tag_a_company_reports_and_names_it():
    """SYNTHETIC: one period tagged with two revenue tags; the first in the priority list wins."""
    s, e = "2020-01-01", "2020-03-31"
    doc = {"facts": {"us-gaap": {
        "SalesRevenueNet": {"units": {"USD": [_row(s, e, 50, "2020-04-30", "a1")]}},
        "Revenues": {"units": {"USD": [_row(s, e, 60, "2020-04-30", "a1")]}},
        "GrossProfit": {"units": {"USD": [_row(s, e, 20, "2020-04-30", "a1")]}},
    }}}  # fmt: skip
    (row,) = fin.fundamentals_rows(json.dumps(doc).encode())
    assert (row.revenue, row.revenue_tag, row.gross_profit, row.operating_income) == (
        Decimal("60"), "Revenues", Decimal("20"), None  # no operating income reported: empty
    )  # fmt: skip


@pytest.mark.req("IG-15-AC1")
@pytest.mark.code("src/earnings/financials.py")
def test_a_call_before_the_filing_and_one_after_both_give_the_earlier_time_as_the_cutoff():
    releases = fin.parse_earnings_releases([(FX / "aapl_submissions_8k_sample.json").read_bytes()])
    assert len(releases) == 8 and all("2.02" in r.items.split(",") for r in releases)
    release = next(r for r in releases if r.filed == date(2026, 7, 30))
    assert release.accepted_utc == datetime(2026, 7, 30, 20, 30, 28, tzinfo=UTC)
    # call at 16:30 Eastern in July (EDT) is 20:30 UTC: before 20:30:28, so the call is the cutoff
    before = fin.call_time_utc("2026-07-30 16:30:00")
    assert before == datetime(2026, 7, 30, 20, 30, tzinfo=UTC)
    assert fin.t0_cutoff(before, release.accepted_utc) == before
    # call at 17:00 Eastern is after the filing, so the filing is the cutoff
    after = fin.call_time_utc("2026-07-30 17:00:00")
    assert fin.t0_cutoff(after, release.accepted_utc) == release.accepted_utc
    # a winter call: 17:00 EST is 22:00 UTC, which shows daylight saving is applied
    assert fin.call_time_utc("2026-01-15 17:00:00") == datetime(2026, 1, 15, 22, 0, tzinfo=UTC)


@pytest.mark.req("IG-15")
@pytest.mark.code("src/earnings/financials.py")
def test_a_placeholder_call_time_gives_the_filing_time_and_no_time_gives_none():
    accepted = datetime(2026, 7, 30, 20, 30, tzinfo=UTC)
    assert fin.call_time_utc("2016-08-02 00:00:00") is None  # the 00:00:00 placeholder
    assert fin.t0_cutoff(None, accepted) == accepted
    assert fin.t0_cutoff(accepted, None) == accepted
    assert fin.t0_cutoff(None, None) is None


@pytest.mark.req("IG-15")
@pytest.mark.code("src/earnings/financials.py")
def test_older_submission_pages_are_read_like_the_recent_block():
    """SYNTHETIC older page: the same columns without the `filings` wrapper."""
    page = {"form": ["8-K", "10-Q"], "items": ["2.02,9.01", ""], "accessionNumber": ["x1", "x2"],
            "filingDate": ["2016-02-02", "2016-02-03"],
            "acceptanceDateTime": ["2016-02-02T21:05:00.000Z", "2016-02-03T10:00:00.000Z"],
    }  # fmt: skip
    (release,) = fin.parse_earnings_releases([json.dumps(page).encode()])
    assert (release.accession, release.accepted_utc.hour) == ("x1", 21)


class _Session:
    """SYNTHETIC stand-in for HTTP that serves two payloads and counts requests."""

    def __init__(self):
        self.calls = []

    def get(self, url, *, headers, timeout):
        self.calls.append(url)
        body = (
            json.dumps({"filings": {"recent": {"form": []}, "files": [
                {"name": "CIK-submissions-001.json", "filingTo": "2016-01-01"},
                {"name": "CIK-submissions-000.json", "filingTo": "2010-01-01"}]}}).encode()
            if "/submissions/CIK0" in url and "-submissions-" not in url else FACTS
        )  # fmt: skip

        class R:
            status_code, content, headers = 200, body, {"Content-Type": "application/json"}

        return R()


@pytest.mark.req("IG-09")
@pytest.mark.code("src/earnings/backfill.py")
def test_backfill_counts_requests_skips_stored_payloads_and_reads_only_pages_that_can_matter(
    test_db,
):
    from earnings.clients.edgar import EdgarClient
    from earnings.db import get_engine

    engine = get_engine("worker")
    session = _Session()
    client = EdgarClient("Synthetic Test Client contact@example.invalid", session=session)
    first = backfill.fetch_company_payloads(engine, client, AAPL)
    # facts, submissions and the one older page that can hold filings from 2014-12-01 on
    assert first == 3 and len(session.calls) == 3
    assert not any("000.json" in c for c in session.calls)  # the page ending in 2010 is skipped
    assert backfill.fetch_company_payloads(engine, client, AAPL) == 0  # stored: nothing refetched
