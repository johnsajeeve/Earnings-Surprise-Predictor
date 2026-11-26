"""Earnings call transcripts: parsing, cleaning, sections, linking, loading
(Ingestion IG-11, IG-14, IG-17, IG-18; Data TX-01, TX-02, TX-05, TX-06; Product PL-06, ER-07).

Parsing reads stored payloads and makes no network call. Cleaning never changes the raw text.
"""

import csv
import hashlib
import json
import random
import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import UTC, date, datetime, timedelta
from pathlib import Path
from typing import Any

from sqlalchemy import Engine, text

from earnings import calendar as cal
from earnings import financials as fin
from earnings.clients import huggingface as hf
from earnings.clients.edgar import SOURCE as EDGAR_SOURCE
from earnings.clients.edgar import RawResponse
from earnings.rawstore import store_payload
from earnings.runlog import run_record

CLEANING_RULES_VERSION = "1"
FIRST_CALL_DATE = date(2013, 1, 1)  # earlier calls feed the sentiment surprise (FR-18)
LAST_CALL_DATE = date(2024, 12, 31)
LINK_WINDOW_DAYS = 3  # an earnings release must be filed within this many days of the call

OPERATOR = re.compile(r"\boperator\b", re.IGNORECASE)
_QUESTION = re.compile(r"question", re.IGNORECASE)
_ZERO_WIDTH = dict.fromkeys(map(ord, "​‌‍⁠﻿"), None)
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_QUOTES = str.maketrans({"‘": "'", "’": "'", "‚": "'", "“": '"', "”": '"'})
_SPACES = re.compile(r"[ \t  -   　]+")


# ---- cleaning (IG-17, PL-06) ---------------------------------------------------------------


def clean_text(raw: str) -> str:
    """Rules, version 1: remove zero-width and control characters, turn curly quotes into straight
    ones, turn every kind of space into a plain space, collapse runs of spaces, trim each line,
    and collapse three or more newlines into two. Words are never removed, so the text a person
    reads is unchanged. The raw text is not touched: this returns a new string."""
    text_ = raw.translate(_ZERO_WIDTH).translate(_QUOTES)
    text_ = text_.replace("\r\n", "\n").replace("\r", "\n")
    text_ = _CONTROL.sub("", text_)
    text_ = _SPACES.sub(" ", text_)
    text_ = "\n".join(line.strip() for line in text_.split("\n"))
    text_ = re.sub(r"\n{3,}", "\n\n", text_)
    return text_.strip()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


# ---- the stored source row -----------------------------------------------------------------


@dataclass(frozen=True)
class SourceRow:
    symbol: str
    year: int | None
    quarter: int | None
    stamp: str
    content: str
    turns: list[dict[str, str]]

    @property
    def call_date(self) -> date:
        return date.fromisoformat(self.stamp[:10])

    @property
    def ref(self) -> str:
        return f"{hf.REVISION}/{self.symbol}/{self.year}Q{self.quarter}/{self.stamp}"


def row_payload(row: dict[str, Any]) -> RawResponse:
    """A source row as a stored payload, the fields as received."""
    keep = (
        "symbol",
        "company_name",
        "company_id",
        "year",
        "quarter",
        "date",
        "content",
        "structured_content",
    )
    body = json.dumps({k: row.get(k) for k in keep}, sort_keys=True, default=str)
    ref = f"{hf.REVISION}/{row['symbol']}/{row.get('year')}Q{row.get('quarter')}/{row['date']}"
    return RawResponse(
        hf.SOURCE,
        f"hf://{hf.DATASET}@{ref}",
        200,
        "application/json",
        body.encode(),
        datetime.now(UTC),
    )


def parse_source_row(payload: bytes) -> SourceRow:
    d = json.loads(payload)
    turns = [
        {"speaker": (t.get("speaker") or "").strip(), "text": t.get("text") or ""}
        for t in (d.get("structured_content") or [])
    ]
    return SourceRow(
        d["symbol"], d.get("year"), d.get("quarter"), d["date"], d.get("content") or "", turns
    )


# ---- sections and roles (IG-18, TX-06, ER-07), decision C-48 -----------------------------------


def is_operator(speaker: str) -> bool:
    return bool(OPERATOR.search(speaker))


def find_boundary(turns: list[dict[str, str]]) -> int | None:
    """The first Operator turn that comes after at least two other turns and mentions a question or
    "[Operator Instructions]". None means "Segmentation failed" (Product ER-07)."""
    others = 0
    for i, turn in enumerate(turns):
        if is_operator(turn["speaker"]):
            body = turn["text"]
            if others >= 2 and (
                _QUESTION.search(body) or "[operator instructions]" in body.lower()
            ):
                return i
        else:
            others += 1
    return None


def label_turns(turns: list[dict[str, str]], boundary: int | None) -> list[dict[str, Any]]:
    """Add section and role to each turn. Roles are not in the data (labels hold names only), so
    a speaker who first appears at or after the boundary is an analyst and one who spoke before it
    is management; the Operator is the operator. Without a boundary roles other than the operator
    are unknown (TX-06)."""
    before = {t["speaker"] for t in turns[: boundary or 0] if not is_operator(t["speaker"])}
    out = []
    for i, turn in enumerate(turns):
        section = "qa" if boundary is not None and i >= boundary else "prepared"
        if is_operator(turn["speaker"]):
            role = "operator"
        elif boundary is None:
            role = "unknown"
        elif section == "prepared" or turn["speaker"] in before:
            role = "management"
        else:
            role = "analyst"
        low = turn["speaker"].lower()
        if "analyst" in low:
            role = "analyst"
        elif "executive" in low:
            role = "management"
        out.append({**turn, "section": section, "role": role})
    return out


def section_text(turns: list[dict[str, Any]], kind: str) -> str:
    return "\n\n".join(f"{t['speaker']}: {t['text']}" for t in turns if t["section"] == kind)


# ---- linking to the earnings release (IG-14, TX-02) ---------------------------------------------


def link_release(call: date, releases: list[fin.Release]) -> fin.Release | None:
    """The 8-K Item 2.02 filing nearest the call date, within LINK_WINDOW_DAYS; the earlier
    acceptance time wins a tie."""
    near = [(abs((r.filed - call).days), r.accepted_utc, r) for r in releases]
    near = [n for n in near if n[0] <= LINK_WINDOW_DAYS]
    return min(near, key=lambda n: (n[0], n[1]))[2] if near else None


def trading_days_between(start: date, end: date) -> int:
    """Exchange sessions after `start` up to `end` (negative if end is earlier)."""
    step = 1 if end >= start else -1
    days, cursor = 0, start
    while cursor != end:
        cursor += timedelta(days=step)
        if cal.is_trading_day(cursor):
            days += step
    return days


def date_check(call: date, release: fin.Release) -> str | None:
    """Data TX-02. A call before the release is allowed (the cutoff is the earlier of the two,
    decision C-17) and is noted. A call more than one trading day after it is a violation."""
    gap = trading_days_between(release.announced, call)
    if call < release.announced:
        return "call dated before the release (allowed, C-17)"
    if gap > 1:
        return f"call dated {gap} trading days after the release"
    return None


# ---- one prepared transcript ----------------------------------------------------------------


@dataclass
class Prepared:
    row: SourceRow
    company_id: str
    cleaned_text: str
    turns: list[dict[str, Any]]
    boundary: int | None
    release: fin.Release
    note: str | None
    call_at: datetime | None = None
    raw_hash: str = ""
    sections: dict[str, str] = field(default_factory=dict)


def prepare(row: SourceRow, company_id: str, releases: list[fin.Release]) -> Prepared | str:
    """Clean, segment and link one source row. Returns a reason string when it must be rejected."""
    if not row.content.strip():
        return "empty text"
    release = link_release(row.call_date, releases)
    if release is None:
        return f"no earnings release filed within {LINK_WINDOW_DAYS} days of the call"
    cleaned_turns = [
        {"speaker": clean_text(t["speaker"]), "text": clean_text(t["text"])} for t in row.turns
    ]
    cleaned_turns = [t for t in cleaned_turns if t["text"]]
    boundary = find_boundary(cleaned_turns)
    turns = label_turns(cleaned_turns, boundary)
    sections = {k: section_text(turns, k) for k in ("prepared", "qa") if section_text(turns, k)}
    return Prepared(
        row, company_id, clean_text(row.content), turns, boundary, release,
        date_check(row.call_date, release), fin.call_time_utc(row.stamp),
        sha256_text(row.content), sections,
    )  # fmt: skip


# ---- loading (IG-11, IG-14, TX-05, FR-13) ----------------------------------------------------


def _releases_for(engine: Engine, company_id: str) -> list[fin.Release]:
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT DISTINCT ON (url) body FROM raw_payload WHERE source = :s AND "
                "(url = :main OR url LIKE :pages) ORDER BY url, retrieved_at DESC"
            ),
            {"s": EDGAR_SOURCE, "main": fin.SUBMISSIONS_URL.format(cik=company_id),
             "pages": f"https://data.sec.gov/submissions/CIK{company_id}-submissions-%"},
        ).all()  # fmt: skip
    return fin.parse_earnings_releases([bytes(r[0]) for r in rows])


def _ticker_map(
    engine: Engine, company_ids: list[str]
) -> dict[str, list[tuple[str, date, date | None]]]:
    from earnings.membership import ticker_key

    out: dict[str, list[tuple[str, date, date | None]]] = defaultdict(list)
    with engine.connect() as conn:
        for cid, ticker, start, end in conn.execute(
            text("SELECT company_id, ticker, valid_from, valid_to FROM ticker_history "
                 "WHERE company_id = ANY(:ids)"), {"ids": company_ids}
        ):  # fmt: skip
            out[ticker_key(ticker)].append((cid, start, end))
    return out


def _company_for(ticker_map: dict, symbol: str, day: date) -> str | None:
    from earnings.membership import ticker_key

    for cid, start, end in ticker_map.get(ticker_key(symbol), []):
        if start <= day and (end is None or day < end):
            return cid
    return None


def load_transcripts(
    engine: Engine, parquet: Path, company_ids: list[str], out_dir: Path | None = None
) -> dict[str, Any]:
    """Read the transcript file in batches, keep the calls of the listed companies, store each as
    received, then clean, segment, link and write them. Running it again changes nothing."""
    import pyarrow.parquet as pq

    tmap = _ticker_map(engine, company_ids)
    wanted = set(tmap)
    release_cache: dict[str, list[fin.Release]] = {}
    report: dict[str, Any] = {
        "revision": hf.REVISION, "sha256": hf.EXPECTED_SHA256, "rows_in_file": 0,
        "other_companies": 0,
        "outside_dates": 0, "rejected": defaultdict(int), "loaded": 0, "duplicates": 0,
        "segmentation_failed": 0, "call_before_release": 0, "call_late": 0, "placeholder_times": 0,
    }  # fmt: skip
    rejects: list[dict[str, str]] = []
    prepared: list[tuple[Prepared, int]] = []
    store_payload(engine, hf.manifest_payload(hf.manifest(parquet, downloaded=False)))
    with run_record(engine, "load-transcripts", hf.SOURCE) as run:
        file = pq.ParquetFile(parquet)
        columns = [
            "symbol",
            "company_name",
            "company_id",
            "year",
            "quarter",
            "date",
            "content",
            "structured_content",
        ]
        for batch in file.iter_batches(batch_size=256, columns=columns):
            for row in batch.to_pylist():
                report["rows_in_file"] += 1
                from earnings.membership import ticker_key

                if not (row["symbol"] or "").strip():  # TX-01: every row names its company
                    report["rejected"]["missing ticker"] += 1
                    rejects.append(
                        {"company_id": "", "ref": str(row["date"]), "reason": "missing ticker"}
                    )
                    continue
                if ticker_key(row["symbol"]) not in wanted:
                    report["other_companies"] += 1
                    continue
                try:
                    call = date.fromisoformat(str(row["date"])[:10])
                except ValueError:  # TX-01: every row has its event date
                    report["rejected"]["missing or invalid call date"] += 1
                    rejects.append(
                        {"company_id": "", "ref": f"{row['symbol']}/{row['date']}",
                         "reason": "missing or invalid call date"}
                    )  # fmt: skip
                    continue
                if not (FIRST_CALL_DATE <= call <= LAST_CALL_DATE):
                    report["outside_dates"] += 1
                    continue
                cid = _company_for(tmap, row["symbol"], call)
                if cid is None:
                    report["other_companies"] += 1
                    continue
                raw = row_payload(row)
                store_payload(engine, raw)
                src = parse_source_row(raw.body)
                if cid not in release_cache:
                    release_cache[cid] = _releases_for(engine, cid)
                result = prepare(src, cid, release_cache[cid])
                if isinstance(result, str):
                    report["rejected"][result] += 1
                    rejects.append({"company_id": cid, "ref": src.ref, "reason": result})
                    continue
                prepared.append((result, 0))
        run.rows_read = report["rows_in_file"]
        # TX-05: for one release, the earliest call is kept; the others are duplicates
        groups: dict[tuple[str, str], list[Prepared]] = defaultdict(list)
        for p, _ in prepared:
            groups[(p.company_id, p.release.accession)].append(p)
        kept_ref: dict[tuple[str, str], str] = {}
        for key, items in groups.items():
            first = min(
                items,
                key=lambda p: (
                    p.call_at or datetime.combine(p.row.call_date, datetime.min.time(), UTC),
                    p.row.ref,
                ),
            )
            kept_ref[key] = first.row.ref
        with engine.begin() as conn:
            for p, _ in prepared:
                status = (
                    "kept"
                    if kept_ref[(p.company_id, p.release.accession)] == p.row.ref
                    else "duplicate"
                )
                run.rows_written += _insert(conn, p, status)
                report["duplicates" if status == "duplicate" else "loaded"] += 1
                report["segmentation_failed"] += p.boundary is None
                report["placeholder_times"] += p.call_at is None
                if p.note:
                    report["call_before_release" if "before" in p.note else "call_late"] += 1
                    rejects.append({"company_id": p.company_id, "ref": p.row.ref, "reason": p.note})
    report["rejected"] = dict(report["rejected"])
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)
        with (out_dir / "transcript_load_notes.csv").open("w", newline="", encoding="utf-8") as fh:
            w = csv.DictWriter(fh, ["company_id", "ref", "reason"], lineterminator="\n")
            w.writeheader()
            w.writerows(rejects)
        (out_dir / "transcript_load_report.json").write_text(
            json.dumps(report, indent=1), encoding="utf-8"
        )
    return report


def _insert(conn: Any, p: Prepared, status: str) -> int:
    payload_id = conn.execute(
        text(
            "SELECT payload_id FROM raw_payload WHERE source = :s AND url = :u "
            "ORDER BY payload_id DESC LIMIT 1"
        ),
        {"s": hf.SOURCE, "u": f"hf://{hf.DATASET}@{p.row.ref}"},
    ).scalar()
    inserted = conn.execute(
        text(
            "INSERT INTO transcript (company_id, ticker, fiscal_year, fiscal_quarter, call_date, "
            "call_at, source, source_ref, payload_id, release_accession, release_accepted_at, "
            "raw_text, raw_hash, cleaned_text, cleaning_rules_version, turns, segmentation_status, "
            "boundary_turn, status) VALUES "
            "(:c, :t, :fy, :fq, :cd, :ca, :src, :ref, :pid, :acc, :acct, :raw, :rh, :clean, :ver, "
            "CAST(:turns AS jsonb), :seg, :bt, :st) "
            "ON CONFLICT ON CONSTRAINT transcript_one_source_row DO NOTHING"
        ),
        {"c": p.company_id, "t": p.row.symbol, "fy": p.row.year, "fq": p.row.quarter,
         "cd": p.row.call_date, "ca": p.call_at, "src": hf.SOURCE, "ref": p.row.ref,
         "pid": payload_id, "acc": p.release.accession, "acct": p.release.accepted_utc,
         "raw": p.row.content, "rh": p.raw_hash, "clean": p.cleaned_text,
         "ver": CLEANING_RULES_VERSION, "turns": json.dumps(p.turns),
         "seg": "ok" if p.boundary is not None else "failed", "bt": p.boundary, "st": status},
    ).rowcount  # fmt: skip
    if inserted:
        tid = conn.execute(
            text("SELECT transcript_id FROM transcript WHERE company_id = :c AND source_ref = :r"),
            {"c": p.company_id, "r": p.row.ref},
        ).scalar_one()
        for kind, body in p.sections.items():
            conn.execute(
                text("INSERT INTO transcript_section (transcript_id, kind, text) "
                     "VALUES (:t, :k, :x) "
                     "ON CONFLICT ON CONSTRAINT transcript_section_one_kind DO NOTHING"),
                {"t": tid, "k": kind, "x": body},
            )  # fmt: skip
    return int(inserted)


# ---- the boundary review sheet for John (TX-03, IG-18) ---------------------------------------

REVIEW_SEED = 2033  # fixed so the same 50 calls can be drawn again


def review_sheet(
    engine: Engine, n: int, out: Path, ids_out: Path, seed: int = REVIEW_SEED
) -> list[int]:
    """Draw n kept transcripts at random and write a sheet showing the turns around the detected
    boundary, for a person to mark correct or wrong. The sheet holds short excerpts and stays
    on this machine; the file of ids is committed."""
    with engine.connect() as conn:
        rows = conn.execute(
            text("SELECT transcript_id, company_id, ticker, call_date, segmentation_status, "
                 "boundary_turn, turns FROM transcript WHERE status = 'kept' "
                 "ORDER BY transcript_id")
        ).all()  # fmt: skip
    chosen = random.Random(seed).sample(rows, min(n, len(rows)))
    lines = ["# Boundary review sheet", "",
             "For each call, mark whether the line marked BOUNDARY starts the question session.",
             "Write `correct` or `wrong` after the arrow. Excerpts are cut to 160 characters.",
             ""]  # fmt: skip
    for k, r in enumerate(chosen, 1):
        tid, cid, ticker, call, seg, bt, turns = r
        lines.append(f"## {k}. {ticker} {call} (transcript {tid})")
        if bt is None:
            lines += ["Rule result: SEGMENTATION FAILED (no boundary found).", ""]
            for i, t in enumerate(turns[:12]):
                lines.append(f"  {i:>3} {t['speaker'][:24]:24} | {t['text'][:160]!r}")
            lines += ["", "Is there really no question session in this call? -> ", ""]
            continue
        lo, hi = max(0, bt - 3), min(len(turns), bt + 3)
        for i in range(lo, hi):
            mark = "BOUNDARY >>" if i == bt else "           "
            lines.append(
                f"  {mark} {i:>3} {turns[i]['speaker'][:24]:24} | {turns[i]['text'][:160]!r}"
            )
        lines += ["", "Verdict -> ", ""]
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("\n".join(lines), encoding="utf-8")
    ids_out.parent.mkdir(parents=True, exist_ok=True)
    with ids_out.open("w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(
            [
                "order",
                "transcript_id",
                "company_id",
                "call_date",
                "segmentation_status",
                "boundary_turn",
            ]
        )
        for k, r in enumerate(chosen, 1):
            w.writerow([k, r[0], r[1], r[3], r[4], r[5]])
    return [r[0] for r in chosen]


def main(argv: list[str]) -> int:
    from earnings.config import get_settings
    from earnings.db import get_engine

    if len(argv) < 2:
        print(
            "python -m earnings.transcripts download | load LIST_FILE OUT_DIR | sheet OUT_DIR [N]"
        )
        return 2
    engine = get_engine("worker")
    parquet = Path(get_settings().data_dir) / "hf" / hf.REVISION / "part-0.parquet"
    if argv[1] == "download":
        print(json.dumps(hf.download(parquet), indent=1))
    elif argv[1] == "load" and len(argv) > 3:
        from earnings import universe as u

        companies, _ = u.read_list(Path(argv[2]))
        ids = [c["company_id"] for c in companies]
        print(json.dumps(load_transcripts(engine, parquet, ids, Path(argv[3])), indent=1))
    elif argv[1] == "sheet" and len(argv) > 2:
        n = int(argv[3]) if len(argv) > 3 else 50
        out = Path(argv[2])
        drawn = review_sheet(
            engine, n, out / "boundary_review_sheet.md", out / "boundary_review_ids.csv"
        )
        print(len(drawn), "calls drawn")
    else:
        return 2
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
