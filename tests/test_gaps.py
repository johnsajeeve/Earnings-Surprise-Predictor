"""Checks of the built waves that had no real test: scheduled jobs, capture-gap flags, killed
tasks, re-running stages, event documents, listed differences, the survivorship threshold and the
network guard (Ingestion IG-01, IG-05, IG-06, IG-12, IG-19; Data AE-01, SR-10, LB-03, VL-05;
Product NFR-03).

Rows written here are SYNTHETIC.
"""

import os
import signal
import socket
import subprocess
import sys
from datetime import UTC, date, datetime, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from conftest import ExternalNetworkBlocked
from earnings import events as ev
from earnings import pressrelease as pr
from earnings import validation as val
from test_events import CO, CO2, ENDS, _eps, _fake_releases, _release, _transcript

TESTS = Path(__file__).parent


@pytest.fixture
def engine(test_db):
    from earnings.db import get_engine

    return get_engine("worker")


@pytest.mark.req("IG-05-AC1", "NFR-03-AC1")
@pytest.mark.code("src/earnings/schedule.py", "src/earnings/tasks.py")
def test_the_schedule_file_lists_the_four_daily_jobs_with_the_approved_times():
    from earnings import schedule, tasks  # noqa: F401
    from earnings.celery_app import celery_app

    times = {name: (job["hour"], job["minute"]) for name, job in schedule.JOBS.items()}
    assert times == {
        "capture-consensus": (22, 30),
        "check-8k": (3, 30),
        "check-transcripts": (3, 45),
        "data-gates": (4, 15),
    }
    everything = schedule.beat_schedule(yahoo_collection=True)
    for name, job in schedule.JOBS.items():
        assert job["task"] in celery_app.tasks
        entry = everything[name]["schedule"]
        # every day: once in each 24 hours (NFR-03)
        assert len(entry.day_of_week) == 7 and len(entry.hour) == len(entry.minute) == 1


@pytest.mark.req("IG-05")
@pytest.mark.code("src/earnings/tasks.py")
def test_the_filing_check_stores_each_list_and_counts_only_new_earnings_releases(engine):
    import json

    from earnings import financials as fin
    from earnings import tasks
    from earnings.clients.edgar import RawResponse

    def listing(accessions):  # SYNTHETIC submissions payload
        n = len(accessions)
        return json.dumps({"filings": {"recent": {
            "form": ["8-K"] * n, "items": ["2.02"] * n, "accessionNumber": accessions,
            "filingDate": ["2024-05-02"] * n,
            "acceptanceDateTime": ["2024-05-02T20:30:00.000Z"] * n}}}).encode()  # fmt: skip

    pages = {CO: listing(["a-1"])}

    class Client:
        def get(self, url):
            for cid, body in pages.items():
                if url == fin.SUBMISSIONS_URL.format(cik=cid):
                    return RawResponse("sec-edgar", url, 200, "application/json", body,
                                       datetime.now(UTC))  # fmt: skip
            raise RuntimeError("no such company")

    first = tasks.new_releases(engine, Client(), [CO, CO2])
    assert first == {"checked": 1, "new": {}, "failed": [CO2]}  # nothing to compare with yet
    pages[CO] = listing(["a-2", "a-1"])
    second = tasks.new_releases(engine, Client(), [CO])
    assert second["new"] == {CO: ["a-2"]}


@pytest.mark.req("IG-06-AC1", "SR-10-AC2")
@pytest.mark.code("src/earnings/validation.py", "src/earnings/consensus.py")
def test_a_four_day_capture_gap_is_reported_and_the_events_in_it_are_flagged(engine):
    from earnings import consensus

    _eps(engine, CO, count=1)
    start = consensus.CAPTURE_START.date()
    insert = (
        "INSERT INTO estimate_snapshot (company_id, mean_estimate, period_label, source, "
        "source_version, captured_at, raw_payload) VALUES (:c, 1, '0q', 'synthetic', 'x', :t, '{}')"
    )
    with engine.begin() as conn:  # captures on day 0 and day 5: four days missing between them
        for offset in (0, 5):
            moment = datetime.combine(start + timedelta(days=offset), datetime.min.time(), UTC)
            conn.execute(text(insert), {"c": CO, "t": moment + timedelta(hours=23)})
        for n, offset in enumerate((0, 2, 5, 7)):  # announcement days
            tid = _transcript(engine, CO, n, start + timedelta(days=offset), f"g{n}")
            conn.execute(
                text(
                    "INSERT INTO earnings_event (company_id, transcript_id, release_accession, "
                    "eps_basis, label_route, incomplete, status, sue_reason, announcement_date) "
                    "VALUES (:c, :t, 'x', 'gaap-diluted', 'time-series', true, 'included', "
                    "'none', :d)"
                ),
                {"c": CO, "t": tid, "d": start + timedelta(days=offset)},
            )
    today = start + timedelta(days=6)
    assert [(g.days) for g in consensus.gaps(engine, today)] == [4]  # reported
    flagged = val.capture_gap_events(engine, today)
    with engine.connect() as conn:
        days = sorted(
            conn.execute(
                text("SELECT announcement_date FROM earnings_event WHERE event_id = ANY(:i)"),
                {"i": flagged},
            ).scalars()
        )
    # day 2 is inside the gap and day 5 is the day after it; days 0 and 7 are not affected
    assert days == [start + timedelta(days=2), start + timedelta(days=5)]


KILLED_TASK = """
import os, signal, sys
sys.path.insert(0, {tests!r})
from datetime import timedelta
from earnings import events as ev, label, transcripts as tr
from earnings.db import get_engine
from test_events import ENDS, _release
announce = ENDS[12] + timedelta(days=25)
releases = {{c: [_release(announce, f"rel-{{i}}")] for i, c in enumerate({companies!r})}}
tr._releases_for = lambda engine, cid: releases.get(cid, [])
real, calls = label.compute_sue, []
def killing(*a, **k):
    calls.append(1)
    if len(calls) == 2:
        os.kill(os.getpid(), signal.SIGKILL)  # the process dies with no clean-up
    return real(*a, **k)
label.compute_sue = killing
ev.build_events(get_engine("worker"))
"""


@pytest.mark.req("IG-01-AC2")
@pytest.mark.code("src/earnings/events.py")
def test_a_task_killed_halfway_and_run_again_gives_the_row_count_of_a_clean_run(
    engine, test_db, monkeypatch
):
    _eps(engine, CO)
    _eps(engine, CO2)
    announce = ENDS[12] + timedelta(days=25)
    for i, cid in enumerate((CO, CO2)):
        _transcript(engine, cid, i, announce, f"rel-{i}")
    script = KILLED_TASK.format(tests=str(TESTS), companies=[CO, CO2])
    src = str(Path(ev.__file__).resolve().parents[1])
    env = {**os.environ, "POSTGRES_DB": test_db, "PYTHONPATH": src}
    done = subprocess.run([sys.executable, "-c", script], env=env, capture_output=True, timeout=120)
    assert done.returncode == -signal.SIGKILL, done.stderr.decode()[-800:]
    count = text("SELECT count(*) FROM earnings_event")
    with engine.connect() as conn:
        assert conn.execute(count).scalar_one() == 1  # only the first event was written
    releases = {c: [_release(announce, f"rel-{i}")] for i, c in enumerate((CO, CO2))}
    _fake_releases(monkeypatch, releases)
    ev.build_events(engine)  # the restart
    with engine.connect() as conn:
        assert conn.execute(count).scalar_one() == 2  # the count of a clean run


@pytest.mark.req("IG-19-AC1")
@pytest.mark.code("src/earnings/transcripts.py", "src/earnings/events.py", "src/earnings/prices.py")
def test_running_the_transcript_event_price_and_gate_stages_again_changes_no_table(
    engine, tmp_path, monkeypatch
):
    import json

    from earnings import prices
    from earnings import transcripts as tr
    from earnings.clients import huggingface as hf
    from test_prices import _payload
    from test_transcripts import ROWS, _parquet

    monkeypatch.setattr(tr, "LAST_CALL_DATE", date(2026, 12, 31))
    monkeypatch.setattr(hf, "manifest", lambda path, downloaded: {"revision": hf.REVISION})
    _eps(engine, CO)
    announce = ENDS[12] + timedelta(days=25)
    with engine.begin() as conn:
        conn.execute(text("UPDATE company SET name = 'Northwind Widgets Inc.'"))
        conn.execute(
            text("INSERT INTO ticker_history (company_id, ticker, valid_from) "
                 "VALUES (:c, 'SYN', '2000-01-01')"), {"c": CO},
        )  # fmt: skip
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    row = {**ROWS["boundary_after_four_turns"], "symbol": "SYN", "year": 2023, "quarter": 2,
           "date": f"{announce} 17:00:00"}  # fmt: skip
    parquet = _parquet(tmp_path / "t.parquet", [row])
    body = _payload([(str(announce), 10), (str(announce + timedelta(days=1)), 11)])

    def run_all():
        tr.load_transcripts(engine, parquet, [CO])
        ev.build_events(engine)
        prices.store_prices(engine, CO, "SYN", body)
        val.run_checks(engine)

    def hashes():
        tables = ("transcript", "transcript_section", "earnings_event", "price_daily",
                  "adjustment_factor", "quarantine", "raw_payload")  # fmt: skip
        with engine.connect() as conn:
            return {
                t: sorted(
                    json.dumps(
                        {k: str(v) for k, v in r.items()
                         if k not in ("retrieved_at", "captured_at", "first_seen_at")},
                        sort_keys=True,
                    )
                    for r in conn.execute(text(f"SELECT * FROM {t}")).mappings()
                )
                for t in tables
            }  # fmt: skip

    run_all()
    first = hashes()
    assert len(first["transcript"]) == 1 and len(first["earnings_event"]) == 1
    run_all()
    assert hashes() == first


@pytest.mark.req("AE-01-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_every_labelled_event_has_its_document_announcement_date_and_eps_filing(
    engine, monkeypatch
):
    _eps(engine, CO)
    announce = ENDS[12] + timedelta(days=25)
    _transcript(engine, CO, 1, announce, "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    ev.build_events(engine)
    assert val.event_documents(engine) == {
        "labelled_events": 1, "no_document": 0, "no_announcement_date": 0, "no_eps_filing": 0,
    }  # fmt: skip
    with engine.begin() as conn:  # a planted event whose quarter has no EPS filing is counted
        conn.execute(text("UPDATE earnings_event SET period_end = '1999-01-01'"))
    assert val.event_documents(engine)["no_eps_filing"] == 1


@pytest.mark.req("LB-03-AC2", "TH-12")
@pytest.mark.code("src/earnings/pressrelease.py")
def test_the_derived_quarter_comparison_lists_every_difference_above_one_percent():
    def record(stored, press):  # SYNTHETIC comparison records
        return {"company_id": "x", "period_end": "2023-12-31", "result": "differ",
                "stored_eps": stored, "press_eps": press}  # fmt: skip

    report = pr.summary([record("6.09", "6.22"), record("1.23", "1.22")])  # 2.1% and 0.8%
    assert [d["press"] for d in report["differences_above_1pct"]] == ["6.22"]
    assert report["differences_above_1pct"][0]["relative_difference"] == pytest.approx(0.0213)
    assert pr.summary([record("1.00", "1.01")])["differences_above_1pct"] == []  # exactly 1%


@pytest.mark.req("TH-06-AC1", "VL-05-AC1")
@pytest.mark.code("src/earnings/validation.py")
def test_a_mean_gap_above_the_threshold_is_marked_for_investigation():
    def years(*gaps):  # SYNTHETIC yearly gaps
        return {i: {"gap_vs_RSP": g} for i, g in enumerate(gaps)}

    assert val.SURVIVORSHIP_THRESHOLD == 0.02 and val.SURVIVORSHIP_INDEX == "RSP"
    assert val.survivorship_flag(years(0.05, 0.02))["investigate"] is True
    assert val.survivorship_flag(years(-0.03, -0.02))["investigate"] is True  # either direction
    assert val.survivorship_flag(years(0.05, -0.04))["investigate"] is False  # not persistent
    assert val.survivorship_flag(years(0.02, 0.02))["investigate"] is False  # not above
    assert val.survivorship_flag({})["investigate"] is False


@pytest.mark.req("IG-12-AC1")
@pytest.mark.code("tests/conftest.py")
def test_the_whole_test_run_has_no_outside_network():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        with pytest.raises(ExternalNetworkBlocked):
            s.connect(("93.184.216.34", 443))  # a public address: refused before any packet
    for name in ("HTTP_PROXY", "HTTPS_PROXY"):
        assert os.environ[name] == "http://127.0.0.1:9"


def _runs(engine, job):
    with engine.connect() as conn:
        return (
            conn.execute(
                text("SELECT status FROM ingestion_run WHERE job_name = :j ORDER BY run_id"),
                {"j": job},
            )
            .scalars()
            .all()
        )


@pytest.mark.req("EQ-07", "IG-05")
@pytest.mark.code("src/earnings/tasks.py")
def test_the_filing_check_run_twice_stores_one_copy_and_finds_nothing_new(engine, monkeypatch):
    from earnings import tasks, universe
    from earnings.clients.edgar import RawResponse

    body = b'{"filings": {"recent": {"form": [], "items": [], "accessionNumber": []}}}'

    class Client:  # SYNTHETIC source
        def get(self, url):
            return RawResponse("sec-edgar", url, 200, "application/json", body, datetime.now(UTC))

    monkeypatch.setattr(tasks, "edgar_client", lambda: Client())
    monkeypatch.setattr(universe, "read_list", lambda path: ([{"company_id": CO}], {}))
    results = [tasks.check_new_filings.apply().get() for _ in range(2)]
    assert results[0] == results[1] == {"checked": 1, "new": {}, "failed": []}
    with engine.connect() as conn:
        assert conn.execute(text("SELECT count(*) FROM raw_payload")).scalar_one() == 1
    assert _runs(engine, "check-8k") == ["succeeded", "succeeded"]


@pytest.mark.req("EQ-07", "NFR-03")
@pytest.mark.code("src/earnings/tasks.py", "src/earnings/clients/huggingface.py")
def test_the_transcript_check_run_twice_changes_no_data(engine, monkeypatch):
    from earnings import tasks
    from earnings.clients import huggingface as hf

    monkeypatch.setattr(hf, "latest_revision", lambda session=None: "0" * 40)  # SYNTHETIC
    results = [tasks.check_new_transcripts.apply().get() for _ in range(2)]
    assert results[0] == results[1] and results[0]["new_revision"] is True
    with engine.connect() as conn:  # a new revision is reported, never loaded by itself
        assert conn.execute(text("SELECT count(*) FROM transcript")).scalar_one() == 0
    assert _runs(engine, "check-transcripts") == ["succeeded", "succeeded"]


@pytest.mark.req("EQ-07", "IG-05", "IG-06")
@pytest.mark.code("src/earnings/tasks.py", "src/earnings/validation.py")
def test_the_data_gates_run_twice_leave_the_same_rows(engine, monkeypatch):
    from earnings import tasks

    _eps(engine, CO)
    announce = ENDS[12] + timedelta(days=40)  # SYNTHETIC late call, so one row is quarantined
    _transcript(engine, CO, 1, announce + timedelta(days=7), "rel-1")
    _fake_releases(monkeypatch, {CO: [_release(announce, "rel-1")]})
    ev.build_events(engine)

    def rows():
        with engine.connect() as conn:
            return conn.execute(text("SELECT row_key, reason FROM quarantine ORDER BY 1, 2")).all()

    first_report = tasks.run_data_gates.apply().get()
    first = rows()
    second_report = tasks.run_data_gates.apply().get()
    assert first and rows() == first
    assert first_report["events_hash"] == second_report["events_hash"]
    assert second_report["quarantined_this_run"] == 0
    assert _runs(engine, "data-gates") == ["succeeded", "succeeded"]


@pytest.mark.req("VL-05-AC2")
@pytest.mark.code("src/earnings/validation.py")
def test_the_threshold_in_the_code_is_the_one_recorded_in_the_decision_log():
    from requirement_support import repo_path

    log = repo_path("docs/decision-log.md").read_text(encoding="utf-8")
    entry = next(line for line in log.splitlines() if line.startswith("| C-57 |"))
    assert "TH-06" in entry and "set from the first comparison run" in entry
    assert "before the validation set is read" in entry
    assert f"**{val.SURVIVORSHIP_THRESHOLD * 100:.1f} percentage points**" in entry
    assert val.SURVIVORSHIP_INDEX in entry
