# Wave 0.3: forward consensus capture job

Measured 23 November 2026, branch `build/wave-0-1`, on top of commit `bbee62e`.

## Wave 0.3

Requirements: SR-08, SR-10 (this wave). Finishing later: CE-01 to CE-03 (Wave 1.7), FR-14 (1.6), CE-04 and TH-04 (3.4). Not applicable here: VL-12 and TH-10 (see Not verified). Approvals: decision C-44 (snapshot schema, embedded beat) and the run-time answers of 23 November 2026 (22:30 UTC, catch-up at worker start).

## Commands run

- Wrote the tests first (`tests/test_consensus_capture.py`), then migration 0002, `src/earnings/consensus.py`, `src/earnings/capture_universe.csv`, the `capture_consensus` task, the beat schedule and the worker catch-up.
- `docker compose up --build -d --wait --wait-timeout 300`. The worker now starts with `-B -s /tmp/celerybeat-schedule`. On start it found no snapshot for the day and captured by itself.
- Full-repository and CI-style pytest, `ruff check`, `ruff format --check`, `mypy`, `scripts/test_matrix.py build` and `verify`, the generator and the other checks of Wave 0.2.
- Planted faults in migration 0002: removed the `REVOKE UPDATE` and replaced the start-date CHECK with `true`, then ran the SR-08 tests; restored the file after.
- Read the stored snapshots back as the API role, and ran `python -m earnings.consensus` for the gap report.

## Output

| Run | Passed | Failed | Skipped | Expected failures |
|---|---|---|---|---|
| Wave 0.2 (full repo) | 60 | 0 | 568 | 3 |
| Now, full repository | 69 | 0 | 567 | 3 |
| Now, CI style | 51 | 0 | 586 | 2 |

`ruff check`, `ruff format --check` and `mypy` pass. No test that passed in the Wave 0.2 run fails now. Nine tests are new passes. The planted faults made `test_sr_08_ac1_...` and `test_sr_08_snapshots_are_append_only_...` fail.

First real capture, 23 November 2026, 16:27 to 16:28 UTC, run by the worker itself through the catch-up: 10 captured, 0 failed, 12.1 seconds. Rows in `estimate_snapshot`: 10, one per company, all period `0q`, source `yfinance` version `1.8.0`, standard deviation empty, raw table kept as received (about 870 bytes each). Means as stored: AAPL 2.91173, MSFT 4.85575, JPM 5.85966, KO 0.60823, F 0.35365, IBM 4.62568, PFE 0.68499, GOOGL 3.19133, AMZN 2.3942, INTC 0.24895. Basis: AAPL, GOOGL and AMZN `gaap`; the others `normalized`. Analyst counts 11 to 43.

Gap report after the first day: 1 capture day (2026-11-23), no gaps.

## Result per requirement

- SR-08: PASS at this wave. The database rejects a snapshot with no capture time and one before 2026-11-23 00:00 UTC; the start instant itself is accepted; the worker cannot update or delete a snapshot. No backfilled row exists.
- SR-10: PARTIAL. The job exists, runs on a daily schedule at 22:30 UTC plus a catch-up at worker start, is safe to run twice, records failures instead of rows, and the gap report works. It has run on one day. SR-10-AC1 (a successful run on each day) and SR-10-AC2 (a gap over 3 days reported, and affected events flagged) need real days and events, so both stay NEEDS MEASUREMENT. Coverage is 10 companies, not the whole universe (Wave 1.3 widens it).
- CE-01, CE-02, CE-03, CE-04, FR-14: not claimed here.

## Not verified

- A scheduled run at 22:30 UTC has not happened yet. Only the catch-up run has. The schedule is checked by a test of its configuration, not by waiting for the time.
- A run on a second day. Expected tomorrow.
- What happens when Docker is off at 22:30 and on again later: the catch-up covers a restart of the worker, and the daily gap report covers a missed day. Not exercised for real.
- VL-12 and TH-10 (pre-announcement estimate test): they apply to a source that stores an estimate beside each past actual. yfinance `earnings_estimate` returns current values only, so they do not apply to this capture source. Whether `get_earnings_dates` is ever adopted is open.
- Finnhub and FMP as a second source. John is getting the Finnhub key.
- Yahoo's own terms of use (the register says they were not read).
- Running on GitHub Actions.

## Drift found

- DR-12: all 10 rows of the first run carry the run's start time (16:27:56 UTC), not each answer's arrival time, because the code stamped the run, not the row. Fixed in the same change (each row is stamped when its answer arrives), so only the first day's rows differ, by at most 12 seconds. Left as stored, since rows are append-only.
- The `captured_at` start-date CHECK is a literal in migration 0002 and a constant in `consensus.py`. A test refuses a mismatch only through the boundary check. If the start date ever changes, both must change.
- XOM is left out of the capture list on purpose, because its CIK is undecided (DR-06).

## Assumptions

- The capture list is 10 companies with CIKs read from the SEC ticker file on 23 November 2026 (AAPL, MSFT, JPM, KO, F, IBM, PFE, GOOGL, AMZN, INTC). Chosen because yfinance returned a mean and analyst count for each. They are not a sample of the future universe.
- One snapshot per company, source, period and UTC day. The key means two captures in one UTC day keep the first.

## Measured values

- Hours for this wave: about 4. Acceptance checks moved from NOT TESTED to a real result: 1 (SR-08-AC1). Id-level tests added: 8 (SR-08, SR-10).
- Capture duration: 12.1 s for 10 companies, with a 1 second pause between calls.
