# Implementation Audit

The accountability file for the build. It holds me to [Deterministic_audit.md](../Deterministic_audit.md) while the code is written, wave by wave. It does not replace that file or the generated [requirements_traceability.md](requirements_traceability.md). If this file and the SSOT or a requirement disagree, the SSOT or the requirement wins and the disagreement is entered in the drift register (Section 5).

Plan: [docs/implementation-plan.md](../docs/implementation-plan.md). Coverage map: [plan_coverage.txt](plan_coverage.txt). Checker: `python3 scripts/check_plan_coverage.py`.

## 1. What I am accountable for

1. **No claim without evidence.** Every statement in a completion report that something works, passes, exists or was measured names the command that produced it and the evidence file that holds the output. A statement with no command and file is written as "not verified".
2. **No self-grading.** I never mark a wave or requirement PASS from my own earlier claims. PASS needs the wave gate output (Section 2) and, at phase end, the independent audit (Section 4).
3. **Status words are exact.** PASS, PARTIAL, FAIL, BLOCKED, UNVERIFIED (Deterministic_audit.md Section 8), plus NOT STARTED and IN PROGRESS for the ledger. A skipped test is NOT TESTED or BLOCKED, never PASS. A placeholder is not a test.
4. **Verify before I cite.** Before I name a file, function, library version, flag or API, I check that it exists in the repository or the installed environment in this session. Memory of an earlier session is not a source.
5. **No invented values.** A value still pending in [pending_values.md](pending_values.md) is never defaulted. Tests that need it stay BLOCKED and I ask.
6. **No weakened checks.** I never delete, skip, loosen or reword a test or an acceptance check to make it pass, and I never edit a requirement to fit the code. A disagreement goes in the drift register.
7. **Data is labelled.** Real, synthetic and mock data are named as such in every test, table and report. No synthetic or mock data in a reported result (SC-04).
8. **Estimates are not measurements.** Hours, speeds and sizes are "estimate" until measured, and the measured figure replaces them in the ledger.
9. **Scope.** I build only what the wave brief lists. Anything else is a change entry (SS-04) first.
10. **Corrections are recorded.** If I find that something I said earlier was wrong, I write it in Section 6 with the date, even if no one noticed.

## 2. Wave gate: the commands and what they decide

A wave is PASS only when every line below was run in this session, in order, and its output is saved in `audits/evidence/wave-X.Y.md` under the headings shown. Replace the first command with the one in `.github/workflows/ci.yml` if CI changes.

| # | Check | Command | Decides |
|---|---|---|---|
| 1 | Stack builds and starts from clean | `cp .env.example .env && docker compose up --build -d --wait --wait-timeout 300` | Environment OK or BLOCKED |
| 2 | Full test run | the `pytest` command in the `tests` job of `.github/workflows/ci.yml`, with `--junitxml` | Counts of passed, failed, skipped, with each skip reason |
| 3 | Regression against the baseline | compare the counts with `audits/evidence/wave-0.1-baseline.md` | No test that passed before now fails or skips |
| 4 | Lint, format, types | `ruff check .`, `ruff format --check .`, `mypy` (inside the dev environment as CI does) | EQ-02 |
| 5 | Requirement documents consistent | `python3 docs/tools/check_requirements.py` | DO-05 |
| 6 | Generated files match | `python3 audits/generate_traceability.py` then `git diff --exit-code audits/` | Generated files are current, never hand-edited |
| 7 | Test matrix | `python3 scripts/test_matrix.py build` then `python3 scripts/test_matrix.py verify` | Every check has a test, no stale check text |
| 8 | Test and commit references | `python3 scripts/check_requirement_refs.py`, `python3 scripts/check_commit_refs.py` | Markers and commit IDs real |
| 9 | Plan coverage | `python3 scripts/check_plan_coverage.py` | Plan, map and ledger agree |
| 10 | Wave requirement result | list each requirement ID of the wave with PASS, PARTIAL, FAIL, BLOCKED, UNVERIFIED and the test names that support it | The wave's own result |
| 11 | Coverage where a floor exists | `python -m coverage run -m pytest tests` then the report (EQ-09) | At least 80% where required |
| 12 | Idempotence for each new task | run twice, compare table state | EQ-07 |
| 13 | Drift and deviations | list each disagreement found, or write "none found" and say which checks were run to look | Section 5 entries |
| 14 | Hours and checks | hours spent in the wave and the number of acceptance checks that moved from NOT TESTED to a real test, from `audits/test_matrix.md` before and after | Velocity for the December forecast |

A wave with any FAIL stays IN PROGRESS. A wave with only BLOCKED or NEEDS PERSON items is PARTIAL, naming each item, never PASS.

## 3. Evidence file format

`audits/evidence/wave-X.Y.md` contains, with these headings: `Wave X.Y`, `Requirements`, `Commands run` (exact text), `Output` (the real output or a trimmed excerpt with its line count), `Result per requirement`, `Not verified`, `Drift found`, `Assumptions`, `Measured values` (with units and the command), including hours spent in the wave and acceptance checks closed, which feed the velocity forecast in plan Section 5.1. The file must contain the text "Wave X.Y", which the checker looks for.

## 4. Phase gate: independent audit

At the end of each phase, in this order:

1. Mechanical: Section 2 checks over the whole phase, run again from a fresh clone.
2. A fresh subagent gets only the phase's requirement IDs and the repository path. It does not get my reports. It runs the tests itself and writes its own result per requirement in `audits/evidence/phase-N-independent.md`. Where its result differs from mine, the lower status stands until the difference is explained.
3. John checks at least five requirements per phase against the evidence, chosen by him.
4. The phase row below is updated only after steps 1 to 3.

| Phase | Mechanical | Independent audit | John spot-check | Result |
|---|---|---|---|---|
| P0 | run (every wave commit) | run 23 Nov 2026, see audits/evidence/phase-0-independent.md | not run | PARTIAL |
| P1 (Waves 1.1 to 1.4 so far) | run on every wave commit | run 24 Nov 2026, see audits/evidence/phase-1-independent.md | not run | PARTIAL |
| P2 | not run | not run | not run | NOT STARTED |
| P3 | not run | not run | not run | NOT STARTED |
| P4 | not run | not run | not run | NOT STARTED |
| P5 | not run | not run | not run | NOT STARTED |
| P6 | not run | not run | not run | NOT STARTED |
| P7 | not run | not run | not run | NOT STARTED |
| P8 | not run | not run | not run | NOT STARTED |

The overall project cannot be PASS while any Must requirement is FAIL, PARTIAL, BLOCKED or UNVERIFIED (Deterministic_audit.md Section 8).

## 5. Drift register

Each row is something where code, a test, a document or the plan does not agree with a requirement or decision. Rows are closed only by John's decision or by the disagreement ending, never by editing the requirement to fit.

| # | Date | Found in | Disagreement | Status |
|---|---|---|---|---|
| DR-01 | 23 Nov 2026 | decision-log C-23, `.github/workflows/ci.yml` | C-23 says five CI checks are required. The workflow has six jobs (pins, lint-and-types, tests, requirements, secrets, vulnerabilities) | OPEN. Needs John (plan decision K) |
| DR-02 | 23 Nov 2026 | Product Section 11, Data SR-10 | EstimateSnapshot has a required `event_id` but a forward snapshot is taken before the event exists | OPEN. Schema change, needs John (D-38, plan decision E) |
| DR-03 | 23 Nov 2026 | decision-log C-06, plan Section 5.1 | C-06 says pipeline, models, API, agent and evaluation are finished by end of December. The estimated plan, at about 15 minutes per acceptance check, reaches only part of that and no speed has been measured | DECIDED by John (keep December). RISK OPEN: forecast at each checkpoint, apply PD-04 if it misses by more than a week |
| DR-06 | 23 Nov 2026 | decision-log C-19, Spike B | C-19 matches current tickers to a CIK through the SEC file. XOM maps to CIK 2115436 (ExxonMobil Holdings Corp, history from 2025-06-30), while its history is under CIK 34088 | OPEN. Needs John |
| DR-07 | 23 Nov 2026 | Product FR-22, Ingestion IG-15, Spike A | Call times must be stored in UTC, but the Hugging Face `date` field states no time zone | CLOSED 23 Nov 2026 by decision C-42: stamps are US Eastern with daylight saving, stored in UTC. Evidence: Spike A2 |
| DR-08 | 23 Nov 2026 | `.github/workflows/ci.yml`, tests | The CI `tests` job mounts only `tests/` and one file, so 20 checks that read documents, the workflow and scripts skip as NEEDS REPO there | OPEN. John did not approve a new CI job on 23 Nov 2026 (C-45) |
| DR-09 | 23 Nov 2026 | decision-log C-19, D-32, Spike D | The membership candidate is keyed by ticker with no company identifier, but C-19 makes the CIK the permanent identifier | OPEN. The ticker to CIK mapping is an IM-03 task for Wave 1.3 |
| DR-10 | 23 Nov 2026 | Data SR-06, source register | The register has no documented fallback for the 8-K announcement time, and every other fallback is untested | OPEN. Needs John: name a fallback or accept a stated scope limit |
| DR-12 | 23 Nov 2026 | `src/earnings/consensus.py`, first capture | The first day's 10 rows carry the run start time, not each row's arrival time (up to 12 s) | FIXED in code for later rows; the stored rows stay as they are (append-only) |
| DR-13 | 23 Nov 2026 | `main` branch protection, `.github/workflows/ci.yml` | C-23 listed five required checks and the sixth CI job (Requirements consistency) was not required | CLOSED 23 Nov 2026 by decision C-45: the sixth check is now required (applied with gh) |
| DR-14 | 23 Nov 2026 | Data SR-04, `raw_payload` (C-45) | SR-04 asks for the source version to be stored; the approved table has no such column | OPEN. Needs John: add a nullable `source_version` column |
| DR-15 | 23 Nov 2026 | Data SR-08, Phase 0 audit finding 3 | The database enforces only a lower bound on `captured_at`; the worker could insert a future time. The code stamps real time | OPEN, accepted: a check against now() would break tests that use fixed dates |
| DR-16 | 23 Nov 2026 | Ingestion IG-13 | The rename-adjacent rule (same-day end and start with no recorded index change) is not among the matching methods IG-13 names | OPEN. Needs John to confirm the method; all 21 links were read by hand |
| DR-17 | 23 Nov 2026 | Data IM-02, Wikipedia | Removal reasons are the source's wording and can describe the paired event | OPEN, stated limit |
| DR-18 | 24 Nov 2026 | Product Section 11, migration 0005 | `eps_history` and `fundamentals_filing` have columns beyond the Section 11 field lists | OPEN. Needs John's approval and a Section 11 update |
| DR-19 | 24 Nov 2026 | Data LB-02, SEC company facts | Dimensioned facts are missing from the API, so Visa and Danaher have no EPS and a few companies have two quarters | OPEN, stated limit. A fallback source is not built |
| DR-20 | 24 Nov 2026 | `fja05680/sp500`, Data IM-03 | The membership file can carry a company's current ticker for years when it used another (Dr Pepper Snapple as KDP from 2008), so a lookup by the old ticker finds nothing | OPEN, stated limit of the source |
| DR-21 | 24 Nov 2026 | git history, Project-Wide SP-06, decision C-10 | John's email address is the Author header of one commit made through the GitHub website. It is not file content | OPEN. Needs John (leave, or use a no-reply address from now on) |
| DR-22 | 24 Nov 2026 | Data SR-10 | The capture list holds 10 companies captured before the universe existed; 9 are outside the 100-company list | OPEN, in D-47 (h) |
| DR-23 | 25 Nov 2026 | Data TX-03, Ingestion IG-18, decision C-48 | The approved boundary rule can mark the wrong turn when the opening operator turn speaks of a question session and the transcript starts with two list turns (sample item 1, Caterpillar 2017-10-24: boundary at turn 2, the opening announcement). The rule is not changed; John's 50 labels measure it (TH-02, 95%) | OPEN, waits for John's labels |
| DR-24 | 25 Nov 2026 | Data TX-07, SR-03 | 7 of the 100 companies have no transcript in the Hugging Face set (CSRA, Dun & Bradstreet, Hospira, Keurig Green Mountain, Precision Castparts, St Jude Medical, Whole Foods Market); 138 calls have no 8-K Item 2.02 within 3 days; 3,183 calls loaded (about 66% of 12 years x 4 x 100) | OPEN, coverage gaps reported, nothing filled |
| DR-25 | 25 Nov 2026 | Data TX-07, GATE-1, Product PG-4 | Transcript coverage differs by group: 2,794 of 3,069 releases (91%) of companies still in the index have a transcript, but 389 of 661 (59%) of companies that left it. A model trained on this set sees fewer removed companies (survivorship, IM-02) | OPEN, reported for the Wave 1.7 gates and John |
| DR-26 | 25 Nov 2026 | Data LB-02, AE-02, DR-19 | The label is available for 2,619 of 3,183 events (82%). Unavailable: 243 no quarter of that period in the EPS data, 178 fewer than 6 prior differences, 143 no quarterly EPS stored for the company at all (the SEC tag differs) | OPEN, no fallback source chosen (DR-19) |
| DR-27 | 26 Nov 2026 | Data DV-04, AE-04, LB-04 | Two 10-K filings give quarterly EPS in thousands (Intercontinental Exchange, Hartford); the first-filed value is then wrong by a factor of a million and two labels are about 1.8 and 1.1 million, and 24 labels in all use an inflated value (corrected 26 Nov). Quarantined, not removed or corrected | OPEN, John decides whether to exclude, correct from a later filing, or keep flagged |
| DR-28 | 26 Nov 2026 | Data AE-02, LB-03, VL-08, TH-03 | The automatic press-release parser reads about half of the releases; AE-02 (98%) cannot be shown by it | OPEN, needs either a better parser or a person to check the sample |
| DR-29 | 26 Nov 2026 | Data DV-05 against decision C-17 | DV-05 says the announcement is on or before the transcript; C-17 allows a call before the 8-K. 11 events | OPEN, a wording change to DV-05 needs John |
| DR-30 | 26 Nov 2026 | Data LB-04, DV-06 | Found and fixed: a quarter re-filed with a shifted start date was treated as a second period and could replace the first-filed value. 47 company-quarters had the pattern; 15 labels changed | CLOSED, regression test added |
| DR-31 | 26 Nov 2026 | Wave 1.6 brief point 3, Data LB-05 | I built split inference from filing ratios, which the approved brief did not allow ("from the EPS facts' own share-basis fields in the SEC data where present; otherwise BLOCKED"). It was wrong in many cases and my evidence file reported it as working. Nine defects in all, see `audits/evidence/bug-review-2026-11-26.md` | CLOSED for the defects listed, regression tests added |
| DR-32 | 26 Nov 2026 | Data LB-05, PX-01 | Companies that do not report the SEC split tag, and reverse splits, are not adjusted | OPEN until the price source's dated factors are stored (Wave 1.8) |
| DR-05 | 23 Nov 2026 | decision-log D-38, Database DB-03 | D-38 lists pool and time-out values as "not approved" but gives none | CLOSED 23 Nov 2026 by decision C-44 (values proposed and approved) |
| DR-11 | 23 Nov 2026 | `docker-compose.yml`, Database DB-02 | All role passwords were in every service's environment, with the superuser password | PARTLY FIXED 24 Nov 2026: the worker no longer gets the superuser password. The api service keeps it because the CI tests run inside it (a CI change John has not approved). Cloud must give each service only its own secret (DP-06) |
| DR-04 | 23 Nov 2026 | `requirements-pending.txt`, `requirements.txt` | Alembic (needed for PL-05) is pinned but not installed. Moving it is a dependency change | OPEN. Shown in the Wave 0.2 brief |

## 6. Corrections to my own earlier statements

| Date | What I said | What is true | How I know |
|---|---|---|---|
| 22 Nov 2026 | The first plan draft said P0 to P3 finish by 31 December | Phases cannot overlap, and the cumulative estimate to the end of P3 is about 112 hours against 70 to 90 available | Plan Section 5 recomputed |
| 22 Nov 2026 | The plan said the pipeline has five CI checks | `.github/workflows/ci.yml` has six jobs | Read the file on 23 Nov 2026 |
| 23 Nov 2026 | The plan put the SUE class thresholds in Wave 1.6 | LB-06 and VL-06 set them during EDA and freeze them after, so they belong to Wave 2.5 | Read the requirement text during the second review |
| 23 Nov 2026 | The plan put SR-02 and SR-03 in Wave 0.1 as a source register | They are code checks (feature source tag, demo bundle manifest) for Waves 2.4 and 7.4 | `tests/test_req_data.py` |
| 23 Nov 2026 | The plan said Wave 0.2 covers DB-04, DB-05 and DB-17 and Wave 0.3 covers CE-01 to CE-04 and FR-14 | Their checks need ticker history, later tables, announcement dates and events, which do not exist in P0 | `audits/test_matrix.json` checks |
| 23 Nov 2026 | I cited 22:30 UTC in code and a test as approved by C-44 and D-45 | John did approve it, in an answer to a question that day, but I did not record it in the decision log, so the log did not support the claim (found by the Phase 0 independent audit). Recorded as C-46 | `docs/decision-log.md`, audit finding 2 |
| 23 Nov 2026 | An early draft of the gap table said the plan cited "385 of 480" IDs | The check I ran counted 95 uncited Must requirements among 414 parsed rows. 385 was subtraction I had not measured | Re-ran the check, replaced the sentence |

## 7. Wave ledger

One row per wave in the plan. The checker fails if a wave is missing, if a status word is wrong, or if PASS has no existing evidence file naming the wave. Update a row only when the gate output exists.

| Wave | Name | Status | Evidence |
|---|---|---|---|
| W0.1 | Baseline, source register and spikes | IN PROGRESS | audits/evidence/wave-0.1-register-and-adr.md |
| W0.2 | Database foundation and plumbing slice | PARTIAL | audits/evidence/wave-0.2.md |
| W0.3 | Forward consensus capture job | IN PROGRESS | audits/evidence/wave-0.3.md |
| W1.1 | Task framework and client rules | PARTIAL | audits/evidence/wave-1.1.md |
| W1.2 | Storage rules | PARTIAL | audits/evidence/wave-1.2.md |
| W1.3 | Universe and identifiers | PARTIAL | audits/evidence/wave-1.3.md |
| W1.4 | Financial data | PARTIAL | audits/evidence/wave-1.4.md |
| W1.5 | Transcripts and preparation | PARTIAL | audits/evidence/wave-1.5.md |
| W1.6 | Events, label and validation | PARTIAL | audits/evidence/wave-1.6.md |
| W1.7 | Dataset validation and sign-off | PARTIAL | audits/evidence/wave-1.7.md |
| W1.8 | Prices | NOT STARTED | - |
| W2.1 | Sentences and FinBERT | NOT STARTED | - |
| W2.2 | Linguistic features | NOT STARTED | - |
| W2.3 | Tabular features | NOT STARTED | - |
| W2.4 | Matrix, registry and versioning | NOT STARTED | - |
| W2.5 | EDA and feature report | NOT STARTED | - |
| W3.1 | Split and baseline | NOT STARTED | - |
| W3.2 | Tuning, calibration, freezing | NOT STARTED | - |
| W3.3 | Full model, SHAP and metrics | NOT STARTED | - |
| W3.4 | One-time test read, report, scoring task | NOT STARTED | - |
| W3.5 | Model governance and promotion | NOT STARTED | - |
| W4.1 | Layers and prediction endpoints | NOT STARTED | - |
| W4.2 | Operability | NOT STARTED | - |
| W4.3 | Evaluation endpoint and authentication | NOT STARTED | - |
| W5.1 | Selection and retrieval | NOT STARTED | - |
| W5.2 | Generation | NOT STARTED | - |
| W5.3 | Verification and safety | NOT STARTED | - |
| W5.4 | Job endpoints and faithfulness harness | NOT STARTED | - |
| W6.1 | Client and prediction card | NOT STARTED | - |
| W6.2 | Explanation and evaluation views | NOT STARTED | - |
| W6.3 | Packaging and study readiness | NOT STARTED | - |
| W7.1 | Resilience | NOT STARTED | - |
| W7.2 | Security and supply chain | NOT STARTED | - |
| W7.3 | Operations and performance | NOT STARTED | - |
| W7.4 | Optional cloud | NOT STARTED | - |
| W8.1 | Evidence closure | NOT STARTED | - |
| W8.2 | Usability study | NOT STARTED | - |
| W8.3 | Dissertation | NOT STARTED | - |
| W8.4 | Buffer and polish | NOT STARTED | - |

## 8. Time-gated checks (cannot be run yet)

Checks that need a later moment or later data. Anyone continuing the work runs these first and records the result in the evidence file of the wave they belong to. A passed date does not mean a pass: run the command.

| Check | Earliest | Command | What a pass looks like | Belongs to |
|---|---|---|---|---|
| The scheduled 22:30 UTC capture fires by itself | after 2026-11-23 22:30 UTC | `docker compose exec -T api python -m earnings.consensus`, and `docker compose logs worker | grep "Scheduler: Sending due task"` | at least 2 capture days listed, no gap, a beat line for `capture-consensus` | Wave 0.3 (SR-10-AC1) |
| SEC bulk files refreshed nightly (second observation: done 24 Nov, refreshed; every night not shown) | 2026-11-24 | HEAD request to `companyfacts.zip` and `submissions.zip` under `https://www.sec.gov/Archives/edgar/daily-index/`, compare Last-Modified with 2026-11-21 05:08 and 05:15 GMT | a later Last-Modified on both | Wave 0.1 (IG-09) |
| Capture has run on 4 or more days without a gap over 3 days | 2026-11-27 | `python -m earnings.consensus` | no GAP line | Wave 0.3 (SR-10-AC2), VL-10 needs 4 weeks |
| The 22:30 UTC schedule fires on its own (not seen yet: the day-2 snapshots came from the start-up catch-up at 01:24 UTC) | after 22:30 UTC on any day the stack is running | `docker compose logs worker | grep "Scheduler: Sending due task"` and `python -m earnings.consensus` | a beat line for `capture-consensus` and a capture run started at about 22:30 | Wave 0.3 (SR-10-AC1) |
| Retry waits are real (30, 60, 120 s before jitter) | any time | inject a failing task into the running worker and read the worker log | three retries at roughly those intervals, one dead letter | Wave 1.1 (IG-02) |

## 9. Audit health check, 23 November 2026

What was run to see that the auditing itself works, and what it showed:

- `python3 scripts/check_plan_coverage.py`: 480 of 480 requirements mapped, 38 waves in the plan and the ledger, passes. A planted PASS without evidence and a planted invented ID were both rejected earlier.
- The drift controls (`check_requirements`, generator diff, matrix `verify`, reference and commit checks) pass on every wave commit.
- A fault injected into each new rule (roles, time-outs, retries, rate limit, host check, as-of strictness, validity boundary, append-only privileges) made at least one test fail, and the files were restored each time.
- The independent audit of Phase 0 (Section 4) ran with a fresh agent, in an isolated clone, given only requirement IDs. Its report is in `audits/evidence/phase-0-independent.md` with my reconciliation. It found real problems: a writable migration history table, an approval I had not recorded, a test that accepted "not tested", a pool test that followed its own constants, and an unguarded outside call on stack start. All but three were fixed the same day; the rest are listed in its reconciliation table.
- Where my own checks were wrong I wrote it down (Section 6), for example the test arithmetic error in the late-job test and the first fault injection that only broke the migration.
