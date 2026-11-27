# Wave 0.2: database foundation and plumbing slice

Measured 23 November 2026, branch `build/wave-0-1` (the wave 0.2 changes are on top of commit `ed44402`).

## Wave 0.2

Requirements: DB-01, DB-02, DB-03, DB-07, DB-16, PL-05, EQ-07 (first task). Started here and finished later: DB-04 (Wave 1.3), DB-05 (Wave 5.4), DB-17 (Wave 7.1). Approvals: decision C-44 (dependencies, role and pool values, EstimateSnapshot, scheduler).

## Commands run

- `docker compose up --build -d --wait --wait-timeout 300` (the new one-shot `migrate` service exits 0; the worker and API start after it).
- CI-style pytest: tests mounted over the image. Full-repository pytest: repository mounted at `/repo`.
- In the image: `ruff check .`, `ruff format --check .`, `mypy`.
- On the host: `scripts/test_matrix.py build` and `verify`, `audits/generate_traceability.py`, `scripts/check_requirement_refs.py`, `docs/tools/check_requirements.py`, `scripts/check_plan_coverage.py`, `scripts/check_pins.py`.
- Planted faults: gave the worker role DELETE and set the api statement time-out to 600 s, then ran the role and time-out tests.
- Regression comparison of the JUnit files of the Wave 0.1 run and this run, test by test.

## Output

| Run | Passed | Failed | Skipped | Expected failures |
|---|---|---|---|---|
| Wave 0.1 baseline (full repo) | 47 | 0 | 575 | 2 |
| CI style now | 42 | 0 | 587 | 2 |
| Full repository now | 60 | 0 | 568 | 3 |

New passing tests (13): DB-01-AC2, DB-02 (three roles), DB-03-AC1, DB-03-AC2, DB-04, DB-05 (company only), DB-07-AC1, DB-16-AC1, EQ-07 (load_companies), PL-05-AC1 and three missing-setting cases for the new password settings. Previously passing tests that do not pass now: none. The 3 expected failures: SC-06-AC1, SR-06-AC1 and DB-02-AC1 (no `earnings_agent` role yet).

`ruff check`, `ruff format --check` and `mypy` pass. The two planted faults made `test_db_02_migrator_worker_and_api_roles_allowed_and_forbidden` and `test_db_03_ac2_a_long_query_is_cancelled` fail; the file was restored afterwards.

Dependencies: `alembic==1.20.1` and `yfinance==1.8.0` moved into `requirements.txt`. `requirements.lock` regenerated in `python:3.12.16-slim` with the old lock as constraints: 20 packages added, none changed.

## Result per requirement

- DB-01: PASS (no other database in code; the extension list equals the migrations: none beyond plpgsql).
- DB-02: PARTIAL. Migrator, worker and API roles exist, none is a superuser, each was tested for an allowed and a forbidden statement. The agent role named in the requirement does not exist yet (Wave 5.1), so DB-02-AC1 is a strict expected failure.
- DB-03: PASS at this wave. The load test ran 30 clients against a pool of 5 plus 5 overflow with no failure and a peak of at most 10 connections; a 30-second query was cancelled by the api role's 10-second limit; the worker role carries 120 s, 5 s and 60 s. The 28-connection worst case in C-44 is arithmetic, not measured.
- DB-07: PASS as written, but the check is weak today: the only table, `company`, has no time column. The test is a schema-wide query that guards every later table.
- DB-16: PASS. The suite builds `<project>_test` from nothing every session and refuses any name that does not end in `_test`.
- PL-05: PASS. A clean database migrated from nothing reaches head, holds only the expected tables and columns, and downgrades to empty.
- EQ-07: PARTIAL. `load_companies` run twice leaves the same rows. Every later task needs its own test.
- DB-04, DB-05, DB-17: PARTIAL or not started, as planned. The company key and canonical CIK form are enforced by the database. DB-04-AC1 (ticker change join) and DB-05-AC1 (every unique key) stay NOT IMPLEMENTED.

## Not verified

- The stack was not rebuilt from a deleted volume. The `earnings` database was migrated in place by the `migrate` service on the existing volume (it worked; the `public` schema was empty). Deleting the volume was not done, so a first start on a fresh volume is covered only by the test-database path, which runs the same code.
- Not run on GitHub Actions. The CI workflow uses `.env.example`, whose password placeholders are `change-me-*`.
- The agent role and its grants.
- Concurrency beyond the one load test, and connection counts of the worker with `--concurrency=2` (two processes, each with its own pool, so up to 20 worker connections rather than 10).

## Drift found

- DR-11: the database passwords of all three roles, and the superuser password, are present in the environment of every service (the `x-app-env` block), because the test run uses the API service's environment and needs all of them. The services only use their own role, but any container can read the others. Acceptable on one developer machine. For the cloud, each service must receive only its own secret (Deployment DP-06). Reported, not fixed.
- The `.env` file on this machine was extended with three generated passwords (`DB_MIGRATOR_PASSWORD`, `DB_WORKER_PASSWORD`, `DB_API_PASSWORD`), because compose requires them. I did not read the rest of the file. It is git-ignored.

## Assumptions

- A one-shot `migrate` compose service is the way to run migrations before the worker and API start. It was not named in the approved plan, but it is what PL-05 and DB-02 need in practice, and it was the smallest design that works with a pre-existing volume.
- Passwords from `.env.example` use plain letters and digits to avoid quoting problems.

## Measured values

- Hours: about 4 for this wave so far. Acceptance checks moved from NOT TESTED to a real result: 8 (DB-01-AC2, DB-03-AC1, DB-03-AC2, DB-07-AC1, DB-16-AC1, PL-05-AC1, and DB-02-AC1 as a recorded expected failure, plus the SP-06 setting cases).
- Test suite time: 16.9 s full repository, 15.3 s CI style (the 10 s statement time-out test dominates).
