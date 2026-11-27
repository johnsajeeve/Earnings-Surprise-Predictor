# Phase 0 independent audit (Waves 0.1 to 0.3)

Run 23 November 2026 by a fresh agent in an isolated clone (`/tmp/auditp0`, Compose project `auditp0`, ports 19000, 15433, 16380) of commit `2909322` on branch `build/wave-0-1`. It was given only the requirement IDs and the repository. It did not read `audits/evidence/`, `audits/implementation_audit.md`, the logbook, the plan, or the status columns of the traceability file, and it did not touch the main project or its volumes. Its report is recorded here as received (condensed only in layout). My reconciliation is in the next section and in the drift register. Where its status is lower than mine, the lower status stands.

Wave 1.1 and 1.2 changes came after the audited commit, so some findings were already fixed or are fixed below.

## 1. Results table (auditor's)

| ID | Status | Reason |
|---|---|---|
| SR-01 | PARTIAL | 7 rows, each with licence and dated checks; the test checks only that fields are non-empty and date-shaped, cannot detect a missing dataset; sector (switched off, C-29) and 8-K exhibits have no row |
| SR-05 | UNVERIFIED | no written answer or refusal on file; D-21 still open; skipped as NEEDS PERSON |
| SR-06 | FAIL | `announcement_times` has "none documented", every fallback "not tested"; strict xfail marks it honestly; the test is weak (finding 5) |
| SR-08 | PARTIAL | NOT NULL and `CHECK (captured_at >= 2026-11-23 UTC)` confirmed by mutation; worker cannot UPDATE, DELETE or TRUNCATE; only a lower bound, the worker can insert a future date |
| SR-09 | PASS (against the acceptance text) | cost column exists and every primary row is 0; test fails when a cost is set to 5; the zeros are self-asserted and Yahoo's terms are recorded as not read |
| TH-14 | PASS | sum of primary costs is 0; fails on mutation |
| SC-07 | PARTIAL | AC1 passes (ADR 0004 exists); supervisor agreement not on file (ADR says so); AC2 skipped; AC1 skipped in the CI test container (NEEDS REPO) |
| IG-16 | UNVERIFIED | Section 12 paragraph read, numbers not checkable by the auditor (evidence off limits); test is a NEEDS MEASUREMENT placeholder |
| PL-05 | PARTIAL | clean build, head equals `alembic_version`, hardcoded table set and company columns, reversible; fails on an untracked column; compares to a hardcoded list, never to the deployed database; only `company` columns checked |
| DB-01 | PARTIAL | AC2 passes (only plpgsql); AC1 scans imports of 8 named libraries, cannot catch other stores; Redis ignored (rate-limit state only, not data of record) |
| DB-02 | PARTIAL | three roles exist, none superuser, passwords from env, one allowed and one forbidden statement each; agent role absent; AC1 is a strict xfail |
| DB-03 | PARTIAL | AC2 passes (`pg_sleep(30)` cancelled at 10 s, confirmed live); AC1 is weak: it imports POOL_SIZE and MAX_OVERFLOW, so 50+50 still passes (mutation M6) |
| DB-07 | PASS (partial depth) | schema query is real (adding a `timestamp` column fails it); few timestamp columns exist yet |
| DB-16 | PARTIAL | refuses non-`_test` names; after the run the project database held only the 10 real snapshots; the test checks the helper only, nothing forces a new test to use the fixture |
| DB-04 | PARTIAL | canonical 10-digit CIK enforced; the ten-ticker-change join (AC1) is not tested |
| DB-05 | PARTIAL | company key only; the snapshot daily unique index has no duplicate-insert test of its own |
| DB-17 | BLOCKED | waits on D-38; no test compares Section 11 with the schema |
| SR-10 | PARTIAL | one real daily run exists (10 read, 10 written, run record); gap detection tested on synthetic dates; AC1 and AC2 skipped; 10 companies not 100; nothing calls `gaps()` automatically; the flag on affected events is not built |
| VL-12, TH-10 | N/A | no vendor estimate source adopted |

## 2. Auditor's exact results (commit 2909322)

- CI-style tests: 76 passed, 577 skipped, 2 expected failures, 0 failed (skips: NOT IMPLEMENTED 391, BLOCKED 50, NEEDS PERSON 35, NEEDS MEASUREMENT 81, NEEDS REPO 20). Full-repository: 94 passed, 558 skipped, 3 expected failures, 0 failed.
- `ruff check`, `ruff format --check` (72 files), `mypy` (25 files) pass. Requirement, generator, matrix, reference, pin and commit checks pass and `git diff --exit-code audits/` is clean.
- Mutations: M1 (primary cost 5) fails SR-09 and TH-14; M2 (start date earlier) fails SR-08; M3 (UPDATE no longer revoked) fails the append-only test; M4 and M4b (a `timestamp` column) fail DB-07 and PL-05; M5 (api time-out 100 s) fails DB-03-AC2; **M6 (pool 50+50) still passes DB-03-AC1**.
- Live probes: worker UPDATE, DELETE and TRUNCATE on `estimate_snapshot` denied; API insert, update and CREATE denied; API `pg_sleep(12)` cancelled; no application role is a superuser; worker CREATE TEMP denied.
- Secrets scan of tracked files and all history: no keys or real passwords; no SEC contact string; the owner's personal email appears only as commit author metadata.
- Decision-log consistency: roles, pools, time-outs, retries, backoff, visibility timeout, request rate, embedded beat all match C-44 and C-45, except the capture time (finding 2).

## 3. Auditor's defects and weaknesses (ranked)

1. The worker could UPDATE `alembic_version` (confirmed live) through the default privileges.
2. The capture time of 22:30 UTC is cited in `schedule.py` and a test as approved by C-44 and D-45, but the decision log records no such approval.
3. SR-08 is only a lower bound; `captured_at` is client supplied (a future date can be inserted); the start date is duplicated in code and migration with no test tying them.
4. SR-10 gap reporting is not wired in; `gaps()` runs only from `__main__`; the flag on events is absent; 10 companies not 100.
5. The SR-06 test accepts "not tested" as a recorded result, so naming a fallback would turn it green while the requirement is unmet.
6. DB-03-AC1 follows the pool constants, so changing them does not fail it; the 10 s pool time-out, pre-ping and worker pool are untested.
7. PL-05 is close to tautological: a hardcoded table list, only `company` columns, never the deployed database.
8. DB-02-AC1 is an xfail; the real role test is tagged bare `DB-02`; other tests are bare IDs too.
9. SC-07-AC1 is a keyword search with no check of status or sign-off; skipped in the CI test container.
10. Register facts are self-asserted (Yahoo terms not read, Hugging Face origin unknown, single-day checks).
11. Starting the stack makes the worker call Yahoo (the catch-up capture) with no off switch, including in a CI or test stack.
12. The worker can connect to the `postgres` database (CONNECT is granted to PUBLIC); `.env.example` passwords are weak placeholders.
13. Many requirement checks are skipped, so a green run says little beyond the tests that ran.

## 4. Auditor could not verify

IG-16 and the other spike numbers, source licences and terms, SR-05 and the supervisor's agreement, whether branch protection and the gitleaks and pip-audit jobs run, behaviour over many days (SR-10-AC1, the 22:30 schedule), and one test that needs `git` in the image.

## 5. Reconciliation (builder's response, 23 November 2026, after commit 76250a2)

Each finding was checked against the repository, not accepted on trust.

| # | Finding | Response | State |
|---|---|---|---|
| 1 | Worker can UPDATE `alembic_version` | True at the audited commit. Closed in migration 0004 (Wave 1.2). Re-probed live as the worker: `InsufficientPrivilege`. The privilege registry test now covers it | FIXED |
| 2 | 22:30 UTC cited as approved but not in the decision log | True. John chose 22:30 UTC and the start-up catch-up in answers to two questions on 23 November 2026, and I never wrote it down. Recorded as C-46; the comment in `schedule.py` now cites it | FIXED (documentation drift of mine) |
| 3 | SR-08 only a lower bound; start date duplicated | The duplication is fixed: a test reads the literal in the migration and compares it with `consensus.CAPTURE_START`. The upper bound is not enforced by the database: the worker may insert a future `captured_at`. The application code stamps real time, and a database check against `now()` would break the synthetic tests that use fixed dates, so I did not add it. Left as a known limit | PARTIAL, limit stated (DR-15) |
| 4 | Gap reporting not wired in | The capture task now logs a warning for every gap over 3 days and returns the gap count. The flag on affected events needs events (Wave 1.6). The 10-company list stays until Wave 1.3 | FIXED in part |
| 5 | SR-06 test accepts "not tested" | Tightened: only `passed` or a recorded `scope narrowed` counts. The test is still a strict expected failure | FIXED |
| 6 | DB-03-AC1 follows the constants | Added a test that pins the approved values (pool 5+5, 10 s pool time-out, pre-ping, 10, 120 and 300 s statement time-outs, 5 s and 60 s) | FIXED |
| 7 | PL-05 tautological | The test now also compares every column of every table with an expected list and compares the clean-built schema with the deployed project database. It still depends on the migrations as the source of truth | FIXED in part |
| 8 | DB-02-AC1 is an xfail; real tests are bare IDs | Accepted. The AC says "each role" and the agent role does not exist, so the xfail is the honest state. The traceability file shows both | ACCEPTED |
| 9 | SC-07-AC1 keyword search | Now requires the ADR to say it is accepted and to mention the supervisor, as well as the label route. Still skipped in the CI test container (DR-08) | FIXED in part |
| 10 | Register facts self-asserted | True, and the register says so ("not read", "unknown"). Reading Yahoo's terms and the Hugging Face origin remain open items | OPEN |
| 11 | Starting the stack calls Yahoo | Fixed: the catch-up is behind `CAPTURE_CATCH_UP`, off by default and in `.env.example`, on in John's `.env` (C-46). A test and CI stack makes no outside call | FIXED |
| 12 | Worker can connect to `postgres`; weak example passwords | CONNECT on `postgres` revoked from PUBLIC in the bootstrap, with a test. The example passwords are placeholders for a machine whose ports bind to 127.0.0.1 | FIXED / ACCEPTED |
| 13 | Many checks skipped | Known and reported on every run | ACCEPTED |

Statuses of the auditor that stand for now (lower of the two): SR-06 FAIL; SR-05 and IG-16 UNVERIFIED; SR-01, SR-08, SC-07, PL-05, DB-01, DB-02, DB-03, DB-16, DB-04, DB-05, SR-10 PARTIAL; DB-17 BLOCKED; SR-09, TH-14 and DB-07 PASS (against the acceptance text). Phase 0 therefore does not pass: the P0 gate result is PARTIAL. Items the auditor could not verify stay open (see section 4); John's spot-check of five requirements has not happened.
