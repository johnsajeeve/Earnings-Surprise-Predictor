"""The time-series standardised unexpected earnings, SUE (Data LB-01, LB-02, LB-04, LB-05, CE-05;
Product FR-02, label route B, decision ADR 0004).

SUE for an event in quarter q announced on D is (EPS(q) - EPS(q-4)) divided by the standard
deviation of the previous seasonal differences. The history uses only first-filed values filed
strictly before D, put on the share basis known at D. Pure functions: no database, no network.

Choices made here and not fixed by the requirement text (decision D-47, items j and k):
- the standard deviation is the sample standard deviation (n - 1);
- a split is inferred from the data: two or more quarters of one company re-reported by a later
  filing with the same ratio (at least 20% away from 1, within 2% of each other). The ratio applies
  to every quarter first filed before that later filing. Split tables from the price source
  (Data PX-01) replace this when John approves them.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from statistics import median, stdev

ROUTE_TIME_SERIES = "time-series"
EPS_BASIS = "gaap-diluted"
MAX_DIFFERENCES = 8  # TH-11: window of 8 seasonal differences
MIN_DIFFERENCES = 6  # TH-11: at least 6 are needed (10 quarters of history)
QUARTER_GAP = range(70, 116)  # days between the ends of consecutive fiscal quarters
MAX_REPORT_LAG_DAYS = 130  # the quarter being announced ended at most this long before D
SPLIT_MIN_DISTANCE = 0.20
SPLIT_TOLERANCE = 0.02


class LookaheadError(Exception):
    """An input to the label is dated on or after the announcement it must not see (IG-20)."""


class MixedRouteError(Exception):
    """Events of different label routes in one training set (CE-05)."""


@dataclass(frozen=True)
class EpsVersion:
    period_start: date
    period_end: date
    value: Decimal
    filed: date
    derived: bool = False


@dataclass(frozen=True)
class Split:
    ratio: float  # old basis value divided by new basis value, for example 7 for a 7-for-1 split
    known_from: date  # the first filing that re-reported quarters on the new basis
    periods: int


@dataclass(frozen=True)
class SueResult:
    period_end: date | None
    sue: Decimal | None
    reason: str | None  # why the label is unavailable
    differences: int
    information_date: date | None  # filing date of the latest EPS used (Product FR-02, LB-04)
    splits_applied: int = 0


def first_filed(versions: list[EpsVersion]) -> dict[tuple[date, date], EpsVersion]:
    """One row per period: the earliest filing, a directly reported value before a derived one."""
    out: dict[tuple[date, date], EpsVersion] = {}
    for v in sorted(versions, key=lambda v: (v.filed, v.derived)):
        out.setdefault((v.period_start, v.period_end), v)
    return out


def detect_splits(versions: list[EpsVersion], before: date) -> list[Split]:
    """Splits known before `before`, found from quarters that a later filing re-reported on a new
    share basis (LB-05). A restatement of one quarter is not enough: two quarters must agree."""
    known = [v for v in versions if v.filed < before]
    firsts = first_filed(known)
    candidates: list[tuple[float, date, tuple[date, date]]] = []
    for v in known:
        base = firsts[(v.period_start, v.period_end)]
        if v is base or v.value == 0 or base.value == 0 or v.filed <= base.filed:
            continue
        ratio = float(base.value / v.value)
        if ratio > 0 and abs(ratio - 1) >= SPLIT_MIN_DISTANCE:
            candidates.append((ratio, v.filed, (v.period_start, v.period_end)))
    groups: list[list[tuple[float, date, tuple[date, date]]]] = []
    for cand in sorted(candidates):
        for group in groups:
            if abs(cand[0] / group[0][0] - 1) <= SPLIT_TOLERANCE:
                group.append(cand)
                break
        else:
            groups.append([cand])
    splits = []
    for group in groups:
        periods = {c[2] for c in group}
        if len(periods) >= 2:
            splits.append(
                Split(median(c[0] for c in group), min(c[1] for c in group), len(periods))
            )
    return sorted(splits, key=lambda s: s.known_from)


def adjusted_value(v: EpsVersion, splits: list[Split]) -> tuple[Decimal, int]:
    """The value on the share basis known at D, and how many splits were applied."""
    value, applied = v.value, 0
    for s in splits:
        if v.filed < s.known_from:
            value /= Decimal(str(round(s.ratio, 6)))
            applied += 1
    return value, applied


def assert_inputs_before(filed_dates: list[date], announcement: date) -> None:
    """Date gate (IG-20): every input to the history was filed strictly before D."""
    late = [d for d in filed_dates if d >= announcement]
    if late:
        raise LookaheadError(
            f"input filed on {max(late)} is not before the announcement {announcement}"
        )


def _chain(known: dict[date, EpsVersion], start_end: date) -> list[date]:
    """Quarter ends going back from `start_end`, stopping at a gap that is not one quarter."""
    ends = [start_end]
    for end in sorted((e for e in known if e < start_end), reverse=True):
        if (ends[-1] - end).days in QUARTER_GAP:
            ends.append(end)
        elif (ends[-1] - end).days > max(QUARTER_GAP):
            break
    return ends


def compute_sue(versions: list[EpsVersion], announcement: date) -> SueResult:
    """Data LB-01, LB-02, LB-04, LB-05 for one event announced on `announcement`."""
    quarters = [v for v in versions if (v.period_end - v.period_start).days in range(80, 101)]
    if not quarters:
        return SueResult(None, None, "no quarterly EPS stored for this company", 0, None)
    everything = first_filed(quarters)  # includes values filed after D: only the label may use them
    target_ends = [
        e for (_, e) in everything if e < announcement
        and (announcement - e).days <= MAX_REPORT_LAG_DAYS
    ]  # fmt: skip
    if not target_ends:
        return SueResult(None, None, "no quarter ended within the reporting window", 0, None)
    q_end = max(target_ends)
    q_first = next(v for (_, e), v in everything.items() if e == q_end)
    history = {
        v.period_end: v
        for v in first_filed([v for v in quarters if v.filed < announcement]).values()
    }
    splits = detect_splits(quarters, announcement)
    chain = _chain({**history, q_end: q_first}, q_end)
    if len(chain) < 5:
        return SueResult(q_end, None, "fewer than 6 prior seasonal differences", 0, None)

    def val(end: date) -> tuple[Decimal, int]:
        v = q_first if end == q_end else history[end]
        return adjusted_value(v, splits)

    diffs, applied, used = [], 0, [chain[4]]
    for k in range(1, MAX_DIFFERENCES + 1):
        if k + 4 >= len(chain):
            break
        a, na = val(chain[k])
        b, nb = val(chain[k + 4])
        diffs.append(a - b)
        applied += na + nb
        used += [chain[k], chain[k + 4]]
    if len(diffs) < MIN_DIFFERENCES:
        return SueResult(q_end, None, "fewer than 6 prior seasonal differences", len(diffs), None)
    cur, prev = val(chain[0])[0], val(chain[4])[0]
    info = max(history[e].filed for e in set(used))
    assert_inputs_before([history[e].filed for e in set(used)], announcement)
    sd = stdev(diffs)
    if sd == 0:
        return SueResult(
            q_end, None, "standard deviation of the differences is zero", len(diffs), info
        )
    sue = ((cur - prev) / sd).quantize(Decimal("0.000001"))
    return SueResult(q_end, sue, None, len(diffs), info, applied)


def assert_one_route(routes: list[str]) -> str:
    """Routes are never mixed in one training set (CE-05)."""
    distinct = sorted(set(routes))
    if len(distinct) > 1:
        raise MixedRouteError(f"training set mixes label routes: {distinct}")
    return distinct[0] if distinct else ROUTE_TIME_SERIES
