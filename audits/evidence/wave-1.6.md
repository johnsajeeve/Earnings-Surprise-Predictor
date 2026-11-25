# Wave 1.6: events and the time-series SUE (PARTIAL, 25 November 2026)

Brief: `wave-1.6-task-brief.md`, approved by John on 25 November 2026 (his message), including the three points (extra columns, one event per kept linked transcript, split factors inferred when the price tables are absent, flagged D-47 j to l).

## Commands and results

| Check | Result |
|---|---|
| ruff format, ruff check, mypy | PASS (104 files formatted, all checks passed, 41 source files) |
| Full repository pytest | PASS: 182 passed, 534 skipped, 3 expected failures, 0 failed |
| CI-style pytest (image rebuilt) | PASS: 161 passed, 556 skipped, 2 expected failures, 0 failed |
| Migration 0008 on the project database | applied (head 0008); PL-05 schema test updated and passing |
| Test matrix rebuilt, verified | checks whose best test is real: 94 (was 71) |
| Mutation checks on `label.py` (13) | 13 of 13 killed. One survived first (the reporting-window length); a test was added and it is killed |

One real defect was found by a test and fixed: with floating point arithmetic a series of equal differences gave a standard deviation of about 1e-16, not zero, and a label of 6.4e15. The label now uses exact decimal arithmetic.

## Real data

`python -m earnings.events build` on the 3,183 kept transcripts of the Wave 1.5 load, and `report`:
- Label available (SUE): 2,619 events (82%). Unavailable: 243 no quarter of that period in the stored EPS, 178 fewer than 6 prior seasonal differences, 143 no quarterly EPS stored for the company (DR-19: for example Kimberly-Clark, eBay, PepsiCo, FedEx, Danaher). Per year in `wave-1.6/wave-1.6-report.json` (LB-02).
- 24 events are excluded for a transcript dated more than one trading day after the announcement (FR-02). 564 events are marked incomplete (no information date because the label is unavailable).
- Real Apple facts: the 7-for-1 split of June 2014 is detected from the facts alone (ratio 7.0, known from 23 July 2014), and it is not seen before that date.
- Coverage (IG-22): releases with a transcript, still in the index 2,794 of 3,069 (91%); left the index 389 of 661 (59%). 547 releases have no transcript, all listed in `wave-1.6/coverage_missing.csv`. DR-25.
- Size (DB-15): database 677,035,031 bytes now (measured, 93 companies; the transcript tables and stored payloads are 84%). Full index of 500 companies about 3.6 GB (ESTIMATE, a straight company ratio). DR-26 for the label gaps.

## Result per requirement

| ID | Status | Basis |
|---|---|---|
| LB-01 | PARTIAL | Hand calculation to 4 decimals passes. Not yet compared with the press release (LB-03, Wave 1.7). Sample standard deviation is my choice (D-47 j) |
| LB-02 | PASS locally | Fewer than 6 differences and zero variance give an unavailable label; per-year counts reported |
| LB-04 | PASS locally | Planted restatement before, on and after D leaves the label unchanged; Python as-of rule equals the SQL function |
| LB-05 | PARTIAL | Passes with inferred splits (D-47 k), real Apple split detected. The dated split factors from the price source (PX-01) are not built; waits for John's price tables |
| CE-05 | PARTIAL | Route stored, constraint, mixed set raises. No dataset-version table exists yet to hold the route (Wave 2.4) |
| FR-02 | PASS locally | Three dates non-null or incomplete; late transcript excluded |
| FR-14 | PASS locally | AC1 (a new snapshot is a new row, the earlier one unchanged) and AC2 (snapshot on or after D not used) both tested |
| IG-20 | PARTIAL | The date gate fails on a planted input dated at D. The planted-future tests for the whole pipeline are Waves 1.7 and 2.4 |
| IG-22 | PASS locally | Hand count on 5 synthetic companies matches; real report produced (coverage by year, removed companies apart, every missing release listed) |
| DB-06 | PARTIAL | Missing dates and bad route refused. The probability range check has no table yet (predictions, Phase 3) |
| DB-15 | PASS locally | Size report with measured and estimated apart |
| TH-11 | PASS locally | Window 8, minimum 6 |
| PL-04 | PASS locally | Fixture with 9 quarters gets no label and the stored reason `fewer than 6 prior seasonal differences` |
| DB-13 | PASS locally | A failure injected in the middle of the build leaves only whole events; a rerun gives the clean-run count and a third run changes nothing |
| LB-02-AC2, CE-05-AC2, SC-07-AC2 | PASS locally | Zero-variance fixture is unavailable; two routes in one set raise |
| AE-01, IG-06, NFR-09 | NOT TESTED | AE-01 needs the EPS filing date of the quarter itself (stored as the label's own filing, not yet a column); IG-06 needs the capture-gap flag on events; NFR-09 needs a 100-company timing run |
| TH-15 | NOT TESTED | Null-rate gate is DV-02, Wave 1.7 |

Not an independent audit. Open for John: D-47 (j) to (l), DR-25, DR-26.
