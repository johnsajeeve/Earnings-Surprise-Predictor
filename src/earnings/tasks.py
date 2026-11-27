"""Celery tasks. Ingestion and feature tasks are added here in later steps."""

import logging
from pathlib import Path
from typing import Any

import redis
from celery.signals import worker_ready
from sqlalchemy import text

from earnings import consensus, universe, validation
from earnings import financials as fin
from earnings.celery_app import celery_app
from earnings.clients import huggingface
from earnings.clients.edgar import (
    MAX_REQUESTS_PER_SECOND,
    EdgarClient,
)
from earnings.clients.edgar import (
    SOURCE as EDGAR_SOURCE,
)
from earnings.config import get_settings
from earnings.db import get_engine
from earnings.identifiers import canonical_cik
from earnings.limits import RedisSlidingWindowLimiter
from earnings.rawstore import latest_payload, store_payload
from earnings.runlog import late_jobs, run_record
from earnings.schedule import JOBS
from earnings.tasking import IdempotentTask

log = logging.getLogger(__name__)


@celery_app.task(name="earnings.ping")
def ping() -> str:
    """Round-trip test: API to Redis to worker and back."""
    return "pong"


@celery_app.task(name="earnings.load_companies", base=IdempotentTask, bind=True)
def load_companies(self: IdempotentTask, companies: list[list[str]]) -> int:
    """Write company rows as the worker role. Running it twice leaves the same rows
    (Project-Wide EQ-07). It fetches nothing from outside: the caller supplies the rows.

    Each item is [cik, name]. Returns the number of rows in the table after the load.
    """
    rows = [{"company_id": canonical_cik(cik), "name": name} for cik, name in companies]
    engine = get_engine("worker")
    with run_record(engine, "load-companies", "caller", self.request.id) as run:
        run.rows_read = len(rows)
        with engine.begin() as conn:
            if rows:
                run.rows_written = conn.execute(
                    text(
                        "INSERT INTO company (company_id, name) VALUES (:company_id, :name) "
                        "ON CONFLICT (company_id) DO NOTHING"
                    ),
                    rows,
                ).rowcount
            return int(conn.execute(text("SELECT count(*) FROM company")).scalar_one())


@celery_app.task(name="earnings.capture_consensus", base=IdempotentTask, bind=True)
def capture_consensus(self: IdempotentTask) -> dict[str, Any]:
    """Record today's consensus snapshot for each company in the capture list (Data SR-10).

    Safe to run twice in a day: a second run adds nothing (Project-Wide EQ-07). When every company
    fails, the run is recorded as failed and the task is retried (Ingestion IG-02, IG-03).
    """
    universe = consensus.load_universe()
    engine = get_engine("worker")
    with run_record(engine, "capture-consensus", consensus.SOURCE, self.request.id) as run:
        result = consensus.capture_all(engine, universe, pause=consensus.PAUSE_SECONDS)
        run.rows_read = len(universe)
        run.rows_written = result.captured
        summary = {
            "captured": result.captured,
            "already_captured": result.already_captured,
            "failed": result.failed,
        }
        log.log(logging.ERROR if result.failed else logging.INFO, "consensus capture: %s", summary)
        if result.failed and not result.captured and not result.already_captured:
            raise RuntimeError("consensus capture failed for every company")
        # Report any run of more than 3 missing days (Data SR-10, Ingestion IG-06).
        found = consensus.gaps(engine)
        for gap in found:
            log.warning(
                "consensus capture gap: %s to %s (%d days)",
                gap.first_missing,
                gap.last_missing,
                gap.days,
            )
        summary["gaps"] = len(found)
        return summary


def edgar_client() -> EdgarClient:
    """A client whose request limit is shared by every worker process, through Redis."""
    settings = get_settings()
    limiter = RedisSlidingWindowLimiter(
        redis.Redis.from_url(settings.celery_broker_url, decode_responses=True),
        "ratelimit:sec-edgar",
        MAX_REQUESTS_PER_SECOND,
    )
    return EdgarClient(settings.sec_user_agent, limiter=limiter)


@celery_app.task(name="earnings.fetch_company_facts", base=IdempotentTask, bind=True)
def fetch_company_facts(self: IdempotentTask, cik: str) -> dict[str, Any]:
    """Fetch one company's XBRL facts from EDGAR and store the payload as received.

    Started by hand for backfill, not on a schedule (Ingestion IG-05). Fetching the same content
    twice stores one row (EQ-07). Parsing is a separate step (IG-10).
    """
    company_id = canonical_cik(cik)
    url = f"https://data.sec.gov/api/xbrl/companyfacts/CIK{company_id}.json"
    engine = get_engine("worker")
    with run_record(engine, "fetch-company-facts", EDGAR_SOURCE, self.request.id) as run:
        raw = edgar_client().get(url)
        stored = store_payload(engine, raw)
        run.rows_read, run.rows_written = 1, int(stored)
        return {"company_id": company_id, "bytes": len(raw.body), "stored": stored}


@celery_app.task(name="earnings.capture_catch_up", base=IdempotentTask)
def capture_catch_up() -> bool:
    """Capture now if today has no snapshot yet. Retried like any task (Ingestion IG-02).

    After a restart the worker can come up before PostgreSQL has finished recovering, so the first
    attempt may fail; the retries (30, 60, 120 seconds) cover that. Returns whether it queued a
    capture.
    """
    if consensus.missing_today(get_engine("worker")):
        log.info("no consensus snapshot yet today, capturing now")
        capture_consensus.delay()
        return True
    return False


def new_releases(engine: Any, client: Any, companies: list[str]) -> dict[str, Any]:
    """Fetch each company's filing list, store it, and count the earnings releases (8-K Item 2.02)
    that the previously stored list did not have. Loading them is a later, hand-started step."""
    found: dict[str, list[str]] = {}
    failed: list[str] = []
    for company_id in companies:
        url = fin.SUBMISSIONS_URL.format(cik=company_id)
        before = latest_payload(engine, EDGAR_SOURCE, url)
        try:
            raw = client.get(url)
        except Exception as exc:  # noqa: BLE001  one failing company must not stop the others
            log.error("filing check failed for %s: %s", company_id, type(exc).__name__)
            failed.append(company_id)
            continue
        store_payload(engine, raw)
        if before is None:
            continue  # nothing to compare with yet
        old = {r.accession for r in fin.parse_earnings_releases([before])}
        added = [
            r.accession for r in fin.parse_earnings_releases([raw.body]) if r.accession not in old
        ]
        if added:
            found[company_id] = added
    return {"checked": len(companies) - len(failed), "new": found, "failed": failed}


@celery_app.task(name="earnings.check_new_filings", base=IdempotentTask, bind=True)
def check_new_filings(self: IdempotentTask) -> dict[str, Any]:
    """The daily check for new 8-K Item 2.02 filings (Ingestion IG-05)."""
    companies, _ = universe.read_list(Path(universe.__file__).parent / "universe.csv")
    engine = get_engine("worker")
    with run_record(engine, "check-8k", EDGAR_SOURCE, self.request.id) as run:
        result = new_releases(engine, edgar_client(), [c["company_id"] for c in companies])
        run.rows_read, run.rows_written = result["checked"], sum(map(len, result["new"].values()))
        if companies and not result["checked"]:
            raise RuntimeError("the filing check failed for every company")
        log.info("filing check: %s", {k: v for k, v in result.items() if k != "failed"})
        return result


@celery_app.task(name="earnings.check_new_transcripts", base=IdempotentTask, bind=True)
def check_new_transcripts(self: IdempotentTask) -> dict[str, Any]:
    """The daily check for new transcripts (IG-05, NFR-03). The transcript set is a pinned
    snapshot, so a new revision is reported for John and is not loaded by itself."""
    engine = get_engine("worker")
    with run_record(engine, "check-transcripts", huggingface.SOURCE, self.request.id) as run:
        latest = huggingface.latest_revision()
        changed = latest != huggingface.REVISION
        run.rows_read = 1
        if changed:
            log.warning("the transcript set has a new revision %s (pinned %s)", latest,
                        huggingface.REVISION)  # fmt: skip
        return {"pinned": huggingface.REVISION, "latest": latest, "new_revision": changed}


@celery_app.task(name="earnings.run_data_gates", base=IdempotentTask, bind=True)
def run_data_gates(self: IdempotentTask) -> dict[str, Any]:
    """The daily run of the data checks (IG-05), with the report of late jobs (IG-06)."""
    engine = get_engine("worker")
    with run_record(engine, "data-gates", "derived", self.request.id) as run:
        report = validation.run_checks(engine)
        report["late_jobs"] = late_jobs(engine, list(JOBS), since=consensus.CAPTURE_START)
        run.rows_read = report["null_rates"]["events"]
        run.rows_written = report["quarantined_this_run"]
        if report["late_jobs"]:
            log.warning("late scheduled jobs: %s", ", ".join(report["late_jobs"]))
        return report


@worker_ready.connect
def queue_catch_up(**_: Any) -> None:
    """At worker start, queue the catch-up check if the setting allows it (decision C-46)."""
    if not get_settings().yahoo_collection:
        log.info("Yahoo collection is off (YAHOO_COLLECTION): no capture is queued")
        return
    if not get_settings().capture_catch_up:
        log.info("capture catch-up is off (CAPTURE_CATCH_UP)")
        return
    capture_catch_up.delay()
