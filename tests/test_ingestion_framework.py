"""Task framework: run records, retries, dead letters, idempotence (Ingestion IG-01 to IG-04,
Product PL-01, PL-02, Project-Wide EQ-07).

Failures here are injected on purpose, and rows written by tests are synthetic.
"""

import re

import pytest
from sqlalchemy import text

from db_support import table_hash
from earnings import consensus, tasking
from earnings.celery_app import celery_app
from earnings.runlog import run_record
from earnings.tasking import IdempotentTask

CALLS: list[int] = []


@celery_app.task(base=IdempotentTask, bind=True, name="tests.always_fails")
def _always_fails(self, marker):
    CALLS.append(self.request.retries)
    raise ValueError("injected failure")


@celery_app.task(base=IdempotentTask, bind=True, name="tests.fails_once")
def _fails_once(self):
    CALLS.append(self.request.retries)
    if self.request.retries == 0:
        raise ValueError("injected failure")
    return "ok"


def _scalar(sql, **params):
    from earnings.db import get_engine

    with get_engine("api").connect() as conn:
        return conn.execute(text(sql), params).scalar_one()


@pytest.mark.req("IG-02-AC1", "PL-02-AC1")
@pytest.mark.code("src/earnings/tasking.py", "src/earnings/migrations/versions")
def test_an_injected_failure_gives_three_retries_and_one_dead_letter_row(test_db):
    CALLS.clear()
    result = _always_fails.apply(args=["synthetic"])
    assert result.failed()
    assert CALLS == [0, 1, 2, 3]  # the first run and three retries
    assert _scalar("SELECT count(*) FROM dead_letter") == 1
    from earnings.db import get_engine

    with get_engine("api").connect() as conn:
        row = conn.execute(
            text("SELECT task_name, args_hash, error_class, attempt_count FROM dead_letter")
        ).one()
    assert row.task_name == "tests.always_fails"
    assert re.fullmatch(r"[0-9a-f]{64}", row.args_hash)
    assert (row.error_class, row.attempt_count) == ("ValueError", 4)


@pytest.mark.req("IG-02")
@pytest.mark.code("src/earnings/tasking.py")
def test_a_task_that_recovers_leaves_no_dead_letter(test_db):
    CALLS.clear()
    result = _fails_once.apply()
    assert result.get() == "ok" and CALLS == [0, 1]
    assert _scalar("SELECT count(*) FROM dead_letter") == 0


@pytest.mark.req("IG-02")
@pytest.mark.code("src/earnings/tasking.py")
def test_retry_settings_and_late_acknowledgement_follow_decision_c_45():
    assert IdempotentTask.retry_kwargs == {"max_retries": 3}
    assert (IdempotentTask.retry_backoff, IdempotentTask.retry_backoff_max) == (30, 300)
    assert IdempotentTask.retry_jitter is True
    assert IdempotentTask.acks_late is True and IdempotentTask.reject_on_worker_lost is True
    assert tasking.args_hash([1], {"a": 2}) == tasking.args_hash([1], {"a": 2})
    assert tasking.args_hash([1], {}) != tasking.args_hash([2], {})


@pytest.mark.req("IG-04")
@pytest.mark.code("src/earnings/celery_app.py", "src/earnings/tasking.py")
def test_the_redis_redelivery_timeout_is_four_hours():
    assert celery_app.conf.broker_transport_options["visibility_timeout"] == 4 * 60 * 60


@pytest.mark.req("IG-03-AC1", "PL-01-AC1")
@pytest.mark.code("src/earnings/runlog.py", "src/earnings/migrations/versions")
def test_each_run_produces_a_queryable_row(test_db):
    from earnings.db import get_engine

    with run_record(get_engine("worker"), "synthetic-job", "synthetic-source", "t-1") as run:
        run.rows_read, run.rows_written = 5, 4
    with get_engine("api").connect() as conn:
        row = conn.execute(
            text(
                "SELECT job_name, source, status, rows_read, rows_written, error_class, "
                "ended_at IS NOT NULL AS ended FROM ingestion_run WHERE task_id = 't-1'"
            )
        ).one()
    assert tuple(row) == ("synthetic-job", "synthetic-source", "succeeded", 5, 4, None, True)


@pytest.mark.req("IG-03-AC2")
@pytest.mark.code("src/earnings/runlog.py")
def test_a_forced_error_gives_status_failed(test_db):
    from earnings.db import get_engine

    with pytest.raises(ValueError):
        with run_record(get_engine("worker"), "synthetic-job", "synthetic-source", "t-2"):
            raise ValueError("forced")
    with get_engine("api").connect() as conn:
        row = conn.execute(
            text("SELECT status, error_class FROM ingestion_run WHERE task_id = 't-2'")
        ).one()
    assert tuple(row) == ("failed", "ValueError")


@pytest.mark.req("IG-03")
@pytest.mark.code("src/earnings/runlog.py")
def test_a_run_that_reports_failure_with_zero_rows_is_not_a_success(test_db):
    from earnings.db import get_engine

    with run_record(get_engine("worker"), "synthetic-job", "synthetic-source", "t-3") as run:
        run.fail("every item failed")
    assert _scalar("SELECT status FROM ingestion_run WHERE task_id = 't-3'") == "failed"


@pytest.mark.req("IG-03", "SR-10")
@pytest.mark.code("src/earnings/tasks.py")
def test_capture_task_records_a_failed_run_when_every_company_fails(test_db, monkeypatch):
    from earnings import tasks

    monkeypatch.setattr(
        consensus,
        "capture_all",
        lambda *a, **k: consensus.CaptureResult(failed=["AAPL", "MSFT"]),
    )
    result = tasks.capture_consensus.apply()
    assert result.failed()
    assert _scalar("SELECT count(*) FROM ingestion_run WHERE status = 'failed'") == 4
    assert _scalar("SELECT count(*) FROM ingestion_run WHERE status = 'succeeded'") == 0
    assert _scalar("SELECT count(*) FROM dead_letter") == 1


@pytest.mark.req("IG-01-AC1")
@pytest.mark.code("src/earnings/tasks.py", "src/earnings/consensus.py")
def test_running_the_same_tasks_twice_gives_an_identical_table_hash(test_db, monkeypatch):
    from datetime import timedelta

    from earnings import tasks
    from earnings.db import get_engine

    synthetic = [["320193", "SYNTHETIC one"], ["789019", "SYNTHETIC two"]]
    now = consensus.CAPTURE_START + timedelta(days=1, hours=1)
    recorded = {
        "mean": 1.5, "low": 1.0, "high": 2.0, "count": 3, "basis": "gaap", "period": "0q",
        "version": "x", "payload": {"0q": {"avg": 1.5}},
    }  # fmt: skip
    universe = [("AAPL", "0000320193", "SYNTHETIC one")]

    def run():
        tasks.load_companies.apply(args=[synthetic]).get()
        consensus.capture_all(get_engine("worker"), universe, fetch=lambda _t: recorded, now=now)

    def state():
        with get_engine("api").connect() as conn:
            return (
                table_hash(conn, "company", ["company_id", "name"]),
                table_hash(
                    conn, "estimate_snapshot", ["company_id", "mean_estimate", "captured_at"]
                ),
            )

    run()
    first = state()
    run()
    assert state() == first


@pytest.mark.req("IG-05-AC2")
@pytest.mark.code("src/earnings/schedule.py", "src/earnings/celery_app.py")
def test_a_job_missing_from_the_schedule_file_does_not_run():
    from earnings import schedule

    scheduled = set(celery_app.conf.beat_schedule)
    assert scheduled == set(schedule.JOBS)  # the file is the only source of the schedule
    scheduled_tasks = {entry["task"] for entry in celery_app.conf.beat_schedule.values()}
    # Registered tasks that are not in the file are never scheduled, for example the backfill.
    for unlisted in ("earnings.fetch_company_facts", "earnings.load_companies", "earnings.ping"):
        assert unlisted in celery_app.tasks and unlisted not in scheduled_tasks


@pytest.mark.req("IG-05")
@pytest.mark.code("src/earnings/schedule.py")
def test_every_listed_job_has_a_utc_time_and_a_registered_task():
    from earnings import schedule, tasks  # noqa: F401  (importing tasks registers them)

    for name, job in schedule.JOBS.items():
        assert job["task"] in celery_app.tasks, name
        assert 0 <= job["hour"] < 24 and 0 <= job["minute"] < 60, name


@pytest.mark.req("IG-06")
@pytest.mark.code("src/earnings/runlog.py")
def test_a_job_with_no_success_for_more_than_three_days_is_reported(test_db):
    """Synthetic run rows. The flag on affected events comes with events (Wave 1.6)."""
    from datetime import UTC, datetime, timedelta

    from earnings.db import get_engine
    from earnings.runlog import late_jobs

    now = datetime(2026, 12, 1, 12, tzinfo=UTC)
    engine = get_engine("worker")

    def run_ended(days_ago, job="synthetic-job", status="succeeded"):
        with engine.begin() as conn:
            conn.execute(
                text(
                    "INSERT INTO ingestion_run (job_name, source, status, started_at, ended_at) "
                    "VALUES (:j, 's', :st, :t, :t)"
                ),
                {"j": job, "st": status, "t": now - timedelta(days=days_ago)},
            )

    assert late_jobs(engine, ["synthetic-job"], now=now) == []  # never ran, nothing scheduled yet
    assert late_jobs(engine, ["synthetic-job"], now=now, since=now - timedelta(days=2)) == []
    run_ended(2.9)
    assert late_jobs(engine, ["synthetic-job"], now=now) == []
    run_ended(0, status="failed")  # a failed run does not count as a success
    # Last success was 2.9 days before `now`. At now + 0.05 days it is 2.95 days: not late yet.
    assert late_jobs(engine, ["synthetic-job"], now=now + timedelta(days=0.05)) == []
    # At now + 0.2 days it is 3.1 days (more than 3), and the later failed run does not help.
    assert late_jobs(engine, ["synthetic-job"], now=now + timedelta(days=0.2)) == ["synthetic-job"]
    assert late_jobs(engine, ["never-ran"], now=now, since=now - timedelta(days=4)) == ["never-ran"]
