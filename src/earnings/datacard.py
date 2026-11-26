"""Data card for a dataset version (Data GS-02): source, licence, coverage, date range,
transformations and known gaps. Built from the database and the source register, not typed."""

import csv
from pathlib import Path

from sqlalchemy import Engine, text

REGISTER = Path(__file__).parent / "source_register.csv"
TRANSFORMATIONS = [
    "Transcript text: cleaning rules version 1 (characters and spaces only); raw text kept apart.",
    "Sections: prepared remarks and Q&A split by the boundary rule of decision C-48.",
    "EPS: diluted EPS from XBRL; fourth quarter derived as the year minus nine months and flagged.",
    "Label: time-series SUE (Data LB-01) from first-filed history; sample standard deviation.",
    "Split basis: the dated split ratios companies report to the SEC; companies without the tag "
    "are not adjusted until the price source's factors are stored.",
]


def build(engine: Engine, version: str, known_gaps: list[str]) -> str:
    """The card as Markdown for one dataset version."""
    with engine.connect() as conn:
        events, usable, companies, first, last = conn.execute(
            text(
                "SELECT count(*), count(*) FILTER (WHERE sue IS NOT NULL AND status = 'included'), "
                "count(DISTINCT company_id), min(announcement_date), max(announcement_date) "
                "FROM earnings_event"
            )
        ).one()
        route, basis = conn.execute(
            text(
                "SELECT string_agg(DISTINCT label_route, ','), string_agg(DISTINCT eps_basis, ',') "
                "FROM earnings_event"
            )  # fmt: skip
        ).one()
    with REGISTER.open(encoding="utf-8") as fh:
        sources = list(csv.DictReader(fh))
    lines: list[str] = [f"# Data card: dataset version {version}", ""]
    lines += [
        "## Coverage",
        f"- Events: {events} ({usable} usable as labelled rows)",
        f"- Companies: {companies}",
        f"- Announcement dates: {first} to {last}",
        f"- Label route: {route}; EPS basis: {basis}",
        "",
        "## Sources and licences",
    ]
    for s in sources:
        lines.append(
            f"- {s['dataset']}: {s['source']}. Licence: {s['licence']} (status {s['status']})"
        )
    lines += ["", "## Transformations", *[f"- {t}" for t in TRANSFORMATIONS], "", "## Known gaps"]
    lines += [f"- {g}" for g in known_gaps] or ["- none recorded"]
    lines += [
        "",
        "## Sign-off",
        "- Not signed off: no reviewer who did not build the dataset has been named "
        "(Data GS-01, decision D-09).",
    ]
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    from earnings.db import get_engine

    if len(argv) < 3:
        print("python -m earnings.datacard VERSION OUT_FILE [GAP ...]")
        return 2
    card = build(get_engine("worker"), argv[1], argv[3:])
    Path(argv[2]).write_text(card, "utf-8")
    print(card)
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
