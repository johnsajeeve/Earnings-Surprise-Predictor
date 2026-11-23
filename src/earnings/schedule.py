"""Every scheduled job, with its time, in one place (Ingestion IG-05, decision C-45).

A job that is not listed here does not run on a schedule. Times are UTC. Backfill is started by
hand and is never listed. The other initial jobs of IG-05 (the daily check for new transcripts,
the daily check for new 8-K Item 2.02 filings, the daily run of the data gates) are added in the
step that builds each one, with the run time John approves under D-45.
"""

from typing import Any

from celery.schedules import crontab

# name -> {"task": registered task name, "hour": UTC hour, "minute": UTC minute}
JOBS: dict[str, dict[str, Any]] = {
    # After the US close in summer and winter (decision C-44, D-45 run time).
    "capture-consensus": {"task": "earnings.capture_consensus", "hour": 22, "minute": 30},
}


def beat_schedule() -> dict[str, dict[str, Any]]:
    """The schedule in the form Celery beat reads."""
    return {
        name: {"task": job["task"], "schedule": crontab(hour=job["hour"], minute=job["minute"])}
        for name, job in JOBS.items()
    }
