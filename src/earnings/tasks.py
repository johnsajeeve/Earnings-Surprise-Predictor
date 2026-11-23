"""Celery tasks. Ingestion and feature tasks are added here in later steps."""

import logging
from typing import Any

from celery.signals import worker_ready
from sqlalchemy import text

from earnings import consensus
from earnings.celery_app import celery_app
from earnings.db import get_engine
from earnings.identifiers import canonical_cik


@celery_app.task(name="earnings.ping")
def ping() -> str:
    """Round-trip test: API to Redis to worker and back."""
    return "pong"


@celery_app.task(name="earnings.load_companies")
def load_companies(companies: list[list[str]]) -> int:
    """Write company rows as the worker role. Running it twice leaves the same rows
    (Project-Wide EQ-07). It fetches nothing from outside: the caller supplies the rows.

    Each item is [cik, name]. Returns the number of rows in the table after the load.
    """
    rows = [{"company_id": canonical_cik(cik), "name": name} for cik, name in companies]
    with get_engine("worker").begin() as conn:
        if rows:
            conn.execute(
                text(
                    "INSERT INTO company (company_id, name) VALUES (:company_id, :name) "
                    "ON CONFLICT (company_id) DO NOTHING"
                ),
                rows,
            )
        return int(conn.execute(text("SELECT count(*) FROM company")).scalar_one())


log = logging.getLogger(__name__)


@celery_app.task(name="earnings.capture_consensus")
def capture_consensus() -> dict[str, Any]:
    """Record today's consensus snapshot for each company in the capture list (Data SR-10).

    Safe to run twice in a day: a second run adds nothing (Project-Wide EQ-07).
    """
    result = consensus.capture_all(
        get_engine("worker"), consensus.load_universe(), pause=consensus._PAUSE_SECONDS
    )
    summary = {
        "captured": result.captured,
        "already_captured": result.already_captured,
        "failed": result.failed,
    }
    level = logging.ERROR if result.failed else logging.INFO
    log.log(level, "consensus capture: %s", summary)
    return summary


@worker_ready.connect
def catch_up_capture(**_: Any) -> None:
    """When the worker starts after the scheduled time, capture now if today has no snapshot."""
    try:
        if consensus.missing_today(get_engine("worker")):
            log.info("no consensus snapshot yet today, capturing now")
            capture_consensus.delay()
    except Exception:  # noqa: BLE001  a start-up check must never stop the worker
        log.exception("capture catch-up check failed")
