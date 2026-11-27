# Wave 0.1: source register and label-route ADR (Steps 0.1.8 and 0.1.9)

Measured 23 November 2026, branch `build/wave-0-1`.

## Wave 0.1

Requirements: SR-01, SR-06, SR-09, TH-14, OR-02 (check AC1), SC-07 (check AC1). Also touched: SR-05 (no change), IG-16 (draft for Data Section 12 written, see wave-0.1-section12-draft.md).

## Commands run

- Wrote `src/earnings/source_register.csv` (7 rows) and `docs/adr/0004-label-route-time-series-sue.md`.
- Replaced placeholders in `tests/test_req_data.py` (SR-01-AC1, SR-06-AC1, SR-09-AC1, TH-14-AC1) and `tests/test_req_project_wide.py` (OR-02-AC1), added the helper `source_register()` to `tests/requirement_support.py`, and removed the expected-failure marker from `test_sc_07_ac1` because the ADR now exists.
- `docker compose up --build -d --wait --wait-timeout 300`, then the CI-style and full-repository pytest runs of wave-0.1-baseline.md.
- `python3 scripts/test_matrix.py build` then `verify`, `audits/generate_traceability.py`, `scripts/check_requirement_refs.py`, `docs/tools/check_requirements.py`, `scripts/check_plan_coverage.py`, and in the image `ruff check .`, `ruff format --check .`, `mypy`.
- Planted-fault check: set one primary row's cost to 9.99 and blanked another row's licence date, then ran the register tests. Restored the file afterwards (SHA-256 identical to the backup).

## Output

| Run | Baseline | Now | Change |
|---|---|---|---|
| CI style | 25 passed, 599 skipped, 0 failed | 29 passed, 594 skipped, 1 expected failure, 0 failed | +4 passed (SR-01, SR-09, TH-14, OR-02); SR-06 is an expected failure; NOT IMPLEMENTED skips 407 to 402 |
| Full repository | 42 passed, 580 skipped, 2 expected failures, 0 failed | 47 passed, 575 skipped, 2 expected failures, 0 failed | +5 passed (the four above and SC-07); SC-07 left the expected failures and SR-06 joined, so SC-06 and SR-06 remain |

`ruff check`, `ruff format --check` and `mypy` pass. `test_matrix.py verify` passes. The first full run after the change failed `test_do_03_the_committed_matrix_...` because the committed matrix was out of date. That is the check working. I regenerated the matrix with the script (not by hand) and the test passed.

Planted fault: 4 of the register tests failed (SR-01-AC1, SR-09-AC1, TH-14-AC1, OR-02-AC1) and SR-06 stayed an expected failure. The registers tests are not vacuous.

## Result per requirement

- SR-01 (a register row per dataset, with licence and dated access check): PASS at the wave gate for the 7 datasets in use. Datasets not yet checked (Alpha Vantage, Finnhub, FMP, Tiingo) are not in the register. They appear only as fallback names. An independent audit is still to come.
- SR-09 and TH-14 and OR-02-AC1 (every primary-route entry costs zero): PASS at the wave gate. OR-02-AC2 (a budget alert before any spend) is not built.
- SR-06 (a fallback per dataset with its test result): **FAIL** (expected failure). `announcement_times` has no documented fallback. Every other fallback is recorded as "not tested", so even without that gap SR-06 would not be satisfied in substance: a fallback has to pass the same tests, or the scope is narrowed.
- SC-07 (label route chosen by ADR and recorded with the supervisor's agreement): PARTIAL. AC1 (the ADR) passes. The supervisor's agreement is not on file (C-25, D-46). AC2 (a test that two label routes never mix) is a placeholder for Wave 1.6.
- SR-05: NEEDS PERSON, unchanged. TH-14's single check is covered by the same test as SR-09.

## Not verified

- The register records what I read on 23 November 2026. It does not prove redistribution rights. `redistributable_in_demo` is "unverified" for the SEC data and "no" for the transcripts and Yahoo data.
- Yahoo's own terms of use were not read. The register says so.
- `quote_limit_chars` (SR-11) is "unknown" or "not applicable" in every row. The limit for transcripts needs the licence question (D-18) first.
- Independent audit of this wave: not done (it happens at the P0 gate).

## Drift found

- DR-09: the membership candidate (`fja05680/sp500`) is keyed by ticker with no company identifier, but C-19 makes the CIK the permanent identifier. The mapping from ticker to CIK is an IM-03 task and is not yet designed.
- DR-10: SR-06 is not satisfied, because there is no documented fallback for the 8-K announcement time. Needs John: accept a stated scope limit, or name a fallback.
- SC-07 is incomplete without the supervisor's agreement (known since C-25).

## Assumptions

- I put the register inside the application image (`src/earnings/`) so the CI test job can read it. The CI test job mounts only `tests/`, so a register under `docs/` would be skipped there as NEEDS REPO (the problem in DR-08). This is a file in `src/`, which the plan did not list for Wave 0.1. John's approval is requested for that placement.
- ADR number 0004: 0003 is left for the deployment ADR named in Deployment DP-11.
- The ADR status says "Accepted by John on 18 November 2026" because C-25 records that decision. I did not mark it complete.

## Measured values

- Hours spent on Steps 0.1.8 and 0.1.9 including the tests: about 1.5. Checks moved from NOT TESTED to a real result: 5 (SR-01-AC1, SR-09-AC1, TH-14-AC1, OR-02-AC1, SC-07-AC1) plus SR-06-AC1 as a recorded expected failure.
