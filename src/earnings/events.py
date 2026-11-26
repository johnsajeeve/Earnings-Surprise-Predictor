"""Earnings events, the SUE label, the coverage report and the size report
(Product FR-02, FR-14; Data LB-01, LB-02, LB-04, LB-05, CE-05; Ingestion IG-20, IG-22;
Database DB-06, DB-15).

An event is one kept transcript that is linked to an earnings release. Everything is rebuilt from
stored rows, so running it again gives the same table.
"""

import csv
import json
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

from earnings import calendar as cal
from earnings import financials as fin
from earnings import label
from earnings import transcripts as tr
from earnings.runlog import run_record

FULL_CORPUS_COMPANIES = 500  # the index size, used only to scale the size estimate (DB-15)


def _versions(engine: Engine, company_id: str) -> list[label.EpsVersion]:
    """Every stored quarterly EPS version of a company. A preparation stage, not feature code, so
    it reads the table; the as-of rule is applied in `label.compute_sue` and tested against the
    database function."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT period_start, period_end, eps_diluted, filed_at, derived, accession "
                "FROM eps_history "
                "WHERE company_id = :c AND period_kind = 'quarter'"
            ),
            {"c": company_id},
        ).all()
    return [label.EpsVersion(r[0], r[1], r[2], r[3], r[4], r[5]) for r in rows]


def _splits(engine: Engine, company_id: str) -> list[label.Split]:
    return fin.company_splits(engine, company_id)


def build_events(engine: Engine, company_ids: list[str] | None = None) -> dict[str, Any]:
    """Create or refresh the event row of every kept transcript. Returns counts per outcome."""
    report: dict[str, Any] = {
        "events": 0,
        "sue_ok": 0,
        "sue_unavailable": defaultdict(int),
        "excluded": 0,
        "incomplete": 0,
        "scale_suspect": [],
    }
    with engine.connect() as conn:
        companies = [
            r[0]
            for r in conn.execute(
                text("SELECT DISTINCT company_id FROM transcript WHERE status = 'kept' ORDER BY 1")
            )
            if company_ids is None or r[0] in company_ids
        ]
    with run_record(engine, "build-events", "derived") as run:
        for cid in companies:
            versions = _versions(engine, cid)
            splits = _splits(engine, cid)
            releases = {r.accession: r for r in tr._releases_for(engine, cid)}
            with engine.connect() as conn:
                transcripts = conn.execute(
                    text(
                        "SELECT transcript_id, call_date, release_accession, fiscal_year, "
                        "fiscal_quarter FROM transcript WHERE company_id = :c AND status = 'kept' "
                        "ORDER BY transcript_id"
                    ),
                    {"c": cid},
                ).all()
            for tid, call_date, accession, fy, fq in transcripts:
                _write_event(
                    engine,
                    cid,
                    tid,
                    call_date,
                    releases.get(accession),
                    versions,
                    splits,
                    fy,
                    fq,
                    report,
                )
            run.rows_written = report["events"]
    report["sue_unavailable"] = dict(report["sue_unavailable"])
    return report


def _write_event(engine, cid, tid, call_date, release, versions, splits, fy, fq, report):  # type: ignore[no-untyped-def]
    announcement = release.announced if release else None
    result = (
        label.compute_sue(versions, announcement, splits)
        if announcement
        else label.SueResult(None, None, "release not found", 0, None)
    )
    reasons = []
    if release is not None:
        gap = tr.trading_days_between(release.announced, call_date)
        if gap > 1:
            reasons.append(f"transcript dated {gap} trading days after the announcement")
        if result.target_filed is not None and result.target_filed < release.announced:
            reasons.append("the quarter's EPS was filed before the earnings release")
    if result.scale_suspect:
        reasons.append("an input EPS value has a scale error in the source (excluded, C-51)")
    exclusion = "; ".join(reasons) or None
    reason = result.reason if result.sue is None else None
    incomplete = result.information_date is None or announcement is None
    report["events"] += 1
    if result.sue is not None:
        report["sue_ok"] += 1
    else:
        report["sue_unavailable"][reason] += 1
    report["excluded"] += exclusion is not None
    if result.scale_suspect:
        report["scale_suspect"].append(tid)
    report["incomplete"] += incomplete
    with engine.begin() as conn:
        conn.execute(
            text(
                "INSERT INTO earnings_event (company_id, transcript_id, period_end, fiscal_period, "
                "transcript_date, information_date, announcement_date, announcement_time_utc, "
                "release_accession, eps_basis, label_route, sue, sue_reason, differences_used, "
                "splits_applied, incomplete, status, exclusion_reason, eps_accession, "
                "eps_filed_at) "
                "VALUES (:c, :t, :pe, :fp, "
                ":td, :idate, :ad, :at, :acc, :basis, :route, :sue, :reason, :n, :sp, :inc, :st, "
                ":ex, :eacc, :efiled) ON CONFLICT (transcript_id) DO UPDATE SET "
                "eps_accession = EXCLUDED.eps_accession, eps_filed_at = EXCLUDED.eps_filed_at, "
                "period_end = EXCLUDED.period_end, "
                "fiscal_period = EXCLUDED.fiscal_period, "
                "transcript_date = EXCLUDED.transcript_date, "
                "information_date = EXCLUDED.information_date, "
                "announcement_date = EXCLUDED.announcement_date, "
                "announcement_time_utc = EXCLUDED.announcement_time_utc, "
                "release_accession = EXCLUDED.release_accession, sue = EXCLUDED.sue, "
                "sue_reason = EXCLUDED.sue_reason, differences_used = EXCLUDED.differences_used, "
                "splits_applied = EXCLUDED.splits_applied, incomplete = EXCLUDED.incomplete, "
                "status = EXCLUDED.status, exclusion_reason = EXCLUDED.exclusion_reason"
            ),
            {
                "c": cid, "t": tid, "pe": result.period_end,
                "fp": f"FY{fy}Q{fq}" if fy and fq else None, "td": call_date,
                "idate": result.information_date, "ad": announcement,
                "at": release.accepted_utc if release else None,
                "acc": release.accession if release else "", "basis": label.EPS_BASIS,
                "route": label.ROUTE_TIME_SERIES, "sue": result.sue, "reason": reason,
                "n": result.differences, "sp": result.splits_applied, "inc": incomplete,
                "st": "excluded" if exclusion else "included", "ex": exclusion,
                "eacc": result.target_accession or None, "efiled": result.target_filed,
            },
        )  # fmt: skip


def cutoffs(engine: Engine, event_id: int | None = None) -> list[tuple[int, date]]:
    """(event, session of its prediction cutoff). The cutoff is the earlier of the call time and
    the 8-K acceptance time (C-17). A call with no usable time on an earlier day than the filing
    counts from the start of that day. The session is the trading day the cutoff counts for."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT e.event_id, e.announcement_time_utc, t.call_at, e.transcript_date, "
                "e.announcement_date FROM earnings_event e JOIN transcript t USING "
                "(transcript_id) WHERE e.announcement_time_utc IS NOT NULL "
                "AND (CAST(:e AS bigint) IS NULL OR e.event_id = :e) ORDER BY e.event_id"
            ),
            {"e": event_id},
        ).all()
    out = []
    for found, accepted, call_at, call_day, announced in rows:
        moment = fin.t0_cutoff(call_at, accepted)
        assert moment is not None
        if call_at is None and call_day is not None and call_day < announced:
            moment = min(moment, start_of_day(call_day))
        out.append((found, cal.trading_day_for(moment)))
    return out


def cutoff_day(engine: Engine, event_id: int) -> date:
    """The day from which nothing may be used: the earlier of the announcement date and the New
    York day of the call."""
    with engine.connect() as conn:
        announced, call_day, call_at = conn.execute(
            text(
                "SELECT e.announcement_date, e.transcript_date, t.call_at FROM earnings_event e "
                "JOIN transcript t USING (transcript_id) WHERE e.event_id = :e"
            ),
            {"e": event_id},
        ).one()
    days = [announced, call_day]
    if call_at is not None:
        days.append(call_at.astimezone(fin.EASTERN).date())
    return min(d for d in days if d is not None)


def event_snapshots(engine: Engine, event_id: int) -> list[dict[str, Any]]:
    """Consensus snapshots an event may use: captured before the day of its cutoff began in New
    York, so nothing from the announcement date or from an earlier call's day (FR-14, C-17)."""
    day = cutoff_day(engine, event_id)
    with engine.connect() as conn:
        company = conn.execute(
            text("SELECT company_id FROM earnings_event WHERE event_id = :e"), {"e": event_id}
        ).scalar_one()
        found = conn.execute(
            text("SELECT * FROM estimate_snapshot_as_of(:c, :t)"),
            {"c": company, "t": start_of_day(day)},
        ).mappings()
        return [dict(r) for r in found]


def start_of_day(day: date) -> datetime:
    return datetime.combine(day, datetime.min.time(), fin.EASTERN)


def exclusion_report(engine: Engine) -> dict[str, dict[str, int]]:
    """Events by announcement year: label counted, or the reason it is unavailable (LB-02)."""
    out: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    with engine.connect() as conn:
        for year, reason, n in conn.execute(
            text(
                "SELECT extract(year FROM announcement_date)::int, "
                "coalesce(sue_reason, 'label ok'), "
                "count(*) FROM earnings_event GROUP BY 1, 2 ORDER BY 1, 2"
            )
        ):
            out[str(year)][reason] = n
    return {y: dict(v) for y, v in out.items()}


def coverage_report(engine: Engine, out_dir: Path | None = None) -> dict[str, Any]:
    """Share of earnings releases in the index years that have a transcript, by year, with the
    companies that left the index counted apart and every missing release listed (IG-22)."""
    by_year: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    missing: list[dict[str, str]] = []
    with engine.connect() as conn:
        companies = conn.execute(
            text(
                "SELECT company_id, name FROM company WHERE EXISTS "
                "(SELECT 1 FROM index_membership m WHERE m.company_id = company.company_id) "
                "ORDER BY 1"
            )  # fmt: skip
        ).all()
        spells: dict[str, list[tuple[date, date | None]]] = defaultdict(list)
        for cid, start, end in conn.execute(
            text("SELECT company_id, valid_from, valid_to FROM index_membership")
        ):
            spells[cid].append((start, end))
        linked = {
            (r[0], r[1])
            for r in conn.execute(
                text("SELECT company_id, release_accession FROM transcript WHERE status = 'kept'")
            )
        }
    for cid, name in companies:
        left = any(
            end is not None and date(2015, 1, 1) <= end <= date(2024, 12, 31)
            for _, end in spells[cid]
        )
        group = "left the index" if left else "still in the index"
        for r in tr._releases_for(engine, cid):
            if not (tr.FIRST_CALL_DATE <= r.announced <= tr.LAST_CALL_DATE):
                continue
            if not any(s <= r.announced and (e is None or r.announced < e) for s, e in spells[cid]):
                continue
            key = f"{r.announced.year} {group}"
            by_year[key]["releases"] += 1
            if (cid, r.accession) in linked:
                by_year[key]["with_transcript"] += 1
            else:
                missing.append({"company_id": cid, "name": name, "release_filed": str(r.announced)})
    shortfall: dict[str, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    for m in missing:
        if int(m["release_filed"][:4]) >= 2015:  # TX-04: the target years
            shortfall[m["name"]][m["release_filed"][:4]] += 1
    report = {
        "shortfall_by_company_and_year": {k: dict(v) for k, v in sorted(shortfall.items())},
        "by_year_and_group": {k: dict(v) for k, v in sorted(by_year.items())},
        "missing_count": len(missing),
    }
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "coverage_report.json").write_text(json.dumps(report, indent=1), "utf-8")
        with (out_dir / "coverage_missing.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["company_id", "name", "release_filed"], lineterminator="\n")
            w.writeheader()
            w.writerows(missing)
    return report


def size_report(engine: Engine, companies: int) -> dict[str, Any]:
    """Database size now (measured) and a scaled figure for the full index (estimated), kept
    apart (DB-15). The estimate multiplies the measured size by the company ratio: a rough guide."""
    with engine.connect() as conn:
        total = conn.execute(text("SELECT pg_database_size(current_database())")).scalar_one()
        tables = {
            r[0]: r[1]
            for r in conn.execute(
                text(
                    "SELECT relname, pg_total_relation_size(oid) FROM pg_class "
                    "WHERE relkind = 'r' AND relnamespace = 'public'::regnamespace "
                    "ORDER BY 2 DESC LIMIT 8"
                )  # fmt: skip
            )
        }
    factor = FULL_CORPUS_COMPANIES / companies
    return {
        "measured": {
            "companies": companies,
            "database_bytes": total,
            "largest_tables_bytes": tables,
        },
        "estimated": {
            "companies": FULL_CORPUS_COMPANIES,
            "database_bytes": int(total * factor),
            "method": f"measured size times {factor:.1f} (company ratio); ESTIMATE, not measured",
        },
    }


def main(argv: list[str]) -> int:
    from earnings.db import get_engine

    engine = get_engine("worker")
    if len(argv) > 1 and argv[1] == "build":
        print(json.dumps(build_events(engine), indent=1))
    elif len(argv) > 2 and argv[1] == "report":
        out = Path(argv[2])
        out.mkdir(parents=True, exist_ok=True)
        cov = coverage_report(engine, out)
        with engine.connect() as conn:
            n = conn.execute(text("SELECT count(DISTINCT company_id) FROM transcript")).scalar_one()
        everything = {"coverage": cov, "label_exclusions": exclusion_report(engine),
                      "size": size_report(engine, max(n, 1))}  # fmt: skip
        (out / "wave-1.6-report.json").write_text(json.dumps(everything, indent=1), "utf-8")
        print(json.dumps(everything["size"], indent=1))
    else:
        print("python -m earnings.events build | report OUT_DIR")
        return 2
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
