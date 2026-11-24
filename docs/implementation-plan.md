# Implementation Plan

Status: methodology and gate structure approved by John on 23 November 2026. Decision A: the December target (C-06) stays (Section 5.1). Revised twice that day after gap reviews (Section 2.3). This is a plan, not a requirements document. It defines no requirement. It orders the work, and every item cites the requirement IDs that define it. If this plan disagrees with the [SSOT](SSOT.md) or a requirement, the SSOT or the requirement wins and the plan is corrected.

Inputs read for this plan: the SSOT, the requirements index, the 12 requirement documents (IDs only for the component ones), the [decision log](decision-log.md), [pipeline.md](architecture/pipeline.md), the CI workflow, the current `src/` and `tests/`, and [audits/test_matrix.md](../audits/test_matrix.md).

## 1. Where the project is today

- Built: the Docker skeleton (PostgreSQL, Redis, Celery worker, FastAPI with /health), CI with five checks, the requirement documents, the generated acceptance index, traceability file and test matrix.
- Not built: everything else. `src/earnings/` is 232 lines. Almost every test in `tests/test_req_*.py` is a placeholder that calls `not_tested("NOT IMPLEMENTED", ...)`. Each wave below turns placeholders into real checks.
- Dates: today is 22 November 2026. By the end of December the pipeline, models, API, explanation agent and evaluation are to be finished, with Christmas week as buffer (C-06). Final submission is probably late February 2027 (C-13, D-29).

## 2. Methodology: gated incremental delivery

### 2.1 The options, judged against this project

| Method | Fits | Does not fit | Verdict |
|---|---|---|---|
| Waterfall | Requirements are frozen, written and traceable. The ML pipeline has hard data dependencies (no model without features, no features without events). | One long pass finds integration and data problems too late. A dataset that fails a data gate in week 6 would be found after everything else is built. | Use for the phase order only |
| Scrum | Time-boxed iterations. | It needs a team, a product owner and ceremonies (planning, review, retrospective, daily meetings). One person working 15 to 20 hours a week would spend the time on the ceremonies. Its "the backlog changes every sprint" idea conflicts with the drift controls and Project-Wide SS-04. | Do not use |
| Kanban | Light, solo friendly, work-in-progress limit. | No built-in verification gate. | Borrow the limit of one open wave |
| Spiral or risk-driven | The riskiest unknowns here are data availability (free transcripts, EPS history, point-in-time dates) and FinBERT speed on a CPU. | Heavy as a full method. | Borrow the idea: spikes and a walking skeleton first |
| Test-driven and acceptance-test-driven | The acceptance checks already exist (`ID-ACn` in [acceptance_index.md](../audits/acceptance_index.md)) with placeholder tests that name them. | Not a lifecycle by itself. | Use inside every step |

### 2.2 Recommendation

**Plan-driven phases, agile waves, test-first steps, with a gate at every level.**

1. **Phases are sequential and gated** (waterfall-like). A phase starts when its entry gate is met and ends when its exit gate passes. The order follows the data: data, features, model, API, agent, dashboard, hardening.
2. **Waves are short, time-boxed increments** (agile-like), about one week each, ending in something that runs. Only one wave is open at a time.
3. **Steps are test-first** (acceptance-test-driven). A step starts by turning one or more placeholder tests into a failing real test, then the code that makes it pass.
4. **Risk first.** Phase 0 runs the data spikes and builds a thin end-to-end slice on 5 companies before anything is widened to 100. Integration problems then appear in week 2, not week 10.
5. **Scope is controlled, not iterated.** The backlog is the frozen requirements. Nothing is added without a change entry (SS-04). If capacity runs out, the drop order in PD-06 is applied, not a re-plan.

Why this and not Scrum: the project's real constraints are frozen requirements, an audit-first governance rule, a single developer and fixed dates. That calls for a plan-driven spine with agile execution inside it.

### 2.3 Gap review of this methodology (23 November 2026)

The first draft was checked mechanically and against the repository. These problems were found and fixed in this revision. The coverage check is `python3 scripts/check_plan_coverage.py`.

| # | Problem found | Evidence | Fix |
|---|---|---|---|
| 1 | The first draft left 95 Must requirements uncited. They are in no wave. Most are data validation (DV, VL, GS, TX, AE, CE, PX, FD), source rules (SR), model governance (ML-03 to ML-06, MR-02, TR) and project-wide items. | A script read the requirement tables in `docs/requirements/` (414 rows, 290 of them Must) and listed the Must IDs the plan did not cite. It used the plan text only, so it could not tell whether a prefix-level mention such as "Data AE, FD, PX" covered an ID | Every one of the 480 IDs in the traceability file is now mapped exactly once in [audits/plan_coverage.txt](../audits/plan_coverage.txt) and the check fails if one is missing |
| 2 | Three waves were missing: the forward consensus capture job (time-critical, its four-week trial needs data to accumulate), dataset validation and sign-off, and model governance | Data SR-10 and VL-10; Data GS-01, DV-01 to DV-08; ML-05, ML-06, MR-02 | Added Waves 0.3, 1.7 and 3.5 |
| 3 | The phase windows overlapped (P1 to 13 Dec, P2 from 7 Dec, P3 from 14 Dec) while the rules say one wave is open at a time and a phase starts after the previous gate | Section 5 of the first draft | Windows are now sequential and the capacity table is cumulative |
| 4 | The first draft said CI has five checks. `.github/workflows/ci.yml` has six jobs (pins, lint-and-types, tests, requirements, secrets, vulnerabilities). Decision C-23 says branch protection requires five. | `.github/workflows/ci.yml` | The plan says "all CI jobs". The C-23 count is reported as a possible drift to John, not corrected here |
| 5 | A subagent audit is not independent of me: it is the same model and can share my blind spots | Deterministic_audit.md Section 7 asks for independent inspection | Mechanical checks run first and decide what they can. The subagent is told nothing of my claims. John spot-checks a sample (Section 3.3) |
| 6 | Reading the test set is irreversible, but the first draft treated it as a normal step | Product ML-02, Data GATE-4 | Step 3.4.2 now needs John's explicit approval first |
| 7 | Step sizes were inconsistent: some waves had seven steps of up to three hours inside a one-week wave | Wave 2.1 | Waves are capped at 12 hours. A wave estimated above that is split before it starts |
| 8 | No rule for a failed gate, a changed plan or a wave that needs a value that is still pending | none | Section 4.1 |
| 9 | A walking skeleton was promised in P0 but the step needed a network fetch that belongs to the task framework in P1 | Wave 0.2 of the first draft | P0 builds the plumbing slice (task, database, migration, roles). The first real EDGAR slice for 5 companies is Step 1.1.7 |
| 10 | The EstimateSnapshot entity in Product Section 11 has a required `event_id`, but a forward capture job takes snapshots before the event row exists | Product Section 11; Data SR-10 | Reported as an open schema question for Wave 0.3. Not decided here (D-38 covers schema additions) |
| 11 | The scheduled daily capture needs a scheduler. The compose file has four services and no Celery beat. A fifth service is an architecture change. Capture also only runs while the owner's PC is on. | `docker-compose.yml`; IG-05 | Step 0.3.4 asks John to approve the scheduler. The SR-10 gap rule (report more than 3 missing days) covers the PC-off case |
| 12 | The tools the plan needs are not installed locally: Python is 3.14.4 here, the project pins 3.12.16, and pytest is not installed locally | `python3 --version`; `python3 -m pytest` | All tests run in the Docker stack, as CI does. Stdlib-only scripts run locally |

**Second review, 23 November 2026, against the requirement text and the test matrix.** Method: for every requirement, read its acceptance checks and the tests that name them in `audits/test_matrix.json`, and compare with the wave it was mapped to. Findings:

| # | Problem found | Evidence | Fix |
|---|---|---|---|
| 13 | The class thresholds (LB-06, VL-06, TH-07) were placed in Wave 1.6 but the requirement says they are set during EDA and frozen after. The EDA notebook is in Wave 2.5, so the first draft contradicted itself (Step 1.6.2 against Step 2.5.3) | Data LB-06 and VL-06 text | Moved to Wave 2.5. Wave 1.6 stores the continuous SUE only |
| 14 | SR-02 (source tag on every feature column, untagged column fails the build) and SR-03 (demo bundle manifest, personal-use source fails the check) are code checks. They were placed in Wave 0.1 as if they were a document | `tests/test_req_data.py` placeholders | SR-02 to Wave 2.4, SR-03 to Wave 7.4. The register in 0.1 is a machine-readable file with its own test |
| 15 | DB-05's check says an insert of a duplicate "of each" unique key fails, but its entities (prediction, explanation) arrive in Waves 3 to 5. DB-04's check is a join across ten known ticker changes. DB-17 compares Section 11 with the final migrated schema | Database requirements checks | DB-05 to 5.4, DB-04 to 1.3, DB-17 to 7.1. Wave 0.2 claims only what it can test |
| 16 | CE-01 to CE-03 and FR-14 need announcement dates, events or other waves' tests (VL-01, VL-07), none of which exist in Wave 0.3 | Data CE-01 to CE-03 checks | CE-01 to CE-03 to Wave 1.7, FR-14 to 1.6, CE-04 and TH-04 to 3.4. Wave 0.3 claims SR-08 and SR-10 |
| 17 | `test_sc_07_ac1` and `test_sc_06_ac1` are expected failures because no ADR exists. The first draft never scheduled the ADRs. SC-07 says the label-route ADR is due at the end of week 2 | `audits/test_matrix.md` | SC-07 ADR is Step 0.1.9. SC-06 ADR stays in Wave 5.1 |
| 18 | D-38 says pool and time-out values are "not approved" but states no numbers. My request to "approve the D-38 items" asked for approval of values that do not exist yet | Decision log D-38; DB-03 | Wave 0.2 cannot finish DB-02 and DB-03 until concrete values are proposed and approved. Proposed in the Wave 0.2 brief, not assumed |
| 19 | The first draft's hours (178 for P0 to P7) came from judgement. The matrix shows 531 checks to P8, so the estimates imply a few minutes a check | `audits/test_matrix.json` | Section 5.1 adds a measured velocity and checkpoints |

Limits that remain. The estimates in Section 5 are my guesses until measured. A map from requirement to wave shows where the work is planned. It does not show the requirement is met. The audit does that.

## 3. The levels and the three gates

| Level | What it is | Size | Ends with |
|---|---|---|---|
| Phase | A major feature, mapped to an SSOT milestone | 1 to 3 weeks | Phase gate |
| Wave | An important part of a phase that runs on its own | 12 hours at most, about a week | Wave gate |
| Step | One small change leading to a wave, tied to requirement IDs | one session, 1 to 3 hours | Step gate |

### 3.1 Step gate (every step, seconds to minutes)

1. The new test fails for the right reason (red). A placeholder is replaced by a real check carrying `@pytest.mark.req("ID-ACn")` and, where useful, `@pytest.mark.code(...)`.
2. The smallest change makes it pass (green).
3. `ruff check`, `ruff format --check` and `mypy` pass.
4. The step's test and every test that already passed still pass.

### 3.2 Wave gate (every wave)

All of these, with the output kept as evidence:

1. All tests for the wave's requirement IDs pass. None is a placeholder any more, unless the reason is a blocked decision or a person (then it is reported as BLOCKED or NEEDS PERSON, never PASS).
2. Full regression: the whole `pytest` run against the running Docker stack.
3. `python3 scripts/test_matrix.py verify`, `python3 audits/generate_traceability.py`, `python3 docs/tools/check_requirements.py`, `scripts/check_requirement_refs.py` and `scripts/check_commit_refs.py` show no drift. Generated files are regenerated, never edited.
4. Coverage is measured where a requirement sets a floor (EQ-09: feature engineering, split logic, sector scoring, at least 80%).
5. Idempotence check for any new Celery task: run twice, compare state (EQ-07, IG-01).
6. The wave's completion report is written (Deterministic_audit Phase F) with PASS, FAIL, BLOCKED and NOT TESTED kept apart.
7. Commit messages name the requirement ID. The logbook is updated. The pull request goes through every CI job and John reviews it. One branch per wave, named `build/wave-X-Y`, merged to `main` by pull request (EQ-03). `python3 scripts/check_plan_coverage.py` passes.

### 3.3 Phase gate (end of every phase)

1. **Clean-checkout demonstration** of the milestone deliverable from a fresh clone (PD-03).
2. **Independent audit** (Deterministic_audit Section 7), in three layers, because a subagent of the same model is not fully independent. (a) Mechanical checks decide what they can: tests, coverage, the generator, the matrix, the plan coverage check, planted-future tests. (b) A fresh subagent is given only the requirement IDs and the repository, never my claims, and runs the tests itself. (c) John spot-checks at least five requirements per phase against the evidence file. Result is PASS, PARTIAL, FAIL, BLOCKED or UNVERIFIED per requirement, recorded in [audits/implementation_audit.md](../audits/implementation_audit.md). I do not grade my own work.
3. **Phase-specific quality gate** (listed per phase: data gates, leakage tests, test-set-read-once, faithfulness).
4. Capacity check against PD-01 and, if the phase ran more than a week late, the drop order is applied and recorded (PD-04).
5. A short review with John. Fortnightly, the supervisor sees the same summary (SS-01).

### 3.4 Test kinds used, by where they bite

| Kind | Used for | Examples |
|---|---|---|
| Unit | Pure functions: label, features, split, SHAP direction | LB-01 hand calculation, FE-08 trajectory |
| Recorded-response | Source clients without live network calls | IG-12 |
| Contract | API shapes, envelope, errors | API-03, API-04, SV-04 |
| Integration against the Compose stack | Database, queue, API together | `tests/test_stack_integration.py` |
| Data validation | Real loaded data meets the thresholds | GATE-1 to GATE-5, TH-nn |
| Planted-future (leakage) | A record dated after the cutoff must not change a feature | FE-26, VL-01, VL-02 |
| Fault injection | Worker killed, database restarted, Redis down | EQ-06 |
| Measurement | Speed, latency, size, on real hardware | FE-09, SV-09, DB-15 |
| Evaluation integrity | Test set read once, frozen thresholds, no synthetic input | SC-04, FE-30, MD-08, TestReadLog |
| Agent faithfulness | Rank agreement, sign agreement, citation existence, injection set | AG-14, AG-17, AG-24 |

Synthetic data appears only in automated tests, labelled as synthetic (SC-04). No reported result uses it.

## 4. The wave routine (how each wave runs on its own)

Each wave follows the same loop so it can run with little supervision.

1. **Task brief** shown to John (drift control 2): requirement IDs and `ID-ACn` checks, files to change, tests to write, open decisions it cites from [pending_values.md](../audits/pending_values.md), out of scope.
2. **Read** the owner document of each requirement touched. Inspect the existing code (Phase B).
3. **Red**: write the tests.
4. **Green**: implement in small steps, one commit per step.
5. **Verify**: the wave gate.
6. **Report**: the completion report, deviations stated, drift reported not hidden.

**Stop and ask** (never fill in a default) when: a value is still pending in `pending_values.md`; a requirement and the code disagree; a change touches schema, dependencies, core interfaces or security (change control, Section 6 of the instructions); a source fails its data gate; SSOT or requirement wording would need editing; spend, API keys, Docker, or a person's sign-off is needed.

### 4.1 Rules for failure, change and pending values

1. **A failed gate is not merged.** Fix inside the wave. If the same cause fails the gate twice, stop and report. A test is never weakened, deleted or skipped to pass, and an acceptance check is never reworded to fit the code (drift controls 4 and 7).
2. **A needed value is pending.** The affected test stays `BLOCKED`, the wave continues on other steps, and John is asked. No default is used.
3. **A requirement and the code disagree.** Report it in the completion report and the drift register. Do not edit either to hide it.
4. **The plan changes.** Any change to this plan (new wave, moved requirement, new phase date) is a dated entry in the logbook, the coverage map is updated in the same change and the check passes. Scope additions need a change entry (SS-04).
5. **Spikes decide before they run.** The question and the pass rule are written before the spike runs, so the result cannot be fitted afterwards. Spike output is evidence, not a requirement, and is kept in `audits/evidence/`.
6. **One-way actions need John.** Reading the test set, freezing thresholds, freezing the feature set, spending money, using an API key, and any edit to requirement or SSOT wording.
7. **Environment.** Tests run in the Docker stack as CI does. Local Python is 3.14.4 and the project pins 3.12.16, so only standard-library scripts run on the host.

## 5. Timeline and capacity

Estimates are mine, unmeasured. They are replaced by measured hours at each wave gate, and the forecast is redone at every phase gate.

Available time: 23 November to 31 December is about 5.5 weeks. Christmas week (21 to 27 December) is buffer (C-06), so about 4.5 working weeks at 15 to 20 hours, roughly 70 to 90 hours. Phases are sequential. Hours, not calendar windows, are the constraint.

| Phase | SSOT milestone | Estimate (hours) | Cumulative | Planned window |
|---|---|---|---|---|
| P0 Foundations and de-risking | prerequisite | 30 (Waves 0.1 to 0.3: 12, 8, 10) | 30 | 23 Nov to 6 Dec |
| P1 Data pipeline | M1 | 34 | 64 | 7 to 20 Dec, spills to 28 to 31 Dec |
| P2 Feature engineering | M2 | 22 | 86 | January |
| P3 Modelling and evaluation | M3 | 26 | 112 | January |
| P4 Backend API | M4 | 14 | 126 | January |
| P5 Explanation agent | M6 | 22 | 148 | January and early February |
| P6 Dashboard | M5 | 10 | 158 | February |
| P7 Hardening and release | none (Product Section 16) | 20 | 178 | February |
| P8 Study, write-up, final audit | M7 | rest | | to late February |

**This does not fit C-06.** With these estimates only P0 and most of P1 finish by 31 December, against C-06's target of pipeline, models, API, agent and evaluation. The first draft of this plan said P0 to P3 would finish. That was wrong: I had overlapped phases that cannot overlap. Cumulative hours to the end of P3 are about 112, against 70 to 90 available in December and about 225 to 300 in total to late February (D-29). The whole plan, about 180 hours plus the write-up, fits the February total only if the estimates hold and P8 is kept to the buffer. The first P0 wave measures the real cost, so the figures are re-forecast at the end of P0 and P1. See Section 8, decision A.

### 5.1 Decision A: the December target stays (John, 23 November 2026)

John decided that the pipeline, models, API, explanation agent and evaluation are finished in December, as C-06 says. This plan keeps that target and does not move it. It does not make the arithmetic fit, so these are the facts and the controls.

**The facts, from the test matrix.** Counting acceptance checks mapped to P0 to P6 in `audits/plan_coverage.txt` and `audits/test_matrix.json`: P0 22, P1 130, P2 63, P3 89, P4 76, P5 73, P6 32. That is 485 checks, 7 of which are already real tests. Reaching the end of P5 in December is 453 checks in about 82 to 110 hours (5.5 weeks at 15 to 20 hours, with Christmas week used), which is 4 to 5.5 checks an hour including the code that makes them pass. My hour estimates above are about 15 minutes a check and I have not measured any real speed. If real speed is lower, December cannot hold.

**What is cut for December (the D-28 slice).** Only items that are Should or Could, or that D-28 puts outside December, move to January. About 40 of the 485 checks: the benchmark replication (FR-27), the T1 report (FR-29), results by year (TR-04), the model inventory (MR-01), pagination and contract extras (API-03, API-05), rate limit and metrics (SV-10, SV-11, NFR-12), the human-rating sample and LLM regression set (EX-05, AI-02, AI-03), accessibility and keyboard extras (NFR-07, UI-02, UI-05, UX-08, UX-10, UX-11), and the full frontend polish. P7 and P8 are January and February either way. No Must requirement and no proposal-derived Must item is dropped (PD-06). This cut is under 10% of the checks, so it does not close the gap alone.

**Controls so the target is honest, not hoped for.**
1. **Velocity.** Every wave gate records hours spent and checks closed. The forecast for the rest of December is remaining checks divided by measured checks per hour, replacing my estimates from the end of Wave 0.2.
2. **Checkpoints.** End of P0 (about 6 December), end of P1 (about 15 December), end of P2 (about 22 December). At each, if the forecast misses 31 December by more than a week, PD-04 applies: the drop order is applied that week and recorded, and John is told, not surprised in late December.
3. **Levers that are John's to pull, in order:** raise weekly hours in December (PD-01 caps planned effort at 20 a week, so this needs his explicit approval); re-tag the candidate data requirements and halve the sample sizes of VL-09 and AE-02 (D-26); shrink the company list below 100 (C-18 fixes 100 as the subset, so this changes a closed decision); use part of Christmas week, which C-06 calls buffer.
4. **What I will not do** to hit the date: skip a gate, mark a BLOCKED or NOT TESTED item PASS, shrink an acceptance check, or default a pending value.

## 6. Phases, waves and steps

Notation: requirement IDs cite the owner document (README index). "D-nn" are open decisions in the decision log that block the step.

### P0. Foundations and de-risking (M0)

**Goal:** the sources are checked with real data before anything is built on them, the database foundation is correct, and the time-critical forward consensus capture is running.
**Entry gate:** this plan approved; John has answered the questions in the Wave 0.1 task brief.
**Exit gate:** spike evidence files exist and the source register is written; D-19, D-32 and the consensus source are decided; the database foundation passes its tests; the capture job has produced real snapshots on at least two separate days; independent audit of Waves 0.1 to 0.3.
**Estimate:** 30 hours in three waves (12, 8, 10).

**Wave 0.1. Baseline, source register and spikes** (SR-01, SR-05, SR-06, SR-09, TH-14; the ADR check SC-07-AC1; IG-16; Data Section 12, C-12; IG-09; EQ-01, EQ-04 re-verified)
- Step 0.1.1 **Regression baseline.** Bring the stack up from a clean state and run the full test suite with the command in `.github/workflows/ci.yml`. Record pass, skip and fail counts and each skip reason in `audits/evidence/wave-0.1-baseline.md`. This is the anchor every later regression run is compared with. Nothing changes if it fails: it is reported as found.
- Step 0.1.2 **Spike plan.** For each spike below, write the question, the data to use and the pass rule into the evidence file before running it.
- Step 0.1.3 **Spike A, announcement time (IG-16).** For 50 events, compare the call time with the 8-K Item 2.02 acceptance time. Decides the T0 cutoff rule (C-17). Needs the SEC contact variable set (C-10). Throwaway script, not committed to `src/`.
- Step 0.1.4 **Spike B, EPS depth and bulk files (LB-02, LB-03, IG-09).** For 10 companies, count the quarters of diluted EPS available in EDGAR XBRL facts and check whether the fourth quarter has to be derived. Check whether the SEC bulk files are refreshed nightly.
- Step 0.1.5 **Spike C, consensus source (SR-10, CE-01, VL-12).** Call yfinance, Finnhub and FMP free tiers for 5 tickers. Record which return an estimate mean, a standard deviation, an analyst count, and what terms apply. This decides the source for Wave 0.3.
- Step 0.1.6 **Spike D, transcript source (D-18, SR-03).** Read the Hugging Face dataset card and licence file. Check whether delisted companies are present. Check the Alpha Vantage free limit. Decides D-18.
- Step 0.1.7 **Spike E, FinBERT speed (FE-09).** In a throwaway container outside the project image, so no dependency file changes, score 1,000 real sentences on the CPU. Record sentences per second and the projected hours for the 100-company corpus. This sets the true size of P2.
- Step 0.1.8 **Source register.** A machine-readable file with one row per dataset: source, licence, access route, dated access check, cost (zero, SR-09) and a fallback with its test result (SR-01, SR-06), plus a test that reads it (SR-01-AC1, SR-06-AC1, SR-09-AC1, TH-14). Draft wording for the data requirements is shown to John first (C-12, drift control 4). SR-02 (a source tag on every feature column) is built in Wave 2.4 and SR-03 (the demo bundle manifest) in Wave 7.4, because both need code that does not exist yet.
- Step 0.1.9 **Label-route ADR** (SC-07, C-25, DO-02). The test `test_sc_07_ac1` is an expected failure today because no ADR exists. The ADR records the time-series SUE route, the reason, and the supervisor position. C-25 says no written supervisor agreement exists, so the ADR says that plainly and John decides whether to ask for one (D-46).
- Step 0.1.10 **Decision session with John.** Close D-19, D-32, D-18 and the consensus source from the spikes. Approve the D-38 items Wave 0.2 needs. Hand John the two long-lead actions: the ethics route (D-16) and the library enquiry (D-21).
- Tests: spikes have no pass or fail test. The rule is that each has a pre-written question and rule, the raw output is saved, and the decision cites the evidence. A spike that fails a source starts the fallback decision, not a workaround. The baseline run is the only executed test suite in this wave.

**Wave 0.2. Database foundation and plumbing slice** (DB-01 to DB-03, DB-07, DB-16; PL-05; EQ-07; DP-06; DB-04, DB-05 and DB-17 start here and finish in Waves 1.3, 5.4 and 7.1)
- Step 0.2.1 Write the failing tests first: duplicate company rejected by the database (the first case of DB-05, whose check says "each" unique key and so completes only in Wave 5.4), timestamps carry a time zone (DB-07, a schema-wide query that covers every later table), tests use a separate database (DB-16), migration applies on an empty database (PL-05), no other database holds entities and the extension list matches the migrations (DB-01).
- Step 0.2.2 **Separate test database** and fixtures that never touch project data (DB-16).
- Step 0.2.3 **Alembic** (PL-05, DB-17). `alembic==1.20.1` is already pinned in `requirements-pending.txt`: moving it to `requirements.txt` and regenerating the lock is a dependency change, shown in the brief for approval.
- Step 0.2.4 **Migration 0001:** the Company table keyed on the SEC CIK in one canonical form (C-19) with a database unique key. The ticker-change join test of DB-04 needs ticker history, so it is Wave 1.3. Further tables are added by later waves, each by its own migration.
- Step 0.2.5 **Roles and pools** (DB-02, DB-03, DB-07): separate roles for migrations, workers and the API, bounded pools, UTC-only timestamp helper. The role split and pool values are D-38 and D-38 is not yet approved, so this step waits for John's answer and is `BLOCKED` otherwise.
- Step 0.2.6 **Plumbing slice:** a Celery task that writes company rows through the worker role, run twice leaves identical state (EQ-07). It fetches nothing from outside. The first real EDGAR slice is Step 1.1.7.
- Tests: the Step 0.2.1 tests turn green; the existing health and stack tests still pass; ruff, mypy and the generators pass.

**Wave 0.3. Forward consensus capture job** (SR-08, SR-10; VL-12, TH-10 if the source stores past estimates; CE-01 to CE-03 finish in Wave 1.7, FR-14 in 1.6, CE-04 and TH-04 in 3.4)
- Why now: the snapshot trial (VL-10, TH-09) needs four weeks of daily captures, and consensus cannot be backfilled (SR-08, CE-02). Every day of delay is lost data for the check set.
- Open questions for John, which this wave does not decide: (a) EstimateSnapshot in Product Section 11 has a required `event_id`, but a snapshot is taken before the event exists, so the table needs a company key and a nullable event link (a D-38 schema addition); (b) the daily trigger needs a scheduler, and the compose file has none, so a Celery beat service is an architecture change under ADR 0001 that needs approval (IG-05 later holds the job list); (c) capture only runs while the owner's PC is on, which SR-10's gap rule reports but does not prevent.
- Step 0.3.1 Failing tests first: a snapshot with no capture time is rejected, a snapshot dated before the start date is rejected, a standard deviation of NULL is stored as NULL (SR-08-AC1, SR-10). The checks that need an announcement date (CE-01, FR-14 second check) cannot run until events exist in Wave 1.6, so they are not claimed here.
- Step 0.3.2 Migration for the snapshot table, per the answer to (a). Append-only by privilege now, enforced by DB-08 in Wave 1.2.
- Step 0.3.3 Client for the source chosen in Spike C, with a recorded-response test labelled real or synthetic, and the source's request limit respected.
- Step 0.3.4 Capture task, one row per company per day, idempotent. Daily trigger once (b) is approved.
- Step 0.3.5 Gap report: more than 3 consecutive days without a run is reported and the affected events flagged (SR-10-AC).
- Step 0.3.6 Start on the 10 companies from the spikes, widen to the universe when Wave 1.3 produces it. Until then SR-10 is `PARTIAL`, and the ledger says so.
- Step 0.3.7 If the source stores an estimate beside past actuals, run the 30-event pre-announcement test (VL-12, TH-10); otherwise record that it does not apply.
- Tests: the Step 0.3.1 tests; run the task twice and compare state; a log of real captures on at least two separate days as evidence (SR-10-AC1, NEEDS MEASUREMENT). SR-10-AC2 (gap report) is checked by deliberately skipping a day in a test. No synthetic snapshot appears in any reported result (SC-04).

### P1. Data pipeline (M1)

**Goal:** a populated, validated PostgreSQL database for 100 companies (C-18) with events, dated rows and the label.
**Entry gate:** P0 exit gate.
**Exit gate:** the M1 demonstration; GATE-1 to GATE-5 evaluated on real data and reported with their results, including any shortfall (LB-06, VL-06, TX-04); independent audit of IG, DB and Data requirements in scope.

**Wave 1.1. Task framework and client rules** (IG-01 to IG-05, IG-07, IG-08; PL-01, PL-02; EQ-07). Plan change of 24 November 2026, after inspecting which checks each wave can really test: IG-10 and IG-12 move to Wave 1.5 (they cover every client, and the transcript and Alpha Vantage clients are built there), FR-13 and NFR-03 to 1.5 (they need transcripts), IG-06 and SC-07 to 1.6 (they need events and a training set), SR-07 to 7.4 (its second check needs the demo bundle).
- Step 1.1.1 Task base: idempotent, run record (IG-01, IG-03, EQ-07).
- Step 1.1.2 Retry with backoff and jitter, dead letter (IG-02).
- Step 1.1.3 Redis redelivery timeout (IG-04).
- Step 1.1.4 EDGAR client: 10 requests a second cap, refuses to send without `SEC_USER_AGENT` (IG-07, IG-08).
- Step 1.1.5 Other source clients and recorded-response fixtures (IG-10, IG-12).
- Step 1.1.6 Scheduler config and late-job reporting (IG-05, IG-06; D-45 values).
- Step 1.1.7 **First real slice:** 5 companies through the EDGAR client, a task, the database and a read back. This is the first end-to-end proof on real data and runs before any widening to 100.
- Test: unit and recorded-response; injected failure gives three retries and one dead-letter row (IG-02-AC1); kill a worker mid-task and restart (IG-01-AC2, first EQ-06 case).

**Wave 1.2. Storage rules** (DB-08, DB-09, DB-10; Data SR-04). Plan change of 23 November 2026: DB-11-AC1 moves to Wave 1.4 (a rebuild needs the parsed tables), DB-12 to Wave 2.4 (the lineage check needs the FeatureVector table), DB-13 to Wave 1.6 (it needs events) and DB-14 to Wave 1.7 (the plan check needs the loaded 100-company data). The raw payload table itself was built in Wave 1.1 (C-45).
- Step 1.2.1 Append-only by privilege and a registry of append-only tables, with a check that the registry and the database agree (DB-08). Step 1.2.2 One documented as-of function pattern, the first instance on `estimate_snapshot`, strictly before the date (DB-09). Step 1.2.3 Half-open validity ranges with overlap refused by the database: the `btree_gist` extension by migration, and the `ticker_history` and `index_membership` tables of Product Section 11 (DB-10). Step 1.2.4 A hash check of every stored raw payload (SR-04).
- Test: the worker's UPDATE and DELETE fail on every registered table; a planted version dated D is not returned for date D; an overlapping membership insert fails and a boundary date resolves to one period; a tampered payload is found by the hash check.

**Wave 1.3. Universe and identifiers** (IG-13, IG-21; Data IM-01 to IM-03; DB-04 join test across ten known ticker changes; TH-05)
- Step 1.3.1 Build the membership table from the D-32 source. Step 1.3.2 CIK as `company_id`, ticker matching, name matching with a logged review list (C-19). Step 1.3.3 Company list as a parameter, 100 companies with about 20 removed from the index (C-18).
- Test: IM-01 and IM-02 checks against real data; removed companies present (survivorship).

**Wave 1.4. Financial data** (AE-04; FD-01 to FD-03; IG-09, IG-15; DB-11; AE-03-AC1). Plan change of 23 and 24 November 2026: AE-03 (its second check is the basis test VL-07) and TH-06 (the survivorship gap, VL-05) move to Wave 1.7; AE-01 moves to Wave 1.6 (an event is needed to hold the document and dates), AE-02, FD-04 and TH-12 to Wave 1.7 (they need press-release values, the five non-calendar companies and the 200-event sample), and prices (PX-01 to PX-03) to a new Wave 1.8, because price tables are not in Product Section 11 and need John's approval.
- Step 1.4.1 EPS history and fundamentals as append-only versions with as-of functions (AE-04, FD-01 to FD-03). Step 1.4.2 Derived quarters, flagged: fourth quarter from the year, and quarters from cumulative figures (LB-03). Step 1.4.3 Earnings-release 8-K parsing and the T0 cutoff, earlier of call time and acceptance time (IG-15). Step 1.4.4 Backfill of the 100 companies with the request count recorded (IG-09). Step 1.4.5 A rebuild of the tables from stored payloads gives identical hashes (DB-11).
- Test: a simulated correction leaves the first-filed value; a planted filing dated D or later is excluded; call before and after the filing both give the earlier time; the rebuild hash is identical.

**Wave 1.8. Prices** (PX-01 to PX-03). Not started. Needs John's approval of price tables (daily bars and dated split and dividend factors), which Product Section 11 does not list. Removed companies have no yfinance prices, so coverage will be reported.

**Wave 1.5. Transcripts and preparation** (IG-11, IG-14, IG-17 to IG-19; Data TX)
- Step 1.5.1 Hugging Face snapshot with revision recorded (IG-11). Step 1.5.2 Link transcript to company, quarter and announcement (IG-14). Step 1.5.3 Cleaning that removes only non-speech artefacts (IG-17). Step 1.5.4 Prepared remarks and Q&A boundary by the written rule (IG-18, D-45). Step 1.5.5 Fixed stage order (IG-19).
- Test: segmentation accuracy on a hand-labelled sample against the TX threshold; cleaning is lossless for speech text.

**Wave 1.6. Events and the time-series SUE** (Data LB-01 to LB-05, CE-05, SC-07 test; FR-02, FR-14; IG-20, IG-22; DB-06, DB-15; TH-11, TH-15)
- Step 1.6.1 Time-series SUE label with the three dates per event (LB-01, DB-06). Step 1.6.2 Store the continuous SUE only. Class labels are not assigned here, because LB-06 and VL-06 set the class cut-offs during EDA on 2015 to 2021 and freeze them before validation is read, so they belong to Wave 2.5. Step 1.6.3 The two label routes can never mix in one training set (CE-05, SC-07). Step 1.6.4 Date gates in the preparation stages (IG-20); the planted-future tests themselves are Waves 1.7 and 2.4. Consensus snapshot link to events and the exclusion of snapshots on or after the announcement (FR-14). Step 1.6.5 Coverage report after each load (IG-22). Step 1.6.6 Database size measured (DB-15).
- Test: the SUE formula against a hand calculation on stored values (LB-01); a test fails if two label routes are in one set (CE-05); the data gates are run in Wave 1.7 and the results recorded, not assumed.

**Wave 1.7. Dataset validation and sign-off** (DV-01 to DV-08, CE-01 to CE-03, VL-01, VL-05, VL-07 to VL-09, GS-01, GS-02, GATE-1 to GATE-3, GATE-5, TX-04, TX-07, TH-01, TH-03, TH-08, SRS-14)
- Step 1.7.1 Schema validation with quarantine of failing rows, null-rate limits, unique events, date-order, UTC and trading-day checks (DV-01 to DV-07). Re-run on the same snapshot gives identical tables (DV-08).
- Step 1.7.2 Planted-future test, survivorship check, basis check, known-event canary of 20 widely reported releases (VL-01, VL-05, VL-07, VL-08).
- Step 1.7.3 Hand audit of 100 sampled events against primary documents (VL-09). It is a person's work, so it is `NEEDS PERSON`. D-26 asks whether to halve the sample.
- Step 1.7.4 Coverage and bias reports against the loaded 100-company list (TX-04, TX-07, TH-01).
- Step 1.7.5 Sector assessment: record that the dated-sector source was not found and sector scoring is off for this scope (SRS-14, C-29).
- Step 1.7.6 Dataset sign-off by a reviewer who did not build it, and a data card per dataset (GS-01, GS-02, GATE-5).
- Test: every gate result is a measured number in the evidence file, including any miss. A miss is stated, thresholds are not changed (C-37).

**P1 quality gate:** GATE-1, GATE-2, GATE-3 and GATE-5 results written down with real numbers; every unmet threshold stated as such. Class balance (VL-06, TH-07) is reported at the P2 gate because the class cut-offs are set in Wave 2.5.

### P2. Feature engineering (M2)

**Goal:** a versioned feature matrix in the database and the EDA notebook.
**Entry gate:** P1 exit gate; D-35, D-34, D-36 closed.
**Exit gate:** feature matrix for all events, feature-set version recorded, FE-26 leakage tests pass for every feature, EDA notebook runs from a clean checkout (FE-32).

**Wave 2.1. Sentences and FinBERT** (FE-01 to FE-07, FE-09; Product FR-15)
- Step 2.1.1 spaCy sentence split with version pinned (FE-01). Step 2.1.2 Operator and safe-harbour marking (FE-02). Step 2.1.3 Exact-substring guarantee (FE-03). Step 2.1.4 Missing speaker roles stored as unavailable (FE-04). Step 2.1.5 FinBERT scoring with named checkpoint and revision, long-sentence handling, batching (FE-05, FE-06). Step 2.1.6 Call-level means (FE-07). Step 2.1.7 Scoring speed recorded (FE-09).
- Test: FE-03 property check on real sentences; scoring is idempotent (FE-29).

**Wave 2.2. Linguistic features** (FE-08, FE-10 to FE-18; Product FR-16 to FR-18)
- Step 2.2.1 Hedge words from the Loughran and McDonald list, licence recorded first (FE-10, FE-11). Step 2.2.2 Word count, negation, forward-guidance flag (FE-12 to FE-14). Step 2.2.3 Question count and Q&A features (FE-15 to FE-17). Step 2.2.4 Trajectory and sentiment surprise with the prior-calls rule at T0 (FE-08, FE-18).
- Test: each rule has hand-built examples with expected values; FE-26 planted future call must not change sentiment surprise.

**Wave 2.3. Tabular features** (FE-19 to FE-22)
- Step 2.3.1 Revenue growth. Step 2.3.2 Margins. Step 2.3.3 Four-quarter surprise trend. Step 2.3.4 Price momentum over 63 trading days. Step 2.3.5 Surprise dispersion on the time-series route (SSOT Section 5).
- Test: hand calculations; a price dated after the cutoff must not change momentum.

**Wave 2.4. Matrix, registry and versioning** (FE-23 to FE-30; SR-02; VL-02; EQ-09)
- Step 2.4.1 Feature registry (FE-27). Step 2.4.2 T0 and T1 tagging (FE-23). Step 2.4.3 NULL with reason codes (FE-24). Step 2.4.4 Learned transformations fitted on training years only (FE-25). Step 2.4.5 Feature-set version hash (FE-28). Step 2.4.6 Idempotent writes (FE-29). Step 2.4.7 Freeze rule recorded (FE-30). Step 2.4.8 Source tag on every feature column, and an untagged column fails the build (SR-02-AC1, AC2); planted-future replay for 30 events (VL-02).
- Test: the leakage test for every registered feature (FE-26-AC); re-running leaves identical rows.

**Wave 2.5. EDA, class thresholds and feature report** (FE-31, FE-32; LB-06, VL-06, TH-07)
- Step 2.5.1 EDA notebook on training years. Step 2.5.2 Per-version feature report. Step 2.5.3 **Class thresholds.** Propose the beat, in-line and miss cut-offs from the 2015 to 2021 SUE distribution, report class shares per year, and write the frozen threshold record (LB-06, VL-06, TH-07, D-23). The freeze is one-way and needs John's written approval, with the validation and test years unread.
- Test: the notebook runs headless from a clean checkout in CI or a documented command.

**P2 quality gate:** a coverage report of 80% or more for feature engineering (EQ-09); the registry equals the features in the matrix.

### P3. Modelling and evaluation (M3)

**Goal:** baseline and full models, SHAP, and an evaluation report that answers the research question, including a negative result if that is what the data shows.
**Entry gate:** P2 exit gate; D-42 closed; feature set frozen (FE-30).
**Exit gate:** trained, checksummed model artefacts; evaluation report produced by code; the test set read once, recorded; independent audit.

**Wave 3.1. Split and baseline** (MD-01 to MD-04, MD-06 to MD-09; ML-01, ML-02)
- Step 3.1.1 Split by announcement date, 2015 to 2021 train, 2022 validate, 2023 to 2024 test, no shuffling (MD-03). Step 3.1.2 Three-class XGBoost and class weights (MD-01, MD-04). Step 3.1.3 Missing values passed as missing (MD-06). Step 3.1.4 One command trains from a config file, records snapshot and seed (MD-07). Step 3.1.5 Native-format artefact with SHA-256 checksum, never pickle (MD-09, SP-01).
- Test: a test that fails if any training row is dated in or after 2022, and one that fails if test rows are read before freezing (MD-03, MD-08).

**Wave 3.2. Tuning, calibration, freezing** (MD-05, MD-08, MD-10, MD-11, MD-19)
- Step 3.2.1 Search space written before the search (MD-05). Step 3.2.2 Tuning on 2022 only. Step 3.2.3 Temperature scaling fitted on 2022 and frozen (MD-11). Step 3.2.4 Freeze config, feature-set version and thresholds, with a ThresholdFreeze record (MD-08). Step 3.2.5 Count every variant for the multiple-testing rule (MD-19).
- Test: tuning code cannot read 2023 or later rows.

**Wave 3.3. Full model, SHAP and metrics** (MD-02, MD-12 to MD-18, MD-10)
- Step 3.3.1 Train full model at T0 and the T1 nowcast separately (MD-02, C-17). Step 3.3.2 SHAP on the registered artefact, direction relative to the predicted class (MD-12, MD-13). Step 3.3.3 Global importance (MD-14). Step 3.3.4 Metrics fixed in code: F1, Brier, precision at the top 20% (MD-15, MD-10). Step 3.3.5 Per-class precision and recall, bootstrap intervals by event (MD-16, MD-17). Step 3.3.6 Majority-class and prior-quarter baselines on the same rows (MD-18).
- Test: metric functions against hand-computed values; SHAP values sum check; interval seed is fixed.

**Wave 3.4. One-time test read, report, scoring task** (MD-20 to MD-23; FR-25; SC-04)
- Step 3.4.1 Pretraining-cutoff check, reporting "cannot show a jump" if no labelled quarter precedes the cutoff (MD-20, C-36). Step 3.4.2 **The single test-set read**, written to TestReadLog (MD-15). It is irreversible, so it runs only after John gives explicit written approval, with the feature set, thresholds and model configuration already frozen (FE-30, MD-08). Step 3.4.3 Report tables produced by code with data source stated (MD-21, SC-04). Step 3.4.4 Celery task scores each event once per prediction point (MD-22). Step 3.4.5 Artefact check refuses a tampered model (MD-23).
- Test: a second test-set read is refused; the evaluation job refuses synthetic input (SC-04); a corrupted artefact is rejected (MD-23).

**P3 quality gate:** Evaluation criteria 1 and 2 in SSOT Section 10 answered with measured numbers. Nothing in the report is rounded up or reworded after the test read.

**Wave 3.5. Model governance and promotion** (ML-05, ML-06, MR-01, MR-02)
- Step 3.5.1 Metrics report written before the model is registered (ML-05). Step 3.5.2 Model inventory entry (MR-01). Step 3.5.3 Model card with objective, data, assumptions, limitations and tests (MR-02). Step 3.5.4 Promotion to serving only after the baseline comparison on the sealed test result, with the independent reviewer named under D-09 signing off (ML-06).
- Test: promotion is refused when the metrics report is missing or the sign-off is absent.

### P4. Backend API (M4)

**Goal:** a documented read-only API on stored data (C-15).
**Entry gate:** P3 exit gate; D-43 values approved.
**Exit gate:** contract tests pass for every endpoint EP-01 to EP-10 in scope; authentication built before any exposure and before the milestone is signed off (SV-15, SV-16); independent audit.

**Wave 4.1. Layers and prediction endpoints** (SV-01 to SV-05, SV-14; API-01 to API-05; EP-01, EP-06, EP-10; ER-01; EP-02 is off, C-29)
- Step 4.1.1 Routes, services, repositories (SV-02). Step 4.1.2 Envelope and warnings (SV-04, API-04). Step 4.1.3 Input validation before lookup (SV-05). Step 4.1.4 Latest T0 prediction (SV-03, EP-01). Step 4.1.5 History with realised outcome or "Pending" (SV-07, EP-06). Step 4.1.6 Universe list (EP-10). Step 4.1.7 Database and queue errors mapped to ER-14 (SV-14).
- Test: contract test on each endpoint; a no-transcript ticker returns the ER-01 state; no data source call occurs inside a request (SV-01).

**Wave 4.2. Operability** (SV-08 to SV-13; EP-08, EP-09; API-07; NFR-01)
- Step 4.2.1 /health with artefact check and ingestion status (SV-08, SV-12, C-31, C-33). Step 4.2.2 Rate limit in Redis (SV-10, D-43). Step 4.2.3 /metrics (SV-11). Step 4.2.4 Size, time and page bounds, cross-origin settings (SV-13). Step 4.2.5 Latency measured with a load test on the real stack (SV-09).
- Test: stop a dependency and check /health; 429 under load; the measured latency is recorded with the number, not a pass flag.

**Wave 4.3. Evaluation endpoint and authentication** (EP-07; SV-15, SV-16; API-06; SP-02)
- Step 4.3.1 Evaluation metrics endpoint from stored report tables. Step 4.3.2 Single-user JWT design for every endpoint except /health, /metrics included (C-40, SV-15). Step 4.3.3 Client reads the token from the environment (SV-16).
- Test: 401 without a token on every protected route; first pass of the OWASP checklist (SP-02).

### P5. Explanation agent (M6)

**Goal:** a grounded, verified rationale that is judged on faithfulness to SHAP values, not on fluency.
**Entry gate:** P4 gate; D-27 provider, budget and licence check closed; D-37 values approved; the `TranscriptSentence` retrieval table populated.
**Exit gate:** faithfulness rates on a held-out sample reported with ranges over three runs; injection set passes; independent audit.

**Wave 5.1. Selection and retrieval** (AG-01 to AG-08; EX-01; C-11, C-20)
- Step 5.1.1 Stored prediction as the only input (AG-02). Step 5.1.2 Top 3 features by absolute SHAP with a stable tie-break (AG-03). Step 5.1.3 Feature-to-evidence map for every registered feature (AG-04, AG-06). Step 5.1.4 Parameterised SQL templates only (AG-05). Step 5.1.5 Cutoff rule for T0 and T1 evidence (AG-07). Step 5.1.6 Features with no evidence handled (AG-08).
- Test: a model cannot supply SQL; a sentence dated after the cutoff is never retrieved.

**Wave 5.2. Generation** (AG-09 to AG-13, AG-16, AG-18 to AG-20, AG-22)
- Step 5.2.1 Versioned prompt file, evidence quoted as data (AG-09). Step 5.2.2 JSON output validated against a schema (AG-10). Step 5.2.3 Citations by sentence id, excerpt copied from the database (AG-11). Step 5.2.4 Wording rule: describes the model, not causes of results or advice (AG-12). Step 5.2.5 Pinned model identifier, temperature from D-37 (AG-13). Step 5.2.6 Minimum data sent, token and spend caps, timeout, retry (AG-18, AG-20, AG-22). Step 5.2.7 Plain-text rendering rule (AG-16).
- Test: recorded provider responses; cap reached behaves as specified; no live key in tests.

**Wave 5.3. Verification and safety** (AG-14, AG-15, AG-17, AG-21, AG-26; SP-03)
- Step 5.3.1 Pre-storage checks: citation exists, rank and sign agree with SHAP (AG-14). Step 5.3.2 Failed claim removed and logged (AG-15). Step 5.3.3 Injection test set with planted instructions in transcript text (AG-17, SP-03). Step 5.3.4 Reuse the stored explanation for the same prediction, prompt and model version (AG-21). Step 5.3.5 Evidence stored with each claim (AG-26).
- Test: a planted fabricated citation is rejected; injection sentences do not change the output; two identical requests make one provider call.

**Wave 5.4. Job endpoints and faithfulness harness** (SV-06; EP-03 to EP-05; FR-19; AG-23 to AG-25)
- Step 5.4.1 Explanation row as the job, unique key on prediction, prompt and model version (C-32, DB-05). Step 5.4.2 POST and GET job endpoints, 503 on failed queue send (SV-06). Step 5.4.3 Prompt tuning on 2022 predictions only (AG-23). Step 5.4.4 Written protocol before the run, then the run on the held-out sample, three times (AG-24, AG-25). Step 5.4.5 No ROUGE or BERTScore gate (SC-05).
- Test: faithfulness measured on real held-out predictions and reported with the number of runs and range; the result stays as measured even if low.

### P6. Dashboard (M5)

**Goal:** a Streamlit client that shows the prediction and explanation side by side. It is built after P4 and P5 so it consumes real endpoints. A minimal card can be built after P4 if December capacity allows (D-28).
**Entry gate:** P4 gate; D-39 values approved.
**Exit gate:** UI states match the screens (SCR) and error states (ER); independent audit.

**Wave 6.1. Client and prediction card** (UX-01, UX-02, UX-05, UX-06; SCR; FR-01)
- Steps: API client module with timeout and failure mapping; ticker input with validation; prediction card with confidence; every API warning visible; T0 and T1 labelled apart; no database import.
- Test: Streamlit app tested against the real API on the Compose stack (AppTest where it fits); a warning in the envelope is rendered.

**Wave 6.2. Explanation and evaluation views** (UX-03, UX-04, UX-07, UX-09)
- Steps: job polling with limit; claim, label, reason and cited sentence beside each factor; evaluation page showing the baseline table first with intervals; only cited sentences shown, never the full transcript.
- Test: pending, complete and failed states; a failed job does not hide the prediction.

**Wave 6.3. Packaging and study readiness** (UX-08, UX-10, UX-11; ET-01, ET-02)
- Steps: usage statistics off; dashboard as its own Compose service with a health check; usability tasks written before testing. The user study itself waits for ethics approval (D-16) and is NEEDS PERSON.

### P7. Hardening and release

**Goal:** the Compose build is solid, secure and provable; the cloud step is optional (C-07).
**Entry gate:** P4 to P6 gates, or the dropped items recorded under PD-04.
**Exit gate:** release checklist passes from a clean machine, timed.

**Wave 7.1. Resilience** (EQ-06, EQ-07, IG-01, IG-06; DB-17)
- Steps: three scripted fault-injection tests (worker killed, database restarted, Redis unavailable), each ends with no duplicate or missing rows; all tasks re-run twice; remaining migrations from D-38.

**Wave 7.2. Security and supply chain** (SP-01 to SP-06, EQ-08; DP-06, DP-10; API-06, API-07)
- Steps: OWASP API checklist signed off (SP-02); dependency vulnerability scan blocks high findings (EQ-08); no secrets, data, or model artefacts in the public repository (DP-10).

**Wave 7.3. Operations and performance** (EQ-05, DO-01, DO-04, DP-01 to DP-05, DP-09; NFR-01)
- Steps: memory limits so the stack with FinBERT fits the machine (DP-02); named volumes (DP-04); runbook with each step run once, rollback timed (DP-05, DO-04); load test of 100 concurrent cached requests; the README start tested in a timed clean run (DO-01).

**Wave 7.4. Optional cloud** (DP-11 to DP-15; D-15, D-44; DO-02)
- Demo bundle manifest lists each source and its licence, and a personal-use source fails the check (SR-03-AC1, AC2). This part is needed even for the local demo.
- Only if D-15 allows spend. ADR 0003 first, spend ceiling and an 80% alert before the first resource (DP-12), only redistributable data in the cloud database (DP-13). Otherwise record a demo of the local build.

### P8. Study, write-up and final audit

**Wave 8.1. Evidence closure** (DO-03, ASM-01, SC-04)
- A full independent audit of the whole repository against every requirement. Traceability file has no requirement without evidence or an explicit status. Anything NOT TESTED, BLOCKED or FAIL is listed in the dissertation as such. The overall result is not PASS if any Must is FAIL, PARTIAL, BLOCKED or UNVERIFIED.

**Wave 8.2. Usability study** (UX-10, ET-01, ET-02) after ethics approval.
**Wave 8.3. Dissertation** (ASM-05, SC-07, SS-04): includes the label-route change, the data-route difference, negative results as findings, and the AI declaration format (D-17).
**Wave 8.4. Buffer and polish** in the last two to three weeks (PD-01).

## 7. Dependency order and what can run in parallel

```
P0 ─► P1 ─► P2 ─► P3 ─► P4 ─► P5 ─► P6 ─► P7 ─► P8
 │     │                  │
 │     └ 1.2/1.3 can overlap 1.1
 └ forward consensus capture runs in the background from week 1
```

Safe overlaps (solo, so only where the second item waits on idle compute): FinBERT scoring runs in the background while tabular features (Wave 2.3) are written; the ethics application and library enquiry run in parallel with every phase. Everything else stays sequential, because each phase reads the previous phase's stored output.

## 8. Decisions

| # | Decision | Status |
|---|---|---|
| A | The December target stays (C-06) | **Decided by John, 23 Nov 2026.** Consequences and controls are in Section 5.1 |
| B | Methodology and gate structure | **Approved by John, 23 Nov 2026** |
| C | Close D-19, D-32, D-18 and the consensus source | Approved to proceed. The choices themselves are made in Wave 0.1 from the spike evidence, and John confirms each when it is made |
| D | D-38: roles, pools, Alembic, the Company table | The plan was approved, but D-38 lists no numbers for pool size and time-out. Concrete values are proposed in the Wave 0.2 brief for John to approve. Until then DB-02, DB-03 and DB-17 stay BLOCKED |
| E | Wave 0.3: snapshot table key, scheduler, PC-off gaps | Asked in the Wave 0.3 brief |
| F | D-35, D-34, D-36 | Needed before Wave 2.1 |
| G | D-42, D-43, D-37, D-39 | Needed before P3, P4, P5, P6 |
| H | D-27 LLM provider, budget, licence check | Needed before Wave 5.2 |
| I | D-16 ethics route, D-21 library enquiry | John's actions this week |
| J | D-03 drop order, D-26 re-tagging | Needed before Wave 1.7 (the VL-09 sample size) |
| K | C-23 names five required CI checks and CI has six jobs | Still open. A specific question: which six, or which five, are the required checks in the branch protection setting? |

## 9. Risks that change the plan

| Risk | Trigger | Response |
|---|---|---|
| Free transcript or EPS data is thinner than needed | Spike or P1 coverage report misses the TX or LB thresholds | Report the shortfall (C-37), decide fallback (D-18), do not lower the threshold |
| FinBERT too slow on the CPU | Spike 0.1.4 shows scoring the corpus takes more than about 2 days | Smaller subset, batch overnight, or GPU (C-08); never skip sentences silently |
| Lookahead found late | A planted-future test fails | Stop the wave, fix at the as-of layer (DB-09), re-run downstream |
| NLP adds no signal | P3 result | Valid finding (SSOT Section 2). Report as measured |
| Capacity | Wave takes more than 1.5 times its estimate | Apply PD-06, record under PD-04 |
| Capture job misses days because the PC is off | More than 3 consecutive days without a run | Report the gap and flag events (SR-10), do not interpolate |
| LLM cost or injection | Cap reached, injection test fails | Spend cap and schema checks (AG-20, AG-17), stop and ask |

## 10. What I will not do without you

Edit the SSOT; change requirement wording to match code; fill a pending value with a default; add dependencies, schema, or interfaces without a change entry; spend money or use an API key; run live LLM calls before D-27; claim a requirement is complete without evidence; mark my own work PASS without the independent audit.
