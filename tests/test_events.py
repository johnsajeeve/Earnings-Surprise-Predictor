"""Earnings events, snapshots before the announcement, coverage and size reports
(Product FR-02, FR-14; Data LB-02, CE-05, TX-07; Ingestion IG-22; Database DB-06, DB-15).

Rows written here are SYNTHETIC. Each test says so where a value stands for a real one.
"""

from datetime import UTC, date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import text

from earnings import events as ev
from earnings import financials as fin
from earnings import label
from earnings import transcripts as tr

CO = "0000000001"
CO2 = "0000000002"
ENDS = [date(2020, 3, 31)]
for _ in range(15):
    y, m = ENDS[-1].year, ENDS[-1].month + 3
    y, m = (y + 1, m - 12) if m > 12 else (y, m)
    ENDS.append((date(y, m, 28) + timedelta(days=4)).replace(day=1) - timedelta(days=1))
GAPS = [0.1, 0.3, 0.1, 0.3, 0.1, 0.3, 0.1, 0.3]


def _values():
    c = [0.0] * 13
    c[9:13] = [1.0, 1.1, 1.2, 1.3]
    for k in range(8, 0, -1):
        c[k] = c[k + 4] + GAPS[k - 1]
    c[0] = c[4] + 0.5
    return c  # newest first


def _eps(engine, company, count=13, planted=None):
    """13 quarters ending ENDS[0..12]; each filed 30 days after it ends."""
    values = list(reversed(_values()))[-count:]
    with engine.begin() as conn:
        conn.execute(text("INSERT INTO company VALUES (:c, 'Synthetic')"), {"c": company})
        for end, value in zip(ENDS[13 - count : 13], values, strict=True):
            conn.execute(
                text(
                    "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
                    "eps_diluted, accession, filed_at) VALUES (:c, :s, :e, 'quarter', :v, :a, :f)"
                ),
                {"c": company, "s": end - timedelta(days=90), "e": end, "v": value,
                 "a": f"a-{end}", "f": end + timedelta(days=30)},
            )  # fmt: skip
        for end, value, filed in planted or []:
            conn.execute(
                text(
                    "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
                    "eps_diluted, accession, filed_at) VALUES (:c, :s, :e, 'quarter', :v, :a, :f)"
                ),
                {"c": company, "s": end - timedelta(days=90), "e": end, "v": value,
                 "a": f"restated-{filed}", "f": filed},
            )  # fmt: skip


def _transcript(engine, company, n, call_date, accession):
    with engine.begin() as conn:
        return conn.execute(
            text(
                "INSERT INTO transcript (company_id, ticker, call_date, source, source_ref, "
                "release_accession, release_accepted_at, raw_text, raw_hash, cleaned_text, "
                "cleaning_rules_version, turns, segmentation_status, boundary_turn) VALUES "
                "(:c, 'SYN', :d, 's', :r, :a, now(), 'text', :h, 'x', '1', '[]', 'ok', 1) "
                "RETURNING transcript_id"
            ),
            {"c": company, "d": call_date, "r": f"r{n}", "a": accession, "h": "a" * 64},
        ).scalar_one()


def _release(day, accession):
    return fin.Release(accession, day, datetime.combine(day, datetime.min.time(), UTC), "2.02")


@pytest.fixture
def engines(test_db):
    from earnings.db import get_engine

    return get_engine("worker"), get_engine("api")


def _fake_releases(monkeypatch, per_company):
    monkeypatch.setattr(tr, "_releases_for", lambda engine, cid: per_company.get(cid, []))


@pytest.mark.req("FR-02-AC1", "FR-02-AC2", "CE-05-AC1", "DB-06")
@pytest.mark.code("src/earnings/events.py", "src/earnings/migrations/versions")
def test_events_carry_three_dates_and_a_route_and_a_late_transcript_is_excluded(
    engines, monkeypatch
):
    worker, api = engines
    _eps(worker, CO)
    announce = ENDS[12] + timedelta(days=25)  # the quarter ENDS[12] is announced
    # SYNTHETIC: one call on the day, one four trading days later, one with no release
    t_ok = _transcript(worker, CO, 1, announce, "rel-1")
    t_late = _transcript(worker, CO, 2, announce + timedelta(days=6), "rel-2")
    t_none = _transcript(worker, CO, 3, announce, "rel-3")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1"), _release(announce, "rel-2")]})
    report = ev.build_events(worker)
    assert report["events"] == 3 and report["sue_ok"] == 2
    with api.connect() as conn:
        rows = {
            r[0]: r
            for r in conn.execute(
                text(
                    "SELECT transcript_id, sue, label_route, transcript_date, information_date, "
                    "announcement_date, status, exclusion_reason, incomplete, sue_reason FROM "
                    "earnings_event"
                )
            )
        }
    ok, late, none = rows[t_ok], rows[t_late], rows[t_none]
    assert abs(float(ok[1]) - 4.6771) < 1e-4 and ok[2] == "time-series"
    assert ok[3] and ok[4] and ok[5] and ok[6] == "included" and not ok[8]  # three dates, not null
    assert late[6] == "excluded" and "trading days after" in late[7]  # FR-02-AC2
    assert none[1] is None and none[8] and none[9] == "release not found"  # marked incomplete
    again = ev.build_events(worker)
    assert again["events"] == 3
    with api.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM earnings_event")).scalar_one() == 3


@pytest.mark.req("DB-06-AC1", "CE-05-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_the_event_table_refuses_missing_dates_unmarked_and_a_made_up_route(engines):
    from sqlalchemy.exc import DBAPIError

    worker, _ = engines
    _eps(worker, CO, count=1)
    tid = _transcript(worker, CO, 1, date(2024, 1, 5), "x")
    base = (
        "INSERT INTO earnings_event (company_id, transcript_id, release_accession, eps_basis, "
        "label_route, incomplete, status, transcript_date, information_date, announcement_date, "
        "sue, sue_reason) VALUES ('{c}', {t}, 'x', 'gaap-diluted', '{route}', {inc}, 'included', "
        "{td}, {idate}, {ad}, NULL, 'why')"
    )
    good = dict(c=CO, t=tid, route="time-series", inc="false", td="'2024-01-05'",
                idate="'2024-01-01'", ad="'2024-01-05'")  # fmt: skip
    for bad in (
        {**good, "idate": "NULL"},  # a missing date without the incomplete mark
        {**good, "route": "mixed"},  # a route that does not exist
    ):
        with pytest.raises(DBAPIError):
            with worker.begin() as conn:
                conn.execute(text(base.format(**bad)))
    with worker.begin() as conn:  # marked incomplete: allowed
        conn.execute(text(base.format(**{**good, "idate": "NULL", "inc": "true"})))


@pytest.mark.req("LB-04-AC1", "DB-09")
@pytest.mark.code("src/earnings/events.py", "src/earnings/label.py")
def test_the_label_agrees_with_the_database_as_of_rule_and_ignores_a_later_restatement(
    engines, monkeypatch
):
    worker, _ = engines
    announce = ENDS[12] + timedelta(days=25)
    # SYNTHETIC planted restatements of the quarter a year before: one filed before D, one after
    prev = ENDS[8]
    planted = [(prev, Decimal("9.99"), announce - timedelta(days=3)),
               (prev, Decimal("8.88"), announce + timedelta(days=30))]  # fmt: skip
    _eps(worker, CO, planted=planted)
    _transcript(worker, CO, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    ev.build_events(worker)
    with worker.connect() as conn:
        sue = conn.execute(text("SELECT sue FROM earnings_event")).scalar_one()
        first = {
            r[0]: r[1]
            for r in conn.execute(
                text("SELECT period_end, eps_diluted FROM eps_history_first_filed(:c, :d)"),
                {"c": CO, "d": announce},
            )
        }
    assert abs(float(sue) - 4.6771) < 1e-4  # the planted values did not change it
    versions = ev._versions(worker, CO)
    python_first = {
        e: v.value
        for (_, e), v in label.first_filed([v for v in versions if v.filed < announce]).items()
    }
    assert python_first == {k: v for k, v in first.items()}  # same rows as the SQL function


@pytest.mark.req("FR-14-AC2")
@pytest.mark.code("src/earnings/events.py")
def test_a_snapshot_captured_on_or_after_the_announcement_is_not_an_input(engines, monkeypatch):
    worker, _ = engines
    _eps(worker, CO)
    announce = ENDS[12] + timedelta(days=25)
    _transcript(worker, CO, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    ev.build_events(worker)
    # snapshots exist only from the capture start (2026), so move this event's announcement there
    at = datetime(2027, 3, 1, 21, 0, tzinfo=UTC)  # SYNTHETIC announcement moment
    with worker.begin() as conn:
        conn.execute(text("UPDATE earnings_event SET announcement_time_utc = :t"), {"t": at})
        for hours, mean, period in (
            (-30, 1.0, "a"),
            (-2, 2.0, "b"),
            (0, 3.0, "c"),
            (2, 4.0, "d"),
        ):
            conn.execute(
                text(
                    "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, "
                    "source, source_version, captured_at, raw_payload) VALUES "
                    "(:c, :m, :p, 'synthetic-test', 'x', :t, '{}')"
                ),
                {"c": CO, "m": mean, "p": period, "t": at + timedelta(hours=hours)},
            )
        event_id = conn.execute(text("SELECT event_id FROM earnings_event")).scalar_one()
    used = ev.event_snapshots(worker, event_id)
    assert sorted(float(s["mean_estimate"]) for s in used) == [1.0, 2.0]  # none on or after D


@pytest.mark.req("IG-22-AC1", "TX-07")
@pytest.mark.code("src/earnings/events.py")
def test_the_coverage_report_matches_a_hand_count_and_lists_what_is_missing(engines, monkeypatch):
    worker, _ = engines
    days1 = [date(2020, 2, 4), date(2020, 5, 5), date(2020, 8, 4), date(2020, 11, 3)]
    days2 = [date(2021, 2, 2), date(2021, 5, 4), date(2021, 8, 3)]
    with worker.begin() as conn:
        for cid, name, end in (
            (CO, "Stays", None),
            (CO2, "Leaves", date(2021, 6, 1)),
            ("0000000003", "Third", None),
            ("0000000004", "Fourth", None),
            ("0000000005", "Fifth", None),
        ):
            conn.execute(text("INSERT INTO company VALUES (:c, :n)"), {"c": cid, "n": name})
            conn.execute(
                text("INSERT INTO index_membership (company_id, valid_from, valid_to) "
                     "VALUES (:c, '2010-01-01', :e)"),
                {"c": cid, "e": end},
            )  # fmt: skip
    releases = {CO: [_release(d, f"s{i}") for i, d in enumerate(days1)],
                CO2: [_release(d, f"l{i}") for i, d in enumerate(days2)]}  # fmt: skip
    days3 = [date(2022, 2, 1), date(2022, 5, 3), date(2022, 8, 2), date(2022, 11, 1)]
    for cid in ("0000000003", "0000000004", "0000000005"):  # SYNTHETIC: 4 releases each in 2022
        releases[cid] = [_release(d, f"{cid}-{i}") for i, d in enumerate(days3)]
    _fake_releases(monkeypatch, releases)
    for cid, count in (("0000000003", 4), ("0000000004", 0), ("0000000005", 2)):
        for i in range(count):
            _transcript(worker, cid, i, days3[i], f"{cid}-{i}")
    for n, (cid, i) in enumerate([(CO, 0), (CO, 1), (CO, 3), (CO2, 0)]):  # 4 of 7 have transcripts
        _transcript(
            worker, cid, n, (days1 if cid == CO else days2)[i], f"{'s' if cid == CO else 'l'}{i}"
        )
    report = ev.coverage_report(worker)
    groups = report["by_year_and_group"]
    assert groups["2020 still in the index"] == {"releases": 4, "with_transcript": 3}
    assert groups["2021 left the index"] == {"releases": 2, "with_transcript": 1}
    # the third 2021 release (3 August) is after the company left on 1 June: not a target event
    # five companies: 2022 has 3 x 4 = 12 releases and 4 + 0 + 2 = 6 transcripts
    assert groups["2022 still in the index"] == {"releases": 12, "with_transcript": 6}
    assert report["missing_count"] == 2 + 6


@pytest.mark.req("DB-15-AC1")
@pytest.mark.code("src/earnings/events.py")
def test_the_size_report_keeps_measured_and_estimated_figures_apart(engines):
    worker, _ = engines
    report = ev.size_report(worker, companies=100)
    assert report["measured"]["database_bytes"] > 0
    assert report["estimated"]["database_bytes"] == int(report["measured"]["database_bytes"] * 5)
    assert "ESTIMATE" in report["estimated"]["method"]
    assert "estimated" not in report["measured"]


@pytest.mark.req("FR-14-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_a_new_snapshot_is_a_new_row_and_the_earlier_one_is_unchanged(engines):
    worker, _ = engines
    _eps(worker, CO, count=1)
    first = datetime(2027, 3, 1, 21, 0, tzinfo=UTC)  # SYNTHETIC capture times
    insert = (
        "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, source, "
        "source_version, captured_at, raw_payload) VALUES "
        "(:c, :m, '0q', 'synthetic-test', 'x', :t, '{}')"
    )
    with worker.begin() as conn:
        conn.execute(text(insert), {"c": CO, "m": 1.5, "t": first})
        before = conn.execute(text("SELECT * FROM estimate_snapshot")).all()
        conn.execute(text(insert), {"c": CO, "m": 1.7, "t": first + timedelta(days=1)})
        after = conn.execute(text("SELECT * FROM estimate_snapshot ORDER BY captured_at")).all()
    assert len(after) == 2 and after[0] == before[0]  # the earlier row is exactly as it was
    assert float(after[1].mean_estimate) == 1.7


@pytest.mark.req("PL-04-AC1", "DB-13-AC1", "DB-13-AC2")
@pytest.mark.code("src/earnings/events.py")
def test_short_history_is_rejected_with_its_reason_and_a_failed_build_leaves_whole_events_only(
    engines, monkeypatch
):
    worker, api = engines
    _eps(worker, CO)  # 13 quarters: enough
    _eps(worker, CO2, count=9)  # SYNTHETIC fixture with insufficient history
    announce = ENDS[12] + timedelta(days=25)
    for i, cid in enumerate((CO, CO2)):
        _transcript(worker, cid, i, announce, f"rel-{i}")
    _fake_releases(
        monkeypatch, {CO: [_release(announce, "rel-0")], CO2: [_release(announce, "rel-1")]}
    )
    real, calls = label.compute_sue, []

    def failing(versions, day):
        calls.append(1)
        if len(calls) == 2:
            raise RuntimeError("injected failure in the middle of the build")
        return real(versions, day)

    monkeypatch.setattr(label, "compute_sue", failing)
    with pytest.raises(RuntimeError):
        ev.build_events(worker)
    with api.connect() as conn:  # the first event is whole, the failed one left nothing behind
        assert conn.execute(text("SELECT count(*) FROM earnings_event")).scalar_one() == 1
    monkeypatch.setattr(label, "compute_sue", real)
    ev.build_events(worker)
    ev.build_events(worker)  # a second run changes nothing
    with api.connect() as conn:
        rows = conn.execute(
            text("SELECT company_id, sue, sue_reason FROM earnings_event ORDER BY company_id")
        ).all()
    assert len(rows) == 2
    assert rows[0][1] is not None and rows[1][1] is None
    assert rows[1][2] == "fewer than 6 prior seasonal differences"  # the logged reason
