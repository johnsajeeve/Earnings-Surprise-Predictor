"""EPS history, fundamentals and earnings-release times, built from stored SEC payloads
(Data LB-03, LB-04, AE-03, AE-04, FD-01 to FD-03; Ingestion IG-10, IG-15).

Parsing reads stored payloads only. Every version of a fact that a filing reported becomes a row,
so the first-filed value and any restatement are both kept (the tables are append only).
"""

import json
from collections import defaultdict
from dataclasses import dataclass
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo

from sqlalchemy import Engine, text

from earnings.clients.edgar import SOURCE as EDGAR_SOURCE
from earnings.runlog import run_record

FACTS_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json"
SUBMISSIONS_URL = "https://data.sec.gov/submissions/CIK{cik}.json"
SUBMISSIONS_PAGE_URL = "https://data.sec.gov/submissions/{name}"

EPS_TAG = "EarningsPerShareDiluted"
# The first tag that a company reports for a period is used, in this order (decision in the
# evidence file of Wave 1.4). The tag that was used is stored.
REVENUE_TAGS = (
    "Revenues",
    "RevenueFromContractWithCustomerExcludingAssessedTax",
    "RevenueFromContractWithCustomerIncludingAssessedTax",
    "SalesRevenueNet",
)
GROSS_PROFIT_TAG = "GrossProfit"
OPERATING_INCOME_TAG = "OperatingIncomeLoss"

QUARTER_DAYS = range(80, 101)
YEAR_DAYS = range(350, 381)
EASTERN = ZoneInfo("America/New_York")


@dataclass(frozen=True)
class Fact:
    tag: str
    start: date
    end: date
    value: Decimal
    filed: date
    form: str | None
    accession: str
    fiscal_year: int | None
    fiscal_period: str | None

    @property
    def kind(self) -> str | None:
        days = (self.end - self.start).days
        return "quarter" if days in QUARTER_DAYS else "year" if days in YEAR_DAYS else None


def extract_facts(payload: bytes, tag: str) -> list[Fact]:
    """The facts of one us-gaap tag from a company-facts payload (the first unit it reports)."""
    node = json.loads(payload)["facts"].get("us-gaap", {}).get(tag)
    if not node:
        return []
    out = []
    for unit_rows in node["units"].values():
        for f in unit_rows:
            if "start" not in f:  # a point-in-time fact, not a period
                continue
            out.append(
                Fact(
                    tag,
                    date.fromisoformat(f["start"]),
                    date.fromisoformat(f["end"]),
                    Decimal(str(f["val"])),
                    date.fromisoformat(f["filed"]),
                    f.get("form"),
                    f["accn"],
                    f.get("fy"),
                    f.get("fp"),
                )  # fmt: skip
            )
        break
    return out


@dataclass(frozen=True)
class EpsRow:
    period_start: date
    period_end: date
    period_kind: str
    fiscal_year: int | None
    fiscal_period: str | None
    eps: Decimal
    derived: bool
    form: str | None
    accession: str
    filed: date


def _first_filed(facts: list[Fact]) -> dict[tuple[date, date], Fact]:
    first: dict[tuple[date, date], Fact] = {}
    for f in sorted(facts, key=lambda x: (x.filed, x.accession)):
        first.setdefault((f.start, f.end), f)
    return first


def _fills_year_before_q4(quarters: list[Fact], year: Fact) -> bool:
    """Three quarters that start with the year, follow each other, and stop a quarter early.

    A year in which the fourth quarter is already reported as a fact, or where the quarters do not
    line up, is not derived: a wrong derived value is worse than a missing one.
    """
    if abs((quarters[0].start - year.start).days) > 7:
        return False
    for earlier, later in zip(quarters, quarters[1:], strict=False):
        if abs((later.start - earlier.end).days - 1) > 7:
            return False
    return 60 <= (year.end - quarters[-1].end).days <= 125


def derive_fourth_quarters(facts: list[Fact]) -> list[tuple[Fact, date, Decimal]]:
    """Fourth quarter = the year minus the three quarters inside it, on first-filed values.

    Returns (the year fact, the quarter start, the derived value). A year is skipped unless
    exactly three quarters lie inside it (Data LB-03).
    """
    first = _first_filed(facts)
    years = [f for (s, e), f in first.items() if f.kind == "year"]
    quarters = [f for f in first.values() if f.kind == "quarter"]
    out = []
    for year in sorted(years, key=lambda f: f.end):
        inside = sorted(
            (q for q in quarters if q.start >= year.start and q.end <= year.end),
            key=lambda q: q.start,
        )
        if len(inside) != 3 or not _fills_year_before_q4(inside, year):
            continue
        q4_start = inside[-1].end + timedelta(days=1)
        out.append((year, q4_start, year.value - sum((q.value for q in inside), Decimal(0))))
    return out


YTD_DAYS = {3: range(80, 101), 6: range(170, 201), 9: range(260, 291), 12: range(350, 381)}


def _months(fact: Fact) -> int | None:
    days = (fact.end - fact.start).days
    return next((m for m, r in YTD_DAYS.items() if days in r), None)


@dataclass(frozen=True)
class DerivedQuarter:
    start: date
    end: date
    value: Decimal
    filed: date
    form: str | None
    accession: str
    fiscal_year: int | None
    fiscal_period: str


def derive_from_cumulative(facts: list[Fact]) -> list[DerivedQuarter]:
    """A quarter that is not reported on its own is the difference of two cumulative figures.

    Many companies tag only year-to-date amounts in their 10-Qs. Q2 is the six-month figure minus
    the three-month figure, Q3 the nine-month minus the six-month, Q4 the year minus the nine
    months. First-filed values are used and every result is flagged derived (Data LB-03). The
    result is known when the later of the two filings was made. A quarter that is reported on its
    own is never replaced.
    """
    first = _first_filed(facts)
    direct_ends = {f.end for f in first.values() if f.kind == "quarter"}
    by_start: dict[date, dict[int, Fact]] = defaultdict(dict)
    for f in first.values():
        months = _months(f)
        if months:
            by_start[f.start][months] = f
    out = []
    for classes in by_start.values():
        for lo, hi, label in ((3, 6, "Q2"), (6, 9, "Q3"), (9, 12, "Q4")):
            a, b = classes.get(lo), classes.get(hi)
            if not a or not b:
                continue
            if any(abs((b.end - e).days) <= 3 for e in direct_ends):
                continue  # this quarter is reported on its own
            out.append(
                DerivedQuarter(
                    a.end + timedelta(days=1),
                    b.end,
                    b.value - a.value,
                    max(a.filed, b.filed),
                    b.form,
                    b.accession,
                    b.fiscal_year,
                    label,
                )  # fmt: skip
            )
    return out


def derived_quarters(facts: list[Fact]) -> list[DerivedQuarter]:
    """All derived quarters of one tag: cumulative differences first, the three-quarter sum after.

    The fourth quarter is the year minus the nine-month figure when that exists, because both are
    filed after any share split in the year. Summing three first-filed quarters would mix pre-split
    and post-split values (found with Apple, whose 7-for-1 split was in June 2014). The sum is
    only used for a year that the cumulative method does not cover.
    """
    out = derive_from_cumulative(facts)
    covered = [d.end for d in out]
    for year, q4_start, value in derive_fourth_quarters(facts):
        if not any(abs((year.end - e).days) <= 3 for e in covered):
            out.append(
                DerivedQuarter(
                    q4_start,
                    year.end,
                    value,
                    year.filed,
                    year.form,
                    year.accession,
                    year.fiscal_year,
                    "Q4",
                )  # fmt: skip
            )
    return out


def eps_rows(payload: bytes) -> list[EpsRow]:
    facts = extract_facts(payload, EPS_TAG)
    rows = [
        EpsRow(
            f.start,
            f.end,
            f.kind,
            f.fiscal_year,
            f.fiscal_period,
            f.value,
            False,
            f.form,
            f.accession,
            f.filed,
        )  # fmt: skip
        for f in facts
        if f.kind
    ]
    covered = {r.period_end for r in rows if r.period_kind == "quarter"}
    for d in derived_quarters(facts):
        if not any(abs((d.end - e).days) <= 3 for e in covered):
            rows.append(
                EpsRow(
                    d.start,
                    d.end,
                    "quarter",
                    d.fiscal_year,
                    d.fiscal_period,
                    d.value,
                    True,
                    d.form,
                    d.accession,
                    d.filed,
                )  # fmt: skip
            )
    return rows


@dataclass(frozen=True)
class FundamentalsRow:
    period_start: date
    period_end: date
    fiscal_year: int | None
    fiscal_period: str | None
    revenue: Decimal | None
    revenue_tag: str | None
    gross_profit: Decimal | None
    operating_income: Decimal | None
    derived: bool
    form: str | None
    accession: str
    filed: date


def fundamentals_rows(payload: bytes) -> list[FundamentalsRow]:
    revenue_facts: list[Fact] = []
    for tag in REVENUE_TAGS:
        found = extract_facts(payload, tag)
        have = {(f.start, f.end) for f in revenue_facts}
        revenue_facts += [f for f in found if (f.start, f.end) not in have]  # first tag per period
    gross = extract_facts(payload, GROSS_PROFIT_TAG)
    operating = extract_facts(payload, OPERATING_INCOME_TAG)
    metrics = {"revenue": revenue_facts, "gross": gross, "operating": operating}
    versions: dict[tuple[date, date, str], dict[str, Fact]] = defaultdict(dict)
    for name, facts in metrics.items():
        for f in facts:
            if f.kind == "quarter":
                versions[(f.start, f.end, f.accession)][name] = f
    rows = []
    for (start, end, accession), got in versions.items():
        any_fact = next(iter(got.values()))
        rev = got.get("revenue")
        rows.append(
            FundamentalsRow(
                start,
                end,
                any_fact.fiscal_year,
                any_fact.fiscal_period,
                rev.value if rev else None,
                rev.tag if rev else None,
                got["gross"].value if "gross" in got else None,
                got["operating"].value if "operating" in got else None,
                False,
                any_fact.form,
                accession,
                any_fact.filed,
            )  # fmt: skip
        )
    direct_ends = {r.period_end for r in rows}
    derived: dict[tuple[date, date, str], dict[str, object]] = {}
    for name, metric_facts in metrics.items():
        for dq in derived_quarters(metric_facts):
            if any(abs((dq.end - e).days) <= 3 for e in direct_ends):
                continue  # this quarter is reported on its own for some metric
            cell = derived.setdefault((dq.start, dq.end, dq.accession), {"quarter": dq})
            cell[name] = dq.value
    for cell in derived.values():
        quarter = cell["quarter"]
        assert isinstance(quarter, DerivedQuarter)
        rev_v, gross_v, op_v = cell.get("revenue"), cell.get("gross"), cell.get("operating")
        rows.append(
            FundamentalsRow(
                quarter.start,
                quarter.end,
                quarter.fiscal_year,
                quarter.fiscal_period,
                rev_v if isinstance(rev_v, Decimal) else None,
                "derived" if isinstance(rev_v, Decimal) else None,
                gross_v if isinstance(gross_v, Decimal) else None,
                op_v if isinstance(op_v, Decimal) else None,
                True,
                quarter.form,
                quarter.accession,
                quarter.filed,
            )  # fmt: skip
        )
    return rows


# ---- earnings releases and the T0 cutoff (Ingestion IG-15, decision C-17) -------------------


@dataclass(frozen=True)
class Release:
    accession: str
    filed: date
    accepted_utc: datetime
    items: str


def parse_earnings_releases(payloads: list[bytes]) -> list[Release]:
    """8-K filings that carry Item 2.02, from a submissions payload and its older pages."""
    out = []
    for payload in payloads:
        doc = json.loads(payload)
        block = doc["filings"]["recent"] if "filings" in doc else doc
        for i, form in enumerate(block.get("form", [])):
            items = block["items"][i] or ""
            if form.startswith("8-K") and "2.02" in items.split(","):
                accepted = datetime.strptime(
                    block["acceptanceDateTime"][i][:19], "%Y-%m-%dT%H:%M:%S"
                )
                out.append(
                    Release(
                        block["accessionNumber"][i],
                        date.fromisoformat(block["filingDate"][i]),
                        accepted.replace(tzinfo=UTC),
                        items,
                    )  # fmt: skip
                )
    return sorted(out, key=lambda r: (r.accepted_utc, r.accession))


def call_time_utc(stamp: str) -> datetime | None:
    """A call time from the transcript source, which is US Eastern with daylight saving (C-42).

    A stamp at 00:00:00 is a placeholder with no usable time, so it gives None.
    """
    moment = datetime.strptime(stamp, "%Y-%m-%d %H:%M:%S")
    if (moment.hour, moment.minute, moment.second) == (0, 0, 0):
        return None
    return moment.replace(tzinfo=EASTERN).astimezone(UTC)


def t0_cutoff(call_utc: datetime | None, accepted_utc: datetime | None) -> datetime | None:
    """The earlier of the call time and the 8-K acceptance time; whichever exists if only one."""
    known = [t for t in (call_utc, accepted_utc) if t is not None]
    return min(known) if known else None


# ---- loading ----------------------------------------------------------------------------------


def _payload(engine: Engine, url: str) -> tuple[int, bytes] | None:
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT payload_id, body FROM raw_payload WHERE source = :s AND url = :u "
                "ORDER BY retrieved_at DESC LIMIT 1"
            ),
            {"s": EDGAR_SOURCE, "u": url},
        ).first()
    return None if row is None else (int(row[0]), bytes(row[1]))


def load_financials(engine: Engine, company_id: str) -> dict[str, int]:
    """Parse the stored company-facts payload and write EPS and fundamentals rows.

    Reads the database only. Running it again adds nothing (Project-Wide EQ-07).
    """
    found = _payload(engine, FACTS_URL.format(cik=company_id))
    if found is None:
        raise LookupError(f"no stored company facts for {company_id}")
    payload_id, body = found
    counts = {"eps": 0, "fundamentals": 0}
    with run_record(engine, "load-financials", EDGAR_SOURCE) as run, engine.begin() as conn:
        eps = eps_rows(body)
        fund = fundamentals_rows(body)
        run.rows_read = len(eps) + len(fund)
        for r in eps:
            counts["eps"] += conn.execute(
                text(
                    "INSERT INTO eps_history (company_id, period_start, period_end, period_kind, "
                    "fiscal_year, fiscal_period, eps_diluted, derived, form, accession, filed_at, "
                    "payload_id) VALUES (:c, :s, :e, :k, :fy, :fp, :v, :d, :f, :a, :fi, :p) "
                    "ON CONFLICT ON CONSTRAINT eps_history_one_version DO NOTHING"
                ),
                {"c": company_id, "s": r.period_start, "e": r.period_end, "k": r.period_kind,
                 "fy": r.fiscal_year, "fp": r.fiscal_period, "v": r.eps, "d": r.derived,
                 "f": r.form, "a": r.accession, "fi": r.filed, "p": payload_id},
            ).rowcount  # fmt: skip
        for g in fund:
            counts["fundamentals"] += conn.execute(
                text(
                    "INSERT INTO fundamentals_filing (company_id, period_start, period_end, "
                    "fiscal_year, fiscal_period, revenue, revenue_tag, gross_profit, "
                    "operating_income, derived, form, accession, filed_at, payload_id) VALUES "
                    "(:c, :s, :e, :fy, :fp, :rev, :tag, :gp, :oi, :d, :f, :a, :fi, :p) "
                    "ON CONFLICT ON CONSTRAINT fundamentals_one_version DO NOTHING"
                ),
                {"c": company_id, "s": g.period_start, "e": g.period_end, "fy": g.fiscal_year,
                 "fp": g.fiscal_period, "rev": g.revenue, "tag": g.revenue_tag,
                 "gp": g.gross_profit, "oi": g.operating_income, "d": g.derived, "f": g.form,
                 "a": g.accession, "fi": g.filed, "p": payload_id},
            ).rowcount  # fmt: skip
        run.rows_written = counts["eps"] + counts["fundamentals"]
    return counts
