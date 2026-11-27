# Inspection of Waves 0.1 to 1.4, 24 November 2026 (refreshed after the second independent audit)

Generated from `audits/test_matrix.json` and `audits/plan_coverage.txt` by a short script. It states what the tests show. It is not an audit result: PASS needs the independent audit (`phase-0-independent.md`, `phase-1-independent.md`).

A check counts as real when a test that names it runs and passes. Requirements with no acceptance check (needs, goals, conflicts, gates) are not listed.

## Checks per wave

| Wave | Real | Expected failure | Not tested |
|---|---|---|---|
| 0.1 | 4 | 1 | 1 |
| 0.2 | 7 | 1 | 0 |
| 0.3 | 1 | 0 | 5 |
| 1.1 | 9 | 0 | 4 |
| 1.2 | 6 | 0 | 0 |
| 1.3 | 9 | 0 | 0 |
| 1.4 | 6 | 0 | 2 |
| **all** | **42** | **2** | **12** |

## Requirements whose every check is real

AE-04, DB-01, DB-03, DB-04, DB-07, DB-08, DB-09, DB-10, DB-11, DB-16, EQ-07, FD-02, FD-03, IG-02, IG-03, IG-08, IG-13, IG-15, IG-16, IG-21, IM-01, IM-02, IM-03, PL-01, PL-02, PL-05, SR-01, SR-04, SR-08, SR-09, TH-05, TH-14

## Requirements with some real checks and some not

| Requirement | Wave | Priority | Real of all | Checks not yet real |
|---|---|---|---|---|
| FD-01 | 1.4 | Must | 1 of 2 | FD-01-AC2 |
| IG-01 | 1.1 | Must | 1 of 2 | IG-01-AC2 |
| IG-05 | 1.1 | Must | 1 of 2 | IG-05-AC1 |

## Requirements with no real check yet

| Requirement | Wave | Priority | Checks |
|---|---|---|---|
| DB-02 | 0.2 | Must | DB-02-AC1 |
| IG-04 | 1.1 | Should | IG-04-AC1 |
| IG-07 | 1.1 | Must | IG-07-AC1 |
| IG-09 | 1.4 | Should | IG-09-AC1 |
| SR-05 | 0.1 | Should | SR-05-AC1 |
| SR-06 | 0.1 | Must | SR-06-AC1 |
| SR-10 | 0.3 | Must | SR-10-AC1, SR-10-AC2 |
| TH-10 | 0.3 | - | TH-10-AC1 |
| VL-12 | 0.3 | Must if a vendor estimate source is adopted | VL-12-AC1, VL-12-AC2 |

## Where a real check is not the whole requirement (my judgement, 24 November 2026)

Checks are narrower than some requirement texts. These are the gaps between a passing check and the full wording. Nothing here is hidden by the tables above.

| Requirement | What the check covers | What the text asks beyond it |
|---|---|---|
| DB-08, DB-09 | the three-plus tables that exist | `ActualEps` (Wave 1.6); the as-of scan has no feature code to scan yet |
| DB-02 | three roles | the agent role (Wave 5.1); a strict expected failure says so |
| SR-01 | every source the code uses has a row | sources not yet used (Alpha Vantage, FMP) have no row |
| SR-04 | hash of each stored payload | the source version is not stored (DR-14, needs John) |
| IM-01, TH-05 | company counts within 5 of 500 on the real data | 500 is the nominal count, not a published yearly figure |
| IM-02 | 20 removed companies, each with a date and reason | reasons are Wikipedia's wording; 62 of 230 removed tickers have no CIK |
| IG-13 | ten renames, review list | the rename rule goes beyond the written methods (DR-16); 431 of 1,209 tickers unmatched |
| IG-15 | the cutoff function and parsing | storing the time on an event (Wave 1.6) |
| FD-01 | rows carry filing date, form, source | the growth and margin features (Wave 2.3); the 20-value hand check (Wave 1.7) |
| AE-04 | `eps_history` keeps the first-filed value | the same for `ActualEps` (Wave 1.6) |
| SR-10 | capture, gap report, retry, catch-up | AC1 and AC2 need real days; the 22:30 UTC schedule has not been seen firing |
| IG-01, IG-07 | idempotent tasks, EDGAR limit | killing a worker mid-task (Wave 7.1); the Alpha Vantage counter (Wave 1.5) |
| PL-05, DB-16 | clean-database migration, test database | none known |

## Checks still not real, and who can close them

| Check | Reason | Closed by |
|---|---|---|
| SR-05-AC1 | needs a written answer or decision from John | John (D-21) |
| IG-05-AC1 | needs run times for three more jobs (D-45) | John, then Waves 1.4 to 1.7 |
| SR-06-AC1 (expected failure) | no fallback for the announcement time; other fallbacks untested | John (DR-10) |
| DB-02-AC1 (expected failure) | agent role | Wave 5.1 |
| IG-04-AC1 | the longest task of the 100-company run | Wave 1.7 measurement |
| SR-10-AC1, SR-10-AC2 | real days and events | time, Wave 1.6 |
| VL-12-AC1, VL-12-AC2, TH-10-AC1 | apply only if a vendor estimate source is adopted; none is (Finnhub free plan tested and not usable) | not applicable unless John adopts one |
| IG-07-AC1, IG-01-AC2, IG-09-AC1 | Alpha Vantage counter, worker kill, bulk files not used | Waves 1.5, 7.1, John |
| FD-01-AC2, TH-12 and AE-03-AC2 | hand checks against filings and press releases | Wave 1.7 |
