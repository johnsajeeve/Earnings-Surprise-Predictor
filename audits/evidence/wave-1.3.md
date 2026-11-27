# Wave 1.3: universe and identifiers

Measured 23 November 2026, branch `build/wave-0-1`, on top of commit `8b3c6d3`. Decisions: C-47 (CIK-change rule, Wikipedia as secondary source, selection rule). Output files: `src/earnings/universe.csv`, `src/earnings/universe_tickers.csv`, and in `audits/evidence/wave-1.3/` the `review_list.csv` and `report.json`.

## Wave 1.3

Requirements: IM-01, IM-02, IM-03, TH-05, IG-13, IG-21, DB-04 (AC1). TH-06 (survivorship gap) waits for the comparison run in Wave 1.7.

## Commands run

- Wrote the tests first, then `clients/public.py`, `membership.py` (parsers), `universe.py` (matching, selection), `universe_build.py` (fetch, build, load).
- `python -m earnings.universe_build fetch` in the real stack: four source files stored as received (membership CSV 28,058 bytes; Wikipedia API response 647,517; SEC `company_tickers.json` 795,972; SEC `cik-lookup-data.txt` 40,528,721).
- `python -m earnings.universe_build build`: matching, selection, and one SEC submissions request for each candidate checked. The selection was run twice and the two outputs were byte-identical.
- `python -m earnings.universe_build load` on the project database with the first 5 companies, then all 100, then again.
- Full-repository and CI-style pytest, `ruff`, `ruff format --check`, `mypy`, matrix, generator, reference, requirement, plan and pin checks. Faults planted in the matching rules.
- While building I read all 23 links of the first rename rule by eye. That found a wrong link (`HCP`, two renames on one day) and a merger taken for a rename (`MWV`); the rule was tightened and the review repeated.

## Output

| Run | Passed | Failed | Skipped | Expected failures |
|---|---|---|---|---|
| Wave 1.2 after audit fixes (full repo) | 111 | 0 | 552 | 3 |
| Now, full repository | 125 | 0 | 543 | 3 |
| Now, CI style | 106 | 0 | 563 | 2 |

`ruff check`, `ruff format --check` (83 files) and `mypy` (31 source files) pass. No test that passed before fails now. Four faults (accept a reused ticker, guess on an ambiguous day, rename from any date, and others) made 4 tests fail; the file was restored.

Real data, from `report.json` and the loaded database:

- Tickers in the membership file: 1,209. Matched to one CIK: 778 (578 by the SEC ticker file, 179 by exact name, 21 by the rename rule). Not matched: 431.
- Current tickers matched: 502 of 503. Removed-in-window tickers matched: 168 of 230 (62 not matched: 6, 10, 10, 9, 10, 5, 2, 5, 2, 3 for 2015 to 2024).
- Companies: 742 (499 current, 144 removed in 2015 to 2024, 99 left before 2015).
- Year-end counts, tickers against companies (each CIK once, each unmatched ticker once): 2015 502 and 499; 2016 506 and 503; 2017 to 2021 505 and 502; 2022 to 2024 503 and 500. The difference is 3 companies that hold two share classes.
- Selection (seed 2031): 80 current and 20 removed, every year of 2015 to 2024 has a removed company, every removed company has a removal date and a reason. Excluded by the CIK rule: XOM, DIS (the new Disney CIK first filed in 2018), Baker Hughes (BHGE and BKR), TechnipFMC, WellCare.
- Loaded into the project database: 5 companies, then 100 (the five not repeated); a third run changed nothing. The database now holds 109 companies (the 100 and 9 from the capture list), 109 ticker spells, 105 membership periods of which 80 are open and 20 carry a removal reason.
- The daily consensus capture list is now 89 companies: the original 10 plus the current members of the 100 list that were not among them.

## Result per requirement

- IM-01: PASS for the check as written, against the nominal 500: companies at each year-end are 499 to 503, within 5, and the difference from the raw ticker count is explained by share classes (3). The reference is 500 because no published yearly count was available from an approved source (see Not verified).
- TH-05: PASS on the same data.
- IM-02: PASS for the loaded list: removed companies in every year 2015 to 2024, each with a removal date and a reason. The reasons are Wikipedia's wording and sometimes describe the paired event (for example the reason shown for Brighthouse Financial and for Fluor is about a different company).
- IM-03: PASS for the ten known renames (14 tested, all linked): one company, one continuous membership period across the old and new ticker.
- DB-04: PASS for AC1 (ten ticker changes join to one history in the database).
- IG-13: PARTIAL. Matching, the review list and the ten renames work, but 431 of 1,209 tickers have no CIK. The rename rule goes beyond the written rules (see drift).
- IG-21: PASS. The same job loads 5 or 100 companies from a list file and is safe to repeat.
- TH-06: not started (Wave 1.7).

## Not verified

- Whether the 100-company list is correct company by company. Matches are exact on normalised names and logged, and a hand check of the full list was not done. The Phase 0 audit shows that tests alone miss matching errors: a human check of the review list is needed.
- The published yearly count of the index from an approved source. 500 is the nominal figure.
- Reasons are not checked against primary documents.
- 62 removed tickers are unmatched and 32 removed tickers are absent from the Wikipedia table; transcripts and EPS for them cannot be loaded in later waves.
- GitHub Actions on this change.

## Drift found

- DR-16: the rename rule (a ticker that ends the day another starts, with no index change recorded by Wikipedia, linked to the same CIK) is not in IG-13, which names only the SEC ticker file and name matching. It links 21 tickers, all read by hand, one wrong link (MWV) is caught later by the CIK rule. Needs John's confirmation as a method.
- DR-17: reasons are copied from the source and can describe the paired event.
- 431 tickers are unmatched. Companies left out are mostly older removals; the removed-company sample is therefore biased toward companies the sources describe well.
- Reused tickers: the SEC file lists tickers for other companies than the index member (found with BBT). A removed ticker is accepted only if a name agrees; 132 were rejected on that rule.

## Assumptions

- 500 is the reference count. Share classes are counted from matched CIKs.
- The 100-company list is stored in the repository (`src/earnings/universe.csv`) because it is data that every environment needs and it is small (5 KB).

## Measured values

- Hours for this wave: about 8. Acceptance checks moved to a real result: DB-04-AC1, IM-01-AC1, IM-02-AC1, IM-02-AC2, IM-03-AC1, IG-13-AC1, IG-13-AC2, IG-21-AC1, TH-05-AC1 (9).

## Update, 24 November 2026, after the second independent audit

The 100-company list was selected again. The first build treated any open membership as "current", so four companies that joined the index in 2025 or 2026 had been selected, against decision C-47. `current` now means in the index on 31 December 2024. Because a seeded draw changes completely when its pool changes, 72 of the 100 companies are different. Current figures: 100 companies (80 in the index at the end of 2024, 20 removed with a date and a source reason, every year 2015 to 2024 covered), 494 current, 144 removed, 31 later and 73 out of window among the 742 matched companies, and 6 companies excluded by the CIK rules. The year-end company counts did not change (they come from the whole membership file). Removal reasons that name another company are marked. A ticker to CIK map is now stored (`ticker_cik_map.csv`) and used by a test that recomputes the year-end counts.
