"""Celery tasks. Ingestion and feature tasks are added here in later steps."""

from earnings.celery_app import celery_app


@celery_app.task(name="earnings.ping")
def ping() -> str:
    """Round-trip test: API to Redis to worker and back."""
    return "pong"
