"""Celery tasks. Ingestion and feature tasks are added here in later steps."""

from sqlalchemy import text

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
