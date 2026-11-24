# Wave 1.4: financial data (EPS history, fundamentals, earnings-release times)

Built 23 and 24 November 2026, branch `build/wave-0-1`, on top of commit `ae76eee`. The wave was finished on 24 November together with an inspection of Waves 0.1 to 1.4 (see inspection-2026-11-24.md).

## Wave 1.4

Requirements: AE-04, AE-03-AC1, FD-01 to FD-03, IG-09, IG-15, DB-11, LB-03 (derived quarters). Plan change (logged in the plan and the coverage map): AE-01 to Wave 1.6, AE-02, FD-04, TH-12, AE-03-AC2 and TH-06 to Wave 1.7, prices (PX-01 to PX-03) to a new Wave 1.8 that waits for John's approval of price tables, which Product Section 11 does not list.

## Commands run

- Tests first, then migration 0005 (`eps_history`, `fundamentals_filing`, their as-of and first-filed functions, append-only for the worker), `financials.py` (parsers, derivation, release parsing, loader), `backfill.py`.
- Backfill of the 100 companies on the real stack: `python -m earnings.backfill /app/src/earnings/universe.csv`.
- Real-data checks by SQL on the loaded tables.
- Full-repository and CI-style pytest, `ruff`, `ruff format --check`, `mypy`, matrix, generator, reference, requirement, plan and pin checks. Faults: the as-of comparison changed to `<=`, and the cumulative derivation removed.

## Output

| Run | Passed | Failed | Skipped | Expected failures |
|---|---|---|---|---|
| Last commit (full repo) | 125 | 0 | 543 | 3 |
| Now, full repository | 145 | 0 | 534 | 3 |
| Now, CI style | 124 | 0 | 555 | 2 |

`ruff check`, `ruff format --check` (89 files), `mypy` (34 source files) pass. The two faults made 4 tests fail; the files were restored. Regression: the committed matrix at the last commit lists 111 real tests; none is missing or failing now (5 names differ only because JUnit adds a parameter suffix to parametrised tests).

Real data, 100 companies (117 requests for the first full run, 2 more for three replacement companies):

- EPS rows: 15,834, of which 582 are derived quarters. 98 of 100 companies have EPS history (Visa and Danaher have none in SEC's company-facts data). 84 have quarterly EPS ending by 2014-09-30 and 67 of those have 10 or more, which is what LB-02 needs for a 2015 event. The rest are companies that listed after 2012 (Solventum, Otis, Reddit and others) or whose diluted EPS the API does not carry as an undimensioned fact (Kimberly-Clark, Omnicom, Fifth Third).
- Versions: 332 of 6,389 EPS periods carry more than one distinct value, because a later filing restated them. Example, Apple fiscal 2014 Q1: first filed 14.50 on 2014-01-28, then 2.07 after the 7-for-1 split of June 2014.
- Fundamentals rows: 14,555 for 99 companies; revenue for 98, gross profit for 49, operating income for 82 (banks and others do not report gross profit).
- Bulk files (IG-09): `companyfacts.zip` was last modified 2026-11-21 05:08 GMT and 2026-11-24 04:13 GMT at the two observations (size 1,428,910,853 to 1,429,204,054 bytes), `submissions.zip` 2026-11-21 05:15 and 2026-11-24 04:21 GMT. Both were refreshed; two observations three days apart do not prove every night. Not used: 117 requests for 100 companies is far below the limit and the zip is 1.4 GB.

## Result per requirement

- AE-04: PASS for `eps_history`: after a simulated correction the first-filed value is unchanged, the correction is a later row, and the worker cannot update or delete.
- FD-02: PASS: a filing dated D or later is not visible at D. FD-03: PASS: a restatement leaves earlier as-of reads unchanged.
- FD-01: PARTIAL. AC1 passes (every row has a filing date, form and accession). AC2 (20 values against the filing) is a hand check for Wave 1.7. The growth and margin features are Wave 2.3.
- AE-03: AC1 passes (one basis, `gaap`). AC2 is the test VL-07 in Wave 1.7.
- IG-15: PARTIAL. Parsing of earnings-release 8-Ks (including older pages), the Eastern-time call stamp and the cutoff (earlier of call and acceptance; a 00:00:00 placeholder gives the filing time) are tested; storing the time on an event is Wave 1.6.
- DB-11: PASS: truncating the derived tables and rebuilding from the stored payload gives identical table hashes.
- IG-09: NOT MET as written (bulk files not used, a stated decision); the question the requirement asks (are the files refreshed) is answered above.
- LB-03: the derivation works, flags every derived row and prefers the year minus the nine-month figure, because summing first-filed quarters across a share split gives nonsense.

## Not verified

- Values against the filings (FD-01-AC2) and against the press releases (AE-02, TH-12): Wave 1.7.
- Whether Q1 to Q3 versions that differ only by a split are handled in the label: split adjustment is LB-05 (Wave 1.6).
- Revenue tag choice is the first tag in a fixed list; a company that changed tags mid-history gets rows from whichever tag it used (`revenue_tag` records which).
- GitHub Actions on this change.

## Drift found

- DR-18: the columns of `eps_history` and `fundamentals_filing` extend the field lists in Product Section 11 (period dates, kind, accession, filing date per version, derived flag, tag). Needs John's approval and a Section 11 update.
- DR-19: the SEC company-facts API leaves out facts that carry a dimension, so some companies' diluted EPS is missing or has only two quarters. Coverage is reported above. A fallback source (yfinance earnings dates) has not been built.
- Found while building: a first selection of the 100 companies included two old registrants with the same name as the index member (Sealed Air, Starwood) and one company the SEC holds no facts for (Lorillard). The selection check now also requires that the CIK was still filing during the index years and that SEC facts exist; the three were replaced (Lincoln National, FLIR, SVB Financial), and the stale rows were removed from the database by the superuser, as the application roles cannot delete.
- Found on 24 November: after a restart the worker came up before PostgreSQL finished recovering and its start-up catch-up check failed. The catch-up is now a retried task. Three of 89 captures failed on Yahoo timeouts; failed tickers now get one more attempt in the same run.

## Assumptions

- Quarter means a 3-month period of 80 to 100 days; year 350 to 380 days; cumulative figures 6 months (170 to 200 days) and 9 months (260 to 290 days).
- Fiscal year and fiscal period are stored as the filing tagged them. They describe the filing, not always the period, and are not used for matching.

## Measured values

- Hours for this wave: about 10 over two days, including the matching fixes it exposed. Acceptance checks moved to a real result: AE-04-AC1, AE-03-AC1, FD-01-AC1, FD-02-AC1, FD-03-AC1, IG-15-AC1, DB-11-AC1, IG-16-AC1 and EQ-07-AC1 (9).
- Backfill duration: about 1 minute for 117 requests plus parsing.
