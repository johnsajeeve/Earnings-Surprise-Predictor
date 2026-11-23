"""Forward consensus capture (Data SR-08, SR-10, CE-01, Product FR-14).

Free sources give only the current consensus, so it is recorded once a day from the start date
and never backfilled (SR-08, CE-02). Each snapshot keeps the source's answer as received.
"""

import csv
import json
import logging
import time
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

log = logging.getLogger(__name__)

SOURCE = "yfinance"
PERIOD = "0q"  # the current quarter, as the source labels it
# The first capture instant. Matches the CHECK in migration 0002 (SR-08).
CAPTURE_START = datetime(2026, 11, 23, tzinfo=UTC)
# A gap is more than this many consecutive days without a capture (SR-10).
MAX_MISSING_DAYS = 3
_UNIVERSE = Path(__file__).parent / "capture_universe.csv"
_PAUSE_SECONDS = 1.0  # between sources calls, to stay polite to the free service

Fetch = Callable[[str], dict[str, Any]]


@dataclass
class CaptureResult:
    captured: int = 0
    already_captured: int = 0
    failed: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class Gap:
    first_missing: date
    last_missing: date
    days: int


def load_universe() -> list[tuple[str, str, str]]:
    """(ticker, company_id, name) for each company to capture."""
    with _UNIVERSE.open(encoding="utf-8", newline="") as fh:
        return [(r["ticker"], r["company_id"], r["name"]) for r in csv.DictReader(fh)]


def fetch_yfinance(ticker: str) -> dict[str, Any]:
    """The current-quarter consensus from yfinance, with the raw table as received."""
    import yfinance

    frame = yfinance.Ticker(ticker).earnings_estimate
    if frame is None or PERIOD not in frame.index:
        raise ValueError(f"no {PERIOD} estimate returned for {ticker}")
    row = frame.loc[PERIOD]

    def number(value: Any) -> float | None:
        return None if value != value else float(value)  # NaN is the only value that != itself

    count = number(row.get("numberOfAnalysts"))
    return {
        "mean": number(row.get("avg")),
        "low": number(row.get("low")),
        "high": number(row.get("high")),
        "count": None if count is None else int(count),
        "basis": row.get("methodology"),
        "period": PERIOD,
        "version": yfinance.__version__,
        "payload": json.loads(frame.to_json(orient="index")),
    }


def capture_all(
    engine: Engine,
    companies: list[tuple[str, str, str]],
    fetch: Fetch = fetch_yfinance,
    now: datetime | None = None,
    pause: float = 0.0,
) -> CaptureResult:
    """Record one snapshot per company, unless it already has one for this UTC day (EQ-07).

    A company whose source call fails, or returns no mean, is listed in `failed` and gets no row.
    """
    if now is not None and now.tzinfo is None:
        raise ValueError("capture time must carry a time zone")
    result = CaptureResult()
    for ticker, company_id, name in companies:
        try:
            data = fetch(ticker)
            if data.get("mean") is None:
                raise ValueError("source returned no mean estimate")
        except Exception as exc:  # noqa: BLE001  one failing company must not stop the others
            log.error("capture failed for %s: %s: %s", ticker, type(exc).__name__, exc)
            result.failed.append(ticker)
            continue
        moment = now or datetime.now(UTC)  # stamped when the answer arrived, not when the run began
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO company (company_id, name) VALUES (:id, :name) "
                    "ON CONFLICT (company_id) DO NOTHING"
                ),
                {"id": company_id, "name": name},
            )
            inserted = conn.execute(
                text(
                    "INSERT INTO estimate_snapshot (company_id, mean_estimate, low_estimate, "
                    "high_estimate, estimate_count, eps_basis, period_label, source, "
                    "source_version, captured_at, raw_payload) VALUES (:company_id, :mean, :low, "
                    ":high, :count, :basis, :period, :source, :version, :captured_at, "
                    "CAST(:payload AS jsonb)) ON CONFLICT DO NOTHING"
                ),
                {
                    "company_id": company_id,
                    "mean": data["mean"],
                    "low": data.get("low"),
                    "high": data.get("high"),
                    "count": data.get("count"),
                    "basis": data.get("basis"),
                    "period": data.get("period", PERIOD),
                    "source": SOURCE,
                    "version": data.get("version", "unknown"),
                    "captured_at": moment,
                    "payload": json.dumps(data.get("payload", {})),
                },
            ).rowcount
        if inserted:
            result.captured += 1
        else:
            result.already_captured += 1
        if pause:
            time.sleep(pause)
    return result


def _capture_days(engine: Engine) -> list[date]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT DISTINCT (captured_at AT TIME ZONE 'UTC')::date AS d "
                "FROM estimate_snapshot ORDER BY d"
            )
        )
        return [r[0] for r in rows]


def gaps(engine: Engine, today: date | None = None) -> list[Gap]:
    """Runs of more than MAX_MISSING_DAYS consecutive UTC days with no capture, from the start
    date up to the day before `today` (SR-10). A run still open at that point is included.
    """
    last_day = today or datetime.now(UTC).date()
    days = _capture_days(engine)
    found: list[Gap] = []
    previous = CAPTURE_START.date() - timedelta(days=1)  # the day before the first capture day
    # `today` is a boundary, not a missing day: its capture may not have run yet.
    for current in sorted({*days, last_day}):
        missing = (current - previous).days - 1
        if missing > MAX_MISSING_DAYS:
            found.append(Gap(previous + timedelta(days=1), current - timedelta(days=1), missing))
        previous = current
    return found


def missing_today(engine: Engine, today: date | None = None) -> bool:
    """True when no snapshot exists for this UTC day (used for the catch-up at worker start)."""
    return (today or datetime.now(UTC).date()) not in _capture_days(engine)


if __name__ == "__main__":
    from earnings.db import get_engine

    api = get_engine("api")
    captured_days = _capture_days(api)
    first, last = captured_days[:1], captured_days[-1:]
    print(f"capture days: {len(captured_days)}; first {first}; last {last}")
    for gap in gaps(api):
        print(f"GAP: {gap.first_missing} to {gap.last_missing} ({gap.days} days)")
