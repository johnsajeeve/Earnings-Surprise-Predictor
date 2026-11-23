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
| P0 | not run | not run | not run | NOT STARTED |
| P1 | not run | not run | not run | NOT STARTED |
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
| DR-08 | 23 Nov 2026 | `.github/workflows/ci.yml`, tests | The CI `tests` job mounts only `tests/` and one file, so 20 checks that read documents, the workflow and scripts skip as NEEDS REPO there | OPEN. Needs John (CI change) |
| DR-09 | 23 Nov 2026 | decision-log C-19, D-32, Spike D | The membership candidate is keyed by ticker with no company identifier, but C-19 makes the CIK the permanent identifier | OPEN. The ticker to CIK mapping is an IM-03 task for Wave 1.3 |
| DR-10 | 23 Nov 2026 | Data SR-06, source register | The register has no documented fallback for the 8-K announcement time, and every other fallback is untested | OPEN. Needs John: name a fallback or accept a stated scope limit |
| DR-05 | 23 Nov 2026 | decision-log D-38, Database DB-03 | D-38 lists pool and time-out values as "not approved" but gives none | CLOSED 23 Nov 2026 by decision C-44 (values proposed and approved) |
| DR-11 | 23 Nov 2026 | `docker-compose.yml`, Database DB-02 | All role passwords and the superuser password are in every service's environment | OPEN, accepted for local use. Cloud must give each service only its own secret (DP-06) |
| DR-04 | 23 Nov 2026 | `requirements-pending.txt`, `requirements.txt` | Alembic (needed for PL-05) is pinned but not installed. Moving it is a dependency change | OPEN. Shown in the Wave 0.2 brief |

## 6. Corrections to my own earlier statements

| Date | What I said | What is true | How I know |
|---|---|---|---|
| 22 Nov 2026 | The first plan draft said P0 to P3 finish by 31 December | Phases cannot overlap, and the cumulative estimate to the end of P3 is about 112 hours against 70 to 90 available | Plan Section 5 recomputed |
| 22 Nov 2026 | The plan said the pipeline has five CI checks | `.github/workflows/ci.yml` has six jobs | Read the file on 23 Nov 2026 |
| 23 Nov 2026 | The plan put the SUE class thresholds in Wave 1.6 | LB-06 and VL-06 set them during EDA and freeze them after, so they belong to Wave 2.5 | Read the requirement text during the second review |
| 23 Nov 2026 | The plan put SR-02 and SR-03 in Wave 0.1 as a source register | They are code checks (feature source tag, demo bundle manifest) for Waves 2.4 and 7.4 | `tests/test_req_data.py` |
| 23 Nov 2026 | The plan said Wave 0.2 covers DB-04, DB-05 and DB-17 and Wave 0.3 covers CE-01 to CE-04 and FR-14 | Their checks need ticker history, later tables, announcement dates and events, which do not exist in P0 | `audits/test_matrix.json` checks |
| 23 Nov 2026 | An early draft of the gap table said the plan cited "385 of 480" IDs | The check I ran counted 95 uncited Must requirements among 414 parsed rows. 385 was subtraction I had not measured | Re-ran the check, replaced the sentence |

## 7. Wave ledger

One row per wave in the plan. The checker fails if a wave is missing, if a status word is wrong, or if PASS has no existing evidence file naming the wave. Update a row only when the gate output exists.

| Wave | Name | Status | Evidence |
|---|---|---|---|
| W0.1 | Baseline, source register and spikes | IN PROGRESS | audits/evidence/wave-0.1-register-and-adr.md |
| W0.2 | Database foundation and plumbing slice | PARTIAL | audits/evidence/wave-0.2.md |
| W0.3 | Forward consensus capture job | NOT STARTED | - |
| W1.1 | Task framework and client rules | NOT STARTED | - |
| W1.2 | Storage rules | NOT STARTED | - |
| W1.3 | Universe and identifiers | NOT STARTED | - |
| W1.4 | Financial data | NOT STARTED | - |
| W1.5 | Transcripts and preparation | NOT STARTED | - |
| W1.6 | Events, label and validation | NOT STARTED | - |
| W1.7 | Dataset validation and sign-off | NOT STARTED | - |
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
