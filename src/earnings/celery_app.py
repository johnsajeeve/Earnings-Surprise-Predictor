"""Celery application. Redis is the broker and the result store."""

from celery import Celery
from celery.schedules import crontab

from earnings.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "earnings",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
    include=["earnings.tasks"],
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    # Retry the broker connection at start-up instead of exiting if Redis is slow.
    broker_connection_retry_on_startup=True,
    # Scheduled jobs (Ingestion IG-05). Run at 22:30 UTC, after the US close in summer and winter
    # (decision C-44 and the D-45 run-time value). Embedded beat in the worker (docker-compose.yml).
    beat_schedule={
        "capture-consensus": {
            "task": "earnings.capture_consensus",
            "schedule": crontab(hour=22, minute=30),
        },
    },
)
