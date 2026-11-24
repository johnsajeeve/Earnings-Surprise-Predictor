# Independent audit of Waves 0.1 to 1.4

Run 24 November 2026 by a fresh agent in an isolated clone (`/tmp/auditp1`, Compose project `auditp1`) of commit `b3dab83`. It was given only the requirement IDs and the repository, and did not read `audits/evidence/`, the audit ledger, the logbook, the plan or the status columns of the traceability file. It made no outside request. This is its report, condensed in layout only. My reconciliation is in section 6. Where its status is lower than mine, the lower one stands.

## 1. Results

- Tests, CI mode: 125 passed, 555 skipped, 2 expected failures, 0 failed. Full repository: 145 passed, 534 skipped, 3 expected failures, 0 failed. Skips (full run): NOT IMPLEMENTED 372, NEEDS MEASUREMENT 77, NEEDS PERSON 35, BLOCKED 49, NEEDS REPO 1.
- `ruff check`, `ruff format --check` (90 files), `mypy` (34 files) pass. Requirement, generator (no diff), matrix, reference, plan, pin and commit checks pass. Not run: pip-audit, gitleaks, GitHub CI.
- Live probes: the worker cannot UPDATE or DELETE `eps_history`, `fundamentals_filing`, `estimate_snapshot`, `raw_payload`, `dead_letter`, cannot read `alembic_version`, cannot connect to the `postgres` database, cannot create tables or read server files; the API role writes nothing; no application role is a superuser; role settings match C-44.
- Secrets: no keys in the whole history; only placeholders in `.env.example`. One of the owner's email addresses appears once in the history as the author of a GitHub-web commit.

## 2. Requirement table (auditor's)

SR-01 PASS. SR-05 UNVERIFIED (needs a person). SR-06 FAIL (the register fails the check more widely than the one dataset the expected-failure names). SR-09 and TH-14 PASS but weak (the zeros are declared, not measured). IG-16 PASS on the literal check (the test looks for strings; the printed quartiles are magnitudes, not ordered values). PL-05 PASS. DB-01 PASS. DB-02 PARTIAL (no agent role; the superuser password is in every service's environment; an unused superuser URL remains in config). DB-03 PASS (the claim that API and worker connections together stay under the server limit is not tested). DB-07 PASS. DB-16 PASS but weak (the guard inside `drop_database` and `truncate_all` is not tested). SR-08 PASS. SR-10 PARTIAL (AC1 and AC2 need real days; 9 of 89 captured companies are outside the 100-company universe). VL-12 and TH-10 NOT APPLICABLE (no vendor source adopted). PL-01, PL-02, IG-02, IG-03, IG-08 PASS (retries tested eagerly only). EQ-07 PARTIAL (a name-in-module check; `capture_consensus` is mapped to a test that calls `capture_all`). IG-01 PARTIAL (no worker-kill test). IG-04 PARTIAL. IG-05 PARTIAL. IG-07 PARTIAL (the EDGAR test is tagged `IG-07`, not `IG-07-AC1`). SR-04 PASS (run on demand, not scheduled). DB-08 PASS for the 5 tables that exist. DB-09 PARTIAL (AC2 passes vacuously, no feature code exists). DB-10 PASS. IM-01 and TH-05 PARTIAL (the count test reads a generated `report.json` and recomputes nothing). IM-02 PASS with a data-quality defect (reasons). IM-03 PASS. IG-13 PASS. IG-21 PASS. DB-04 PASS. AE-04 PASS. FD-01 PARTIAL (the filing-date test is vacuous because the column is NOT NULL). FD-02 PARTIAL (the as-of function is tested; the rule "use the current quarter only if filed before D, otherwise the latest earlier quarter" is not built). FD-03 PASS. IG-09 FAIL (a Should). IG-15 PARTIAL (functions only). DB-11 PASS (the hash covers only some columns). LB-03 PARTIAL. AE-03 PARTIAL (the one-basis test is true by construction; consensus snapshots store the source's own basis, gaap or normalized).

## 3. Mutations (41 run)

37 caught, 4 missed. Missed: M25 (fundamentals uniqueness key widened to include `fiscal_period`), M29 (selection seed changed to 5; only a different seed is compared with the default), M33 (the gap-start offset), M41 (the `_require_test_database` guard disabled). Two more were caught only incidentally (M7 seed, M24 CIK padding).

## 4. Defects and weaknesses (auditor's ranking)

1. The superuser password is in every container's environment, and an unused superuser URL is still built in `config.py`.
2. `fiscal_year` and `fiscal_period` describe the filing, not the period: the same period carries several labels.
3. The universe breaks decision C-47(3): four selected companies joined the index after 31 December 2024 (CRH, Block, Vertiv, Reddit) and ten more joined from 2020 to 2024.
4. Selection and schema rules not recorded as decisions: the older-registrant and no-facts rules, the Q4 method, the revenue tag priority, the table shapes.
5. The IM-01 and TH-05 test is circular.
6. Removal reasons are partly about the wrong company (Brighthouse, Fluor, Dun and Bradstreet).
7. Tickers in `ticker_history` can be the current ticker, not the one used at the time (the upstream file labels Dr Pepper Snapple KDP from 2008).
8. Vacuous or weak tests: DB-09-AC2, FD-01-AC1, the AE-03 one-basis test, EQ-07-AC1, IG-16, DB-16.
9. The consensus capture list (89) is not the universe (9 outside it).
10. The scheduled 22:30 UTC capture calls Yahoo whatever `CAPTURE_CATCH_UP` says.
11. The worker can UPDATE `company`, `ticker_history`, `index_membership` (a judgement under DB-08).
12. IG-09 not met.
13. Plan map: SR-06, IG-04 and IG-05 sit in waves that cannot complete them, and LB-03 is mapped to Wave 1.6 though its derivation was built in 1.4.

## 5. Not verified by the auditor

The spike numbers (no network), real data fetches, source facts after its knowledge cutoff, the 20-value hand check, a worker killed mid-task, real broker timing of the backoff, pip-audit, gitleaks, GitHub CI, and whether the capture runs produced real snapshots.

## 6. Reconciliation (builder's response, 24 November 2026)

| # | Finding | Response | State |
|---|---|---|---|
| 1 | The superuser password is in every container; an unused superuser URL | The unused `database_url` is removed and the superuser settings are optional. The worker no longer receives the superuser at all (a test reads the compose file). The `api` service still has it because the CI job runs the tests inside it and they build a test database; moving that to its own service needs a change to the CI workflow, which John has not approved (DR-11) | FIXED in part |
| 2 | Fiscal labels describe the filing | Migration 0006 renames the columns `filing_fiscal_year` and `filing_fiscal_period`. Periods are matched by their dates only | FIXED |
| 3 | The universe breaks C-47: companies that joined after 31 December 2024 | True and my bug: `current` meant any open membership. It now means in the index on 31 December 2024. The 100 were re-selected (the seeded draw changes entirely when the pool changes), the database tables were rebuilt from the stored payloads, and 72 new companies were fetched. No selected company joined after 2024 | FIXED |
| 4 | Rules and shapes not recorded as decisions | Listed as open decision D-47 for John | OPEN, needs John |
| 5 | The IM-01 and TH-05 test is circular | It now recomputes the year-end company counts from two real fixtures (the full membership file and the ticker to CIK map), no longer reading a report. The map itself is the matcher's output | FIXED in part |
| 6 | Removal reasons about the wrong company | A reason that names another company is stored as "not stated for this company; the source row reads: ...", a blank one as "the source gives no reason", and general statements ("Market capitalization changes.") are kept. Tested | FIXED |
| 7 | Tickers in the upstream file can be the current one, not the one used then | Not fixable here: the membership file is the source. Recorded as DR-20 | OPEN, stated limit |
| 8 | Vacuous or weak tests | DB-16 now tests the guards in `drop_database` and `truncate_all`; FD-01 compares stored filing dates and versions with the payload; EQ-07 runs the capture task itself twice; the approved selection values are pinned; the stack that never captured reports a gap from the start day; fundamentals versioning is tested. DB-09-AC2 stays vacuous until feature code exists; AE-03's one basis is a column default (the consensus snapshots carry their own basis, which VL-07 in Wave 1.7 must reconcile) | FIXED in part |
| 9 | The capture list is not the universe | The list keeps the 10 companies captured before the universe existed, plus every current member of the list (86 now). Recorded in D-47 (h) | ACCEPTED, needs John |
| 10 | The scheduled capture calls Yahoo whatever the catch-up setting | True: the setting governs the start-up catch-up only. The `.env.example` text now says so | FIXED (wording) |
| 11 | The worker can update `company`, `ticker_history`, `index_membership` | A judgement under DB-08; they are not versioned facts. Left | ACCEPTED |
| 12 | IG-09 not met | Known, a Should, stated | ACCEPTED |
| 13 | Plan map | LB-03 moved to Wave 1.7. SR-06, IG-04 and IG-05 stay where they are: each has a part that can be tested there and a part that waits | FIXED in part |
| 14 | The owner's email address appears once in the git history | It is the Author header of one commit made through the GitHub website, not file content. Rewriting history is not something to do without John; recorded as DR-21 for him to decide | OPEN, needs John |
| 15 | IG-16 quartiles printed as unordered magnitudes | The Section 12 text says "quartiles 1,008, 180 and 59 minutes" for gaps that are negative (the filing came first). Correcting the wording of an approved requirement text needs John | OPEN, needs John |

Mutations missed by the auditor (M25, M29, M33, M41): each now has a test that fails under it (a fundamentals versioning test, the pinned selection values, the start-day gap test, the guard test).

Statuses of the auditor that stand for now (lower of the two): SR-06 FAIL; IG-09 FAIL (a Should); SR-05 UNVERIFIED; DB-02, SR-10, EQ-07, IG-01, IG-04, IG-05, IG-07, DB-09, FD-01, FD-02, IG-15, LB-03, AE-03 and others PARTIAL as in its table. The gate result for Phase 1 is PARTIAL.
