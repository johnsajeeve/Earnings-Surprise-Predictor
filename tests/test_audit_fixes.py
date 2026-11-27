"""Defects found by the independent audit of 26 November 2026, one test per defect, built from the
real filing patterns (Data LB-03, LB-04, LB-05, TX-01; Ingestion IG-14, IG-15; Product FR-14).

Facts built here are SYNTHETIC copies of real shapes; each test names the real case.
"""

import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import text

from earnings import events as ev
from earnings import financials as fin
from earnings import label
from earnings import transcripts as tr
from test_events import CO, ENDS, _eps, _fake_releases, _release, _transcript
from test_label import _announcement, _series, _versions


def _payload(units):
    return json.dumps({"facts": {"us-gaap": {fin.EPS_TAG: {"units": units}}}}).encode()


def _raw(start, end, val, filed, accn, form="10-Q"):
    return {"start": start, "end": end, "val": val, "filed": filed, "accn": accn,
            "form": form, "fy": 2020, "fp": "Q"}  # fmt: skip


@pytest.mark.req("LB-02", "PL-04", "IG-10")
@pytest.mark.code("src/earnings/financials.py")
def test_the_per_share_unit_is_read_even_when_another_unit_comes_first():
    # real: PepsiCo, FedEx, Danaher and 8 more list "pure" or "shares" before "USD/shares"
    quarter = _raw("2020-01-01", "2020-03-31", 1.5, "2020-04-30", "a1")
    body = _payload({"pure": [_raw("2020-01-01", "2020-03-31", 99, "2020-04-30", "x")],
                     "USD/shares": [quarter]})  # fmt: skip
    assert [r.eps for r in fin.eps_rows(body)] == [Decimal("1.5")]
    with pytest.raises(ValueError, match="USD/shares"):  # never silently empty
        fin.eps_rows(_payload({"pure": [quarter]}))


@pytest.mark.req("LB-04", "LB-03", "AE-04")
@pytest.mark.code("src/earnings/financials.py")
def test_a_later_direct_quarter_does_not_erase_the_value_derivable_earlier():
    # real: CSX Q4 2020 was derivable on 2021-02-10; the direct fact came a year later
    body = _payload({"USD/shares": [
        _raw("2020-01-01", "2020-09-30", 3.0, "2020-10-30", "n9"),
        _raw("2020-01-01", "2020-12-31", 3.99, "2021-02-10", "fy", "10-K"),
        _raw("2020-10-01", "2020-12-31", 0.33, "2022-02-16", "late", "10-K"),
    ]})  # fmt: skip
    q4 = [r for r in fin.eps_rows(body)
          if r.period_end == date(2020, 12, 31) and r.period_kind == "quarter"]  # fmt: skip
    assert sorted((r.filed, r.eps, r.derived) for r in q4) == [
        (date(2021, 2, 10), Decimal("0.99"), True),
        (date(2022, 2, 16), Decimal("0.33"), False),
    ]
    # a direct quarter filed no later than the derivable one still replaces it
    same = _payload({"USD/shares": [
        _raw("2020-01-01", "2020-09-30", 3.0, "2020-10-30", "n9"),
        _raw("2020-01-01", "2020-12-31", 3.99, "2021-02-10", "fy", "10-K"),
        _raw("2020-10-01", "2020-12-31", 1.0, "2021-02-10", "fy", "10-K"),
    ]})  # fmt: skip
    assert [r.derived for r in fin.eps_rows(same) if r.period_end == date(2020, 12, 31)
            and r.period_kind == "quarter"] == [False]  # fmt: skip


@pytest.mark.req("LB-03", "LB-05")
@pytest.mark.code("src/earnings/financials.py")
def test_a_quarter_derived_across_a_split_puts_both_figures_on_one_basis():
    # real: Copart FY2023. Nine months 1.84 filed before a 2-for-1 split, year 1.28 filed after
    body = _payload({"USD/shares": [
        _raw("2022-08-01", "2023-04-30", 1.84, "2023-05-18", "n9"),
        _raw("2022-08-01", "2023-07-31", 1.28, "2023-09-28", "fy", "10-K"),
    ]})  # fmt: skip
    split = [label.Split(Decimal(2), date(2023, 8, 22))]
    q4 = next(r for r in fin.eps_rows(body, split) if r.derived)
    assert q4.eps == Decimal("0.36")  # 1.28 - 1.84 / 2, not -0.56


@pytest.mark.req("LB-04")
@pytest.mark.code("src/earnings/label.py")
def test_a_quarter_refiled_with_a_shifted_end_date_is_still_the_same_quarter():
    # real: CSX Q4 2012, first filed as 0.43 ending 28 December; refiled as 0.44 ending 30th
    first = label.EpsVersion(date(2012, 9, 29), date(2012, 12, 28), Decimal("0.43"),
                             date(2013, 1, 22))  # fmt: skip
    later = label.EpsVersion(date(2012, 10, 1), date(2012, 12, 30), Decimal("0.44"),
                             date(2014, 2, 12))  # fmt: skip
    rows = label.first_filed([later, first])
    assert list(rows.values()) == [first]
    c = _series()
    base = _versions(c)
    prev = base[-5]
    moved = label.EpsVersion(prev.period_start, prev.period_end + timedelta(days=2),
                             Decimal("9.99"), prev.filed + timedelta(days=400))  # fmt: skip
    d = _announcement(c)
    assert label.compute_sue([*base, moved], d).sue == label.compute_sue(base, d).sue


@pytest.mark.req("LB-04", "LB-01")
@pytest.mark.code("src/earnings/label.py")
def test_a_target_value_first_filed_long_after_the_announcement_gives_no_label():
    c = _series()
    d = _announcement(c)
    versions = _versions(c)
    q = versions[-1]
    for days, expected_label in ((100, True), (101, False)):
        moved = label.EpsVersion(q.period_start, q.period_end, q.value, d + timedelta(days=days))
        result = label.compute_sue([*versions[:-1], moved], d)
        assert (result.sue is not None) is expected_label
    assert "first filed more than 100 days after" in result.reason


@pytest.mark.req("LB-05")
@pytest.mark.code("src/earnings/label.py", "src/earnings/financials.py")
def test_an_unknown_share_basis_inside_the_window_gives_no_label():
    # shaped like a real case: a ratio that is a reverse split mixed with spin-offs. SYNTHETIC
    c = _series()
    d = _announcement(c)
    unknown = label.Split(Decimal("0.4731"), ENDS[-6] + timedelta(days=40), ambiguous=True)
    result = label.compute_sue(_versions(c), d, [unknown])
    assert result.sue is None and result.reason == "the share basis in the window is unknown"
    long_ago = label.Split(Decimal("0.4731"), date(2001, 1, 1), ambiguous=True)
    assert label.compute_sue(_versions(c), d, [long_ago]).sue is not None
    assert label.is_unknown_basis(Decimal("0.4731")) and not label.is_unknown_basis(
        Decimal("1.046")
    )
    assert not label.is_unknown_basis(Decimal("0.5"))  # a plain 1-for-2 is known


@pytest.mark.req("IG-14", "TX-01", "IM-03", "TX-04")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_call_filed_under_the_current_ticker_before_a_rename_is_matched():
    # real: the source files Facebook's 2013 to 2021 calls under META
    spans = {
        "META": [("1", date(2022, 6, 9), None)],
        "FB": [("1", date(2013, 1, 1), date(2022, 6, 9))],
    }
    assert tr._company_for(spans, "META", date(2019, 4, 24)) == "1"
    assert tr._company_for(spans, "FB", date(2019, 4, 24)) == "1"
    assert tr._company_for(spans, "ZZZ", date(2019, 4, 24)) is None
    # a ticker that is no company's current one is not matched outside its dates
    assert tr._company_for(spans, "FB", date(2023, 4, 24)) is None
    two = {"X": [("1", date(2020, 1, 1), None), ("2", date(2021, 1, 1), None)]}
    assert tr._company_for(two, "X", date(2010, 1, 1)) is None  # ambiguous: not guessed


@pytest.mark.req("IG-15", "FR-14", "PX-02")
@pytest.mark.code("src/earnings/events.py", "src/earnings/prices.py")
def test_a_call_before_the_filing_moves_the_cutoff_for_snapshots_and_prices(test_db, monkeypatch):
    from earnings import prices
    from earnings.db import get_engine

    engine = get_engine("worker")
    _eps(engine, CO)
    announce = ENDS[12] + timedelta(days=25)
    tid = _transcript(engine, CO, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    ev.build_events(engine)
    call_day = date(2027, 2, 26)  # SYNTHETIC: a Friday call, filing on Monday 1 March 2027
    call_at = datetime(2027, 2, 26, 14, tzinfo=UTC)
    accepted = datetime(2027, 3, 1, 21, tzinfo=UTC)
    with engine.begin() as conn:
        conn.execute(
            text("UPDATE earnings_event SET announcement_date = '2027-03-01', "
                 "announcement_time_utc = :a, transcript_date = :d"),
            {"a": accepted, "d": call_day},
        )  # fmt: skip
        conn.execute(
            text("UPDATE transcript SET call_at = :c WHERE transcript_id = :t"),
            {"c": call_at, "t": tid},
        )
        for name, moment in (("before", call_at - timedelta(days=2)),
                             ("after", call_at + timedelta(days=1))):  # fmt: skip
            conn.execute(
                text(
                    "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, "
                    "source, source_version, captured_at, raw_payload) VALUES "
                    "(:c, 1, :p, 'synthetic', 'x', :t, '{}')"
                ),
                {"c": CO, "p": name, "t": moment},
            )
    event_id, session = ev.cutoffs(engine)[0]
    assert session == call_day  # the call was before Friday's close
    assert [s["period_label"] for s in ev.event_snapshots(engine, event_id)] == ["before"]
    assert prices.session_of_cutoff(engine, event_id) == call_day
    # a call with no usable time still counts by its day
    with engine.begin() as conn:
        conn.execute(text("UPDATE transcript SET call_at = NULL"))
    assert ev.cutoff_day(engine, event_id) == call_day
    assert ev.cutoffs(engine)[0][1] == call_day


@pytest.mark.req("LB-01", "DV-06")
@pytest.mark.code("src/earnings/label.py")
def test_a_sixteen_week_fourth_quarter_is_a_quarter():
    # real: PepsiCo reports quarters of 12, 12, 12 and 16 weeks; its Q4 spans 111 days
    c = _series()
    d = _announcement(c)
    base = _versions(c)
    target = base[-1]
    long = label.EpsVersion(target.period_end - timedelta(days=111), target.period_end,
                            target.value, target.filed, derived=True)  # fmt: skip
    assert label.compute_sue([*base[:-1], long], d).sue == label.compute_sue(base, d).sue
    year = label.EpsVersion(target.period_end - timedelta(days=364), target.period_end,
                            Decimal("99"), target.filed - timedelta(days=1))  # fmt: skip
    assert label.compute_sue([*base, year], d).sue == label.compute_sue(base, d).sue


def _admin(test_db, statement):
    import os

    import psycopg

    with psycopg.connect(host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"],
                         password=os.environ["POSTGRES_PASSWORD"], dbname=test_db,
                         autocommit=True) as conn:  # fmt: skip
        conn.execute(statement)


@pytest.fixture
def built(test_db, monkeypatch):
    """One SYNTHETIC labelled event with prices around its announcement."""
    from earnings import prices
    from earnings.db import get_engine
    from test_prices import _payload as price_payload

    engine = get_engine("worker")
    _eps(engine, CO)
    announce = ENDS[12] + timedelta(days=25)
    _transcript(engine, CO, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    ev.build_events(engine)
    days = [(str(announce + timedelta(days=i)), 10 + i) for i in range(-6, 7)]
    prices.store_prices(engine, CO, "SYN", price_payload(days))
    return engine, announce


@pytest.mark.req("DV-05", "PX-02")
@pytest.mark.code("src/earnings/prices.py")
def test_the_price_window_check_fails_when_a_read_lets_the_announcement_day_through(built, test_db):
    from earnings import prices

    engine, _ = built
    assert prices.price_window_violations(engine) == {"events_checked": 1, "violations": 0}
    _admin(
        test_db,
        """CREATE OR REPLACE FUNCTION price_daily_before(p_company text, p_day date)
        RETURNS SETOF price_daily LANGUAGE sql STABLE AS $$
        SELECT * FROM price_daily WHERE company_id = p_company AND price_date <= p_day $$""",
    )
    try:  # the planted fault: the boundary day leaks into the momentum window
        assert prices.price_window_violations(engine)["violations"] == 1
    finally:
        _admin(
            test_db,
            """CREATE OR REPLACE FUNCTION price_daily_before(p_company text, p_day date)
            RETURNS SETOF price_daily LANGUAGE sql STABLE AS $$
            SELECT DISTINCT ON (source, price_date) * FROM price_daily
            WHERE company_id = p_company AND price_date < p_day
            ORDER BY source, price_date, captured_at DESC, price_id DESC $$""",
        )


@pytest.mark.req("CE-01", "VL-01", "DV-02", "DV-03", "AE-03", "IG-20")
@pytest.mark.code("src/earnings/validation.py", "src/earnings/label.py")
def test_each_gate_counts_a_planted_fault(built, test_db, monkeypatch):
    from earnings import validation as val

    engine, announce = built
    # CE-01: if the snapshot read ever returned a late capture, the check counts it
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, "
                 "source, source_version, captured_at, raw_payload) VALUES (:c, 1, '0q', "
                 "'synthetic', 'x', '2027-01-01', '{}')"), {"c": CO},
        )  # fmt: skip
    assert val.capture_after_announcement(engine) == 0
    late = [{"captured_at": datetime(2030, 1, 1, tzinfo=UTC)}]
    monkeypatch.setattr(val, "event_snapshots", lambda e, i: late)
    assert val.capture_after_announcement(engine) == 1
    # DV-02: a usable event with a missing date is counted
    with engine.begin() as conn:
        conn.execute(text("UPDATE earnings_event SET information_date = NULL, incomplete = true"))
    assert val.null_rates(engine)["nulls_in_usable_events"]["information_date"] == 1
    # DV-03 and AE-03: with the database rule removed, a duplicate and a second basis are seen
    _admin(test_db, "DROP INDEX earnings_event_one_per_quarter")
    try:
        tid = _transcript(engine, CO, 2, announce, "rel-2")
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO earnings_event (company_id, transcript_id, period_end, "
                     "announcement_date, release_accession, eps_basis, label_route, incomplete, "
                     "status, sue_reason) SELECT company_id, :t, period_end, announcement_date, "
                     "'x', 'adjusted', 'time-series', true, 'included', 'n' FROM earnings_event "
                     "LIMIT 1"), {"t": tid},
            )  # fmt: skip
        assert len(val.duplicate_events(engine)) == 1
        assert sorted(val.basis_values(engine)) == ["adjusted", "gaap-diluted"]
    finally:
        _admin(test_db, "TRUNCATE earnings_event CASCADE")
        _admin(
            test_db,
            "CREATE UNIQUE INDEX earnings_event_one_per_quarter ON earnings_event "
            "(company_id, period_end, announcement_date) WHERE period_end IS NOT NULL",
        )
    # IG-20: the label really calls its date gate with the dates of its inputs
    seen = []
    monkeypatch.setattr(label, "assert_inputs_before", lambda dates, day: seen.append(len(dates)))
    label.compute_sue(_versions(_series()), _announcement(_series()))
    assert seen and seen[0] >= 8


@pytest.mark.req("PX-01", "LB-05", "VL-05")
@pytest.mark.code("src/earnings/prices.py", "src/earnings/financials.py")
def test_price_coverage_has_its_stated_threshold_and_the_latest_factor_version_wins(built, test_db):
    from earnings import prices

    engine, _ = built
    assert prices.MIN_EVENT_COVERAGE == 0.9
    days = [date(2024, 1, 2) + timedelta(days=30 * i) for i in range(10)]
    assert prices.event_coverage(days[:8], days) == 0.8  # below the threshold: refused
    with engine.begin() as conn:
        for value, when in (("2", "2026-01-01"), ("4", "2026-06-01")):  # a corrected factor
            conn.execute(
                text("INSERT INTO adjustment_factor (company_id, ex_date, kind, value, source, "
                     "source_version, captured_at) VALUES (:c, '2020-01-01', 'split', :v, "
                     "'yfinance-prices', 'x', :t)"), {"c": CO, "v": value, "t": when},
            )  # fmt: skip
    assert fin.company_splits(engine, CO) == [label.Split(Decimal(4), date(2020, 1, 1))]


@pytest.mark.req("TX-01", "AE-01")
@pytest.mark.code("src/earnings/events.py", "src/earnings/migrations/versions")
def test_a_transcript_has_a_call_type_and_an_event_keeps_its_eps_filing(built):
    engine, announce = built
    with engine.connect() as conn:
        call_type = conn.execute(text("SELECT call_type FROM transcript")).scalar_one()
        accession, filed = conn.execute(
            text("SELECT eps_accession, eps_filed_at FROM earnings_event")
        ).one()
    assert call_type == "earnings call"
    assert accession == f"a-{ENDS[12]}" and filed == ENDS[12] + timedelta(days=30)


@pytest.mark.req("LB-01", "DV-06")
@pytest.mark.code("src/earnings/label.py")
def test_a_seventeen_week_quarter_in_a_53_week_year_does_not_break_the_run_of_quarters():
    # real: PepsiCo, quarters ending 3 September and 31 December 2016 are 119 days apart
    ends = [date(2016, 12, 31)]
    for gap in (119, 84, 84, 112, 84, 84, 84, 112, 84, 84, 84, 112):
        ends.append(ends[-1] - timedelta(days=gap))
    chain = label._chain({e: None for e in ends}, ends[0])
    assert chain == ends  # all thirteen quarters, none lost at the long one
    broken = [ends[0], ends[0] - timedelta(days=182)]  # a missing quarter still breaks it
    assert label._chain({e: None for e in broken}, ends[0]) == [ends[0]]


@pytest.mark.req("IG-05", "IG-10", "DV-08")
@pytest.mark.code("src/earnings/transcripts.py")
def test_a_release_that_rolls_off_the_newest_filing_list_is_still_known(test_db):
    # found by the second audit: the daily check stores a newer list, and the older filings drop
    # off it. Every stored version must count. SYNTHETIC lists
    from earnings.clients.edgar import RawResponse
    from earnings.db import get_engine
    from earnings.rawstore import store_payload

    engine = get_engine("worker")

    def listing(accessions):
        n = len(accessions)
        return json.dumps({"filings": {"recent": {
            "form": ["8-K"] * n, "items": ["2.02"] * n, "accessionNumber": accessions,
            "filingDate": ["2024-05-02"] * n,
            "acceptanceDateTime": ["2024-05-02T20:30:00.000Z"] * n}}}).encode()  # fmt: skip

    url = fin.SUBMISSIONS_URL.format(cik=CO)
    for day, accessions in ((1, ["old", "kept"]), (2, ["kept", "new"])):
        stored_at = datetime(2026, 1, day, tzinfo=UTC)
        body = listing(accessions)
        store_payload(
            engine, RawResponse("sec-edgar", url, 200, "application/json", body, stored_at)
        )
    found = [r.accession for r in tr._releases_for(engine, CO)]
    assert sorted(found) == ["kept", "new", "old"]  # nothing lost, and "kept" only once


@pytest.mark.req("LB-01", "LB-04", "IG-10")
@pytest.mark.code("src/earnings/financials.py")
def test_a_quarter_reported_as_basic_and_diluted_is_read():
    # shaped like a real case (second audit): a quarter filed first under the combined tag and only
    # months later under the diluted tag. SYNTHETIC values
    def node(rows):
        return {"units": {"USD/shares": rows}}

    both = {
        "facts": {"us-gaap": {
            fin.EPS_TAG: node([
                _raw("2017-01-01", "2017-03-31", 0.80, "2017-04-30", "d1"),
                _raw("2016-10-01", "2016-12-31", 0.66, "2017-12-15", "later"),
                _raw("2017-01-01", "2017-03-31", 0.80, "2017-04-30", "b1"),
            ]),
            fin.BASIC_AND_DILUTED_TAG: node([
                _raw("2016-10-01", "2016-12-31", 0.65, "2017-02-23", "first"),
                _raw("2017-01-01", "2017-03-31", 0.99, "2017-04-30", "d1"),  # same filing
            ]),
        }}
    }  # fmt: skip
    rows = fin.eps_rows(json.dumps(both).encode())
    q4 = sorted((r.filed, r.eps) for r in rows if r.period_end == date(2016, 12, 31))
    assert q4[0] == (date(2017, 2, 23), Decimal("0.65"))  # the first filing is known
    q1 = [r.eps for r in rows if r.period_end == date(2017, 3, 31) and r.accession == "d1"]
    assert q1 == [Decimal("0.8")]  # one filing with both tags: the diluted tag wins
    only_combined = {"facts": {"us-gaap": {fin.BASIC_AND_DILUTED_TAG: node(
        [_raw("2016-10-01", "2016-12-31", 0.65, "2017-02-23", "first")])}}}  # fmt: skip
    assert [r.eps for r in fin.eps_rows(json.dumps(only_combined).encode())] == [Decimal("0.65")]


@pytest.mark.req("LB-03", "LB-04")
@pytest.mark.code("src/earnings/financials.py")
def test_a_later_cumulative_result_does_not_hide_what_the_three_quarters_gave_earlier():
    # shaped like IBM 2011: the year first starts a day earlier than the nine months, so the
    # year-minus-nine-months result only appears with a filing years later. SYNTHETIC values
    quarters = [
        _raw("2011-01-01", "2011-03-31", 1.0, "2011-04-30", "q1"),
        _raw("2011-04-01", "2011-06-30", 1.0, "2011-07-30", "q2"),
        _raw("2011-07-01", "2011-09-30", 1.0, "2011-10-30", "q3"),
        _raw("2011-01-01", "2011-09-30", 3.0, "2011-10-30", "q3"),
        _raw("2010-12-31", "2011-12-31", 5.0, "2012-02-28", "fy", "10-K"),
        _raw("2011-01-01", "2011-12-31", 5.0, "2014-02-25", "refiled", "10-K"),
    ]
    rows = fin.eps_rows(_payload({"USD/shares": quarters}))
    q4 = min((r for r in rows if r.period_end == date(2011, 12, 31)
              and r.period_kind == "quarter"), key=lambda r: r.filed)  # fmt: skip
    assert (q4.filed, q4.eps, q4.derived) == (date(2012, 2, 28), Decimal("2.0"), True)


# ---- the eight planted faults the second audit found no test for ---------------------------------


@pytest.mark.req("LB-03", "LB-05")
@pytest.mark.code("src/earnings/financials.py")
def test_the_three_quarter_sum_also_puts_the_quarters_on_the_years_share_basis():
    quarters = [  # SYNTHETIC: a 2-for-1 split after Q2, year filed after it, no nine-month figure
        _raw("2022-01-01", "2022-03-31", 2.0, "2022-04-30", "q1"),
        _raw("2022-04-01", "2022-06-30", 2.0, "2022-07-30", "q2"),
        _raw("2022-07-01", "2022-09-30", 1.0, "2022-10-30", "q3"),
        _raw("2022-01-01", "2022-12-31", 4.0, "2023-02-15", "fy", "10-K"),
    ]
    split = [label.Split(Decimal(2), date(2022, 8, 22))]
    q4 = next(r for r in fin.eps_rows(_payload({"USD/shares": quarters}), split) if r.derived)
    assert q4.eps == Decimal("1.0")  # 4.0 - (1.0 + 1.0 + 1.0), not 4.0 - 5.0


@pytest.mark.req("LB-05")
@pytest.mark.code("src/earnings/financials.py")
def test_the_loaded_splits_keep_unknown_ratios_and_the_load_uses_the_price_sources_splits(test_db):
    from earnings.clients.edgar import RawResponse
    from earnings.db import get_engine
    from earnings.rawstore import store_payload

    engine = get_engine("worker")
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Synthetic')"), {"c": CO})
        conn.execute(  # the company has prices, so the price source's factors are used
            text("INSERT INTO price_daily (company_id, ticker, price_date, close_raw, source, "
                 "source_version) VALUES (:c, 'S', '2024-01-02', 1, 'synthetic', 'x')"), {"c": CO}
        )  # fmt: skip
        for day, value in (("2023-08-22", "2"), ("2021-01-04", "0.4731")):
            conn.execute(
                text("INSERT INTO adjustment_factor (company_id, ex_date, kind, value, source, "
                     "source_version) VALUES (:c, :d, 'split', :v, 'yfinance-prices', 'x')"),
                {"c": CO, "d": day, "v": value},
            )  # fmt: skip
    found = fin.company_splits(engine, CO)
    assert [(str(s.effective), s.ambiguous) for s in found] == [
        ("2021-01-04", True), ("2023-08-22", False)]  # fmt: skip
    body = _payload({"USD/shares": [
        _raw("2022-08-01", "2023-04-30", 1.84, "2023-05-18", "n9"),
        _raw("2022-08-01", "2023-07-31", 1.28, "2023-09-28", "fy", "10-K")]})  # fmt: skip
    store_payload(engine, RawResponse("sec-edgar", fin.FACTS_URL.format(cik=CO), 200,
                                      "application/json", body, datetime.now(UTC)))  # fmt: skip
    fin.load_financials(engine, CO)  # the payload itself has no split tag
    with engine.connect() as conn:
        q4 = conn.execute(text("SELECT eps_diluted FROM eps_history WHERE derived")).scalar_one()
    assert q4 == Decimal("0.36")


@pytest.mark.req("LB-01", "LB-04")
@pytest.mark.code("src/earnings/label.py")
def test_the_ten_day_and_twenty_day_limits_are_where_they_were_approved():
    c = _series()
    base = _versions(c)
    target = base[-1]
    d = target.period_end + timedelta(days=60)
    for before, labelled in ((10, True), (11, False)):  # filed this many days before D
        early = label.EpsVersion(target.period_start, target.period_end, target.value,
                                 d - timedelta(days=before))  # fmt: skip
        assert (label.compute_sue([*base[:-1], early], d).sue is not None) is labelled
    first = base[-3]
    for shift, same in ((20, True), (21, False)):  # quarter ends this far apart
        other = label.EpsVersion(first.period_start, first.period_end + timedelta(days=shift),
                                 Decimal("9"), first.filed + timedelta(days=5))  # fmt: skip
        assert (len(label.first_filed([first, other])) == 1) is same


@pytest.mark.req("LB-04", "FD-03")
@pytest.mark.code("src/earnings/label.py", "src/earnings/financials.py")
def test_a_reported_value_beats_a_derived_one_filed_the_same_day_and_fundamentals_follow_dates():
    end, filed = date(2024, 3, 31), date(2024, 5, 1)
    derived = label.EpsVersion(date(2024, 1, 1), end, Decimal("2"), filed, derived=True)
    direct = label.EpsVersion(date(2024, 1, 1), end, Decimal("1"), filed)
    assert label.first_filed([derived, direct])[end] == direct

    def revenue(start, finish, value, when, accn):  # SYNTHETIC revenue facts
        return {"start": start, "end": finish, "val": value, "filed": when, "accn": accn,
                "form": "10-Q", "fy": 2020, "fp": "Q"}  # fmt: skip

    payload = json.dumps({"facts": {"us-gaap": {"Revenues": {"units": {"USD": [
        revenue("2020-01-01", "2020-09-30", 300, "2020-10-30", "n9"),
        revenue("2020-01-01", "2020-12-31", 399, "2021-02-10", "fy"),
        revenue("2020-10-01", "2020-12-31", 33, "2022-02-16", "late")]}}}}}).encode()  # fmt: skip
    q4 = sorted((r.filed, r.revenue, r.derived) for r in fin.fundamentals_rows(payload)
                if r.period_end == date(2020, 12, 31))  # fmt: skip
    assert q4 == [
        (date(2021, 2, 10), Decimal("99"), True),
        (date(2022, 2, 16), Decimal("33"), False),
    ]


@pytest.mark.req("IG-06", "SR-10", "DV-01")
@pytest.mark.code("src/earnings/validation.py")
def test_the_checks_put_events_in_a_capture_gap_into_quarantine(built, monkeypatch):
    from earnings import validation as val

    engine, _ = built
    with engine.connect() as conn:
        event_id = conn.execute(text("SELECT event_id FROM earnings_event")).scalar_one()
    monkeypatch.setattr(val, "capture_gap_events", lambda engine: [event_id])
    report = val.run_checks(engine)
    assert report["quarantine_by_reason"][val.GAP_REASON] == 1
