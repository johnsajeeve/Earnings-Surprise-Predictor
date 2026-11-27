"""Parsers for the universe sources. They read stored payloads and never touch the network
(Ingestion IG-10, IG-13; Data IM-01 to IM-03).
"""

import csv
import html
import io
import json
import re
from dataclasses import dataclass
from datetime import date, datetime

MEMBERSHIP_SOURCE = "github-fja05680-sp500"
WIKIPEDIA_SOURCE = "wikipedia-sp500-history"
MEMBERSHIP_URL = (
    "https://raw.githubusercontent.com/fja05680/sp500/master/sp500_ticker_start_end.csv"
)
WIKIPEDIA_URL = (
    "https://en.wikipedia.org/w/api.php?action=parse&page=Historical_components_of_the_S%26P_500"
    "&prop=text&format=json&formatversion=2"
)
SEC_TICKERS_URL = "https://www.sec.gov/files/company_tickers.json"
CIK_LOOKUP_URL = "https://www.sec.gov/Archives/edgar/cik-lookup-data.txt"

_SUFFIXES = {
    "INC", "CORP", "CORPORATION", "CO", "COMPANY", "LTD", "LIMITED", "PLC", "LLC", "LP", "NV",
    "SA", "AG", "THE",
}  # fmt: skip


@dataclass(frozen=True)
class Spell:
    ticker: str
    start: date
    end: date | None  # the end date is not part of the period


@dataclass(frozen=True)
class Change:
    effective: date
    added: str
    added_name: str
    removed: str
    removed_name: str
    reason: str


def ticker_key(ticker: str) -> str:
    """Share classes are written BRK.B in one source and BRK-B in another."""
    return ticker.upper().replace(".", "-").strip()


def normalise_name(name: str) -> str:
    """Upper case, punctuation removed, common company suffixes dropped. Exact matches only."""
    cleaned = re.sub(r"[^A-Z0-9 ]", " ", name.upper().replace("&", " AND "))
    tokens = [t for t in cleaned.split() if t]
    while tokens and tokens[-1] in _SUFFIXES:
        tokens.pop()
    while tokens and tokens[0] in _SUFFIXES:
        tokens.pop(0)
    return " ".join(tokens)


def parse_membership_spells(payload: bytes) -> list[Spell]:
    rows = csv.DictReader(io.StringIO(payload.decode("utf-8")))
    return [
        Spell(
            ticker_key(r["ticker"]),
            date.fromisoformat(r["start_date"]),
            date.fromisoformat(r["end_date"]) if r["end_date"] else None,
        )
        for r in rows
    ]


def _cells(row: str) -> list[str]:
    parts = re.findall(r"<t[dh].*?</t[dh]>", row, flags=re.S)
    return [html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", "", p))).strip() for p in parts]


def parse_wikipedia_history(payload: bytes) -> list[Change]:
    """The change table: effective date, added ticker and name, removed ticker and name, reason."""
    text = json.loads(payload)["parse"]["text"]
    table = re.findall(r"<table.*?</table>", text, flags=re.S)[0]
    changes = []
    for row in re.findall(r"<tr.*?</tr>", table, flags=re.S):
        c = _cells(row)
        if len(c) < 6:
            continue
        try:
            effective = datetime.strptime(c[0], "%B %d, %Y").date()
        except ValueError:
            continue
        changes.append(Change(effective, ticker_key(c[1]), c[2], ticker_key(c[3]), c[4], c[5]))
    return changes


def parse_sec_tickers(payload: bytes) -> dict[str, list[tuple[str, str]]]:
    """ticker -> [(CIK as ten digits, company title)]."""
    out: dict[str, list[tuple[str, str]]] = {}
    for item in json.loads(payload).values():
        out.setdefault(ticker_key(item["ticker"]), []).append(
            (f"{int(item['cik_str']):010d}", item["title"])
        )
    return out


def parse_cik_lookup(payload: bytes) -> dict[str, set[str]]:
    """normalised company name -> the CIKs that carry it."""
    out: dict[str, set[str]] = {}
    for line in payload.decode("utf-8", errors="replace").splitlines():
        try:
            name, cik, _ = line.rsplit(":", 2)
        except ValueError:
            continue
        if cik.isdigit() and name:
            key = normalise_name(name)
            if key:
                out.setdefault(key, set()).add(f"{int(cik):010d}")
    return out


def earliest_filing_date(submissions: bytes) -> date | None:
    """The date of the first filing a CIK has made, from its EDGAR submissions payload."""
    data = json.loads(submissions)["filings"]
    dates = [d for d in data["recent"].get("filingDate", [])]
    dates += [f["filingFrom"] for f in data.get("files", []) if f.get("filingFrom")]
    return min(date.fromisoformat(d) for d in dates) if dates else None


def latest_filing_date(submissions: bytes) -> date | None:
    """The date of the most recent filing a CIK has made, from its EDGAR submissions payload."""
    dates = json.loads(submissions)["filings"]["recent"].get("filingDate", [])
    return max(date.fromisoformat(d) for d in dates) if dates else None
