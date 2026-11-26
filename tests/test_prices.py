"""Prices and dated adjustment factors, the price windows and the survivorship comparison
(Data PX-01 to PX-03, VL-05, DV-05, LB-05; Database DB-09).

The Apple payload is a REAL excerpt (tests/fixtures/README_universe.md). Other values built in a
test are SYNTHETIC and say so.
"""

import json
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import text

from earnings import events as ev
from earnings import label, prices
from earnings.clients import yahoo

FX = Path(__file__).parent / "fixtures"
APPLE = (FX / "aapl_yahoo_prices_june_2014.json").read_bytes()
AAPL = "0000320193"


@pytest.fixture
def engine(test_db):
    from earnings.db import get_engine

    worker = get_engine("worker")
    with worker.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Apple Inc.')"), {"c": AAPL})
    return worker


def _payload(rows, splits=None, dividends=None):  # SYNTHETIC source answer
    return json.dumps(
        {
            "ticker": "SYN", "version": "synthetic", "start": "2024-01-01",
            "rows": [{"date": d, "close": c, "volume": 1} for d, c in rows],
            "splits": splits or {}, "dividends": dividends or {},
        }
    ).encode()  # fmt: skip


@pytest.mark.req("PX-01")
@pytest.mark.code("src/earnings/prices.py")
def test_the_raw_close_is_rebuilt_from_the_real_apple_answer():
    parsed = prices.parse_payload(APPLE)
    closes = {d: c for d, c, _ in parsed.prices}
    # Apple closed near 645.57 on 6 June 2014, before the 7-for-1 split; the source shows 23.056
    assert abs(closes[date(2014, 6, 6)] - Decimal("645.57")) < Decimal("0.05")
    assert abs(closes[date(2014, 6, 9)] - Decimal("93.70")) < Decimal("0.05")  # after it, 4x only
    assert (date(2014, 6, 9), Decimal("7.0")) in parsed.splits
    paid = dict(parsed.dividends)
    assert paid[date(2014, 5, 8)] > Decimal("3")  # the raw dividend before the split


@pytest.mark.req("PX-01")
@pytest.mark.code("src/earnings/prices.py", "src/earnings/migrations/versions")
def test_factors_are_stored_apart_from_raw_prices_with_their_dates_and_a_rerun_adds_nothing(engine):
    first = prices.store_prices(engine, AAPL, "AAPL", APPLE)
    again = prices.store_prices(engine, AAPL, "AAPL", APPLE)
    assert first["loaded"] and first["prices"] == 9 and again["prices"] == again["factors"] == 0
    with engine.connect() as conn:
        raw = conn.execute(
            text("SELECT close_raw FROM price_daily WHERE price_date = '2014-06-06'")
        ).scalar_one()
        split = conn.execute(
            text(
                "SELECT ex_date, value FROM adjustment_factor WHERE kind = 'split' "
                "AND ex_date = '2014-06-09'"
            )  # fmt: skip
        ).one()
        columns = (
            conn.execute(
                text(
                    "SELECT column_name FROM information_schema.columns "
                    "WHERE table_name = 'price_daily'"
                )  # fmt: skip
            )
            .scalars()
            .all()
        )
        version = conn.execute(
            text("SELECT source_version FROM raw_payload WHERE source = :s"), {"s": yahoo.SOURCE}
        ).scalar_one()
    assert abs(raw - Decimal("645.57")) < Decimal("0.05") and float(split[1]) == 7.0
    assert not [c for c in columns if "adj" in c]  # no adjusted price beside the raw one
    assert version == json.loads(APPLE)["version"]  # SR-04: the source version is recorded


@pytest.mark.req("PX-02-AC1")
@pytest.mark.code("src/earnings/prices.py", "src/earnings/migrations/versions")
def test_a_planted_future_price_never_reaches_the_momentum_window(engine):
    days = [("2024-03-01", 10), ("2024-03-04", 11), ("2024-03-05", 12), ("2024-03-06", 99999)]
    prices.store_prices(engine, AAPL, "SYN", _payload(days))  # the last row is the plant
    session = date(2024, 3, 5)
    before = prices.momentum_window(engine, AAPL, session)
    after = prices.outcome_window(engine, AAPL, session)
    assert [d for d, _ in before.points] == [date(2024, 3, 1), date(2024, 3, 4)]
    assert [d for d, _ in after.points] == [session, date(2024, 3, 6)]
    assert max(c for _, c in before.points) == Decimal("11.0000")


@pytest.mark.req("PX-03-AC1")
@pytest.mark.code("src/earnings/prices.py")
def test_a_series_that_mixes_adjusted_and_raw_prices_fails():
    raw = prices.Series(prices.RAW, "s", ((date(2024, 1, 2), Decimal(10)),))
    adjusted = prices.Series(prices.SPLIT_ADJUSTED, "s", ((date(2024, 1, 3), Decimal(5)),))
    with pytest.raises(prices.MixedSeriesError):
        prices.join_series(raw, adjusted)
    with pytest.raises(prices.MixedSeriesError):
        prices.total_return(adjusted, {}, {})
    assert prices.join_series(raw, raw).kind == prices.RAW


@pytest.mark.req("PX-01", "VL-05")
@pytest.mark.code("src/earnings/prices.py")
def test_total_return_counts_a_split_and_a_dividend_and_not_a_false_fall():
    raw = prices.Series(
        prices.RAW, "s",
        ((date(2024, 1, 2), Decimal(100)), (date(2024, 1, 3), Decimal(52)),
         (date(2024, 1, 4), Decimal(51))),
    )  # fmt: skip
    level = prices.total_return(raw, {date(2024, 1, 3): Decimal(2)}, {date(2024, 1, 4): Decimal(1)})
    values = [v for _, v in level.points]
    assert values[1] == Decimal("1.04")  # 52 x 2 against 100: up 4%, not down 48%
    assert values[2] == values[1]  # 51 plus a dividend of 1 against 52: flat


@pytest.mark.req("PX-01", "FE-24")
@pytest.mark.code("src/earnings/prices.py")
def test_a_company_the_source_cannot_serve_is_listed_and_gets_no_rows(engine):
    def fetch(ticker):
        if ticker == "GONE":
            raise ValueError("no data")
        return _payload([("2024-03-01", 10)])

    with engine.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES ('0000000002', 'Gone')"))
    report = prices.load_prices(engine, [(AAPL, "SYN"), ("0000000002", "GONE")], fetch)
    assert report["loaded"] == 1 and "no data" in report["unavailable"]["0000000002"]
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT count(*) FROM price_daily WHERE company_id = '0000000002'")
        ).scalar_one()
    assert rows == 0


@pytest.mark.req("PX-01")
@pytest.mark.code("src/earnings/prices.py")
def test_a_series_that_does_not_cover_the_events_is_refused():
    days = [date(2024, 3, 1) + timedelta(days=i) for i in range(5)]
    assert prices.event_coverage(days, [date(2024, 3, 4)]) == 1.0
    assert prices.event_coverage(days, [date(2024, 3, 4), date(2020, 1, 1)]) == 0.5
    assert prices.event_coverage(days, [date(2024, 3, 12)]) == 1.0  # within a week
    assert prices.event_coverage(days, [date(2024, 3, 13)]) == 0.0
    assert 0.5 < prices.MIN_EVENT_COVERAGE


@pytest.mark.req("LB-05-AC1")
@pytest.mark.code("src/earnings/events.py", "src/earnings/label.py")
def test_labels_use_the_price_sources_dated_share_splits_and_ignore_spin_off_ratios(engine):
    for ratio in ("7", "4", "2", "1.5", "0.5", "0.333333"):
        assert label.is_share_split(Decimal(ratio)), ratio
    for ratio in ("1.046", "2.376", "1.841", "0.4873", "1", "5262.35"):
        assert not label.is_share_split(Decimal(ratio)), ratio
    body = _payload([("2024-03-01", 10)], splits={"2020-08-31": 4.0, "2021-11-15": 1.032})
    prices.store_prices(engine, AAPL, "SYN", body)
    assert ev._splits(engine, AAPL) == [label.Split(Decimal("4.0"), date(2020, 8, 31))]


@pytest.mark.req("VL-05")
@pytest.mark.code("src/earnings/prices.py")
def test_the_equal_weight_universe_uses_only_the_members_of_the_day():
    day = [date(2024, 1, 2), date(2024, 1, 3)]
    series = {
        "a": prices.Series(
            prices.TOTAL_RETURN, "s", ((day[0], Decimal(1)), (day[1], Decimal("1.10")))
        ),
        "b": prices.Series(
            prices.TOTAL_RETURN, "s", ((day[0], Decimal(1)), (day[1], Decimal("0.50")))
        ),
    }
    spells = {"a": [(date(2010, 1, 1), None)], "b": [(date(2010, 1, 1), date(2024, 1, 3))]}
    levels, sizes = prices.equal_weight_levels(series, spells)
    assert abs(float(levels[-1][1]) - 1.10) < 1e-9 and sizes == {2024: 1}  # b had left that day
    spells["b"] = [(date(2010, 1, 1), None)]
    levels, _ = prices.equal_weight_levels(series, spells)
    assert abs(float(levels[-1][1]) - 0.80) < 1e-9  # the average of +10% and -50%


@pytest.mark.req("DV-05")
@pytest.mark.code("src/earnings/prices.py")
def test_the_price_windows_of_an_event_do_not_overlap_the_announcement(engine, monkeypatch):
    from test_events import _fake_releases, _release, _transcript

    days = [(f"2024-03-0{d}", 10 + d) for d in (1, 4, 5, 6, 7)]
    prices.store_prices(engine, AAPL, "SYN", _payload(days))
    announce = date(2024, 3, 5)
    _transcript(engine, AAPL, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {AAPL: [_release(announce, "rel-1")]})  # 16:00 New York: next day
    ev.build_events(engine)
    assert prices.price_window_violations(engine) == {"events_checked": 1, "violations": 0}
    with engine.connect() as conn:
        moment = conn.execute(text("SELECT announcement_time_utc FROM earnings_event")).scalar_one()
    assert moment == datetime(2024, 3, 5, 21, tzinfo=UTC)


@pytest.mark.req("PX-01", "VL-05")
@pytest.mark.code("src/earnings/prices.py")
def test_a_spin_off_the_source_lists_twice_is_counted_once():
    # REAL numbers: Danaher, 5 July 2016 (Fortive spin-off). The source gives a ratio of 1.319
    # and also a dividend of 27.7037 raw on the same day: both stand for the same distribution
    raw = prices.Series(
        prices.RAW,
        "s",
        ((date(2016, 7, 1), Decimal("102.32")), (date(2016, 7, 5), Decimal("80.40"))),
    )
    day = date(2016, 7, 5)
    level = prices.total_return(raw, {day: Decimal("1.319")}, {day: Decimal("27.7037")})
    assert abs(float(level.points[-1][1]) - 80.40 * 1.319 / 102.32) < 1e-6  # about +3.6%
    # an ordinary dividend beside a spin-off ratio, or any dividend beside a share split, counts
    small = prices.total_return(raw, {day: Decimal("1.319")}, {day: Decimal("0.16")})
    assert abs(float(small.points[-1][1]) - (80.40 * 1.319 + 0.16) / 102.32) < 1e-6
    split = prices.total_return(raw, {day: Decimal("2")}, {day: Decimal("27.7037")})
    assert abs(float(split.points[-1][1]) - (80.40 * 2 + 27.7037) / 102.32) < 1e-6


@pytest.mark.req("PX-01")
@pytest.mark.code("src/earnings/prices.py")
def test_a_reused_ticker_is_refused_at_loading_and_stores_no_price(engine, monkeypatch):
    # the REAL shape: ANSS and WBD now return only a few rows from 2026, years after the events
    from test_events import _fake_releases, _release, _transcript

    announce = date(2020, 5, 5)  # SYNTHETIC event years before the returned prices
    _transcript(engine, AAPL, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {AAPL: [_release(announce, "rel-1")]})
    ev.build_events(engine)
    outcome = prices.store_prices(engine, AAPL, "SYN", _payload([("2026-11-23", 10)]))
    assert outcome == {"loaded": False, "reason": "series covers only 0% of the events"}
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM price_daily")).scalar_one() == 0
