"""Earnings press releases (8-K Item 2.02 exhibit 99) and the EPS they state (Data AE-02, LB-03,
VL-08). Parsing reads stored payloads. Only the fetch touches the network, and only sec.gov hosts.
"""

import json
import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from html.parser import HTMLParser

INDEX_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/index.json"
FILE_URL = "https://www.sec.gov/Archives/edgar/data/{cik}/{acc}/{name}"
_EXHIBIT = re.compile(
    r"(ex[h]?[-_]?99|exhibit[-_]?99|99[-_.]?1|press[-_]?release|earnings[-_]?release)",
    re.IGNORECASE,
)
_SKIP_ROW = re.compile(
    r"adjusted|non-gaap|excluding|pro forma|core|operating earnings", re.IGNORECASE
)
_LABEL = re.compile(r"diluted", re.IGNORECASE)
_NOT_PER_SHARE = re.compile(r"shares|weighted|average|outstanding|dilutive|effect|number of", re.I)
_PER_SHARE = re.compile(r"per\s+(common\s+)?share|eps|earnings|income|net", re.IGNORECASE)
TOLERANCE = Decimal("0.005")  # AE-02: within 0.5%
LISTED_DIFFERENCE = Decimal("0.01")  # TH-12: differences above 1% are listed


@dataclass(frozen=True)
class ParsedEps:
    value: Decimal
    row: str  # the table row the number came from
    others: tuple[Decimal, ...] = ()  # the other per-share figures on the same row


def accession_path(accession: str) -> str:
    return accession.replace("-", "")


def exhibit_names(index_payload: bytes) -> list[str]:
    """Candidate press-release files of a filing, best first: exhibit 99.1 before other 99.x."""
    items = json.loads(index_payload).get("directory", {}).get("item", [])
    names = [i["name"] for i in items if i["name"].lower().endswith((".htm", ".html"))]
    hits = [n for n in names if _EXHIBIT.search(n)]
    return sorted(hits, key=lambda n: (not re.search(r"99[-_.]?1|ex[h]?[-_]?99", n, re.I), n))


class _Text(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.rows: list[list[str]] = []
        self._row: list[str] = []
        self._cell: list[str] = []
        self._skip = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in ("script", "style"):
            self._skip += 1
        if tag in ("tr", "p", "div", "br"):
            self._flush_cell()
            self._flush_row()
        if tag in ("td", "th"):
            self._flush_cell()

    def handle_endtag(self, tag: str) -> None:
        if tag in ("script", "style"):
            self._skip = max(0, self._skip - 1)
        if tag in ("td", "th"):
            self._flush_cell()
        if tag in ("tr", "p", "div"):
            self._flush_cell()
            self._flush_row()

    def handle_data(self, data: str) -> None:
        if not self._skip:
            self._cell.append(data)

    def _flush_cell(self) -> None:
        text = re.sub(r"\s+", " ", "".join(self._cell).replace("\xa0", " ")).strip()
        self._cell = []
        if text:
            self._row.append(text)

    def _flush_row(self) -> None:
        if self._row:
            self.rows.append(self._row)
        self._row = []


def html_rows(body: bytes) -> list[list[str]]:
    parser = _Text()
    parser.feed(body.decode("utf-8", errors="replace"))
    parser._flush_cell()
    parser._flush_row()
    return parser.rows


def _as_number(cell: str) -> Decimal | None:
    cleaned = cell.replace("$", "").replace(" ", "")
    negative = cleaned.startswith("(") or cleaned.startswith("-")
    cleaned = cleaned.strip("()-").replace(",", "")
    if not cleaned or not re.fullmatch(r"\d+(\.\d+)?", cleaned):
        return None
    try:
        value = Decimal(cleaned)
    except InvalidOperation:
        return None
    return -value if negative else value


_SHARES_CONTEXT = re.compile(
    r"weighted|shares (used|outstanding)|number of shares|average shares", re.I
)
_EPS_CONTEXT = re.compile(r"per share|per common share|earnings per|income per|\beps\b", re.I)


def parse_diluted_eps(rows: list[list[str]]) -> ParsedEps | None:
    """The first GAAP diluted earnings per share figure in the release tables: a row that names
    diluted per-share earnings, is not an adjusted or non-GAAP row and not a share count, and its
    first number with decimals (the current quarter). A row labelled only "Diluted" counts when the
    table block above it is about per-share earnings, not about shares. None when nothing fits."""
    context = ""
    for i, row in enumerate(rows):
        label = row[0]
        if len(row) == 1 or _as_number(row[1]) is None:  # a heading row sets the block
            if _SHARES_CONTEXT.search(label):
                context = "shares"
            elif _EPS_CONTEXT.search(label):
                context = "eps"
        if not _LABEL.search(label) or _SKIP_ROW.search(" ".join(row)):
            continue
        if _NOT_PER_SHARE.search(label):
            continue
        short = label.strip().lower().strip(" *0123456789:") == "diluted"
        if not _PER_SHARE.search(label) and not short:
            continue
        if short and context != "eps":
            continue
        cells = row[1:] if len(row) > 1 else (rows[i + 1] if i + 1 < len(rows) else [])
        for cell in cells:
            number = _as_number(cell)
            if number is not None and "." in cell:  # per-share figures carry decimals
                rest = tuple(
                    n for c in cells if (n := _as_number(c)) is not None and "." in c and c != cell
                )
                return ParsedEps(number, " | ".join(row)[:200], rest)
    return None


def agrees(press: Decimal, xbrl: Decimal, tolerance: Decimal = TOLERANCE) -> bool:
    """Within the relative tolerance of the XBRL value (AE-02: 0.5%)."""
    return press == xbrl or abs(press - xbrl) <= abs(xbrl) * tolerance


# ---- comparison with the stored EPS (AE-02, LB-03, VL-08) --------------------------------------


def _stored_payload(engine, url: str):  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    from earnings.clients.edgar import SOURCE

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT body FROM raw_payload WHERE source = :s AND url = :u "
                "ORDER BY retrieved_at DESC LIMIT 1"
            ),
            {"s": SOURCE, "u": url},
        ).first()
    return None if row is None else bytes(row[0])


def fetch_cached(engine, client, url: str) -> bytes | None:  # type: ignore[no-untyped-def]
    """The stored copy of a SEC page, or one fetch that is then stored. None if the page is gone."""
    from earnings.clients.edgar import SourceError
    from earnings.rawstore import store_payload

    cached = _stored_payload(engine, url)
    if cached is not None:
        return cached
    try:
        response = client.get(url)
    except SourceError:
        return None
    store_payload(engine, response)
    return response.body


def press_release_eps(engine, client, cik: str, accession: str):  # type: ignore[no-untyped-def]
    """(ParsedEps or None, reason) for one earnings 8-K."""
    acc = accession_path(accession)
    index = fetch_cached(engine, client, INDEX_URL.format(cik=int(cik), acc=acc))
    if index is None:
        return None, "filing index not found"
    names = exhibit_names(index)
    if not names:
        return None, "no exhibit 99 file in the filing"
    for name in names[:2]:
        body = fetch_cached(engine, client, FILE_URL.format(cik=int(cik), acc=acc, name=name))
        if body is None:
            continue
        found = parse_diluted_eps(html_rows(body))
        if found is not None:
            return found, None
    return None, "no GAAP diluted EPS row found in the press release"


def stored_eps(engine, company_id: str, period_end):  # type: ignore[no-untyped-def]
    """The first-filed quarterly diluted EPS of a period and whether it was derived."""
    from sqlalchemy import text

    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT eps_diluted, derived FROM eps_history WHERE company_id = :c "
                "AND period_end = :e AND period_kind = 'quarter' "
                "ORDER BY filed_at, derived LIMIT 1"
            ),
            {"c": company_id, "e": period_end},
        ).first()
    return None if row is None else (Decimal(row[0]), bool(row[1]))


def compare_events(engine, client, events: list[dict]) -> list[dict]:  # type: ignore[no-untyped-def]
    """One record per event: the press-release EPS, the stored EPS and whether they agree."""
    out = []
    for e in events:
        record = {k: str(v) for k, v in e.items()}
        stored = stored_eps(engine, e["company_id"], e["period_end"])
        record["stored_eps"] = "" if stored is None else str(stored[0])
        record["derived"] = "" if stored is None else str(stored[1])
        parsed, why = press_release_eps(engine, client, e["company_id"], e["accession"])
        record["press_eps"] = "" if parsed is None else str(parsed.value)
        record["row"] = "" if parsed is None else parsed.row
        if stored is None:
            record["result"], record["note"] = "no stored EPS", "no stored EPS for the quarter"
        elif parsed is None:
            record["result"], record["note"] = "not parsed", why or ""
        elif agrees(parsed.value, stored[0]):
            record["result"], record["note"] = "agree", ""
        elif any(agrees(o, stored[0]) for o in parsed.others):
            # the stored value is on the row, in another column: the parser took the wrong column
            record["result"], record["note"] = "other column", "stored value is in another column"
        else:
            diff = abs(parsed.value - stored[0]) / abs(stored[0]) if stored[0] else Decimal(1)
            record["result"], record["note"] = "differ", f"relative difference {diff:.4f}"
        out.append(record)
    return out


def summary(records: list[dict]) -> dict:
    counts: dict[str, int] = {}
    for r in records:
        counts[r["result"]] = counts.get(r["result"], 0) + 1
    parsed = sum(counts.get(k, 0) for k in ("agree", "differ", "other column"))
    above = []
    for r in records:
        if r["result"] == "differ" and Decimal(r["stored_eps"]):
            gap = abs(Decimal(r["press_eps"]) - Decimal(r["stored_eps"])) / abs(
                Decimal(r["stored_eps"])
            )
            if gap > LISTED_DIFFERENCE:
                above.append(
                    {"company_id": r.get("company_id"), "period_end": r.get("period_end"),
                     "stored": r["stored_eps"], "press": r["press_eps"],
                     "relative_difference": float(round(gap, 4))}
                )  # fmt: skip
    return {
        "sampled": len(records),
        "differences_above_1pct": above,
        "counts": counts,
        "agree_of_sampled": counts.get("agree", 0) / len(records) if records else 0.0,
        "agree_of_parsed": counts.get("agree", 0) / parsed if parsed else 0.0,
    }


def _sample_events(engine, n: int, seed: int, derived: bool | None = None):  # type: ignore[no-untyped-def]
    import random

    from sqlalchemy import text

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT e.event_id, e.company_id, e.period_end, e.announcement_date, "
                "e.release_accession AS accession FROM earnings_event e WHERE e.sue IS NOT NULL "
                "AND e.status = 'included' ORDER BY e.event_id"
            )
        ).mappings().all()  # fmt: skip
    events = [dict(r) for r in rows]
    if derived is not None:
        events = [
            e for e in events
            if (stored_eps(engine, e["company_id"], e["period_end"]) or (0, None))[1] is derived
        ]  # fmt: skip
    if derived:  # one fourth quarter per company, for the 20-company sample
        seen, picked = set(), []
        random.Random(seed).shuffle(events)
        for e in events:
            if e["company_id"] not in seen:
                seen.add(e["company_id"])
                picked.append(e)
        return picked[:n]
    return random.Random(seed).sample(events, min(n, len(events)))


# VL-08 canary: widely reported companies, each with its latest usable 2024 event. The list was
# proposed in the Wave 1.7 brief, which John approved. It is fixed here so it cannot drift.
CANARY_TICKERS = (
    "AMD", "BAC", "CAT", "CMCSA", "COF", "CSX", "DAL", "IBM", "META", "ORCL",
    "PM", "WFC", "ADBE", "AMAT", "SYY", "TJX", "DECK", "NCLH", "ICE", "KMX",
)  # fmt: skip


def _canary_events(engine) -> list[dict]:  # type: ignore[no-untyped-def]
    from sqlalchemy import text

    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT DISTINCT ON (t.ticker) t.ticker, e.event_id, e.company_id, e.period_end, "
                "e.announcement_date, e.release_accession AS accession FROM earnings_event e "
                "JOIN transcript t USING (transcript_id) WHERE t.ticker = ANY(:t) "
                "AND e.sue IS NOT NULL AND e.status = 'included' "
                "AND e.announcement_date BETWEEN '2024-01-01' AND '2024-12-31' "
                "ORDER BY t.ticker, e.announcement_date DESC"
            ),
            {"t": list(CANARY_TICKERS)},
        ).mappings()
        return [dict(r) for r in rows]


def main(argv: list[str]) -> int:
    import csv
    from pathlib import Path

    from earnings.db import get_engine
    from earnings.tasks import edgar_client

    if len(argv) < 3 or argv[1] not in ("ae02", "lb03", "canary"):
        print("python -m earnings.pressrelease ae02|lb03|canary OUT_DIR")
        return 2
    engine, client, out = get_engine("worker"), edgar_client(), Path(argv[2])
    out.mkdir(parents=True, exist_ok=True)
    if argv[1] == "ae02":
        events, name = _sample_events(engine, 200, 2034), "ae02_sample"  # seed 2034, 200 events
    elif argv[1] == "lb03":
        events, name = _sample_events(engine, 20, 2035, derived=True), "lb03_sample"
    else:
        events, name = _canary_events(engine), "vl08_canary"
    records = compare_events(engine, client, events)
    with (out / f"{name}.csv").open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, list(records[0]), lineterminator="\n")
        w.writeheader()
        w.writerows(records)
    result = summary(records)
    (out / f"{name}_summary.json").write_text(json.dumps(result, indent=1), "utf-8")
    print(json.dumps(result, indent=1))
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
