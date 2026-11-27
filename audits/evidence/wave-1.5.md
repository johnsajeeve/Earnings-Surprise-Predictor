# Wave 1.5: transcripts and preparation (PARTIAL, 25 November 2026)

Requirements: IG-10, IG-11, IG-12, IG-14, IG-17, IG-18, IG-19, FR-13, FR-15, NFR-03, PL-06, TX-01, TX-02, TX-03, TX-05, TX-06, TH-02, ER-07. Decisions: C-45, C-48, D-47 (i), D-45, D-18.

## Commands and results (docker stack rebuilt, migration 0007 applied)

| Check | Result |
|---|---|
| `ruff format --check .`, `ruff check .`, `mypy` | PASS (98 files formatted, all checks passed, 38 source files, no issues) |
| Full repository pytest | PASS: 170 passed, 534 skipped, 3 expected failures, 0 failed |
| CI-style pytest (only `tests/` mounted, image rebuilt) | PASS: 149 passed, 556 skipped, 2 expected failures, 0 failed |
| `tests/test_transcripts.py` | 16 passed |
| Generated files rebuilt (`test_matrix.py build`, `generate_traceability.py`), `test_matrix.py verify` | PASS; checks whose best test is real: 71 (was 61) |
| Mutation checks on `transcripts.py` (10 mutations: boundary count both ways, question keyword, link window, late and early date rules, tie-break, whitespace, newline collapse, empty text) | 10 of 10 killed. Two survived first (link window upper bound, tie-break); tests added; both killed |

## Real data (kurry/sp500_earnings_transcripts, revision f3ded372, sha256 9a305a1c...)

- File: 1,824,805,388 bytes, 33,362 calls, 1 with empty text. Size and checksum verified by the download function.
- Boundary rule on all 33,362 calls: found for 32,540, not found for 822 (2.5%). Boundary turn index 2: 11,144; 4: 5,059; 5: 5,851 and so on (probe, not committed).
- Real load for the 100 companies (calls 2013 to 2024): loaded 3,183; duplicates 2; rejected 138 (no 8-K Item 2.02 within 3 days); segmentation failed 27; call before release 11 (allowed, C-17); call more than one trading day after release 24 (listed with reason in `transcript_load_notes.csv`, TX-02); placeholder call times 20; outside date window 1,400; other companies 28,639.
- Database after the load: 3,185 `transcript` rows (3,183 kept, 2 duplicate), 6,343 `transcript_section` rows, 3,324 stored payloads. A second full run gave the same counts (idempotent, FR-13).
- 93 of 100 companies have transcripts. Missing (TX-07 coverage gap, nothing filled): CSRA, Dun & Bradstreet, Hospira, Keurig Green Mountain, Precision Castparts, St Jude Medical, Whole Foods Market. Per year: 176 (2013) rising to 316 (2024).
- Report and notes: `wave-1.5/transcript_load_report.json`, `transcript_load_notes.csv`. Review sheet ids: `boundary_review_ids.csv` (the sheet itself is git-ignored; it holds transcript text).

## Result per requirement

| ID | Status | Basis |
|---|---|---|
| IG-17, PL-06 | PASS locally | Hash of raw text unchanged, version recorded, tests and mutations |
| IG-11 | PARTIAL | Revision and empty-row count in the report, tested. Original payload per row stored |
| IG-14 | PASS locally | Unlinked rejected with reason, duplicate keeps earliest (TX-05-AC1) |
| TX-01 | PASS locally | Missing ticker or date rejected and listed; DB constraints |
| TX-02 | PARTIAL | 24 late calls listed with reasons; zero violations is not claimed |
| TX-05 | PARTIAL | AC1 tested; AC2 needs DV-03 (Wave 1.7) |
| TX-06, FR-15, ER-07 | PARTIAL | Tested on fixtures and the real load; every real turn labelled is not yet checked on a sample of 20 by a person |
| IG-18, TX-03, TH-02 | NEEDS PERSON | 50-call sheet drawn (seed 2033); John labels it. DR-23: item 1 looks wrong to me |
| IG-10, IG-12 | PARTIAL | HF side tested offline; Alpha Vantage client deferred (C-45) |
| IG-19 | NOT TESTED | Stage order and label freeze come with Waves 1.6 and 1.7 |
| NFR-03 | BLOCKED | Daily check needs D-45 run time |
| TX-07 | gap reported | 7 companies, DR-24 |

Not an independent audit. A fresh-agent audit of this wave is still to be done.

## Correction, 26 November 2026, after the independent audit

The independent audit failed this wave as committed. Several results above are wrong or came from faulty parsing; see `independent-audit-2026-11-26.md` (DR-35) for the findings, the fixes and the corrected numbers. Where this file explains a gap by the SEC data, that explanation is withdrawn.
