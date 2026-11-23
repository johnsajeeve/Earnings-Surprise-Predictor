"""Run records for scheduled and queued jobs (Ingestion IG-03, IG-06; Product PL-01)."""

from collections.abc import Iterator
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta

from sqlalchemy import Engine, text

# A scheduled job that has not succeeded for more than this many days is reported (IG-06).
LATE_AFTER_DAYS = 3


@dataclass
class RunHandle:
    run_id: int
    rows_read: int = 0
    rows_written: int = 0
    failure: str | None = None

    def fail(self, reason: str) -> None:
        """Mark the run failed without raising, for example when every item failed."""
        self.failure = reason


@contextmanager
def run_record(
    engine: Engine, job_name: str, source: str, task_id: str | None = None
) -> Iterator[RunHandle]:
    """Write a run row at the start and finish it at the end.

    The run is `failed` if the block raises or calls `fail()`. It is never recorded as succeeded
    when it ended in an error, even if it wrote no rows (IG-03).
    """
    with engine.begin() as conn:
        run_id = conn.execute(
            text(
                "INSERT INTO ingestion_run (job_name, source, status, task_id) "
                "VALUES (:job, :source, 'running', :task) RETURNING run_id"
            ),
            {"job": job_name, "source": source, "task": task_id},
        ).scalar_one()
    handle = RunHandle(run_id)
    error: str | None = None
    try:
        yield handle
    except BaseException as exc:
        error = type(exc).__name__
        raise
    finally:
        error = error or handle.failure
        with engine.begin() as conn:
            conn.execute(
                text(
                    "UPDATE ingestion_run SET ended_at = now(), status = :status, "
                    "rows_read = :read, rows_written = :written, error_class = :error "
                    "WHERE run_id = :id"
                ),
                {
                    "status": "failed" if error else "succeeded",
                    "read": handle.rows_read,
                    "written": handle.rows_written,
                    "error": error,
                    "id": run_id,
                },
            )


def late_jobs(
    engine: Engine, jobs: list[str], now: datetime | None = None, since: datetime | None = None
) -> list[str]:
    """Scheduled jobs with no successful run in the last LATE_AFTER_DAYS days (IG-06).

    `since` is when scheduling began, so a job is not late before it could have run.
    """
    moment = now or datetime.now(UTC)
    late = []
    with engine.connect() as conn:
        for job in jobs:
            last = conn.execute(
                text(
                    "SELECT max(ended_at) FROM ingestion_run "
                    "WHERE job_name = :job AND status = 'succeeded'"
                ),
                {"job": job},
            ).scalar_one()
            reference = last or since
            if reference is not None and moment - reference > timedelta(days=LATE_AFTER_DAYS):
                late.append(job)
    return late


if __name__ == "__main__":
    from earnings.consensus import CAPTURE_START
    from earnings.db import get_engine
    from earnings.schedule import JOBS

    stale = late_jobs(get_engine("api"), list(JOBS), since=CAPTURE_START)
    print("late jobs:", ", ".join(stale) if stale else "none")
