"""Forward consensus capture (Data SR-08, SR-10, Product FR-14, Project-Wide EQ-07, SC-04).

The fetch function is replaced by a recorded response in these tests, so no network is used. The
recorded values come from a real call to yfinance 1.8.0 for AAPL on 23 November 2026 (Wave 0.1,
Spike C). Rows that tests insert for other purposes are synthetic and say so.
"""

from datetime import UTC, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from earnings import consensus

# Real response, trimmed to the current-quarter row and the raw table as returned.
RECORDED_AAPL = {
    "mean": 2.91173,
    "low": 2.83,
    "high": 3.18,
    "count": 25,
    "basis": "gaap",
    "period": "0q",
    "version": "1.8.0",
    "payload": {
        "0q": {
            "avg": 2.91173,
            "low": 2.83,
            "high": 3.18,
            "yearAgoEps": 2.84,
            "numberOfAnalysts": 25,
            "growth": 0.0253,
            "currency": "USD",
            "methodology": "gaap",
        }
    },
}
START = consensus.CAPTURE_START
UNIVERSE = [("AAPL", "0000320193", "Apple Inc.")]


def _fetch(_ticker):
    return RECORDED_AAPL


def _snapshots(engine):
    with engine.connect() as conn:
        return conn.execute(
            text(
                "SELECT company_id, mean_estimate, std_estimate, captured_at FROM estimate_snapshot"
            )
        ).all()


def _insert(engine, **overrides):
    row = {
        "company_id": "0000320193",
        "captured_at": START + timedelta(hours=1),
        "period_label": "0q",
        "payload": "{}",
    }
    row.update(overrides)
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO company (company_id, name) "
                "VALUES ('0000320193', 'SYNTHETIC test row') ON CONFLICT DO NOTHING"
            )
        )
        conn.execute(
            text(
                "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, source, "
                "source_version, captured_at, raw_payload) VALUES (:company_id, 1.0, :period_label,"
                " 'synthetic-test', 'x', :captured_at, CAST(:payload AS jsonb))"
            ),
            row,
        )


@pytest.mark.req("SR-08-AC1")
@pytest.mark.code("src/earnings/migrations/versions", "src/earnings/consensus.py")
def test_sr_08_ac1_snapshot_rows_without_capture_time_or_before_start_are_rejected(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    with pytest.raises(DBAPIError) as missing:
        _insert(engine, captured_at=None)
    assert type(missing.value.orig).__name__ == "NotNullViolation"
    with pytest.raises(DBAPIError) as early:
        _insert(engine, captured_at=START - timedelta(seconds=1))
    assert type(early.value.orig).__name__ == "CheckViolation"
    _insert(engine, captured_at=START)  # the start instant itself is allowed
    assert len(_snapshots(engine)) == 1


@pytest.mark.req("SR-08")
@pytest.mark.code("src/earnings/migrations/versions")
def test_sr_08_snapshots_are_append_only_for_the_worker_role(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    _insert(engine)
    for statement in (
        "UPDATE estimate_snapshot SET mean_estimate = 9",
        "DELETE FROM estimate_snapshot",
    ):
        with pytest.raises(DBAPIError) as err:
            with engine.begin() as conn:
                conn.execute(text(statement))
        assert type(err.value.orig).__name__ == "InsufficientPrivilege"


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/consensus.py", "src/earnings/tasks.py")
def test_sr_10_capture_stores_what_the_source_returned_and_is_idempotent(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    now = START + timedelta(days=1, hours=22, minutes=30)
    first = consensus.capture_all(engine, UNIVERSE, fetch=_fetch, now=now)
    again = consensus.capture_all(engine, UNIVERSE, fetch=_fetch, now=now + timedelta(minutes=5))
    assert (first.captured, first.failed) == (1, [])
    assert (again.captured, again.already_captured) == (0, 1)  # EQ-07: same day, one row
    rows = _snapshots(engine)
    assert len(rows) == 1
    company_id, mean, std, captured_at = rows[0]
    assert (company_id, float(mean), std) == ("0000320193", 2.91173, None)  # no std from yfinance
    assert captured_at == now


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/consensus.py")
def test_sr_10_a_source_failure_is_reported_and_stores_no_row(test_db):
    from earnings.db import get_engine

    def broken(_ticker):
        raise RuntimeError("source unavailable")

    engine = get_engine("worker")
    result = consensus.capture_all(engine, UNIVERSE, fetch=broken, now=START + timedelta(days=1))
    assert (result.captured, result.failed) == (0, ["AAPL"])
    assert _snapshots(engine) == []


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/consensus.py")
def test_sr_10_gap_longer_than_three_days_is_reported(test_db):
    """Synthetic capture dates. Missing days 3 to 5 are three, so not reported; a fourth is."""
    from earnings.db import get_engine

    engine = get_engine("worker")
    day = START.date()
    for offset in (0, 1, 5, 9):  # missing: days 2-4 (three) and days 6-8 (three)
        _insert(engine, captured_at=START + timedelta(days=offset, hours=2))
    assert consensus.gaps(engine, today=day + timedelta(days=9)) == []
    _insert(engine, captured_at=START + timedelta(days=14, hours=2))  # missing days 10-13 (four)
    found = consensus.gaps(engine, today=day + timedelta(days=14))
    assert [(g.first_missing, g.last_missing, g.days) for g in found] == [
        (day + timedelta(days=10), day + timedelta(days=13), 4)
    ]
    # No capture at all since the last one counts as a gap that is still open.
    open_gap = consensus.gaps(engine, today=day + timedelta(days=19))
    assert open_gap[-1].last_missing == day + timedelta(days=18) and open_gap[-1].days == 4


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/consensus.py", "src/earnings/tasks.py")
def test_sr_10_catch_up_asks_only_when_today_has_no_capture(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    today = START.date() + timedelta(days=2)
    assert consensus.missing_today(engine, today=today) is True
    consensus.capture_all(
        engine,
        UNIVERSE,
        fetch=_fetch,
        now=datetime.combine(today, datetime.min.time(), tzinfo=UTC) + timedelta(hours=9),
    )
    assert consensus.missing_today(engine, today=today) is False


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/celery_app.py", "src/earnings/tasks.py")
def test_sr_10_daily_schedule_runs_at_22_30_utc():
    from earnings.celery_app import celery_app

    entry = celery_app.conf.beat_schedule["capture-consensus"]
    assert entry["task"] == "earnings.capture_consensus"
    schedule = entry["schedule"]
    assert (schedule.hour, schedule.minute) == ({22}, {30})
    assert celery_app.conf.timezone == "UTC"


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/capture_universe.csv", "src/earnings/consensus.py")
def test_sr_10_universe_uses_ten_digit_ciks_and_unique_tickers():
    companies = consensus.load_universe()
    assert len(companies) == 10
    assert len({t for t, _, _ in companies}) == 10
    assert all(len(cik) == 10 and cik.isdigit() for _, cik, _ in companies)


@pytest.mark.req("SR-10")
@pytest.mark.code("src/earnings/consensus.py")
def test_sr_10_a_row_with_no_mean_is_not_stored(test_db):
    from earnings.db import get_engine

    def no_mean(_ticker):
        return {**RECORDED_AAPL, "mean": None}

    engine = get_engine("worker")
    result = consensus.capture_all(engine, UNIVERSE, fetch=no_mean, now=START + timedelta(days=1))
    assert (result.captured, result.failed) == (0, ["AAPL"])
