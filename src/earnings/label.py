"""The time-series standardised unexpected earnings, SUE (Data LB-01, LB-02, LB-04, LB-05, CE-05;
Product FR-02, label route B, decision ADR 0004).

SUE for an event in quarter q announced on D is (EPS(q) - EPS(q-4)) divided by the standard
deviation of the previous seasonal differences. The history uses only first-filed values filed
strictly before D, put on the share basis known at D. Pure functions: no database, no network.

Split factors are the dated ratios companies report in their SEC filings (the XBRL tag
StockholdersEquityNoteStockSplitConversionRatio1), as the approved Wave 1.6 brief says. A company
that does not report the tag gets no adjustment, and Data LB-05 is not met for its splits until the
price source's factors are stored (Data PX-01).

Choices made here and not fixed by the requirement text (decision D-47, items j, k and p):
- the standard deviation is the sample standard deviation (n - 1);
- a ratio counts as a share split only if it is a whole or half number above 1 and at most 100;
  the same ratio reported with effective dates within 400 days is one split;
- the announced quarter must not have been filed more than 10 days before the announcement. If the
  latest quarter in the data is older than that, the announced quarter is missing.
"""

import json
from collections.abc import Sequence
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from statistics import median, stdev

ROUTE_TIME_SERIES = "time-series"
EPS_BASIS = "gaap-diluted"
MAX_DIFFERENCES = 8  # TH-11: window of 8 seasonal differences
MIN_DIFFERENCES = 6  # TH-11: at least 6 are needed (10 quarters of history)
QUARTER_GAP = range(70, 116)  # days between the ends of consecutive fiscal quarters
MAX_REPORT_LAG_DAYS = 100  # the announced quarter ended at most this long before D (seen: 77)
SPLIT_TAG = "StockholdersEquityNoteStockSplitConversionRatio1"
SPLIT_MAX_RATIO = 100
SAME_SPLIT_DAYS = 400
ALREADY_PUBLIC_DAYS = 10
# EPS of more than this size, in a company whose typical EPS is far smaller, is a scale error
SCALE_LIMIT = 1000
SCALE_TYPICAL = 100


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
    ratio: Decimal  # old basis value divided by new basis value, for example 7 for a 7-for-1 split
    effective: date  # the day the split took effect, as the company reported it


@dataclass(frozen=True)
class SueResult:
    period_end: date | None
    sue: Decimal | None
    reason: str | None  # why the label is unavailable
    differences: int
    information_date: date | None  # filing date of the latest EPS used (Product FR-02, LB-04)
    splits_applied: int = 0
    target_filed: date | None = None  # first filing of the announced quarter's EPS
    scale_suspect: bool = False  # an input is out of scale with the company's other values


def first_filed(versions: list[EpsVersion]) -> dict[date, EpsVersion]:
    """One row per quarter, named by its end date: the earliest filing, a directly reported value
    before a derived one. Filings sometimes report the same quarter with a start date shifted by a
    day or a week, so the start date does not identify a quarter."""
    out: dict[date, EpsVersion] = {}
    for v in sorted(versions, key=lambda v: (v.filed, v.derived)):
        out.setdefault(v.period_end, v)
    return out


def splits_from_facts(payload: bytes) -> list[Split]:
    """The dated share splits a company reports in its SEC company facts (LB-05). Share conversions
    at a listing and nonsense values are dropped; a split repeated across filings is one split."""
    node = json.loads(payload).get("facts", {}).get("us-gaap", {}).get(SPLIT_TAG)
    if not node:
        return []
    found: list[tuple[date, Decimal]] = []
    for unit_rows in node["units"].values():
        for f in unit_rows:
            ratio = Decimal(str(f["val"]))
            if 1 < ratio <= SPLIT_MAX_RATIO and (ratio * 2) % 1 == 0:
                found.append((date.fromisoformat(f["end"]), ratio.normalize()))
    out: list[Split] = []
    for effective, ratio in sorted(found):
        if any(s.ratio == ratio and (effective - s.effective).days <= SAME_SPLIT_DAYS for s in out):
            continue
        out.append(Split(ratio, effective))
    return out


def is_share_split(ratio: Decimal) -> bool:
    """A forward split in whole or half shares, or a reverse split of one for a whole number. The
    price source also lists spin-off price ratios (for example 1.046), which leave EPS alone."""
    if 1 < ratio <= SPLIT_MAX_RATIO:
        return (ratio * 2) % 1 == 0
    if 0 < ratio < 1:
        whole = 1 / ratio
        return 2 <= round(whole) <= SPLIT_MAX_RATIO and abs(whole - round(whole)) < Decimal("0.001")
    return False


def adjusted_value(v: EpsVersion, splits: Sequence[Split]) -> tuple[Decimal, int]:
    """The value on the share basis of `splits`, and how many splits were applied: a value first
    filed before a split took effect is on the old basis."""
    value, applied = v.value, 0
    for s in splits:
        if v.filed < s.effective:
            value /= s.ratio
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


def compute_sue(
    versions: list[EpsVersion], announcement: date, splits: Sequence[Split] = ()
) -> SueResult:
    """Data LB-01, LB-02, LB-04, LB-05 for one event announced on `announcement`."""
    quarters = [v for v in versions if (v.period_end - v.period_start).days in range(80, 101)]
    if not quarters:
        return SueResult(None, None, "no quarterly EPS stored for this company", 0, None)
    everything = first_filed(quarters)  # includes values filed after D: only the label may use them
    target_ends = [
        e for e in everything if e < announcement
        and (announcement - e).days <= MAX_REPORT_LAG_DAYS
    ]  # fmt: skip
    if not target_ends:
        return SueResult(None, None, "no quarter ended within the reporting window", 0, None)
    q_end = max(target_ends)
    q_first = everything[q_end]
    if (announcement - q_first.filed).days > ALREADY_PUBLIC_DAYS:
        return SueResult(None, None, "the announced quarter is not in the stored EPS", 0, None)
    history = {
        v.period_end: v
        for v in first_filed([v for v in quarters if v.filed < announcement]).values()
    }
    known_splits = [s for s in splits if s.effective < announcement]  # known before D (LB-05)
    chain = _chain({**history, q_end: q_first}, q_end)
    if len(chain) < 5:
        return SueResult(q_end, None, "fewer than 6 prior seasonal differences", 0, None)

    def val(end: date) -> tuple[Decimal, int]:
        v = q_first if end == q_end else history[end]
        return adjusted_value(v, known_splits)

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
    typical = median(abs(v.value) for v in everything.values())
    raw = [abs(q_first.value if e == q_end else history[e].value) for e in {chain[0], *used}]
    suspect = bool(max(raw) > SCALE_LIMIT and typical <= SCALE_TYPICAL)
    assert_inputs_before([history[e].filed for e in set(used)], announcement)
    sd = stdev(diffs)
    if sd == 0:
        return SueResult(
            q_end, None, "standard deviation of the differences is zero", len(diffs), info,
            target_filed=q_first.filed, scale_suspect=suspect,
        )  # fmt: skip
    sue = ((cur - prev) / sd).quantize(Decimal("0.000001"))
    return SueResult(
        q_end, sue, None, len(diffs), info, applied, target_filed=q_first.filed,
        scale_suspect=suspect,
    )  # fmt: skip


def assert_one_route(routes: list[str]) -> str:
    """Routes are never mixed in one training set (CE-05)."""
    distinct = sorted(set(routes))
    if len(distinct) > 1:
        raise MixedRouteError(f"training set mixes label routes: {distinct}")
    return distinct[0] if distinct else ROUTE_TIME_SERIES
