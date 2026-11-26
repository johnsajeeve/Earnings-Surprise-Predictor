"""Every scheduled job, with its time, in one place (Ingestion IG-05, decision C-45).

A job that is not listed here does not run on a schedule. Times are UTC and were approved by John
(C-46 for the capture, C-56 for the other three). Backfill is started by hand and is never listed.
"""

from typing import Any

from celery.schedules import crontab

# name -> {"task": registered task name, "hour": UTC hour, "minute": UTC minute}
JOBS: dict[str, dict[str, Any]] = {
    # After the US close in summer and winter. 22:30 UTC was approved by John on 23 Nov 2026 as the
    # D-45 run-time value for this job (decision C-46).
    "capture-consensus": {"task": "earnings.capture_consensus", "hour": 22, "minute": 30},
    # EDGAR accepts filings until 22:00 Eastern, which is 02:00 or 03:00 UTC.
    "check-8k": {"task": "earnings.check_new_filings", "hour": 3, "minute": 30},
    "check-transcripts": {"task": "earnings.check_new_transcripts", "hour": 3, "minute": 45},
    "data-gates": {"task": "earnings.run_data_gates", "hour": 4, "minute": 15},
}


def beat_schedule() -> dict[str, dict[str, Any]]:
    """The schedule in the form Celery beat reads."""
    return {
        name: {"task": job["task"], "schedule": crontab(hour=job["hour"], minute=job["minute"])}
        for name, job in JOBS.items()
    }
