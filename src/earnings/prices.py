"""Daily prices and dated adjustment factors (Data PX-01 to PX-03, VL-05, DV-05; decisions C-49,
C-50). Parsing reads stored payloads. A series always carries its kind, and series of different
kinds cannot be joined (PX-03)."""

import json
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

from earnings import calendar as cal
from earnings.clients import yahoo
from earnings.label import is_share_split
from earnings.rawstore import latest_payload, store_payload
from earnings.runlog import run_record

RAW, SPLIT_ADJUSTED, TOTAL_RETURN = "raw", "split_adjusted", "total_return"
CENT = Decimal("0.0001")
# A series is refused when it misses more than this share of the company's announcement dates:
# a ticker can be reused by another company after a delisting.
MIN_EVENT_COVERAGE = 0.9
# A dividend above this share of the previous close, on the day of a spin-off ratio, is the spin-off
# itself listed a second time by the source (found with Danaher, 5 July 2016; drift DR-34)
SPIN_OFF_DIVIDEND = Decimal("0.05")
# A dividend above this share of the previous close, on the day of a spin-off ratio, is the spin-off
# itself listed a second time by the source (found with Danaher, 5 July 2016; drift DR-34)
SPIN_OFF_DIVIDEND = Decimal("0.05")
INDEXES = ("^SP500TR", "RSP")
YEARS = range(2013, 2025)


class MixedSeriesError(Exception):
    """Adjusted and unadjusted prices in one series (PX-03)."""


@dataclass(frozen=True)
class Series:
    kind: str
    source: str
    points: tuple[tuple[date, Decimal], ...]


def join_series(first: Series, second: Series) -> Series:
    if first.kind != second.kind:
        raise MixedSeriesError(f"a series cannot hold both {first.kind} and {second.kind} prices")
    return Series(first.kind, first.source, tuple(sorted({*first.points, *second.points})))


@dataclass(frozen=True)
class Parsed:
    version: str
    prices: list[tuple[date, Decimal, int]]  # raw close
    splits: list[tuple[date, Decimal]]
    dividends: list[tuple[date, Decimal]]  # raw cash amount per share


def parse_payload(body: bytes) -> Parsed:
    """Raw values rebuilt from the stored answer. The source's close and dividends are adjusted for
    every later ratio in its split list, so each is multiplied back by the later ratios."""
    d = json.loads(body)
    splits = sorted((date.fromisoformat(k), Decimal(str(v))) for k, v in d["splits"].items() if v)

    def later(day: date) -> Decimal:
        factor = Decimal(1)
        for ex_date, ratio in splits:
            if ex_date > day:
                factor *= ratio
        return factor

    prices = []
    for row in d["rows"]:
        day = date.fromisoformat(row["date"])
        value = (Decimal(str(row["close"])) * later(day)).quantize(CENT)
        prices.append((day, value, int(row["volume"])))
    dividends = []
    for k, v in sorted(d["dividends"].items()):
        day = date.fromisoformat(k)
        if v:
            dividends.append((day, (Decimal(str(v)) * later(day)).quantize(CENT)))
    return Parsed(d["version"], prices, splits, dividends)


def event_coverage(days: list[date], event_days: list[date]) -> float:
    """Share of announcement dates with a price within a week of them."""
    if not event_days:
        return 1.0
    have = set(days)
    near = sum(any(e + timedelta(days=i) in have for i in range(-7, 8)) for e in event_days)
    return near / len(event_days)


def store_prices(engine: Engine, company_id: str, ticker: str, body: bytes) -> dict[str, Any]:
    """Store the answer as received, then the raw prices and factors parsed from the stored copy.
    Running it again adds nothing (EQ-07)."""
    store_payload(engine, yahoo.response(ticker, body))
    stored = latest_payload(engine, yahoo.SOURCE, yahoo.url_for(ticker))
    assert stored is not None
    parsed = parse_payload(stored)
    with engine.connect() as conn:
        event_days = list(
            conn.execute(
                text("SELECT announcement_date FROM earnings_event WHERE company_id = :c"),
                {"c": company_id},
            ).scalars()
        )
        payload_id = conn.execute(
            text(
                "SELECT payload_id FROM raw_payload WHERE source = :s AND url = :u "
                "ORDER BY retrieved_at DESC LIMIT 1"
            ),
            {"s": yahoo.SOURCE, "u": yahoo.url_for(ticker)},
        ).scalar_one()
    share = event_coverage([p[0] for p in parsed.prices], event_days)
    if share < MIN_EVENT_COVERAGE:
        return {"loaded": False, "reason": f"series covers only {share:.0%} of the events"}
    common = {"c": company_id, "src": yahoo.SOURCE, "ver": parsed.version, "p": payload_id}
    counts = {"prices": 0, "factors": 0}
    with engine.begin() as conn:
        for day, close, volume in parsed.prices:
            counts["prices"] += conn.execute(
                text(
                    "INSERT INTO price_daily (company_id, ticker, price_date, close_raw, volume, "
                    "source, source_version, payload_id) VALUES (:c, :t, :d, :v, :vol, :src, "
                    ":ver, :p) ON CONFLICT ON CONSTRAINT price_daily_one_version DO NOTHING"
                ),
                {**common, "t": ticker, "d": day, "v": close, "vol": volume},
            ).rowcount
        factors = [("split", s) for s in parsed.splits] + [
            ("dividend", d) for d in parsed.dividends
        ]
        for kind, (ex_date, value) in factors:
            counts["factors"] += conn.execute(
                text(
                    "INSERT INTO adjustment_factor (company_id, ex_date, kind, value, source, "
                    "source_version, payload_id) VALUES (:c, :d, :k, :v, :src, :ver, :p) "
                    "ON CONFLICT ON CONSTRAINT adjustment_factor_one_version DO NOTHING"
                ),
                {**common, "d": ex_date, "k": kind, "v": value},
            ).rowcount
    return {"loaded": True, **counts}


def load_prices(
    engine: Engine,
    companies: list[tuple[str, str]],
    fetch: Callable[[str], bytes] = yahoo.fetch_payload,
    pause: float = 0.0,
) -> dict[str, Any]:
    """(company_id, ticker) pairs. A company the source cannot serve is listed with the reason and
    gets no price rows: its price features are unavailable, never zero (FE-24, C-50)."""
    report: dict[str, Any] = {"loaded": 0, "unavailable": {}, "price_rows": 0, "factor_rows": 0}
    with run_record(engine, "load-prices", yahoo.SOURCE) as run:
        for company_id, ticker in companies:
            try:
                body = fetch(ticker.replace(".", "-"))
                outcome = store_prices(engine, company_id, ticker.replace(".", "-"), body)
            except Exception as exc:  # noqa: BLE001  one missing company must not stop the others
                outcome = {"loaded": False, "reason": f"{type(exc).__name__}: {exc}"[:200]}
            if outcome["loaded"]:
                report["loaded"] += 1
                report["price_rows"] += outcome["prices"]
                report["factor_rows"] += outcome["factors"]
            else:
                report["unavailable"][company_id] = outcome["reason"]
            if pause:
                time.sleep(pause)
        run.rows_read, run.rows_written = len(companies), report["price_rows"]
        if not report["loaded"] and companies:
            run.fail("no company could be loaded")
    return report


# ---- reads (PX-02, PX-03) -----------------------------------------------------------------------


def _read(engine: Engine, function: str, company_id: str, day: date) -> Series:
    with engine.connect() as conn:
        rows = conn.execute(
            text(f"SELECT price_date, close_raw FROM {function}(:c, :d) ORDER BY price_date"),
            {"c": company_id, "d": day},
        ).all()
    return Series(RAW, yahoo.SOURCE, tuple((r[0], r[1]) for r in rows))


def momentum_window(engine: Engine, company_id: str, session: date) -> Series:
    """Raw closes dated before the announcement session (PX-02)."""
    return _read(engine, "price_daily_before", company_id, session)


def outcome_window(engine: Engine, company_id: str, session: date) -> Series:
    """Raw closes from the announcement session onwards (PX-02)."""
    return _read(engine, "price_daily_from", company_id, session)


def total_return(
    raw: Series, splits: dict[date, Decimal], dividends: dict[date, Decimal]
) -> Series:
    """A total-return level starting at 1, computed from raw closes and the dated factors."""
    if raw.kind != RAW:
        raise MixedSeriesError(f"total return is computed from raw prices, not {raw.kind}")
    level, out, previous = Decimal(1), [], None
    for day, close in raw.points:
        if previous is not None:
            ratio, paid = splits.get(day, Decimal(1)), dividends.get(day, Decimal(0))
            spin_off = ratio != 1 and not is_share_split(ratio)
            if spin_off and paid > previous * SPIN_OFF_DIVIDEND:
                paid = Decimal(0)  # already inside the ratio
            level *= (close * ratio + paid) / previous
        out.append((day, level))
        previous = close
    return Series(TOTAL_RETURN, raw.source, tuple(out))


def annual_returns(levels: list[tuple[date, Decimal]]) -> dict[int, float]:
    last: dict[int, Decimal] = {}
    for day, level in levels:
        last[day.year] = level
    return {y: float(last[y] / last[y - 1] - 1) for y in last if y - 1 in last}


# ---- survivorship (VL-05) ------------------------------------------------------------------------


def equal_weight_levels(
    series: dict[str, Series], spells: dict[str, list[tuple[date, date | None]]]
) -> tuple[list[tuple[date, Decimal]], dict[int, int]]:
    """Daily equal-weighted return of the companies that were index members on that day, and the
    average number of companies in it per year."""
    daily: dict[date, list[float]] = {}
    for company, s in series.items():
        previous = None
        for day, level in s.points:
            member = any(a <= day and (b is None or day < b) for a, b in spells.get(company, []))
            if previous is not None and member:
                daily.setdefault(day, []).append(float(level / previous) - 1)
            previous = level
    total, out = 1.0, []
    sizes: dict[int, list[int]] = {}
    for day in sorted(daily):
        total *= 1 + sum(daily[day]) / len(daily[day])
        out.append((day, Decimal(str(total))))
        sizes.setdefault(day.year, []).append(len(daily[day]))
    return out, {y: round(sum(v) / len(v)) for y, v in sizes.items()}


def index_levels(engine: Engine, symbol: str) -> list[tuple[date, Decimal]]:
    """Total-return levels of an index or fund from its stored payload (close plus dividends)."""
    body = latest_payload(engine, yahoo.SOURCE, yahoo.url_for(symbol))
    if body is None:
        raise LookupError(f"no stored prices for {symbol}")
    parsed = parse_payload(body)
    raw = Series(RAW, yahoo.SOURCE, tuple((d, c) for d, c, _ in parsed.prices))
    return list(total_return(raw, dict(parsed.splits), dict(parsed.dividends)).points)


def survivorship_report(engine: Engine) -> dict[str, Any]:
    """VL-05: removed companies per year, how many of them have prices, and the universe's yearly
    return against independent index returns. The gap is reported; TH-06 is not set here."""
    with engine.connect() as conn:
        spells: dict[str, list[tuple[date, date | None]]] = {}
        for c, a, b in conn.execute(
            text("SELECT company_id, valid_from, valid_to FROM index_membership")
        ):
            spells.setdefault(c, []).append((a, b))
        priced = set(conn.execute(text("SELECT DISTINCT company_id FROM price_daily")).scalars())
    removed = {
        c for c, s in spells.items() if any(b and date(2015, 1, 1) <= b <= date(2024, 12, 31)
                                            for _, b in s)
    }  # fmt: skip
    series = {}
    for company in sorted(priced & set(spells)):
        with engine.connect() as conn:
            splits: dict[date, Decimal] = dict(
                conn.execute(
                    text("SELECT ex_date, value FROM adjustment_factor WHERE company_id = :c "
                         "AND kind = 'split'"), {"c": company},
                ).all()
            )  # fmt: skip
            dividends: dict[date, Decimal] = dict(
                conn.execute(
                    text("SELECT ex_date, value FROM adjustment_factor WHERE company_id = :c "
                         "AND kind = 'dividend'"), {"c": company},
                ).all()
            )  # fmt: skip
        raw = momentum_window(engine, company, date(2100, 1, 1))
        series[company] = total_return(raw, splits, dividends)
    universe, sizes = equal_weight_levels(series, spells)
    mine = annual_returns(universe)
    out: dict[str, Any] = {"companies_with_prices": len(series), "years": {}}
    indexes = {s: annual_returns(index_levels(engine, s)) for s in INDEXES}
    for year in YEARS:
        members = [
            c for c in removed
            if any(a <= date(year, 12, 31) and (b is None or b > date(year, 1, 1))
                   for a, b in spells[c])
        ]  # fmt: skip
        row: dict[str, Any] = {
            "universe_return": mine.get(year),
            "average_companies": sizes.get(year),
            "later_removed_members": len(members),
            "later_removed_with_prices": len([c for c in members if c in series]),
        }
        for symbol, values in indexes.items():
            row[symbol] = values.get(year)
            if year in mine and year in values:
                row[f"gap_vs_{symbol}"] = mine[year] - values[year]
        out["years"][year] = row
    return out


def price_window_violations(engine: Engine) -> dict[str, int]:
    """DV-05, price window: for events with prices, every momentum day is before the announcement
    session and every outcome day is on or after it."""
    with engine.connect() as conn:
        events = conn.execute(
            text(
                "SELECT company_id, announcement_time_utc FROM earnings_event WHERE company_id IN "
                "(SELECT DISTINCT company_id FROM price_daily) "
                "AND announcement_time_utc IS NOT NULL"
            )
        ).all()
        bad = checked = 0
        for company, moment in events:
            session = cal.trading_day_for(moment)
            row = conn.execute(
                text(
                    "SELECT (SELECT max(price_date) FROM price_daily_before(:c, :s)), "
                    "(SELECT min(price_date) FROM price_daily_from(:c, :s))"
                ),
                {"c": company, "s": session},
            ).one()
            checked += 1
            bad += (row[0] is not None and row[0] >= session) or (
                row[1] is not None and row[1] < session
            )
    return {"events_checked": checked, "violations": bad}


def main(argv: list[str]) -> int:
    """python -m earnings.prices load OUT_DIR | report OUT_DIR"""
    from earnings import universe as u
    from earnings.db import get_engine

    if len(argv) < 3 or argv[1] not in ("load", "report"):
        print("python -m earnings.prices load|report OUT_DIR")
        return 2
    engine, out = get_engine("worker"), Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    if argv[1] == "load":
        companies, _ = u.read_list(Path(__file__).parent / "universe.csv")
        pairs = []
        with engine.connect() as conn:
            for c in companies:
                ticker = conn.execute(
                    text("SELECT ticker FROM ticker_history WHERE company_id = :c "
                         "ORDER BY valid_from DESC LIMIT 1"), {"c": c["company_id"]},
                ).scalar_one()  # fmt: skip
                pairs.append((c["company_id"], ticker))
        report = load_prices(engine, pairs, pause=0.3)
        for symbol in INDEXES:  # the indexes are kept as payloads only (no company)
            store_payload(engine, yahoo.response(symbol, yahoo.fetch_payload(symbol)))
        (out / "price_load_report.json").write_text(json.dumps(report, indent=1), "utf-8")
    else:
        report = {"survivorship": survivorship_report(engine),
                  "price_windows": price_window_violations(engine)}  # fmt: skip
        (out / "price_report.json").write_text(json.dumps(report, indent=1, default=str), "utf-8")
    print(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
