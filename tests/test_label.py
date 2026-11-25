"""The time-series SUE (Data LB-01, LB-02, LB-04, LB-05, CE-05; Product FR-02; Ingestion IG-20).

Series built by hand in these tests are SYNTHETIC and say so. The Apple split check reads the REAL
company facts of tests/fixtures/aapl_companyfacts_2012_2015.json.
"""

from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

from earnings import financials as fin
from earnings import label

FX = Path(__file__).parent / "fixtures"
# SYNTHETIC quarter ends, 13 of them, oldest first; c[0] is the quarter being announced.
ENDS = [date(2020 + (2 + 3 * i) // 12, (2 + 3 * i) % 12 + 1, 1) for i in range(14)]
ENDS = [(e.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1) for e in ENDS]
D_GAPS = [0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3]  # the 8 prior seasonal differences, newest first


def _series(diffs=D_GAPS, jump=0.5, base=(1.0, 1.1, 1.2, 1.3)):
    """EPS c[0..12], newest first, built so c[k] - c[k+4] = diffs[k-1] and c[0] - c[4] = jump."""
    c = [0.0] * 13
    c[9:13] = base
    for k in range(8, 0, -1):
        c[k] = c[k + 4] + diffs[k - 1]
    c[0] = c[4] + jump
    return c


def _versions(c, announced=None, lag=30):
    """One first-filed version per quarter. History is filed `lag` days after its quarter ends; the
    quarter being announced is filed 10 days after the announcement."""
    out = []
    ends = ENDS[-len(c) :]
    for i, value in enumerate(reversed(c)):
        end = ends[i]
        out.append(
            label.EpsVersion(
                end - timedelta(days=90),
                end,
                Decimal(str(round(value, 6))),
                end + timedelta(days=lag),
            )
        )
    return out


def _announcement(c):
    return ENDS[-1] + timedelta(days=25)


@pytest.mark.req("LB-01-AC1", "TH-11-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_sue_matches_a_hand_calculation_to_four_decimals():
    c = _series()
    versions = _versions(c)
    d = _announcement(c)
    # the quarter being announced is first filed after D
    versions[-1] = label.EpsVersion(
        versions[-1].period_start,
        versions[-1].period_end,
        versions[-1].value,
        d + timedelta(days=10),
    )
    result = label.compute_sue(versions, d)
    # by hand: mean of the 8 differences 0.2, sample variance 8 * 0.01 / 7, sd = 0.1069045;
    # the surprise is 0.5, so SUE = 0.5 / 0.1069045 = 4.6771
    assert result.sue is not None and abs(float(result.sue) - 4.6771) < 1e-4
    assert result.differences == 8 and result.reason is None
    assert result.information_date == versions[-2].filed  # latest EPS used, not the label value


@pytest.mark.req("LB-02-AC1", "TH-11-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_too_little_history_or_zero_variance_gives_an_unavailable_label_not_infinity():
    c = _series()
    d = _announcement(c)
    short = label.compute_sue(_versions(c[:10]), d)  # only 5 prior differences
    assert short.sue is None and short.reason == "fewer than 6 prior seasonal differences"
    six = label.compute_sue(_versions(c[:11]), d)  # exactly 6 prior differences: enough
    assert six.sue is not None and six.differences == 6
    flat = _series(diffs=[0.2] * 8)
    zero = label.compute_sue(_versions(flat), d)
    assert zero.sue is None and "zero" in zero.reason
    stale = label.compute_sue(
        _versions(c), ENDS[-1] + timedelta(days=200)
    )  # D far after the quarter
    assert stale.sue is None and "reporting window" in stale.reason
    assert "no quarterly EPS" in label.compute_sue([], d).reason  # data missing, not a short window
    gap = _versions(c)
    del gap[5]  # a missing quarter breaks the run of consecutive quarters
    assert label.compute_sue(gap, d).sue is None


@pytest.mark.req("LB-04-AC1", "IG-20-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_a_planted_restatement_or_future_filing_does_not_change_the_label():
    c = _series()
    d = _announcement(c)
    base = _versions(c)
    expected = label.compute_sue(base, d).sue
    prev = base[-5]  # the quarter a year before the one announced
    for filed in (d - timedelta(days=5), d, d + timedelta(days=40)):  # before, on, after D
        planted = [
            *base,
            label.EpsVersion(prev.period_start, prev.period_end, Decimal("9.99"), filed),
        ]
        assert label.compute_sue(planted, d).sue == expected  # the first-filed value is used
    # a quarter first filed on D or later is not history: the run is broken
    late = list(base)
    late[-2] = label.EpsVersion(late[-2].period_start, late[-2].period_end, late[-2].value, d)
    assert label.compute_sue(late, d).sue != expected
    # the gate itself fails the build when an input dated on or after D reaches the history
    with pytest.raises(label.LookaheadError):
        label.assert_inputs_before([d - timedelta(days=1), d], d)
    label.assert_inputs_before([d - timedelta(days=1)], d)


@pytest.mark.req("LB-05-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_a_split_inside_the_window_gives_the_same_sue_as_the_unsplit_series():
    c = _series()
    d = _announcement(c)
    unsplit = label.compute_sue(_versions(c), d)
    # SYNTHETIC 7-for-1 split: the 9 oldest quarters were first filed on the old basis (7 times the
    # new value); a later filing re-reports two of them on the new basis
    versions = _versions(c)
    split_filed = ENDS[-5] + timedelta(days=30)
    old = [v for v in versions if v.period_end <= ENDS[-6]]
    new = [v for v in versions if v.period_end > ENDS[-6]]
    scaled = [label.EpsVersion(v.period_start, v.period_end, v.value * 7, v.filed) for v in old]
    restated = [
        label.EpsVersion(v.period_start, v.period_end, v.value, split_filed) for v in old[-2:]
    ]
    result = label.compute_sue([*scaled, *new, *restated], d)
    assert result.sue is not None and abs(float(result.sue - unsplit.sue)) < 1e-4
    assert result.splits_applied > 0
    # without the re-reported quarters no split is known, and the surprise is false
    naive = label.compute_sue([*scaled, *new], d)
    assert naive.sue is None or abs(float(naive.sue - unsplit.sue)) > 0.5
    # one restated quarter alone is a restatement, not a split
    single = label.compute_sue([*scaled, *new, restated[0]], d)
    assert label.detect_splits([*scaled, *new, restated[0]], d) == []
    assert single.splits_applied == 0


@pytest.mark.req("LB-05-AC1")
@pytest.mark.code("src/earnings/label.py", "src/earnings/financials.py")
def test_the_real_apple_facts_show_the_seven_for_one_split_of_june_2014():
    rows = fin.eps_rows((FX / "aapl_companyfacts_2012_2015.json").read_bytes())
    versions = [
        label.EpsVersion(r.period_start, r.period_end, r.eps, r.filed, r.derived)
        for r in rows
        if r.period_kind == "quarter"
    ]
    assert label.detect_splits(versions, date(2014, 7, 23)) == []  # not known before it was filed
    splits = label.detect_splits(versions, date(2016, 1, 1))
    assert [round(s.ratio, 2) for s in splits] == [7.0]
    assert splits[0].known_from == date(2014, 7, 23) and splits[0].periods >= 2


@pytest.mark.req("CE-05-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_a_training_set_with_two_label_routes_fails():
    assert label.assert_one_route(["time-series", "time-series"]) == "time-series"
    with pytest.raises(label.MixedRouteError):
        label.assert_one_route(["time-series", "consensus"])
