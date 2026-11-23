"""The company list: membership, identifiers, renames, selection, loading
(Data IM-01 to IM-03, TH-05; Ingestion IG-13, IG-21; Database DB-04).

The fixtures in tests/fixtures are real data, trimmed (see README_universe.md). Companies built
by the selection tests are SYNTHETIC and say so.
"""

import csv
import json
from datetime import date, timedelta
from pathlib import Path

import pytest
from sqlalchemy import text

from earnings import membership as m
from earnings import universe as u
from earnings.universe_build import load

FX = Path(__file__).parent / "fixtures"
ROOT = Path(__file__).resolve().parents[1]
LIST = ROOT / "src" / "earnings" / "universe.csv"

# Renames with the same SEC CIK before and after. Each pair is (old ticker, new ticker).
RENAMES = [
    ("UTX", "RTX"), ("ANTM", "ELV"), ("CTL", "LUMN"), ("BBT", "TFC"), ("MYL", "VTRS"),
    ("LB", "BBWI"), ("PKI", "RVTY"), ("RE", "EG"), ("ABC", "COR"), ("HRS", "LHX"),
    ("TMK", "GL"), ("BHGE", "BKR"), ("FB", "META"), ("DISCA", "WBD"),
]  # fmt: skip


@pytest.fixture(scope="module")
def sources():
    spells = m.parse_membership_spells((FX / "membership_sample.csv").read_bytes())
    sec = m.parse_sec_tickers((FX / "sec_tickers_sample.json").read_bytes())
    changes = m.parse_wikipedia_history((FX / "wikipedia_history_sample.json").read_bytes())
    lookup = m.parse_cik_lookup((FX / "cik_lookup_sample.txt").read_bytes())
    resolved, review = u.resolve_all(spells, sec, changes, lookup)
    return spells, sec, changes, resolved, review


@pytest.mark.req("IG-13")
@pytest.mark.code("src/earnings/membership.py")
def test_names_are_normalised_for_exact_matching_only():
    assert m.normalise_name("The Walt Disney Company") == "WALT DISNEY"
    assert m.normalise_name("Facebook, Inc.") == m.normalise_name("FACEBOOK INC") == "FACEBOOK"
    assert m.normalise_name("AT&T Inc.") == "AT AND T"
    assert m.normalise_name("Smurfit Westrock plc") == "SMURFIT WESTROCK"
    assert m.normalise_name("Marsh & McLennan Companies, Inc.") != m.normalise_name("Marsh Inc")
    assert m.ticker_key("BRK.B") == "BRK-B"


@pytest.mark.req("IG-13")
@pytest.mark.code("src/earnings/membership.py")
def test_the_stored_source_files_parse_offline(sources):
    spells, sec, changes, resolved, _ = sources
    assert len(spells) > 30 and all(s.end is None or s.end > s.start for s in spells)
    assert len(sec["META"]) == 1 and sec["META"][0][0] == "0001326801"
    assert any(c.added == "FB" and "Facebook" in c.added_name for c in changes)
    full = m.parse_membership_spells((FX / "sp500_ticker_start_end_full.csv").read_bytes())
    assert len(full) == 1262 and len({s.ticker for s in full}) == 1209


@pytest.mark.req("IG-13-AC1", "IM-03-AC1")
@pytest.mark.code("src/earnings/universe.py", "src/earnings/membership.py")
def test_ten_known_renames_resolve_to_one_company(sources):
    _, _, _, resolved, _ = sources
    linked = [(a, b) for a, b in RENAMES if a in resolved and b in resolved
              and resolved[a].cik == resolved[b].cik]  # fmt: skip
    assert len(linked) >= 10, f"only {len(linked)} of {len(RENAMES)} renames linked: {linked}"
    assert linked == RENAMES  # all of the listed renames link, so the list is exact


@pytest.mark.req("IG-13-AC2")
@pytest.mark.code("src/earnings/universe.py")
def test_every_match_that_is_not_a_plain_ticker_match_is_in_the_review_list(sources):
    _, _, _, resolved, review = sources
    logged = {(r["ticker"], r["method"]) for r in review}
    for ticker, r in resolved.items():
        if r.method != "sec-ticker":
            assert (ticker, r.method) in logged, f"{ticker} matched by {r.method} but not listed"
    assert any(r["method"] == "name" for r in review)
    assert any(r["method"] == "rename-adjacent" for r in review)


@pytest.mark.req("IG-13")
@pytest.mark.code("src/earnings/universe.py")
def test_a_ticker_that_the_sec_gives_to_another_company_is_not_accepted(sources):
    _, sec, _, resolved, review = sources
    beacon_cik = sec["BBT"][0][0]
    assert resolved["BBT"].cik != beacon_cik  # BBT is BB&T, now Truist, not Beacon Financial
    assert resolved["BBT"].cik == resolved["TFC"].cik
    assert any(r["ticker"] == "BBT" and r["method"] == "ticker-reused" for r in review)


@pytest.mark.req("IG-13")
@pytest.mark.code("src/earnings/universe.py")
def test_two_renames_on_one_day_are_not_guessed(sources):
    _, _, _, resolved, review = sources
    # SYMC to NLOK and HCP to PEAK both happened on 2019-11-05, so neither is linked by adjacency.
    assert "HCP" not in resolved or resolved["HCP"].method != "rename-adjacent"
    assert any(r["method"] == "ambiguous-rename" for r in review)


@pytest.mark.req("DB-04-AC1", "IM-03-AC1", "IG-13-AC1")
@pytest.mark.code("src/earnings/universe_build.py", "src/earnings/migrations/versions")
def test_join_on_company_id_across_ten_renames_gives_one_continuous_history(
    sources, test_db, tmp_path
):
    from earnings.db import get_engine

    spells, sec, changes, resolved, _ = sources
    companies = u.group_companies(spells, resolved, sec, changes)
    wanted = [resolved[a].cik for a, _ in RENAMES]
    u.write_list(tmp_path / "list.csv", companies, wanted, changes)
    load(get_engine("worker"), tmp_path / "list.csv")
    with get_engine("api").connect() as conn:
        for old, new in RENAMES:
            cik = resolved[old].cik
            old_end = max(s.end for s in spells if s.ticker == old and s.end)
            before = conn.execute(
                text("SELECT company_for_ticker(:t, :d)"),
                {"t": old, "d": old_end - timedelta(days=1)},
            ).scalar_one()
            after = conn.execute(
                text("SELECT company_for_ticker(:t, :d)"), {"t": new, "d": old_end}
            ).scalar_one()
            assert before == after == cik, (old, new)
            # one membership period spans both tickers: the history has no break at the rename
            rows = conn.execute(
                text("SELECT valid_from, valid_to FROM index_membership WHERE company_id = :c"),
                {"c": cik},
            ).all()
            day_before = old_end - timedelta(days=1)

            def covers(row, day):
                return row[0] <= day and (row[1] is None or day < row[1])

            spanning = [r for r in rows if covers(r, day_before) and covers(r, old_end)]
            assert len(spanning) == 1, (old, new, rows)


@pytest.mark.req("IG-21-AC1")
@pytest.mark.code("src/earnings/universe_build.py", "src/earnings/universe.csv")
def test_the_same_job_runs_for_5_and_for_100_companies_from_a_list_file(test_db):
    from earnings.db import get_engine

    engine = get_engine("worker")
    first = load(engine, LIST, limit=5)
    assert first["companies"] == 5
    full = load(engine, LIST)
    assert first["companies"] + full["companies"] == 100  # the 5 already there are not repeated
    with get_engine("api").connect() as conn:
        count = conn.execute(text("SELECT count(*) FROM company")).scalar_one()
        open_periods = conn.execute(
            text("SELECT count(*) FROM index_membership WHERE valid_to IS NULL")
        ).scalar_one()
    assert (count, open_periods) == (100, 80)
    assert load(engine, LIST) == {"companies": 0, "ticker_spells": 0, "membership_periods": 0}


@pytest.mark.req("IM-02-AC1", "IM-02-AC2")
@pytest.mark.code("src/earnings/universe.csv")
def test_removed_companies_cover_every_year_and_carry_a_date_and_a_reason():
    rows = list(csv.DictReader(LIST.open(encoding="utf-8")))
    removed = [r for r in rows if r["status"] == "removed"]
    assert len(removed) == 20 and len(rows) - len(removed) == 80
    assert {r["removal_date"][:4] for r in removed} == {str(y) for y in range(2015, 2025)}
    assert all(r["removal_date"] and r["removal_reason"] for r in removed)


@pytest.mark.req("IM-01")
@pytest.mark.code("src/earnings/universe.py")
def test_year_end_counts_on_the_real_membership_file():
    full = m.parse_membership_spells((FX / "sp500_ticker_start_end_full.csv").read_bytes())
    counts = u.year_end_counts(full)
    assert counts == {2015: 502, 2016: 506, 2017: 505, 2018: 505, 2019: 505, 2020: 505,
                      2021: 505, 2022: 503, 2023: 503, 2024: 503}  # fmt: skip


@pytest.mark.req("IM-01")
@pytest.mark.code("src/earnings/universe.py")
def test_company_counts_count_each_company_once_and_explain_share_classes():
    """SYNTHETIC spells: two tickers of one company, one unmatched ticker."""
    day = date(2020, 1, 1)
    spells = [m.Spell("AAA", day, None), m.Spell("AAB", day, None), m.Spell("BBB", day, None),
              m.Spell("CCC", day, None)]  # fmt: skip
    resolved = {t: u.Resolution(t, cik, "sec-ticker", t)
                for t, cik in (("AAA", "1"), ("AAB", "1"), ("BBB", "2"))}  # fmt: skip
    counts = u.year_end_company_counts(spells, resolved)[2020]
    assert counts == {
        "tickers": 4,
        "companies": 3,
        "second_share_classes": 1,
        "unresolved_tickers": 1,
    }


@pytest.mark.req("IM-01-AC1", "TH-05-AC1")
@pytest.mark.code("audits/evidence/wave-1.3/report.json")
def test_the_real_year_end_company_counts_are_within_five_of_500():
    from requirement_support import repo_path

    report = json.loads(repo_path("audits/evidence/wave-1.3/report.json").read_text("utf-8"))
    for year, row in report["year_end_company_counts"].items():
        assert abs(row["companies"] - 500) <= 5, year
        assert row["tickers"] - row["companies"] == row["second_share_classes"], year


def _company(cik, name, spells):
    return u.Company(cik, name, {t: [m.Spell(t, a, b)] for t, a, b in spells})


@pytest.mark.req("IM-02")
@pytest.mark.code("src/earnings/universe.py")
def test_selection_is_reproducible_covers_every_year_and_applies_the_cik_rule():
    """SYNTHETIC companies: 200 current, 60 removed over 2015 to 2024, and one 'successor'."""
    companies = {}
    for i in range(200):
        companies[f"{i:010d}"] = _company(
            f"{i:010d}", f"CUR {i}", [(f"C{i}", date(2000, 1, 1), None)]
        )
    for i in range(60):
        year = 2015 + i % 10
        cik = f"{1000 + i:010d}"
        companies[cik] = _company(cik, f"REM {i}", [(f"R{i}", date(2005, 1, 1), date(year, 6, 1))])
    successor = "0000000007"

    def covers(company):
        return (company.cik != successor, "successor CIK")

    first = u.select_universe(companies, covers)
    again = u.select_universe(companies, covers)
    assert (first.current, first.removed) == (again.current, again.removed)  # fixed seed
    assert len(first.current) == 80 and len(first.removed) == 20
    assert {companies[c].last_end.year for c in first.removed} == set(range(2015, 2025))
    assert successor not in first.current + first.removed
    other = u.select_universe(companies, covers, seed=1)
    assert other.current != first.current  # the seed matters


@pytest.mark.req("IG-13")
@pytest.mark.code("src/earnings/universe.py")
def test_touching_and_overlapping_spells_merge_into_one_period():
    a, b, c = date(2015, 1, 1), date(2018, 1, 1), date(2020, 1, 1)
    s = lambda t, x, y: m.Spell(t, x, y)  # noqa: E731
    assert u.merge_periods([s("A", a, b), s("B", b, None)]) == [(a, None)]  # a rename
    assert u.merge_periods([s("A", a, c), s("B", b, None)]) == [(a, None)]  # two share classes
    assert u.merge_periods([s("A", a, b), s("A", c, None)]) == [(a, b), (c, None)]  # a gap stays
