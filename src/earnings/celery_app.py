"""Celery application. Redis is the broker and the result store."""

from celery import Celery

from earnings.config import get_settings
from earnings.schedule import beat_schedule
from earnings.tasking import VISIBILITY_TIMEOUT_SECONDS

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
    # A task that runs longer than this would be delivered a second time (Ingestion IG-04).
    broker_transport_options={"visibility_timeout": VISIBILITY_TIMEOUT_SECONDS},
    # Scheduled jobs: only those listed in earnings/schedule.py run (Ingestion IG-05).
    # Beat is embedded in the worker (docker-compose.yml).
    beat_schedule=beat_schedule(_settings.yahoo_collection),
)
