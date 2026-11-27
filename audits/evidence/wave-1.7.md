# Wave 1.7: dataset validation (PARTIAL, 25 and 26 November 2026)

Brief: `wave-1.7-task-brief.md`, approved by John on 25 November 2026. Where the brief offered a proposal, it was followed: full sample sizes (point 1), no reviewer named so GS-01 is blocked (2), a committed rule-based NYSE calendar (3), the survivorship and price-window checks wait for Wave 1.8 (4), a proposed canary list (5), flagged rows listed for John (6), five non-December-year companies chosen from the list (7: Oracle, Parker-Hannifin, Agilent, Adobe, TJX; of the brief's examples, Apple, Microsoft and Nike are not in the 100-company list and FedEx has no stored EPS).

## Commands and results

| Check | Result |
|---|---|
| ruff format, ruff check, mypy | PASS (116 files formatted, all checks passed, 46 source files) |
| Full repository pytest | PASS: 206 passed, 534 skipped, 3 expected failures, 0 failed |
| CI-style pytest (image rebuilt) | PASS: 185 passed, 556 skipped, 2 expected failures, 0 failed |
| Migration 0009 on the project database | applied |
| Mutation checks on calendar, validation, press release (15 distinct) | all killed in the end. First run: 6 survived and 1 did not run (quoting error in my script) and 1 did not finish (session ended); tests added for each boundary, then all killed. The three source files were compared with their copies afterwards and are unchanged by the runs |

## A defect found by the real-data check, and fixed

DV-06 on real data showed Adobe and TJX with two stored periods in one calendar quarter. Cause: later filings report the same quarter end with a start date one day or one week different (47 company-quarters in the data). The label code kept periods by start and end, and when it indexed history by end date the later filing replaced the first-filed one, which breaks LB-04. Fixed (a quarter is named by its end date), with a regression test that failed before the fix. Effect: 15 of 3,183 labels changed, all by small amounts; none gained or lost. The Wave 1.6 counts are unchanged. The five companies now map one to one with no gaps (`wave-1.7/dv06_real_companies.json`).

A second, smaller defect: one of my tests opened a database connection and never closed it (the run ended with an idle-transaction timeout message). Fixed.

## Real data results (`wave-1.7/validation_run_2.json`)

- DV-03: 0 duplicate events (the database now refuses them). DV-08: two builds give the same events hash (67e4132a...).
- DV-02, TH-15: 0 nulls in the three date fields among the 2,598 usable events. 564 events are marked incomplete (no label).
- DV-05: 0 events with an information date on or after the announcement. 11 events have a call dated before the release: allowed by decision C-17, against the wording of DV-05 (DR-29).
- DV-01: 26 rows quarantined and kept: 24 flagged for review (call more than one trading day late) and 2 with an impossible label from a scale error in the source EPS (Intercontinental Exchange and Hartford: quarterly EPS in thousands in a 10-K, DR-27). They are still in the events table; they must be excluded before training.
- CE-01: 0 snapshots on or after an announcement are available to any event. AE-03: one EPS basis.
- TX-04, TH-01: **NOT MET.** 3,183 of 3,730 target events have a transcript (85.3%, threshold 90%). Still in the index 91.0%, left the index 58.9% (DR-25). The threshold is unchanged (C-37).

## Press release comparisons (automated)

| Sample | Sampled | Agree | Differ | Other column | Not parsed |
|---|---|---|---|---|---|
| AE-02, 200 events (`ae02_sample.csv`, seed 2034) | 200 | 83 | 19 | 3 | 95 |
| LB-03, derived fourth quarter, one per company (`lb03_sample.csv`) | 20 | 5 | 4 | 0 | 11 |
| VL-08 canary, 20 companies, latest usable 2024 event (`vl08_canary.csv`) | 20 | 13 | 2 | 2 | 3 |

**AE-02 and TH-03 are NOT MET and are not measured.** The parser reads too few releases (95 of 200 unparsed) to say how often press release and XBRL agree. 79% of parsed rows agree. I have not checked the differences by hand, so I do not know how many are parser errors (wrong column, a different line such as continuing operations) and how many are real. Nothing here shows the XBRL values are wrong, and nothing shows they are right beyond the 83 that agree. The yfinance cross-check was not built.
LB-03: of the 4 differences, one is above 1% (CIK 0000719739, derived 6.09 against 6.22, 2.1%, TH-12); the other three are under 1%. Only 9 of 20 releases were read, so the share-count error is not yet measured.
VL-08: 13 of 20 match. The other 7 are not checked by hand. The class half of VL-08 waits for the class cut-offs (Wave 2.5).

## Result per requirement

| ID | Status | Basis |
|---|---|---|
| DV-01, DV-03, DV-08 | PASS locally | Tests and real run. DV-03 also closes TX-05-AC2 |
| DV-02, TH-15 | PARTIAL | Date fields 0 nulls. The other fields' maximum null rates have no values in Section 11, so they are not checked |
| DV-04 | PARTIAL | The function needs a threshold and has no default; the value is pending. Reviewer notes are person work |
| DV-05 | PARTIAL | Passes except the C-17 conflict (DR-29); the price-window part waits for Wave 1.8 |
| DV-06, FD-04 | PASS locally | Synthetic calendars and five real companies |
| DV-07 | PASS locally | Rule-based NYSE calendar with four named special closures. Checked against dates I know, not against a downloaded official list |
| DB-14 | PARTIAL | Index used for ticker and event lookups (planner forced off sequential scans because the test tables are tiny). Sentence, feature and prediction tables do not exist yet |
| CE-01, VL-01 | PASS locally | Planted later snapshot never reaches an event |
| CE-02, CE-03, AE-03-AC2, VL-07 | NOT TESTED | No consensus-route events exist; the 50-event basis check needs them |
| AE-02, TH-03, VL-08 | FAIL for the automated route | See above |
| LB-03 | PARTIAL | Derived values are flagged (AC1). Sample comparison reported on 9 of 20 |
| TX-04, TH-01 | FAIL | 85.3% against 90% |
| TX-07 | PASS locally | Coverage by year and by survivor status (Wave 1.6 report). No dated sector history, so no sector split |
| VL-05, TH-06 | BLOCKED | Needs prices (Wave 1.8) |
| VL-09, TH-08 | NEEDS PERSON | `wave-1.7/hand_audit_sheet.md`: 100 events, seed 2036, with links to the filings |
| GS-01 | BLOCKED | No independent reviewer named (D-09) |
| GS-02 | PASS locally | `wave-1.7/data_card.md`, built by code |
| SRS-14 | NOT TESTED | Sector scoring is off (C-29) and no sector column exists; the configuration test needs the feature matrix (Wave 2.4) |
| GATE-1, GATE-2, GATE-3, GATE-5 | **not passed** | GATE-1: transcript coverage and EPS agreement unmet. GATE-3: survivorship blocked. GATE-5: hand audit and sign-off open |

Not an independent audit. The P1 gate is not passed.

## Correction, 26 November 2026, after the bug review

See `bug-review-2026-11-26.md`. Corrected figures: TX-04 coverage 2015 to 2024 is 86.9% (2,816 of 3,241; still in the index 90.6%, left 58.6%), still NOT MET. Call before the release: 8. Quarantine: 32 flagged, 24 scale error, 1 above one million. AE-02 sample: 90 agree, 17 differ, 2 other column, 91 not parsed (still NOT MET). LB-03: 8 agree, 3 differ, 1 other column, 8 not parsed. Canary: 13 of 20. The hand audit sheet was redrawn (no verdicts had been written). The files in `wave-1.7/` hold the new numbers. Full tests 214 passed, CI-style 193 passed.

## Correction, 26 November 2026, after the independent audit

The independent audit failed this wave as committed. Several results above are wrong or came from faulty parsing; see `independent-audit-2026-11-26.md` (DR-35) for the findings, the fixes and the corrected numbers. Where this file explains a gap by the SEC data, that explanation is withdrawn.
