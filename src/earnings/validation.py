"""Dataset validation (Data DV-01 to DV-08, CE-01, TX-04, TX-07, TH-01; Database DB-14).

Every check returns numbers. A check that misses its threshold says so; no threshold is changed
(decision C-37). Rows that fail are quarantined, never dropped.
"""

import hashlib
import json
from collections import defaultdict
from datetime import date
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

from earnings.label import EPS_BASIS, ROUTE_TIME_SERIES

DATE_FIELDS = ("transcript_date", "information_date", "announcement_date")
# A label this large cannot come from a real surprise: two events show a scale error in the source
# (quarterly EPS in thousands). This is my own flag, not the DV-04 threshold, which is still pending
# (decision D-47, item m). The event stays in its table; the quarantine row is for review.
SCALE_ERROR_SUE = 1e6


def calendar_quarter(start: date, end: date) -> tuple[int, int]:
    """The calendar quarter that holds the middle of a fiscal period (DV-06). A retailer's quarter
    from November to January and a 52-week year that ends in early January both land correctly."""
    mid = start + (end - start) / 2
    return mid.year, (mid.month - 1) // 3 + 1


def fiscal_mapping(engine: Engine, company_id: str) -> dict[str, Any]:
    """Each stored fiscal quarter of one company mapped to a calendar quarter. It is sound when no
    two periods share a calendar quarter and the quarters run without gaps (DV-06, FD-04)."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT min(period_start), period_end FROM eps_history WHERE company_id = :c "
                "AND period_kind = 'quarter' GROUP BY period_end ORDER BY period_end"
            ),
            {"c": company_id},
        ).all()
    quarters = [calendar_quarter(r[0], r[1]) for r in rows]
    seen: dict[tuple[int, int], int] = defaultdict(int)
    for q in quarters:
        seen[q] += 1
    index = sorted(seen)
    gaps = [
        (a, b)
        for a, b in zip(index, index[1:], strict=False)
        if (b[0] * 4 + b[1]) - (a[0] * 4 + a[1]) != 1
    ]
    return {
        "periods": len(rows),
        "shared": sorted(q for q, n in seen.items() if n > 1),
        "gaps": gaps,
        "sound": not [q for q, n in seen.items() if n > 1],
    }


def fiscal_year_end_month(engine: Engine, company_id: str) -> int | None:
    with engine.connect() as conn:
        return conn.execute(
            text(
                "SELECT mode() WITHIN GROUP (ORDER BY extract(month FROM period_end))::int "
                "FROM eps_history WHERE company_id = :c AND period_kind = 'year'"
            ),
            {"c": company_id},
        ).scalar()


def duplicate_events(engine: Engine) -> list[tuple[Any, ...]]:
    """Events not unique on company, fiscal quarter and announcement date (DV-03)."""
    with engine.connect() as conn:
        return [
            tuple(r)
            for r in conn.execute(
                text(
                    "SELECT company_id, period_end, announcement_date, count(*) "
                    "FROM earnings_event "
                    "WHERE period_end IS NOT NULL GROUP BY 1, 2, 3 HAVING count(*) > 1"
                )
            )
        ]


def null_rates(engine: Engine) -> dict[str, Any]:
    """Nulls in the three date fields (DV-02, TH-15). Events that are marked incomplete are counted
    apart: they cannot be used as training rows and the schema allows the marked gap (FR-02)."""
    with engine.connect() as conn:
        total, usable, incomplete = conn.execute(
            text(
                "SELECT count(*), count(*) FILTER (WHERE sue IS NOT NULL AND status = 'included'), "
                "count(*) FILTER (WHERE incomplete) FROM earnings_event"
            )
        ).one()
        nulls = {
            f: conn.execute(
                text(
                    f"SELECT count(*) FROM earnings_event WHERE {f} IS NULL "
                    "AND sue IS NOT NULL AND status = 'included'"
                )
            ).scalar_one()
            for f in DATE_FIELDS
        }
    return {
        "events": total,
        "usable_events": usable,
        "incomplete_events": incomplete,
        "nulls_in_usable_events": nulls,
        "null_rate_usable": {f: (n / usable if usable else 0.0) for f, n in nulls.items()},
    }


def date_order_violations(engine: Engine) -> dict[str, list[tuple[Any, ...]]]:
    """DV-05: information date before the announcement, and the call not before the announcement.
    A call dated before its release is allowed by decision C-17 and is listed as a conflict with the
    wording of DV-05, not as an error."""
    with engine.connect() as conn:
        info_late = conn.execute(
            text(
                "SELECT event_id, information_date, announcement_date FROM earnings_event "
                "WHERE information_date IS NOT NULL AND information_date >= announcement_date"
            )
        ).all()
        call_first = conn.execute(
            text(
                "SELECT event_id, transcript_date, announcement_date FROM earnings_event "
                "WHERE transcript_date < announcement_date"
            )
        ).all()
    return {"information_not_before_announcement": [tuple(r) for r in info_late],
            "call_before_announcement": [tuple(r) for r in call_first]}  # fmt: skip


def capture_after_announcement(engine: Engine) -> int:
    """CE-01: snapshots an event may use that were captured on or after its announcement."""
    with engine.connect() as conn:
        return conn.execute(
            text(
                "SELECT count(*) FROM earnings_event e CROSS JOIN LATERAL "
                "estimate_snapshot_as_of(e.company_id, e.announcement_time_utc) s "
                "WHERE s.captured_at >= e.announcement_time_utc"
            )
        ).scalar_one()


def basis_values(engine: Engine) -> list[str]:
    """AE-03: one EPS basis per dataset."""
    with engine.connect() as conn:
        return [r[0] for r in conn.execute(text("SELECT DISTINCT eps_basis FROM earnings_event"))]


def table_hash(engine: Engine, table: str, columns: list[str], order: list[str]) -> str:
    """A hash of a table's content (DV-08). Surrogate ids are left out, so two builds of the same
    snapshot compare equal."""
    cols = ", ".join(columns)
    with engine.connect() as conn:
        rows = conn.execute(text(f"SELECT {cols} FROM {table} ORDER BY {', '.join(order)}")).all()
    digest = hashlib.sha256()
    for row in rows:
        digest.update(json.dumps([str(v) for v in row]).encode())
    return digest.hexdigest()


EVENT_HASH_COLUMNS = [
    "company_id", "period_end", "fiscal_period", "transcript_date", "information_date",
    "announcement_date", "announcement_time_utc", "release_accession", "eps_basis",
    "label_route", "sue", "sue_reason", "differences_used", "splits_applied", "incomplete",
    "status", "exclusion_reason",
]  # fmt: skip


def events_hash(engine: Engine) -> str:
    return table_hash(engine, "earnings_event", EVENT_HASH_COLUMNS, ["company_id", "transcript_id"])


def quarantine_row(
    engine: Engine, table: str, key: str, reason: str, detail: dict[str, Any] | None = None
) -> bool:
    """Keep a failing row for review (DV-01). The same row and reason is stored once."""
    with engine.begin() as conn:
        return bool(
            conn.execute(
                text(
                    "INSERT INTO quarantine (source_table, row_key, reason, detail) VALUES "
                    "(:t, :k, :r, CAST(:d AS jsonb)) ON CONFLICT ON CONSTRAINT "
                    "quarantine_one_per_reason DO NOTHING"
                ),
                {"t": table, "k": key, "r": reason, "d": json.dumps(detail or {}, default=str)},
            ).rowcount
        )


def schema_failures(engine: Engine) -> list[tuple[int, str]]:
    """Events that do not match the versioned schema of the dataset (DV-01)."""
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT event_id, eps_basis, label_route, sue, status, exclusion_reason FROM "
                "earnings_event"
            )
        ).all()
    bad = []
    for event_id, basis, route, sue, status, why in rows:
        if basis != EPS_BASIS:
            bad.append((event_id, f"eps_basis {basis!r} is not {EPS_BASIS!r}"))
        if route != ROUTE_TIME_SERIES:
            bad.append((event_id, f"label_route {route!r} in a time-series dataset"))
        if sue is not None and abs(sue) > SCALE_ERROR_SUE:
            bad.append((event_id, "sue above one million in size: scale error in the source EPS"))
        if status == "excluded":
            bad.append((event_id, f"flagged for review: {why}"))
    return bad


def run_checks(engine: Engine) -> dict[str, Any]:
    """All the event checks. Failing rows go to quarantine and are counted per reason."""
    failures = schema_failures(engine)
    new = sum(quarantine_row(engine, "earnings_event", str(k), why) for k, why in failures)
    per_reason: dict[str, int] = defaultdict(int)
    for _, why in failures:
        per_reason[why.split(":")[0]] += 1
    order = date_order_violations(engine)
    return {
        "quarantined_this_run": new,
        "quarantine_candidates": len(failures),
        "quarantine_by_reason": dict(per_reason),
        "duplicate_events": len(duplicate_events(engine)),
        "null_rates": null_rates(engine),
        "information_not_before_announcement": len(order["information_not_before_announcement"]),
        "call_before_announcement": len(order["call_before_announcement"]),
        "snapshots_on_or_after_announcement": capture_after_announcement(engine),
        "eps_basis_values": basis_values(engine),
        "events_hash": events_hash(engine),
    }


def extreme_events(engine: Engine, threshold: float) -> list[tuple[int, str, float]]:
    """DV-04. The threshold has no default: the requirement does not state one (pending value)."""
    with engine.connect() as conn:
        return [
            (r[0], r[1], float(r[2]))
            for r in conn.execute(
                text(
                    "SELECT event_id, company_id, sue FROM earnings_event WHERE abs(sue) > :t "
                    "ORDER BY abs(sue) DESC"
                ),
                {"t": threshold},
            )
        ]


def coverage_gate(coverage: dict[str, Any], threshold: float = 0.90) -> dict[str, Any]:
    """TX-04 and TH-01: the share of target events with a transcript, all years together, with the
    two groups apart (TX-07). The threshold is the requirement's 90%; a miss is reported."""
    totals = {"left the index": [0, 0], "still in the index": [0, 0]}
    for key, v in coverage["by_year_and_group"].items():
        group = key.split(" ", 1)[1]
        totals[group][0] += v.get("releases", 0)
        totals[group][1] += v.get("with_transcript", 0)
    releases = sum(t[0] for t in totals.values())
    covered = sum(t[1] for t in totals.values())
    share = covered / releases if releases else 0.0
    return {
        "target_events": releases,
        "with_transcript": covered,
        "share": share,
        "threshold": threshold,
        "met": share >= threshold,
        "by_group": {g: {"events": t[0], "with_transcript": t[1],
                         "share": t[1] / t[0] if t[0] else 0.0} for g, t in totals.items()},
    }  # fmt: skip


def audit_sheet(engine: Engine, n: int, seed: int, out: Path) -> list[int]:
    """Draw n usable events at random for a person to check against the primary documents
    (VL-09). The sheet lists the stored values and the SEC links; the person writes the verdict."""
    import random

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT e.event_id, c.name, e.company_id, e.period_end, e.announcement_date, "
                "e.release_accession, e.sue, e.differences_used, "
                "(SELECT eps_diluted FROM eps_history h WHERE h.company_id = e.company_id "
                " AND h.period_end = e.period_end AND h.period_kind = 'quarter' "
                " ORDER BY filed_at, derived LIMIT 1) AS eps, "
                "(SELECT accession FROM eps_history h WHERE h.company_id = e.company_id "
                " AND h.period_end = e.period_end AND h.period_kind = 'quarter' "
                " ORDER BY filed_at, derived LIMIT 1) AS eps_accession "
                "FROM earnings_event e JOIN company c USING (company_id) "
                "WHERE e.sue IS NOT NULL AND e.status = 'included' ORDER BY e.event_id"
            )
        ).all()
    chosen = random.Random(seed).sample(rows, min(n, len(rows)))
    lines = [
        "# Hand audit sheet (VL-09)",
        "",
        "For each event, open the two filings and check: the quarter's diluted EPS, the "
        "announcement date, and that the EPS filing date is as stored. Write `ok` or "
        "`error: what` after the arrow. The error rate must be at most 2% (TH-08).",
        "",
    ]
    for k, r in enumerate(chosen, 1):
        cik = int(r.company_id)
        base = f"https://www.sec.gov/Archives/edgar/data/{cik}/"
        rel = base + r.release_accession.replace("-", "") + "/"
        eps = base + (r.eps_accession or "").replace("-", "") + "/"
        lines += [
            f"## {k}. {r.name}, quarter ended {r.period_end} (event {r.event_id})",
            f"- Stored: diluted EPS {r.eps}, announcement {r.announcement_date}, "
            f"SUE {r.sue} from {r.differences_used} prior differences",
            f"- Earnings release (8-K {r.release_accession}): {rel}",
            f"- EPS first filed in {r.eps_accession}: {eps}",
            "- Verdict -> ", "",
        ]  # fmt: skip
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), "utf-8")
    return [r.event_id for r in chosen]


def main(argv: list[str]) -> int:
    """python -m earnings.validation OUT_FILE: run the event checks and write the numbers."""
    from earnings.db import get_engine
    from earnings.events import coverage_report

    if len(argv) > 2 and argv[1] == "audit-sheet":
        ids = audit_sheet(get_engine("worker"), 100, 2036, Path(argv[2]))
        print(len(ids), "events drawn")
        return 0
    if len(argv) < 2:
        print("python -m earnings.validation OUT_FILE | audit-sheet OUT_FILE")
        return 2
    engine = get_engine("worker")
    report = run_checks(engine)
    report["coverage_gate"] = coverage_gate(coverage_report(engine))
    Path(argv[1]).write_text(json.dumps(report, indent=1, default=str), "utf-8")
    print(json.dumps(report, indent=1, default=str))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
