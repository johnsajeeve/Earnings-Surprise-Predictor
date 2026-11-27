# Wave 1.2: storage rules

Measured 23 November 2026, branch `build/wave-0-1`, on top of commit `2909322`.

## Wave 1.2

Requirements: DB-08, DB-09, DB-10, SR-04. Plan change of 23 November 2026 (logged in the logbook): DB-11-AC1 moves to Wave 1.4, DB-12 to 2.4, DB-13 to 1.6 and DB-14 to 1.7, because their checks need tables or data that do not exist yet. `audits/plan_coverage.txt` and the plan text were changed together and `scripts/check_plan_coverage.py` passes.

## Commands run

- Tests first (`tests/test_storage_rules.py`), then migration 0004, `src/earnings/schema.py`, `rawstore.verify_hashes`, `docs/architecture/as-of-reads.md`.
- `docker compose up --build -d --wait` (migrations reached 0004), full-repository and CI-style pytest, `ruff check`, `ruff format --check`, `mypy`, matrix build and verify, generator, reference, requirement, plan and pin checks.
- `docker compose exec -T api python -m earnings.rawstore` against the real project database.
- Fault injection: changed the as-of comparison from `<` to `<=` and the validity boundary from `<` to `<=`. A first attempt that broke the migration itself was discarded (it made every test error, which proves nothing); the second, semantic one is reported below.
- Regression comparison with the JUnit file of Wave 1.1.

## Output

| Run | Passed | Failed | Skipped | Expected failures |
|---|---|---|---|---|
| Wave 1.1 (full repo) | 94 | 0 | 558 | 3 |
| Now, full repository | 105 | 0 | 552 | 3 |
| Now, CI style | 87 | 0 | 571 | 2 |

`ruff check`, `ruff format --check` (75 files) and `mypy` (27 source files) pass. No test that passed in Wave 1.1 fails now. The semantic faults made `test_a_planted_version_dated_d_or_later_is_not_returned` and `test_a_date_on_a_boundary_resolves_to_exactly_one_period` fail.

Real data: `python -m earnings.rawstore` on the project database: 5 payloads, 0 hash mismatches.

## Result per requirement

- DB-08: PARTIAL. The worker role cannot UPDATE or DELETE any of the three append-only tables that exist (`estimate_snapshot`, `raw_payload`, `dead_letter`), and a test compares the registry with the privileges in the database in both directions. ActualEps, EpsHistory and FundamentalsFiling, which the requirement names, do not exist yet; each is added to the registry by its own migration (Waves 1.4 and later).
- DB-09: PARTIAL. `estimate_snapshot_as_of` returns the latest version per source and period strictly before the date; a version stamped exactly at D or after is not returned, and one a microsecond before is. The scan for direct reads of a versioned table in feature code runs, and its detector is shown to flag a planted direct read, but `src/earnings/features/` does not exist yet, so the scan currently covers nothing. The functions for the other versioned tables come with their tables.
- DB-10: PASS at this wave for the two tables that exist (`ticker_history`, `index_membership`): the database refuses an overlapping period for the same company, a backwards period, and the same ticker for two companies at once, while two share classes of one company may coexist; on a boundary date exactly one period applies. `sector_assignment` is switched off (C-29). `btree_gist` is created by migration and the extension-list test (DB-01-AC2) still passes.
- SR-04: PARTIAL. The hash of each stored payload is rechecked against its body (5 real, 3 synthetic in tests; a same-length tampered body is detected). The requirement also asks for the source version to be stored, and `raw_payload` has no such column (see drift).

## Not verified

- A second as-of function for any other table. The pattern is documented in `docs/architecture/as-of-reads.md` and has one instance.
- Behaviour on a large `raw_payload` (25.9 MB for 5 companies; a sequential hash scan of 100 companies was not timed).
- GitHub Actions on this change.

## Drift found

- DR-14: SR-04 says raw responses are stored with retrieval time, source name and source version. The `raw_payload` table approved in C-45 has source, URL, retrieval time and hash, but no source version column. Not added without approval. Question for John: add a nullable `source_version` column in the next migration.
- Found while building: the migration history table `alembic_version` was writable by the worker and API roles through the default privileges. Closed in migration 0004 (privileges revoked) and covered by the registry test.
- Plan change: four checks moved to later waves (see top). Recorded in the logbook and the plan.

## Assumptions

- `ticker_history` and `index_membership` are the Product Section 11 entities with the fields listed there, so no table addition beyond Section 11 was made. Whether the membership source (D-32) fills them correctly is Wave 1.3.
- Validity ranges are dates (a day), not instants, so DB-07's timestamp rule does not apply to them.

## Measured values

- Hours for this wave: about 3. Acceptance checks moved to a real result: DB-08-AC1, DB-09-AC1, DB-09-AC2, DB-10-AC1, DB-10-AC2, SR-04-AC1 (6).
