# Wave 1.1: task framework, EDGAR client, request limits

Measured 23 November 2026, branch `build/wave-0-1`, on top of commit `1f9fcf1`. Decisions: C-45.

## Wave 1.1

Requirements: IG-01 to IG-08, IG-10, IG-12, PL-01, PL-02, EQ-07, SR-07, NFR-03 (not started), with the limits listed below. Moved into this wave from 1.2: the `raw_payload` table (DB-11, first half).

## Commands run

- Wrote the tests first in three files (`tests/test_ingestion_framework.py`, `tests/test_edgar_client.py`, additions to `tests/test_db_*`) and then migration 0003 (`ingestion_run`, `dead_letter`, `raw_payload`), `runlog.py`, `tasking.py`, `limits.py`, `clients/edgar.py`, `rawstore.py`, `parsing.py`, `schedule.py` and the `fetch_company_facts` task.
- First real slice: five companies (AAPL, MSFT, JPM, KO, F) fetched through the real queue and worker with `fetch_company_facts.delay`, stored in `raw_payload`.
- Full-repository and CI-style pytest, `ruff check`, `ruff format --check`, `mypy`, `scripts/test_matrix.py build` and `verify`, generator, reference and plan checks, pin check.
- Fault injection: limiter allows one call too many, the sec.gov host check removed, the retry count lowered to 2.
- Regression comparison of the JUnit files of Wave 0.3 and this run.

## Output

| Run | Passed | Failed | Skipped | Expected failures |
|---|---|---|---|---|
| Wave 0.3 (full repo) | 69 | 0 | 567 | 3 |
| Now, full repository | 94 | 0 | 558 | 3 |
| Now, CI style | 76 | 0 | 577 | 2 |

`ruff check`, `ruff format --check` (70 files) and `mypy` (25 source files) pass. No test that passed in Wave 0.3 fails now. Faults: the three injected faults made 7 tests fail (the three host cases, the one-second limit, the retry count, the injected-failure test and the failed-run test); the files were restored.

Real slice, 16:50 UTC: 5 of 5 stored, run records all `succeeded` with 1 row read and 1 written, payloads of 3,859,564 (AAPL), 4,938,072 (MSFT), 8,154,135 (JPM), 5,206,922 (KO) and 3,776,300 bytes (F), 25.9 MB in total. The five calls started within about 1 second, inside the limit. A trimmed real fixture from the AAPL payload is `tests/fixtures/edgar_companyfacts_aapl_trimmed.json` (origin stated inside it). The full AAPL payload holds 341 diluted EPS facts.

## Result per requirement

- IG-02, PL-02: PASS at this wave. An injected failure gives three retries and one dead-letter row (4 attempts, error class and a 64-character argument hash stored, no arguments).
- IG-03, PL-01: PASS at this wave. Each run writes a row; a forced error gives `failed`; a run that reports failure with zero rows is not a success. The capture task records a failed run when every company fails, and retries.
- IG-01: PARTIAL. Tasks are acknowledged late, requeued if their worker is lost, and running the load, capture and fetch tasks twice leaves the same table hashes. IG-01-AC2 (kill a worker mid-task) is a fault-injection test for Wave 7.1.
- EQ-07: PARTIAL. Four tasks are idempotent and tested twice (`load_companies`, `capture_consensus`, `fetch_company_facts`; `ping` has no state). Every later task needs its own test.
- IG-04: PARTIAL. The redelivery timeout is set to 4 hours and tested. The measured part (the longest task in the 100-company run) waits for that run.
- IG-05: PARTIAL. All scheduled jobs are in `src/earnings/schedule.py`; a job not listed does not run (IG-05-AC2). Only one job exists; the other three initial jobs are added by the waves that build them, with their run times from John.
- IG-06: PARTIAL. A job with no success for more than 3 days is reported (`python -m earnings.runlog`). The flag on affected events needs events (Wave 1.6).
- IG-07: PARTIAL. The EDGAR limit is enforced (8 a second against the SEC's 10) by a limiter shared through Redis across worker processes and tested with a mocked clock. The Alpha Vantage client and its persistent counter are deferred (C-45).
- IG-08: PASS at this wave. With the contact unset or blank the client raises and sends nothing; the contact is sent only to sec.gov hosts and never appears in logs, repr, errors or results.
- IG-10: PARTIAL. The EDGAR client returns a raw payload that is stored through `raw_payload` as received (byte for byte) and parsed from the database with name resolution disabled. The other clients do not exist yet.
- IG-12: PARTIAL. The EDGAR and yfinance clients have recorded-response tests that run without the network and fixtures that state their origin. Hugging Face and Alpha Vantage have no client yet.
- SR-07: PASS for AC1 (a log line per EDGAR request, path, status and size, and per yfinance fetch); AC2 (no scraped source in the demo bundle) waits for the bundle (Wave 7.4).
- DB-11: PARTIAL. The table is insert only for the worker, checks the length, and stores one row per source, URL and hash. DB-11-AC1 (rebuild gives identical hashes) is Wave 1.2.
- NFR-03: not started (needs the transcript check, Wave 1.5).

## Not verified

- A worker killed mid-task and restarted (IG-01-AC2, EQ-06).
- The retry waits (30, 60, 120 seconds before jitter): the tests run retries eagerly, so the real delays and the jitter were not observed.
- Late acknowledgement behaviour with a real Redis redelivery.
- The Redis limiter across two real worker processes under load (tested with two limiter objects, one key, a mocked clock).
- GitHub Actions. The new test files add about 25 seconds to the suite (the longest tests wait on database time-outs).

## Drift found

- DR-13 (closed): the sixth CI job was not a required check (see p0-resolutions).
- The full-repository suite now takes about 50 seconds. Not a defect, but it grows with each wave.
- `raw_payload` already holds 25.9 MB for five companies. For 100 companies about 500 MB is expected from this source alone, which matters for DB-15 (database size measured after the 100-company load).
- `requests` was declared in `requirements.txt` (already pinned and in the lock file as a dependency of yfinance) because the code imports it directly.

## Assumptions

- The parser in `parsing.py` is the minimum needed to show IG-10 works from stored payloads. The real EPS parsing (first-filed selection, derived fourth quarters) is Wave 1.4.
- `ingestion_run` is the Product Section 11 entity IngestionRun with extra columns, so no second run table exists.

## Measured values

- Hours for this wave: about 6. Acceptance checks moved from NOT TESTED to a real result: IG-02-AC1, IG-03-AC1, IG-03-AC2, IG-05-AC2, IG-08-AC1, PL-01-AC1, PL-02-AC1, IG-01-AC1, SR-07-AC1 (9). Nine checks keep placeholders with a stated reason: IG-04-AC1, IG-06-AC1, IG-07-AC1, IG-10-AC1, IG-12-AC1, IG-12-AC2, DB-11-AC1, IG-01-AC2 and IG-05-AC1.
