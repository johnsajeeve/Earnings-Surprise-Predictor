"""NYSE trading days and the trading day an announcement counts for (Data DV-07).

The holidays follow the NYSE holiday rules: a holiday that falls on a Sunday is observed on the
Monday and one that falls on a Saturday on the Friday before, except New Year's Day, which is not
moved to the previous year. Good Friday is the Friday before Western Easter. Juneteenth is a holiday
from 2022. Days the exchange closed for other reasons are listed in SPECIAL_CLOSURES with the
reason. Source: the NYSE holiday and trading hours pages (nyse.com/markets/hours-calendars), the
rules as published there; checked in tests/test_calendar.py against known dates.
"""

from datetime import UTC, date, datetime, time, timedelta
from functools import cache
from zoneinfo import ZoneInfo

EASTERN = ZoneInfo("America/New_York")
MARKET_CLOSE = time(16, 0)

SPECIAL_CLOSURES = {
    date(2012, 10, 29): "Hurricane Sandy",
    date(2012, 10, 30): "Hurricane Sandy",
    date(2018, 12, 5): "National Day of Mourning for President George H. W. Bush",
    date(2025, 1, 9): "National Day of Mourning for President Jimmy Carter",
}


def _easter(year: int) -> date:
    a, b, c = year % 19, year // 100, year % 100
    d, e = b // 4, b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i, k = c // 4, c % 4
    el = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * el) // 451
    month = (h + el - 7 * m + 114) // 31
    day = (h + el - 7 * m + 114) % 31 + 1
    return date(year, month, day)


def _nth_weekday(year: int, month: int, weekday: int, n: int) -> date:
    first = date(year, month, 1)
    return first + timedelta(days=(weekday - first.weekday()) % 7 + 7 * (n - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    nxt = date(year + (month == 12), month % 12 + 1, 1)
    last = nxt - timedelta(days=1)
    return last - timedelta(days=(last.weekday() - weekday) % 7)


def _observed(day: date) -> date | None:
    if day.weekday() == 5:
        return day - timedelta(days=1)
    if day.weekday() == 6:
        return day + timedelta(days=1)
    return day


@cache
def holidays(year: int) -> frozenset[date]:
    out: set[date] = set()
    new_year = date(year, 1, 1)
    if new_year.weekday() != 5:  # a Saturday New Year's Day is not moved back into the old year
        out.add(_observed(new_year))  # type: ignore[arg-type]
    out.add(_nth_weekday(year, 1, 0, 3))  # Martin Luther King Jr. Day
    out.add(_nth_weekday(year, 2, 0, 3))  # Washington's Birthday
    out.add(_easter(year) - timedelta(days=2))  # Good Friday
    out.add(_last_weekday(year, 5, 0))  # Memorial Day
    if year >= 2022:
        out.add(_observed(date(year, 6, 19)))  # type: ignore[arg-type]  # Juneteenth
    out.add(_observed(date(year, 7, 4)))  # type: ignore[arg-type]
    out.add(_nth_weekday(year, 9, 0, 1))  # Labor Day
    out.add(_nth_weekday(year, 11, 3, 4))  # Thanksgiving
    out.add(_observed(date(year, 12, 25)))  # type: ignore[arg-type]
    return frozenset(out)


def is_trading_day(day: date) -> bool:
    return day.weekday() < 5 and day not in holidays(day.year) and day not in SPECIAL_CLOSURES


def next_trading_day(day: date) -> date:
    """The first trading day strictly after `day`."""
    day += timedelta(days=1)
    while not is_trading_day(day):
        day += timedelta(days=1)
    return day


def trading_day_for(moment_utc: datetime) -> date:
    """The session an announcement made at `moment_utc` counts for (DV-07). Before the close of a
    trading day it counts for that day (pre-open and intraday). At or after 16:00 Eastern, or on a
    day with no session, it counts for the next session."""
    local = moment_utc.astimezone(EASTERN)
    day = local.date()
    if is_trading_day(day) and local.time() < MARKET_CLOSE:
        return day
    return next_trading_day(day)


def utc(moment: datetime) -> datetime:
    """Timestamps are stored in UTC (DV-07); a naive value is refused."""
    if moment.tzinfo is None:
        raise ValueError("a timestamp without a time zone cannot be converted to UTC")
    return moment.astimezone(UTC)
