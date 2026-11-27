"""The company list: membership spells matched to SEC CIKs, and the 100-company selection
(Data IM-01 to IM-03; Ingestion IG-13, IG-21; decisions C-18, C-19, C-47).

Parsing and matching read stored payloads and make no network call. Only `fetch` and the
filing-history check in `build` use the network.
"""

import csv
import random
import re
from collections import defaultdict
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

from earnings.membership import Change, Spell, normalise_name

SEED = 2031  # decision C-47
N_CURRENT, N_REMOVED = 80, 20
FIRST_YEAR, LAST_YEAR = 2015, 2024
WINDOW_START, WINDOW_END = date(FIRST_YEAR, 1, 1), date(LAST_YEAR, 12, 31)
REASON_TOLERANCE_DAYS = 7
# Renames are linked only from this date. Earlier index swaps are not all recorded in the
# secondary source, so a same-day end and start would be taken for a rename wrongly.
RENAME_FROM = date(2014, 1, 1)


@dataclass(frozen=True)
class Resolution:
    ticker: str
    cik: str
    method: str  # 'sec-ticker' or 'name'
    name: str


@dataclass
class Company:
    cik: str
    name: str
    spells: dict[str, list[Spell]] = field(default_factory=dict)  # ticker -> its spells

    @property
    def first_start(self) -> date:
        return min(s.start for ss in self.spells.values() for s in ss)

    @property
    def last_end(self) -> date | None:
        ends = [s.end for ss in self.spells.values() for s in ss]
        return None if any(e is None for e in ends) else max(e for e in ends if e)

    @property
    def status(self) -> str:
        """current: in the index on 31 December 2024; removed: left it during 2015 to 2024.

        A company that joined after 31 December 2024 is 'later' and is never selected (decision
        C-47 asks for companies in the index at the end of 2024).
        """
        if any(
            s.start <= WINDOW_END and (s.end is None or s.end > WINDOW_END)
            for ss in self.spells.values()
            for s in ss
        ):
            return "current"
        if any(s.end is None for ss in self.spells.values() for s in ss):
            return "later"
        end = self.last_end
        return "removed" if end and WINDOW_START <= end <= WINDOW_END else "out-of-window"


def _names_by_ticker(changes: list[Change]) -> dict[str, list[str]]:
    names: dict[str, list[str]] = defaultdict(list)
    for c in changes:
        for ticker, name in ((c.added, c.added_name), (c.removed, c.removed_name)):
            if ticker and name and name not in names[ticker]:
                names[ticker].append(name)
    return names


def resolve_all(
    spells: list[Spell],
    sec: dict[str, list[tuple[str, str]]],
    changes: list[Change],
    cik_names: dict[str, set[str]],
) -> tuple[dict[str, Resolution], list[dict[str, str]]]:
    """Match every ticker of the membership file to one CIK, or say why not.

    Every match that is not a plain current-ticker match, and every failure, is written to the
    review list (Ingestion IG-13).
    """
    names = _names_by_ticker(changes)
    open_tickers = {s.ticker for s in spells if s.end is None}
    resolved: dict[str, Resolution] = {}
    review: list[dict[str, str]] = []

    def log(ticker: str, method: str, name: str, ciks: set[str] | list[str], note: str) -> None:
        review.append(
            {
                "ticker": ticker,
                "method": method,
                "name": name,
                "ciks": " ".join(sorted(ciks)),
                "note": note,
            }  # fmt: skip
        )

    for ticker in sorted({s.ticker for s in spells}):
        hits = sec.get(ticker, [])
        wiki_names = names.get(ticker, [])
        if len(hits) == 1:
            cik, title = hits[0]
            same = any(normalise_name(n) == normalise_name(title) for n in wiki_names)
            if ticker in open_tickers or same:
                resolved[ticker] = Resolution(ticker, cik, "sec-ticker", title)
                continue
            # A ticker that has left the index may now belong to another company. Without a name
            # that agrees with the SEC title it is not accepted (found while checking BBT).
            log(ticker, "ticker-reused", title, [cik], "SEC lists this ticker; no name agrees")
        elif len(hits) > 1:
            log(ticker, "ambiguous", "", [c for c, _ in hits], "several SEC entries for the ticker")
            continue
        found: dict[str, str] = {}
        for name in wiki_names:
            for cik in cik_names.get(normalise_name(name), set()):
                found[cik] = name
        if len(found) == 1:
            cik, name = next(iter(found.items()))
            resolved[ticker] = Resolution(ticker, cik, "name", name)
            log(ticker, "name", name, [cik], "matched by exact normalised name")
        elif found:
            log(ticker, "ambiguous", " | ".join(wiki_names), set(found), "name gives several CIKs")
        else:
            note = "no name in any source" if not wiki_names else "name not in the SEC lookup"
            log(ticker, "unresolved", " | ".join(wiki_names), set(), note)
    _link_renames(spells, changes, resolved, review)
    return resolved, review


def _link_renames(
    spells: list[Spell],
    changes: list[Change],
    resolved: dict[str, Resolution],
    review: list[dict[str, str]],
) -> None:
    """Link a ticker to the company of the ticker that took over on the same day.

    A rename shows as one ticker ending and another starting on one date, with no index change
    recorded for either on that date. A real swap of two companies is recorded by Wikipedia, so
    it is not linked. Every link is written to the review list (method `rename-adjacent`).
    """
    removed_on = defaultdict(list)
    added_on = defaultdict(list)
    for c in changes:
        if c.removed:
            removed_on[c.removed].append(c.effective)
        if c.added:
            added_on[c.added].append(c.effective)

    def near(dates: list[date], day: date) -> bool:
        return any(abs((d - day).days) <= REASON_TOLERANCE_DAYS for d in dates)

    starts: dict[date, list[str]] = defaultdict(list)
    ends: dict[date, list[str]] = defaultdict(list)
    for s in spells:
        starts[s.start].append(s.ticker)
        if s.end is not None:
            ends[s.end].append(s.ticker)

    def unexplained(day: date) -> tuple[list[str], list[str]]:
        """Tickers that ended and tickers that started on `day` with no recorded index change."""
        out = [x for x in ends.get(day, []) if not near(removed_on.get(x, []), day)]
        new = [x for x in starts.get(day, []) if not near(added_on.get(x, []), day)]
        return sorted(set(out)), sorted(set(new))

    ambiguous_logged: set[date] = set()
    changed = True
    while changed:  # chains such as ABC, COR resolve one link at a time
        changed = False
        for day in sorted(d for d in ends if d >= RENAME_FROM):
            old, new = unexplained(day)
            if len(old) != 1 or len(new) != 1 or old[0] == new[0]:
                if old and new and day not in ambiguous_logged:
                    ambiguous_logged.add(day)
                    review.append(
                        {
                            "ticker": ";".join(old + new),
                            "method": "ambiguous-rename",
                            "name": "",
                            "ciks": "",
                            "note": f"{len(old)} ended and {len(new)} started on {day}",
                        }  # fmt: skip
                    )
                continue
            a, b = resolved.get(old[0]), resolved.get(new[0])
            if a and not b:
                target, source, known = new[0], old[0], a
            elif b and not a:
                target, source, known = old[0], new[0], b
            else:
                continue
            resolved[target] = Resolution(target, known.cik, "rename-adjacent", known.name)
            review.append(
                {
                    "ticker": target,
                    "method": "rename-adjacent",
                    "name": known.name,
                    "ciks": known.cik,
                    "note": f"same day as {source} on {day}",
                }  # fmt: skip
            )
            changed = True


def group_companies(
    spells: list[Spell],
    resolved: dict[str, Resolution],
    sec: dict[str, list[tuple[str, str]]],
    changes: list[Change],
) -> dict[str, Company]:
    names = _names_by_ticker(changes)
    companies: dict[str, Company] = {}
    for s in spells:
        r = resolved.get(s.ticker)
        if r is None:
            continue
        company = companies.setdefault(r.cik, Company(r.cik, r.name))
        company.spells.setdefault(s.ticker, []).append(s)
    for company in companies.values():
        titles = [
            t for ticker in company.spells for c, t in sec.get(ticker, []) if c == company.cik
        ]
        wiki = [n for ticker in company.spells for n in names.get(ticker, [])]
        company.name = (titles or wiki or [company.name])[0]
    return companies


def removal_reason(company: Company, changes: list[Change]) -> tuple[date | None, str]:
    """The removal date from the membership file and the reason from Wikipedia, if one matches."""
    end = company.last_end
    if end is None:
        return None, ""
    best: tuple[int, Change] | None = None
    for c in changes:
        if c.removed in company.spells:
            gap = abs((c.effective - end).days)
            if gap <= REASON_TOLERANCE_DAYS and (best is None or gap < best[0]):
                best = (gap, c)
    if best is None:
        return end, ""
    return end, _reason_text(best[1], company)


_GENERIC_WORDS = {"GROUP", "HOLDINGS", "HOLDING", "INTERNATIONAL", "FINANCIAL", "COMPANIES", "AND"}


def _reason_text(change: Change, company: Company) -> str:
    """The source's reason, marked when it names a different company.

    Some rows give the reason for the company that was added (found by the Phase 1 audit). A
    reason is kept as written when it names this company or its ticker, or names nobody at all
    (for example "Market capitalization changes."). A reason that names another company is kept
    but says so, so it is not read as the reason for this one.
    """
    text = change.reason.strip()
    if not text:
        return "the source gives no reason"
    own = {
        w
        for n in (change.removed_name, company.name)
        for w in normalise_name(n).split()
        if len(w) >= 3 and w not in _GENERIC_WORDS
    }
    words = set(normalise_name(text).split())
    tickers = set(company.spells) | {change.removed}
    if own & words or any(re.search(rf"\b{re.escape(t)}\b", text) for t in tickers):
        return text
    # capitalised words after the first are the names of other companies, people or places
    proper = [w for w in re.findall(r"\b[A-Z][A-Za-z&.\-']+", text)[1:] if w.lower() not in {"the"}]
    if not proper:
        return text  # a general statement such as "Market capitalization changes."
    return f"not stated for this company; the source row reads: {text}"


@dataclass
class Selection:
    current: list[str]
    removed: list[str]
    rejected: list[tuple[str, str, str]]  # (cik, group, reason)
    considered: dict[str, int]


def select_universe(
    companies: dict[str, Company],
    covers: Callable[[Company], tuple[bool, str]],
    seed: int = SEED,
    n_current: int = N_CURRENT,
    n_removed: int = N_REMOVED,
) -> Selection:
    """Decision C-47: a fixed seed; current members first drawn, then removed members with at least
    one removed in each year of 2015 to 2024 and the rest drawn at random. A company is taken
    only if `covers` says its CIK has filings from the time it joined the index (the XOM rule).
    """
    rng = random.Random(seed)
    current = sorted(c for c, co in companies.items() if co.status == "current")
    removed = sorted(c for c, co in companies.items() if co.status == "removed")
    rng.shuffle(current)
    rng.shuffle(removed)
    rejected: list[tuple[str, str, str]] = []
    checked: dict[str, bool] = {}

    def ok(cik: str, group: str) -> bool:
        if cik not in checked:
            good, note = covers(companies[cik])
            checked[cik] = good
            if not good:
                rejected.append((cik, group, note))
        return checked[cik]

    chosen_removed: list[str] = []
    for year in range(FIRST_YEAR, LAST_YEAR + 1):
        for cik in removed:
            end = companies[cik].last_end
            if cik not in chosen_removed and end and end.year == year and ok(cik, "removed"):
                chosen_removed.append(cik)
                break
    for cik in removed:
        if len(chosen_removed) >= n_removed:
            break
        if cik not in chosen_removed and ok(cik, "removed"):
            chosen_removed.append(cik)
    chosen_current: list[str] = []
    for cik in current:
        if len(chosen_current) >= n_current:
            break
        if ok(cik, "current"):
            chosen_current.append(cik)
    return Selection(
        chosen_current, chosen_removed[:n_removed], rejected,
        {"current": len(current), "removed": len(removed)},
    )  # fmt: skip


def merge_periods(spells: list[Spell]) -> list[tuple[date, date | None]]:
    """Union of spells as half-open periods: touching or overlapping spells become one."""
    merged: list[tuple[date, date | None]] = []
    for s in sorted(spells, key=lambda x: x.start):
        if merged:
            start, end = merged[-1]
            if end is None or s.start <= end:  # touches or overlaps the last period
                if end is not None and (s.end is None or s.end > end):
                    merged[-1] = (start, s.end)
                continue
        merged.append((s.start, s.end))
    return merged


LIST_COLUMNS = ["company_id", "name", "status", "removal_date", "removal_reason"]
TICKER_COLUMNS = ["company_id", "ticker", "valid_from", "valid_to"]


def write_list(
    path: Path, companies: dict[str, Company], ciks: list[str], changes: list[Change]
) -> None:
    """Write the company list file and, beside it, the ticker spells of those companies."""
    ticker_path = path.with_name(path.stem + "_tickers.csv")
    with (
        path.open("w", newline="", encoding="utf-8") as fh,
        ticker_path.open("w", newline="", encoding="utf-8") as tf,
    ):
        w, tw = csv.writer(fh, lineterminator="\n"), csv.writer(tf, lineterminator="\n")
        w.writerow(LIST_COLUMNS)
        tw.writerow(TICKER_COLUMNS)
        for cik in ciks:
            co = companies[cik]
            end, reason = removal_reason(co, changes)
            w.writerow([cik, co.name, co.status, end.isoformat() if end else "", reason])
            for ticker in sorted(co.spells):
                for s in sorted(co.spells[ticker], key=lambda x: x.start):
                    tw.writerow(
                        [cik, ticker, s.start.isoformat(), s.end.isoformat() if s.end else ""]
                    )


def read_list(
    path: Path, limit: int | None = None
) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    """The company rows and their ticker rows. `limit` takes the first rows, for a smaller run."""
    with path.open(encoding="utf-8", newline="") as fh:
        companies = list(csv.DictReader(fh))[:limit]
    wanted = {c["company_id"] for c in companies}
    with path.with_name(path.stem + "_tickers.csv").open(encoding="utf-8", newline="") as fh:
        tickers = [r for r in csv.DictReader(fh) if r["company_id"] in wanted]
    return companies, tickers


def year_end_counts(spells: list[Spell]) -> dict[int, int]:
    """Tickers in the index on 31 December of each year (Data IM-01)."""
    return {
        y: sum(
            1
            for s in spells
            if s.start <= date(y, 12, 31) and (s.end is None or date(y, 12, 31) < s.end)
        )
        for y in range(FIRST_YEAR, LAST_YEAR + 1)
    }


def year_end_company_counts(
    spells: list[Spell], resolved: dict[str, Resolution]
) -> dict[int, dict[str, int]]:
    """For each year-end: tickers, companies and the second share classes between them (IM-01).

    Companies are the distinct CIKs plus each ticker that could not be matched, counted once.
    """
    out: dict[int, dict[str, int]] = {}
    for y in range(FIRST_YEAR, LAST_YEAR + 1):
        day = date(y, 12, 31)
        live = [s.ticker for s in spells if s.start <= day and (s.end is None or day < s.end)]
        ciks = {resolved[t].cik for t in live if t in resolved}
        unresolved = [t for t in live if t not in resolved]
        companies = len(ciks) + len(unresolved)
        out[y] = {
            "tickers": len(live),
            "companies": companies,
            "second_share_classes": len(live) - companies,
            "unresolved_tickers": len(unresolved),
        }
    return out
