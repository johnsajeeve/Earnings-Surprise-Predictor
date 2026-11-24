"""Fetch the universe sources, build the 100-company list, and load it (Ingestion IG-13, IG-21).

  python -m earnings.universe_build fetch              download and store the source payloads
  python -m earnings.universe_build build OUT_DIR      parse, match, select, write the list files
  python -m earnings.universe_build load LIST_FILE [N] load a list (the first N companies)

`fetch` and the filing check inside `build` use the network. Everything else reads the database.
"""

import csv
import json
import sys
from collections.abc import Callable
from pathlib import Path

from sqlalchemy import Engine, text

from earnings import membership as m
from earnings import universe as u
from earnings.clients.edgar import SOURCE as EDGAR_SOURCE
from earnings.clients.edgar import EdgarClient, SourceError
from earnings.clients.public import PublicClient
from earnings.db import get_engine
from earnings.identifiers import canonical_cik
from earnings.rawstore import latest_payload, store_payload
from earnings.runlog import run_record

SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"


def fetch_sources(engine: Engine) -> dict[str, int]:
    """Download the four source files and store them as received."""
    from earnings.tasks import edgar_client

    sizes: dict[str, int] = {}
    github = PublicClient(m.MEMBERSHIP_SOURCE, ("raw.githubusercontent.com",))
    wikipedia = PublicClient(m.WIKIPEDIA_SOURCE, ("en.wikipedia.org",))
    sec = edgar_client()
    with run_record(engine, "fetch-universe-sources", "multiple") as run:
        for client, url in (
            (github, m.MEMBERSHIP_URL),
            (wikipedia, m.WIKIPEDIA_URL),
            (sec, m.SEC_TICKERS_URL),
            (sec, m.CIK_LOOKUP_URL),
        ):
            raw = client.get(url)
            store_payload(engine, raw)
            sizes[url] = len(raw.body)
            run.rows_read += 1
            run.rows_written += 1
    return sizes


def _stored(engine: Engine, source: str, url: str) -> bytes:
    body = latest_payload(engine, source, url)
    if body is None:
        raise RuntimeError(f"{url} is not stored yet: run fetch first")
    return body


def make_covers(engine: Engine, client: EdgarClient) -> Callable[[u.Company], tuple[bool, str]]:
    """The check a company must pass to be selected (decision C-47 and Wave 1.4).

    Its CIK must have started filing before the company joined the index (otherwise it is a
    successor, the XOM case), must still have been filing during the company's index years
    (otherwise it is an older registrant of the same name, found with Sealed Air), and the SEC
    must hold XBRL company facts for it (without them no EPS history can be built).
    """

    def fetch(url: str) -> bytes:
        body = latest_payload(engine, EDGAR_SOURCE, url)
        if body is None:
            raw = client.get(url)
            store_payload(engine, raw)
            body = raw.body
        return body

    def covers(company: u.Company) -> tuple[bool, str]:
        needed = max(company.first_start, u.WINDOW_START)
        submissions = fetch(SUBMISSIONS_URL.format(cik=company.cik))
        first, last = m.earliest_filing_date(submissions), m.latest_filing_date(submissions)
        if first is None or first > needed:
            return False, f"first SEC filing {first} is after {needed}: the CIK is a successor"
        if last is None or last < needed:
            return False, f"last SEC filing {last} is before {needed}: an older registrant"
        try:
            fetch(m_facts_url(company.cik))
        except SourceError:
            return False, "the SEC holds no XBRL company facts for this CIK"
        return True, ""

    return covers


def m_facts_url(cik: str) -> str:
    return f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"


def build(engine: Engine, out_dir: Path) -> dict[str, object]:
    spells = m.parse_membership_spells(_stored(engine, m.MEMBERSHIP_SOURCE, m.MEMBERSHIP_URL))
    changes = m.parse_wikipedia_history(_stored(engine, m.WIKIPEDIA_SOURCE, m.WIKIPEDIA_URL))
    sec = m.parse_sec_tickers(_stored(engine, EDGAR_SOURCE, m.SEC_TICKERS_URL))
    lookup = m.parse_cik_lookup(_stored(engine, EDGAR_SOURCE, m.CIK_LOOKUP_URL))
    resolved, review = u.resolve_all(spells, sec, changes, lookup)
    companies = u.group_companies(spells, resolved, sec, changes)

    from earnings.tasks import edgar_client

    covers = make_covers(engine, edgar_client())

    selection = u.select_universe(companies, covers)
    out_dir.mkdir(parents=True, exist_ok=True)
    chosen = selection.current + selection.removed
    u.write_list(out_dir / "universe.csv", companies, chosen, changes)
    for group, ciks in (("current", selection.current), ("removed", selection.removed)):
        for cik in ciks:
            review.append(
                {
                    "ticker": ";".join(sorted(companies[cik].spells)),
                    "method": "selected",
                    "name": companies[cik].name,
                    "ciks": cik,
                    "note": group,
                }  # fmt: skip
            )
    for cik, group, note in selection.rejected:
        review.append(
            {
                "ticker": ";".join(sorted(companies[cik].spells)),
                "method": "excluded",
                "name": companies[cik].name,
                "ciks": cik,
                "note": f"{group}: {note}",
            }  # fmt: skip
        )
    with (out_dir / "review_list.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, ["ticker", "method", "name", "ciks", "note"], lineterminator="\n")
        w.writeheader()
        w.writerows(review)
    report = {
        "tickers_in_file": len({s.ticker for s in spells}),
        "tickers_resolved": len(resolved),
        "tickers_not_resolved": len({s.ticker for s in spells}) - len(resolved),
        "companies": len(companies),
        "companies_by_status": {
            k: sum(1 for c in companies.values() if c.status == k)
            for k in ("current", "removed", "out-of-window")
        },
        "selected_current": len(selection.current),
        "selected_removed": len(selection.removed),
        "excluded_by_rule": len(selection.rejected),
        "year_end_ticker_counts": u.year_end_counts(spells),
        "year_end_company_counts": u.year_end_company_counts(spells, resolved),
    }
    (out_dir / "report.json").write_text(json.dumps(report, indent=1), encoding="utf-8")
    return report


def load(engine: Engine, list_path: Path, limit: int | None = None) -> dict[str, int]:
    """Write companies, ticker history and index membership from a list file (IG-21).

    The same code runs for 5 or for 100 companies. Running it again changes nothing (EQ-07).
    """
    from datetime import date

    from earnings.membership import Spell
    from earnings.universe import merge_periods

    companies, tickers = u.read_list(list_path, limit)
    counts = {"companies": 0, "ticker_spells": 0, "membership_periods": 0}
    with run_record(engine, "load-universe", "list-file") as run:
        run.rows_read = len(companies)
        with engine.begin() as conn:
            for c in companies:
                cik = canonical_cik(c["company_id"])
                counts["companies"] += conn.execute(
                    text("INSERT INTO company VALUES (:c, :n) ON CONFLICT (company_id) DO NOTHING"),
                    {"c": cik, "n": c["name"]},
                ).rowcount
                rows = [r for r in tickers if r["company_id"] == c["company_id"]]
                for r in rows:
                    counts["ticker_spells"] += conn.execute(
                        text(
                            "INSERT INTO ticker_history (company_id, ticker, valid_from, valid_to) "
                            "SELECT :c, :t, :f, :to WHERE NOT EXISTS (SELECT 1 FROM ticker_history "
                            "WHERE company_id = :c AND ticker = :t AND valid_from = :f)"
                        ),
                        {"c": cik, "t": r["ticker"], "f": date.fromisoformat(r["valid_from"]),
                         "to": date.fromisoformat(r["valid_to"]) if r["valid_to"] else None},
                    ).rowcount  # fmt: skip
                spells = [
                    Spell(r["ticker"], date.fromisoformat(r["valid_from"]),
                          date.fromisoformat(r["valid_to"]) if r["valid_to"] else None)
                    for r in rows
                ]  # fmt: skip
                periods = merge_periods(spells)
                for i, (start, end) in enumerate(periods):
                    reason = (
                        c["removal_reason"] if end is not None and i == len(periods) - 1 else None
                    )
                    counts["membership_periods"] += conn.execute(
                        text(
                            "INSERT INTO index_membership (company_id, valid_from, valid_to, "
                            "removal_reason) SELECT :c, :f, :to, :r WHERE NOT EXISTS "
                            "(SELECT 1 FROM index_membership "
                            "WHERE company_id = :c AND valid_from = :f)"
                        ),
                        {"c": cik, "f": start, "to": end, "r": reason or None},
                    ).rowcount
        run.rows_written = sum(counts.values())
    return counts


def main(argv: list[str]) -> int:
    engine = get_engine("worker")
    command = argv[1] if len(argv) > 1 else ""
    if command == "fetch":
        print(json.dumps(fetch_sources(engine), indent=1))
    elif command == "build" and len(argv) > 2:
        print(json.dumps(build(engine, Path(argv[2])), indent=1))
    elif command == "load" and len(argv) > 2:
        limit = int(argv[3]) if len(argv) > 3 else None
        print(json.dumps(load(engine, Path(argv[2]), limit)))
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
