"""Dataset validation checks (Data DV-01 to DV-08, CE-01, TH-01, TH-15, AE-03, VL-01; DB-14).

Rows written here are SYNTHETIC unless a test says it reads real data.
"""

from datetime import UTC, date, datetime, timedelta

import pytest
from sqlalchemy import text
from sqlalchemy.exc import DBAPIError

from earnings import events as ev
from earnings import validation as val
from test_events import CO, ENDS, _eps, _fake_releases, _release, _transcript


@pytest.fixture
def engines(test_db):
    from earnings.db import get_engine

    return get_engine("worker"), get_engine("api")


def _event(engine, cid, n, *, ann, period_end, sue="1.0", info=None, call=None, status="included"):
    """SYNTHETIC event row written directly."""
    tid = _transcript(engine, cid, n, call or ann, f"acc-{cid}-{n}")
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO earnings_event (company_id, transcript_id, "
                "period_end, transcript_date, information_date, announcement_date, "
                "announcement_time_utc, release_accession, "
                "eps_basis, label_route, sue, sue_reason, incomplete, status, exclusion_reason) "
                "VALUES (:c, :t, :pe, :td, :i, :a, :at, 'x', 'gaap-diluted', 'time-series', :s, "
                ":r, :inc, :st, :ex)"
            ),
            {"c": cid, "t": tid, "pe": period_end, "td": call or ann,
             "i": info if info is not None else ann - timedelta(days=30), "a": ann,
             "at": datetime.combine(ann, datetime.min.time(), UTC),
             "s": sue, "r": None if sue is not None else "why", "inc": info is None and sue is None,
             "st": status, "ex": "late call" if status == "excluded" else None},
        )  # fmt: skip
    return tid


@pytest.mark.req("DV-06-AC1", "FD-04-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_fiscal_periods_map_to_calendar_quarters_for_five_non_calendar_companies(engines):
    worker, _ = engines
    assert val.calendar_quarter(date(2021, 11, 1), date(2022, 1, 31)) == (2021, 4)  # retail quarter
    assert val.calendar_quarter(date(2021, 9, 26), date(2021, 12, 25)) == (2021, 4)
    assert val.calendar_quarter(date(2021, 12, 27), date(2022, 3, 26)) == (2022, 1)  # 52-week year
    # SYNTHETIC companies with fiscal years ending in January, March, May, June and September
    ends = {"0000000011": 1, "0000000012": 3, "0000000013": 5, "0000000014": 6, "0000000015": 9}
    with worker.begin() as conn:
        for cid, month in ends.items():
            conn.execute(text("INSERT INTO company VALUES (:c, 'Synthetic')"), {"c": cid})
            for i in range(16):  # four fiscal years of quarters
                total = 2018 * 12 + month - 1 + 3 * i
                end = date(total // 12, total % 12 + 1, 28)
                start = end - timedelta(days=89)
                conn.execute(
                    text(
                        "INSERT INTO eps_history (company_id, period_start, period_end, "
                        "period_kind, eps_diluted, accession, filed_at) VALUES "
                        "(:c, :s, :e, 'quarter', 1, :a, :f)"
                    ),
                    {"c": cid, "s": start, "e": end, "a": f"a{i}", "f": end + timedelta(days=30)},
                )
    for cid in ends:
        result = val.fiscal_mapping(worker, cid)
        assert result["sound"] and result["gaps"] == [] and result["periods"] == 16
    assert {val.fiscal_year_end_month(worker, c) for c in ends} == {
        None
    }  # no year rows stored here
    # a planted fault: two fiscal quarters that land in one calendar quarter is unsound
    with worker.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
                "eps_diluted, accession, filed_at) VALUES ('0000000011', '2018-02-20', "
                "'2018-03-27', 'quarter', 1, 'dup', '2018-05-01')"
            )
        )
    assert not val.fiscal_mapping(worker, "0000000011")["sound"]


@pytest.mark.req("DV-03-AC1", "TX-05-AC2")
@pytest.mark.code("src/earnings/migrations/versions", "src/earnings/validation.py")
def test_an_event_is_unique_on_company_quarter_and_announcement_date(engines):
    worker, _ = engines
    _eps(worker, CO, count=1)
    _event(worker, CO, 1, ann=date(2024, 5, 2), period_end=date(2024, 3, 31))
    with pytest.raises(DBAPIError):
        _event(worker, CO, 2, ann=date(2024, 5, 2), period_end=date(2024, 3, 31))
    _event(
        worker, CO, 3, ann=date(2024, 8, 1), period_end=date(2024, 6, 30)
    )  # another quarter: fine
    assert val.duplicate_events(worker) == []


@pytest.mark.req("DV-02-AC1", "TH-15-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_the_three_date_fields_have_no_nulls_in_usable_events_and_gaps_are_counted_apart(engines):
    worker, _ = engines
    _eps(worker, CO, count=1)
    _event(worker, CO, 1, ann=date(2024, 5, 2), period_end=date(2024, 3, 31))
    _event(worker, CO, 2, ann=date(2024, 8, 1), period_end=date(2024, 6, 30), sue=None, info=None)
    rates = val.null_rates(worker)
    assert rates["events"] == 2 and rates["usable_events"] == 1 and rates["incomplete_events"] == 1
    assert rates["nulls_in_usable_events"] == {f: 0 for f in val.DATE_FIELDS}
    assert all(r == 0 for r in rates["null_rate_usable"].values())


@pytest.mark.req("DV-05-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_date_order_violations_are_listed_and_a_call_before_the_release_is_a_stated_conflict(
    engines,
):
    worker, _ = engines
    _eps(worker, CO, count=1)
    ann = date(2024, 5, 2)
    _event(worker, CO, 1, ann=ann, period_end=date(2024, 3, 31))
    _event(
        worker, CO, 2, ann=date(2024, 8, 1), period_end=date(2024, 6, 30), call=date(2024, 7, 31)
    )
    _event(
        worker, CO, 3, ann=date(2024, 11, 1), period_end=date(2024, 9, 30), info=date(2024, 11, 2)
    )
    # the information date on the day of the announcement is also too late
    _event(
        worker, CO, 4, ann=date(2025, 2, 1), period_end=date(2024, 12, 31), info=date(2025, 2, 1)
    )
    order = val.date_order_violations(worker)
    assert len(order["call_before_announcement"]) == 1  # C-17 allows it; DV-05 text does not
    assert len(order["information_not_before_announcement"]) == 2  # real errors


@pytest.mark.req("DV-01-AC1", "DV-04-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_failing_rows_are_quarantined_once_and_kept_and_extreme_values_need_a_threshold(engines):
    worker, api = engines
    _eps(worker, CO, count=1)
    _event(worker, CO, 1, ann=date(2024, 5, 2), period_end=date(2024, 3, 31), sue="50")
    _event(worker, CO, 2, ann=date(2024, 8, 1), period_end=date(2024, 6, 30), status="excluded")
    first = val.run_checks(worker)
    second = val.run_checks(worker)
    assert first["quarantined_this_run"] == 1 and second["quarantined_this_run"] == 0
    with api.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM quarantine")).scalar_one() == 1
        assert conn.execute(text("SELECT count(*) FROM earnings_event")).scalar_one() == 2  # kept
    assert [e[2] for e in val.extreme_events(worker, 10.0)] == [50.0]
    with pytest.raises(TypeError):
        val.extreme_events(worker)  # type: ignore[call-arg]
    # SYNTHETIC scale error of the kind found in the real data (DR-27): quarantined, not removed
    _event(worker, CO, 3, ann=date(2024, 11, 1), period_end=date(2024, 9, 30), sue="1828351.4")
    third = val.run_checks(worker)
    assert third["quarantined_this_run"] == 1
    assert third["quarantine_by_reason"]["sue above one million in size"] == 1


@pytest.mark.req("DV-01", "DV-04")
@pytest.mark.code("src/earnings/validation.py")
def test_every_label_built_on_a_scaled_value_is_flagged_not_only_the_giant_ones(
    engines, monkeypatch
):
    worker, api = engines
    _eps(worker, CO)
    with worker.begin() as conn:  # SYNTHETIC: a company whose history holds one scaled quarter
        conn.execute(
            text(
                "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
                "eps_diluted, accession, filed_at) VALUES (:c, :s, :e, 'quarter', 1500000, "
                "'scaled', :f)"
            ),
            {"c": CO, "s": ENDS[7] - timedelta(days=90), "e": ENDS[7],
             "f": ENDS[7] + timedelta(days=20)},
        )  # fmt: skip
    ann = ENDS[12] + timedelta(days=25)
    second = ann + timedelta(days=2)
    _transcript(worker, CO, 1, ann, "rel-1")
    _transcript(worker, CO, 2, second, "rel-2")  # two flagged events: each is counted once
    _fake_releases(monkeypatch, {CO: [_release(ann, "rel-1"), _release(second, "rel-2")]})
    ev.build_events(worker)
    report = val.run_checks(worker)
    assert report["quarantine_by_reason"]["label inputs hold a scale error in the source EPS"] == 2
    with api.connect() as conn:  # flagged, and the label itself is left as computed
        assert conn.execute(text("SELECT count(*) FROM earnings_event")).scalar_one() == 2


@pytest.mark.req("DV-08-AC1")
@pytest.mark.code("src/earnings/validation.py", "src/earnings/events.py")
def test_building_events_twice_from_the_same_rows_gives_the_same_table_hash(
    engines, test_db, monkeypatch
):
    import os

    import psycopg

    worker, _ = engines
    _eps(worker, CO)
    ann = ENDS[12] + timedelta(days=25)
    _transcript(worker, CO, 1, ann, "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(ann, "rel-1")]})
    ev.build_events(worker)
    first = val.events_hash(worker)
    with psycopg.connect(  # the owner empties the table: a rebuild from nothing gets new event ids
        host=os.environ["POSTGRES_HOST"], user=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"], dbname=test_db, autocommit=True,
    ) as admin:  # fmt: skip
        admin.execute("DELETE FROM earnings_event")
    ev.build_events(worker)
    assert val.events_hash(worker) == first
    with worker.begin() as conn:
        conn.execute(text("UPDATE earnings_event SET sue = sue + 1"))
    assert val.events_hash(worker) != first  # the hash does notice a change


@pytest.mark.req("CE-01-AC1", "VL-01-AC1", "VL-01-AC2", "CE-02-AC1")
@pytest.mark.code("src/earnings/validation.py", "src/earnings/events.py")
def test_a_planted_snapshot_captured_after_the_announcement_never_reaches_an_event(engines):
    worker, _ = engines
    _eps(worker, CO, count=1)
    ann = date(2027, 3, 1)  # snapshots exist only from the capture start in 2026
    _event(worker, CO, 1, ann=ann, period_end=date(2026, 12, 31))
    at = datetime.combine(ann, datetime.min.time(), UTC)
    with worker.begin() as conn:
        for label, offset in (("before", -26), ("after", 24)):  # SYNTHETIC; "after" is the plant
            conn.execute(
                text(
                    "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, "
                    "source, source_version, captured_at, raw_payload) VALUES "
                    "(:c, 1, :p, 'synthetic-test', 'x', :t, '{}')"
                ),
                {"c": CO, "p": label, "t": at + timedelta(hours=offset)},
            )
    assert val.capture_after_announcement(worker) == 0
    with worker.connect() as conn:
        event_id = conn.execute(text("SELECT event_id FROM earnings_event")).scalar_one()
    assert [s["period_label"] for s in ev.event_snapshots(worker, event_id)] == ["before"]


@pytest.mark.req("TX-04-AC1", "TH-01-AC1", "TX-07-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_the_coverage_gate_reports_a_miss_and_keeps_the_threshold(engines):
    cov = {  # SYNTHETIC coverage table
        "by_year_and_group": {
            "2020 still in the index": {"releases": 100, "with_transcript": 95},
            "2020 left the index": {"releases": 50, "with_transcript": 25},
        }
    }
    cov["by_year_and_group"]["2014 still in the index"] = {"releases": 900, "with_transcript": 0}
    gate = val.coverage_gate(cov)  # TX-04: the target events are 2015 to 2024, so 2014 is outside
    assert gate["share"] == pytest.approx(120 / 150) and gate["met"] is False
    assert gate["threshold"] == 0.90  # the miss is stated, the threshold is not moved
    assert gate["by_group"]["left the index"]["share"] == 0.5
    cov["by_year_and_group"]["2020 left the index"] = {"releases": 50, "with_transcript": 50}
    assert val.coverage_gate(cov)["met"] is True
    cov["by_year_and_group"] = {"2020 still in the index": {"releases": 10, "with_transcript": 9}}
    assert val.coverage_gate(cov)["met"] is True  # exactly 90% meets "at least 90%"


@pytest.mark.req("AE-03-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_the_dataset_has_one_eps_basis(engines):
    worker, _ = engines
    _eps(worker, CO, count=1)
    _event(worker, CO, 1, ann=date(2024, 5, 2), period_end=date(2024, 3, 31))
    assert val.basis_values(worker) == ["gaap-diluted"]


@pytest.mark.req("DB-14-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_the_plans_of_the_ticker_and_event_lookups_use_an_index(engines):
    worker, _ = engines
    _eps(worker, CO, count=1)
    with worker.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO ticker_history (company_id, ticker, valid_from) "
                "VALUES (:c, 'SYN', '2000-01-01')"
            ),
            {"c": CO},
        )
        conn.execute(text("SET LOCAL enable_seqscan = off"))  # tiny tables: ask what is possible
        ticker = "\n".join(
            r[0] for r in conn.execute(text(
                "EXPLAIN SELECT company_id FROM ticker_history WHERE ticker = 'SYN' "
                "AND valid_from <= '2024-01-01' AND (valid_to IS NULL OR valid_to > '2024-01-01')"
            ))
        )  # fmt: skip
        event = "\n".join(
            r[0] for r in conn.execute(text(
                "EXPLAIN SELECT * FROM earnings_event WHERE company_id = 'x' "
                "AND period_end = '2024-03-31'"
            ))
        )  # fmt: skip
    assert "Index" in ticker and "Seq Scan" not in ticker
    assert "Index" in event and "Seq Scan" not in event


@pytest.mark.req("VL-09-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_the_hand_audit_sheet_draws_the_same_events_every_time_without_repeats(engines, tmp_path):
    worker, _ = engines
    _eps(worker, CO, count=1)
    for i in range(8):  # SYNTHETIC usable events
        _event(worker, CO, i, ann=date(2020, 1, 1 + i), period_end=date(2019, 9, 30) + timedelta(i))
    one = val.audit_sheet(worker, 5, 2036, tmp_path / "a.md")
    two = val.audit_sheet(worker, 5, 2036, tmp_path / "b.md")
    assert one == two and len(set(one)) == 5
    sheet = (tmp_path / "a.md").read_text("utf-8")
    assert sheet.count("Verdict ->") == 5 and "https://www.sec.gov/Archives/edgar/data/1/" in sheet


@pytest.mark.req("GS-02-AC1")
@pytest.mark.code("src/earnings/datacard.py")
def test_the_data_card_states_coverage_sources_gaps_and_that_it_is_not_signed_off(engines):
    from earnings import datacard

    worker, _ = engines
    _eps(worker, CO, count=1)
    _event(worker, CO, 1, ann=date(2024, 5, 2), period_end=date(2024, 3, 31))
    _event(worker, CO, 2, ann=date(2024, 8, 1), period_end=date(2024, 6, 30), sue=None, info=None)
    card = datacard.build(worker, "test-1", ["143 events have no EPS"])
    assert "Events: 2 (1 usable" in card and "2024-05-02 to 2024-08-01" in card
    assert "Label route: time-series; EPS basis: gaap-diluted" in card
    assert "SEC EDGAR" in card and "Licence:" in card and "143 events have no EPS" in card
    assert "Not signed off" in card
