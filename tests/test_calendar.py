"""NYSE trading days and the announcement-to-session rule (Data DV-07)."""

from datetime import UTC, date, datetime
from pathlib import Path

import pytest

from earnings import calendar as cal
from earnings import financials as fin

FX = Path(__file__).parent / "fixtures"


@pytest.mark.req("DV-07-AC1")
@pytest.mark.code("src/earnings/calendar.py")
def test_known_exchange_holidays_and_open_days():
    closed = [
        date(2015, 4, 3),  # Good Friday
        date(2012, 10, 29),  # Hurricane Sandy
        date(2018, 12, 5),  # day of mourning
        date(2020, 5, 25),  # Memorial Day
        date(2021, 7, 5),  # 4 July was a Sunday: observed Monday
        date(2022, 6, 20),  # Juneteenth observed (19 June was a Sunday)
        date(2022, 12, 26),  # Christmas was a Sunday
        date(2023, 1, 2),  # New Year's Day was a Sunday
        date(2020, 7, 3),  # 4 July was a Saturday: observed Friday
        date(2025, 1, 9),  # day of mourning
        date(2024, 11, 28),  # Thanksgiving
    ]
    opened = [
        date(2021, 12, 31),  # New Year's Day 2022 was a Saturday: no Friday closure
        date(2021, 6, 18),  # Juneteenth was not a holiday before 2022
        date(2015, 4, 2),
        date(2024, 11, 29),  # the day after Thanksgiving is a session
    ]
    assert not any(cal.is_trading_day(d) for d in closed)
    assert all(cal.is_trading_day(d) for d in opened)
    assert cal.next_trading_day(date(2015, 4, 2)) == date(
        2015, 4, 6
    )  # over Good Friday and a weekend


@pytest.mark.req("DV-07-AC1")
@pytest.mark.code("src/earnings/calendar.py")
def test_pre_open_and_after_close_releases_map_to_the_right_session():
    pre_open = datetime(2024, 10, 23, 11, 30, tzinfo=UTC)  # SYNTHETIC: 07:30 Eastern, a Wednesday
    after_close = datetime(2024, 10, 23, 20, 30, tzinfo=UTC)  # SYNTHETIC: 16:30 Eastern
    assert cal.trading_day_for(pre_open) == date(2024, 10, 23)
    assert cal.trading_day_for(after_close) == date(2024, 10, 24)
    friday_close = datetime(2024, 10, 25, 21, 0, tzinfo=UTC)
    assert cal.trading_day_for(friday_close) == date(2024, 10, 28)  # over the weekend
    # exactly 16:00 Eastern is the close: the release counts for the next session
    assert cal.trading_day_for(datetime(2024, 10, 23, 20, 0, tzinfo=UTC)) == date(2024, 10, 24)
    assert cal.trading_day_for(datetime(2024, 10, 23, 19, 59, tzinfo=UTC)) == date(2024, 10, 23)
    # the clocks: 20:30 UTC is 16:30 in summer and 15:30 in winter
    assert cal.trading_day_for(datetime(2024, 1, 10, 20, 30, tzinfo=UTC)) == date(2024, 1, 10)
    assert cal.trading_day_for(datetime(2024, 7, 10, 20, 30, tzinfo=UTC)) == date(2024, 7, 11)


@pytest.mark.req("DV-07-AC1")
@pytest.mark.code("src/earnings/calendar.py", "src/earnings/financials.py")
def test_real_apple_releases_filed_after_the_close_count_for_the_next_session():
    releases = fin.parse_earnings_releases([(FX / "aapl_submissions_8k_sample.json").read_bytes()])
    sessions = {r.filed: cal.trading_day_for(r.accepted_utc) for r in releases}
    # Apple files at about 16:30 Eastern: the 30 January 2025 release counts for 31 January
    assert sessions[date(2025, 1, 30)] == date(2025, 1, 31)
    assert all(s > f for f, s in sessions.items())


@pytest.mark.req("DV-07-AC1")
@pytest.mark.code("src/earnings/calendar.py")
def test_a_timestamp_without_a_time_zone_is_refused():
    with pytest.raises(ValueError):
        cal.utc(datetime(2024, 1, 1, 12, 0))
    assert cal.utc(datetime(2024, 1, 1, 12, 0, tzinfo=UTC)).tzinfo is not None
