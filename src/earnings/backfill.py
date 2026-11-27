"""Backfill SEC payloads for a company list and load the financials (Ingestion IG-09, IG-21).

  python -m earnings.backfill LIST_FILE [N]

The list is the same file the universe loader reads. Payloads already stored are not fetched
again. The request count is written to the run record. EDGAR's own limit is enforced by the client.
"""

import json
import sys
from pathlib import Path

from sqlalchemy import Engine

from earnings import financials as fin
from earnings import universe as u
from earnings.clients.edgar import SOURCE as EDGAR_SOURCE
from earnings.clients.edgar import EdgarClient, SourceError
from earnings.db import get_engine
from earnings.rawstore import latest_payload, store_payload
from earnings.runlog import run_record

# Older submission pages are fetched only when they can hold filings from this date on.
OLDEST_FILING = "2014-12-01"


def fetch_company_payloads(engine: Engine, client: EdgarClient, cik: str) -> int:
    """Store the company facts, the submissions and the older submission pages. Returns the number
    of requests made."""
    requests_made = 0

    def fetch(url: str) -> bytes:
        nonlocal requests_made
        body = latest_payload(engine, EDGAR_SOURCE, url)
        if body is None:
            raw = client.get(url)
            requests_made += 1
            store_payload(engine, raw)
            body = raw.body
        return body

    fetch(fin.FACTS_URL.format(cik=cik))
    submissions = json.loads(fetch(fin.SUBMISSIONS_URL.format(cik=cik)))
    for page in submissions["filings"].get("files", []):
        if page["filingTo"] >= OLDEST_FILING:
            fetch(fin.SUBMISSIONS_PAGE_URL.format(name=page["name"]))
    return requests_made


def backfill(
    engine: Engine, client: EdgarClient, list_path: Path, limit: int | None = None
) -> dict:
    companies, _ = u.read_list(list_path, limit)
    summary: dict = {"companies": len(companies), "requests": 0, "failed": [], "eps": 0,
                     "fundamentals": 0}  # fmt: skip
    with run_record(engine, "backfill-sec", EDGAR_SOURCE) as run:
        for c in companies:
            cik = c["company_id"]
            try:
                summary["requests"] += fetch_company_payloads(engine, client, cik)
                counts = fin.load_financials(engine, cik)
                summary["eps"] += counts["eps"]
                summary["fundamentals"] += counts["fundamentals"]
            except (SourceError, LookupError) as exc:
                summary["failed"].append(f"{cik} {c['name']}: {exc}")
        run.rows_read = summary["requests"]
        run.rows_written = summary["eps"] + summary["fundamentals"]
        if summary["failed"] and not run.rows_written:
            run.fail("every company failed")
    return summary


def main(argv: list[str]) -> int:
    from earnings.tasks import edgar_client

    if len(argv) < 2:
        print(__doc__)
        return 2
    limit = int(argv[2]) if len(argv) > 2 else None
    print(
        json.dumps(backfill(get_engine("worker"), edgar_client(), Path(argv[1]), limit), indent=1)
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
