"""The time-series SUE (Data LB-01, LB-02, LB-04, LB-05, CE-05; Product FR-02; Ingestion IG-20).

Series built by hand in these tests are SYNTHETIC and say so. The Apple split check reads the REAL
company facts of tests/fixtures/aapl_companyfacts_2012_2015.json.
"""

import json
from datetime import date, timedelta
from decimal import Decimal
from pathlib import Path

import pytest

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


@pytest.mark.req("LB-02-AC1", "LB-02-AC2", "TH-11-AC1")
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
    # the real Realty Income case: the latest quarter in the data ended 121 days before D
    late = label.compute_sue(_versions(c), ENDS[-1] + timedelta(days=121))
    assert late.sue is None and "reporting window" in late.reason
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
    # SYNTHETIC 7-for-1 split: values first filed before it are 7 times the new basis
    versions = _versions(c)
    effective = ENDS[-5] + timedelta(days=45)
    scaled = [
        label.EpsVersion(v.period_start, v.period_end, v.value * 7, v.filed)
        if v.filed < effective
        else v
        for v in versions
    ]
    split = label.Split(Decimal("7"), effective)
    result = label.compute_sue(scaled, d, [split])
    assert result.sue is not None and abs(float(result.sue - unsplit.sue)) < 1e-4
    assert result.splits_applied > 0
    # without the dated factor the surprise is false
    naive = label.compute_sue(scaled, d)
    assert naive.sue is None or abs(float(naive.sue - unsplit.sue)) > 0.5
    # a factor that takes effect on or after D is not known at D and is not applied
    for later in (d, d + timedelta(days=1)):
        assert label.compute_sue(versions, d, [label.Split(Decimal("7"), later)]).sue == unsplit.sue


@pytest.mark.req("LB-05-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_the_real_apple_data_gives_the_two_dated_split_factors_once_each():
    splits = label.splits_from_facts((FX / "aapl_split_ratio_tag.json").read_bytes())
    # the tag repeats each split in several filings; each is applied once
    assert splits == [
        label.Split(Decimal("7"), date(2014, 6, 6)),
        label.Split(Decimal("4"), date(2020, 8, 28)),
    ]


def _tag(*facts):  # SYNTHETIC company facts holding only the split-ratio tag
    rows = [{"end": e, "val": v, "filed": f} for e, v, f in facts]
    return json.dumps({"facts": {"us-gaap": {label.SPLIT_TAG: {"units": {"pure": rows}}}}}).encode()


@pytest.mark.req("LB-05")
@pytest.mark.code("src/earnings/label.py")
def test_ratios_that_are_not_share_splits_are_ignored_and_repeats_are_merged():
    # Shapes seen in the real data: two end dates for one split, a share conversion at a listing
    # (5262.3512, 165582), a pre-listing ratio (3.8) and a nonsense value (10000)
    payload = _tag(
        ("2012-01-17", 2, "2014-04-01"), ("2012-01-28", 2, "2014-04-01"),
        ("2018-10-22", 2, "2018-12-04"), ("2019-02-02", 2, "2019-04-03"),
        ("2014-06-30", 5262.3512, "2014-09-05"), ("2014-08-22", 165582, "2014-11-14"),
        ("2011-12-20", 3.8, "2014-05-28"), ("2026-06-11", 10000, "2026-08-06"),
        ("2015-05-01", 1.5, "2015-08-01"),
    )  # fmt: skip
    assert [(str(s.ratio), str(s.effective)) for s in label.splits_from_facts(payload)] == [
        ("2", "2012-01-17"), ("1.5", "2015-05-01"), ("2", "2018-10-22")
    ]  # fmt: skip
    assert label.splits_from_facts(b'{"facts": {"us-gaap": {}}}') == []


@pytest.mark.req("LB-01")
@pytest.mark.code("src/earnings/label.py")
def test_when_the_announced_quarter_is_missing_the_previous_one_is_not_used_instead():
    c = _series()
    d = _announcement(c)
    versions = _versions(c)[:-1]  # the quarter being announced is not in the data
    # five days after quarter end: the previous quarter is still inside the reporting window
    result = label.compute_sue(versions, ENDS[-1] + timedelta(days=5))
    assert result.sue is None and result.reason == "the announced quarter is not in the stored EPS"
    # filed a few days before the release: still the announced quarter, and its filing is reported
    c_full = _versions(c)
    early = label.EpsVersion(
        c_full[-1].period_start, c_full[-1].period_end, c_full[-1].value, d - timedelta(days=3)
    )
    found = label.compute_sue([*c_full[:-1], early], d)
    assert found.sue is not None and found.target_filed == d - timedelta(days=3)


@pytest.mark.req("DV-04")
@pytest.mark.code("src/earnings/label.py")
def test_a_label_whose_inputs_hold_a_scale_error_is_marked():
    c = _series()
    d = _announcement(c)
    assert label.compute_sue(_versions(c), d).scale_suspect is False
    bad = _versions(c)
    bad[-6] = label.EpsVersion(  # SYNTHETIC: one quarter filed in thousandths of a unit too large
        bad[-6].period_start, bad[-6].period_end, bad[-6].value * 1_000_000, bad[-6].filed
    )
    assert label.compute_sue(bad, d).scale_suspect is True


@pytest.mark.req("CE-05-AC2", "SC-07-AC2")
@pytest.mark.code("src/earnings/label.py")
def test_a_training_set_with_two_label_routes_fails():
    assert label.assert_one_route(["time-series", "time-series"]) == "time-series"
    with pytest.raises(label.MixedRouteError):
        label.assert_one_route(["time-series", "consensus"])


@pytest.mark.req("LB-04-AC1")
@pytest.mark.code("src/earnings/label.py")
def test_a_quarter_refiled_with_a_shifted_start_date_is_still_the_same_quarter():
    # REAL pattern seen in the data (TJX and Adobe): a later filing reports the same quarter end
    # with a start date one day or one week different. The values here are SYNTHETIC.
    c = _series()
    d = _announcement(c)
    base = _versions(c)
    expected = label.compute_sue(base, d)
    prev = base[-5]
    shifted = label.EpsVersion(
        prev.period_start + timedelta(days=1), prev.period_end, Decimal("9.99"),
        prev.filed + timedelta(days=20),
    )  # fmt: skip
    result = label.compute_sue([*base, shifted], d)
    assert result.sue == expected.sue  # the first-filed value, not the later one
    assert len(label.first_filed([*base, shifted])) == len(base)  # one row per quarter end
