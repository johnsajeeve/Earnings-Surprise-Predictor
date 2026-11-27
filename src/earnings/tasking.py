"""Base class for queued tasks (Ingestion IG-01, IG-02, IG-03; Project-Wide EQ-07).

Every task is safe to run twice, so it is acknowledged only after it finishes and is run again if
its worker is lost. A failing task is retried three times with growing, jittered waits, and when
the retries are used up it is written to the dead-letter table (decision C-45).
"""

import hashlib
import json
from typing import Any

from celery import Task
from sqlalchemy import text

from earnings.db import get_engine

MAX_RETRIES = 3
BACKOFF_SECONDS = 30
BACKOFF_MAX_SECONDS = 300
# The Redis redelivery timeout is longer than any planned task (IG-04, decision C-45).
VISIBILITY_TIMEOUT_SECONDS = 4 * 60 * 60


def args_hash(args: Any, kwargs: Any) -> str:
    """A stable hash of a task's arguments. The arguments themselves are not stored."""
    blob = json.dumps([args, kwargs], sort_keys=True, default=str).encode()
    return hashlib.sha256(blob).hexdigest()


class IdempotentTask(Task):
    autoretry_for = (Exception,)
    retry_kwargs = {"max_retries": MAX_RETRIES}
    retry_backoff = BACKOFF_SECONDS
    retry_backoff_max = BACKOFF_MAX_SECONDS
    retry_jitter = True
    acks_late = True
    reject_on_worker_lost = True

    def on_failure(self, exc: Exception, task_id: str, args: Any, kwargs: Any, einfo: Any) -> None:
        """Called once, after the last retry has failed: write the dead-letter row."""
        with get_engine("worker").begin() as conn:
            run_id = conn.execute(
                text("SELECT max(run_id) FROM ingestion_run WHERE task_id = :t"), {"t": task_id}
            ).scalar_one()
            conn.execute(
                text(
                    "INSERT INTO dead_letter (task_name, args_hash, error_class, attempt_count, "
                    "run_id) VALUES (:name, :hash, :error, :attempts, :run)"
                ),
                {
                    "name": self.name,
                    "hash": args_hash(args, kwargs),
                    "error": type(exc).__name__,
                    "attempts": self.request.retries + 1,
                    "run": run_id,
                },
            )
