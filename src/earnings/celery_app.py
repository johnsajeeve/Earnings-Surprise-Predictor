"""Celery application. Redis is the broker and the result store."""

from celery import Celery

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
)
