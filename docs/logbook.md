# Project Log Book

Project: LLM-Powered Earnings Surprise Predictor. BSc Computer Science, University of Manchester, 2026 to 2027.

This is a record of what was done and when, with the commit messages. It is not the report. The report will be written from it after the project is finished.

## How this log is kept

- One short entry per working session or commit. Newest at the bottom.
- Every commit gets a row in the register. A commit cannot contain its own hash, so its row is completed in the next commit.
- Each entry says what was done, the result, any decision, and who did it (John decides, Claude is the AI assistant that did the drafting and checking).
- Plain wording, past tense, no em dashes. Numbers are as measured, or marked as estimates.

## Commit register

| Commit | Date | Subject |
|---|---|---|
| 50af5ee | 25 Oct 2026 | Initial commit |
| c5230be | 30 Oct 2026 | Add requirements and architecture documents |
| aaaeac7 | 14 Nov 2026 | Refresh requirement documents and add project-wide, assessment, operations, LLM controls and broader level 2 |
| 6352c91 | 14 Nov 2026 | Align requirements and deck with the proposal; add sector-scoring breakdown, fundamentals data, ID fixes and drift review |
| a011884 | 14 Nov 2026 | Data requirements: fix duplicates and contradictions, verify sources, add low-cost alternatives and pre-announcement test |
| 4727aa9 | 15 Nov 2026 | Restructure requirements, add SSOT and decision log, rewrite drift review |
| 70149d8 | 15 Nov 2026 | Record owner answers: MVP date, hosting, SQL retrieval, reminders, submission window |
| c6f01ce | 15 Nov 2026 | Spike results, delivery plan, log book |
| 422a6a8 | 15 Nov 2026 | Update log book: fill commit c6f01ce |
| 8c5ba5d | 18 Nov 2026 | Docs: pipeline architecture, ADRs, decisions C-14 to C-24, TranscriptSentence entity |
| 47a23da | 18 Nov 2026 | Docker skeleton: compose stack, pinned dependencies, health check, request logging, CI |
| 03943cb | 18 Nov 2026 | Governance: audit rules, requirements traceability, audit and remediation reports |
| a720023 | 18 Nov 2026 | Update log book: fill commit hashes 8c5ba5d, 47a23da, 03943cb |
| 200b881 | 18 Nov 2026 | Requirements: four component documents, consistency fixes across all documents |
| 173215e | 18 Nov 2026 | Requirements: ingestion, modelling, API and deployment documents; label route decision |
| 46b2a82 | 18 Nov 2026 | Requirement: DO-03, DO-05, DP-07 (drift controls and numbered requirements for tests) |
| Next commit | 19 Nov 2026 | Feasibility review fixes (C-27 to C-40) and a test for every acceptance check |

## Entries

### 25 Oct to 14 Nov 2026: before this log

- Repository created on 25 October.
- Four requirement documents (product, market, data, project-wide) and a six slide architecture deck added on 30 October.
- A refresh commit on 14 November changed the market document.
- State found on 14 November: the market document was an exact copy of the project-wide document, and the assessment document and root README were empty.
- Work by Claude (commit author recorded as Claude for c5230be).

### 14 Nov 2026: review of the repository

- Read all documents and the proposal text. The proposal is the scope baseline. Extensions are allowed if capacity and scope stay at its level.
- Restored the market document from c5230be.
- Found: 9 proposal items with no requirement, 3 requirements that contradicted the proposal, about 215 requirements with no priority on the product ones.
- Work by Claude. Scope rule from John.

### 14 Nov 2026: fixing the drift (commit 6352c91)

- Added the missing proposal items (fundamentals data, full feature set, pretraining cutoff check, global SHAP, stretch objectives).
- Fixed the 3 contradictions: model promotion no longer needs the full model to beat the baseline; the AUC target became a reference, not a pass mark; JWT was no longer attributed to the proposal.
- Added Must, Should or Could to every requirement. Renamed IDs that clashed between documents.
- Decision (John): keep sector relative scoring. Split into 14 requirements, SRS-01 to SRS-14. It is an extension, tagged Should.
- Work by Claude. Decision by John.

### 14 Nov 2026: data source research, round one (commit a011884)

- Read documentation for yfinance, Alpha Vantage, FMP, EODHD, I/B/E/S, Capital IQ, Zacks and others. Nothing was downloaded.
- Result: no free source gives historical analyst consensus with its standard deviation. I/B/E/S via WRDS is the best licensed source, and the Manchester library limits it to AMBS Accounting and Finance researchers.
- The proposal's plan to take transcripts from EDGAR does not work, because transcripts are not systematically filed there.
- Added requirements CE-05, CE-06 and VL-12.
- Could not read: FMP pages (403), one Finnhub page (empty), one EODHD page (404). Marked unverified.
- Work by Claude.

### 14 and 15 Nov 2026: free data route and label change

- Decision (John): the primary data route must be free, sources from any country are acceptable, and forward only is acceptable if the alternatives are worse.
- Working label route: a time series SUE from EDGAR EPS, with analyst consensus captured forward as a check. John agreed to proceed. It changes the proposal's label, so it still needs the supervisor's agreement (D-01).
- Added requirements LB-01 to LB-08, SR-09, SR-10, TX-07, FR-24 (full feature set) and FR-27.
- Free transcript sets found: Hugging Face `kurry/sp500_earnings_transcripts` (33,362 transcripts, 2005 to 2025, origin not named), STRUX (CC BY-NC-ND), FinCall-Surprise (2,688 calls, 2019 to 2021, consensus includes post call forecasts).
- No free point in time GICS sector history found, so sector scoring may be switched off.
- Work by Claude. Decision by John.

### 15 Nov 2026: comparison with published work

- Checked StarMine and the papers. StarMine figures (about 70 percent directional hit rate) are vendor reported and were not independently checked.
- Found an error: the documents said SAE-FiRE's XGBoost baseline had AUC about 0.67. The paper's table gives 0.620 for XGBoost on earnings calls. The 0.67 figure belongs to SAE-FiRE's own models (0.657 to 0.668). Corrected and logged as conflict C20.
- SAE-FiRE's label uses analyst forecasts issued up to a month after the call, on a 2012 to 2014 sample.
- Added FR-27: a replication on FinCall-Surprise for research use, to give an external reference.
- Work by Claude.

### 15 Nov 2026: restructure (commit 4727aa9)

- Created `docs/SSOT.md`, the single source of truth. Only John edits it. Claude asks first.
- Created `docs/decision-log.md`, merging four separate lists of open decisions.
- Rule set: each requirement is defined in one document, by type. Duplicates were merged. Withdrawn IDs are listed in the requirements README.
- Fixed priority clashes (load test, restore drill, regression set, model inventory changed to Should).
- Rewrote the data gate matrix, which still preferred paid sources.
- Added `docs/tools/check_requirements.py` to check duplicate IDs, wrong document, undefined or withdrawn references and broken links.
- Rewrote the drift review against the SSOT.
- Found: 161 of 215 requirements outside the market document are Must, and 66 of 70 data requirements are Must. Logged as D-26.
- Work by Claude. Rules and SSOT ownership from John.

### 15 Nov 2026: readiness check and owner answers (commit 70149d8)

- Claude listed what was missing before building: planning notes and proposal PDF not in the repo, LLM provider and budget, hedge word and negation lists, FinBERT checkpoint, untested data assumptions.
- Answers from John:
  - Build on his own PC, CPU first, GPU later maybe. He installs Docker.
  - Explanation agent: default is one hosted API with a small cap. Final choice later (D-27).
  - Retrieval: plain SQL over per sentence scores, not a vector store. Reason given: each text feature is computed per sentence, so the evidence for a feature is the sentences that produced it.
  - Hosting: local Docker first, then Cloud Run if time allows.
  - SEC EDGAR contact: his email, in an environment variable, never committed.
  - Reminders for Docker, accounts and keys, the LLM choice, ethics approval and assessment criteria.
- Work by Claude. Decisions by John.

### 15 Nov 2026: first data spikes

- John approved running small tests of the data sources and recording the results.
- Hugging Face coverage of companies that left the S&P 500. The first run of 25 tickers failed with timeouts and 500 or 502 errors. A retry returned four:

| Ticker | Rows | Years |
|---|---|---|
| AAPL (current member) | 79 | 2005 to 2025 |
| XLNX (acquired 2022) | 60 | 2006 to 2021 |
| TWTR (acquired 2022) | 16 | 2018 to 2021 |
| ATVI (acquired 2023) | 27 | 2015 to 2021 |

- Reading: the set includes some removed companies, but coverage may be incomplete, since all three end in 2021 or earlier. The meaning of the year field and the other 16 planned tickers were not tested. The list of removed companies came from memory, not index history.
- EDGAR diluted EPS spike: script written, not run. A safeguard refused the first command because it held John's email beside a client name. The variable `SEC_USER_AGENT` is not set in the working environment.
- Work by Claude.

### 15 Nov 2026: delivery plan

- Decision (John): pipeline, models, API, explanation agent and evaluation finished by the end of December. Final submission probably late February 2027. January and February for Cloud Run, frontend polish, the usability study, the write up and final changes.
- Capacity (estimates): about 100 to 130 hours to 31 December, and about 225 to 300 hours to late February, at 15 to 20 hours a week.
- Not every Must requirement will fit by December. D-26 and D-03 are needed before week 3.
- Ethics approval for the usability study should be requested in December.
- Work by Claude. Dates from John.

### 15 Nov 2026: log book

- John asked for a log book of commits and work done. First version was written as a draft report with a word budget and report use notes. John said he wants a plain log only. Rewritten as this file.
- Work by Claude. Direction from John.

### 16 Nov 2026: pipeline architecture and source research

- John asked for a start-to-finish pipeline with the components for each step, then for it to be written into the architecture folder with no contradictions against the existing documents, and for web research on prediction timing, transcript timestamps, index membership and sector sources.
- Written: `docs/architecture/pipeline.md`.
- Found a conflict in the existing documents: transcripts are dated on or after the announcement (TX-02, FR-02), but every input must be dated before it (GATE-2, FR-22). Logged as D-31 with a proposed fix. Not edited in the requirements.
- Facts read from primary pages: the Hugging Face card gives a call date with a time of day, plus fiscal year and quarter, but not what the time means or where the transcripts came from. SEC FAQ gives the EDGAR acceptance time as HHMMSS in Eastern time and a 10 requests a second limit.
- Membership: `fja05680/sp500` (MIT) is the best free candidate, with stated gaps in early years. `Johnbrick123/sp500-data` has no licence. Logged as D-32.
- Sector: no free point-in-time GICS history found. SIC from EDGAR mapped to Fama-French groups is the only free option, and whether the SIC is dated was not verified (the SEC pages that would say returned 404). Added to D-20.
- Closed from John's answers: Loughran and McDonald hedge list (C-14), stored-prediction lookup (C-15), Streamlit (C-16).
- Not run: no spike. `SEC_USER_AGENT` is still not set.
- SSOT and requirement documents not edited.
- Work by Claude. Decisions by John.

### 17 Nov 2026: Docker skeleton

- John installed Docker Desktop and set WSL memory to about 10 GB (`free -g` showed 9 total).
- Built the skeleton: `docker-compose.yml` (PostgreSQL 16, Redis 7, Celery worker, FastAPI), `Dockerfile` (Python 3.12, CPU PyTorch, spaCy small English model), `requirements.txt`, `requirements.lock`, `.env.example`, `.gitignore`, `.dockerignore`, and `src/earnings/` with settings, Celery app, one test task and a `/health` endpoint.
- Result, measured: image 3.64 GB. From a clean start all four containers report healthy. `/health` returns 200 with Postgres, Redis and worker all ok. A Celery task made the full round trip. With the worker stopped, `/health` returns 503 and names the worker. All planned ML packages import (torch 2.15.0 CPU, transformers 5.23.0, spaCy 3.8.18, XGBoost 3.4.1, SHAP 0.54.1).
- Checked: `.env` is ignored by git, and no email address or key appears in any new file. The `SEC_USER_AGENT` pass-through works (tested with a dummy value, then reset). It is still unset in the real shell.
- Not done: no database tables, no ingestion, no model downloads, no commit.
- Work by Claude.

### 17 Nov 2026: working rules and proposal read

- John supplied a set of audit rules ("Deterministic Auditing") and asked that Claude always follow them, with the SSOT as the source of truth. Saved first as `CLAUDE.md` in the repository root, text unchanged, with a short binding note added at the top that points "original requirements" at the SSOT, the requirement documents and the decision log. John then renamed it to `Deterministic_audit.md`. Claude Code only loads `CLAUDE.md` automatically, so the rules no longer load by themselves (see audit finding F-08).
- The pasted rules have no Section 2 (numbering goes from 1 to 3). Kept as supplied.
- Read the proposal PDF in `docs/source/` (8 pages, text extracted inside a throwaway Docker container, nothing installed on the PC).
- Findings against earlier work are in the session reply: the proposal's task uses the call transcript itself (bears on D-31); the proposal defines the guidance ratio but not the negation patterns; the skeleton added dependencies and has no automated tests.
- Not done: `audits/requirements_traceability.md` does not exist yet. No SSOT or requirement edits. No commit.
- Work by Claude. Rules from John.

### 17 Nov 2026: independent audit of the Docker skeleton

- John asked for the audit under the new rules. Scope: the Docker skeleton only.
- Added: `audits/audit_2026-11-17.md` (evidence and findings), `audits/requirements_traceability.md` (generated by `audits/generate_traceability.py`, 263 requirements, same file on every run), `tests/` (3 files, 16 tests) and `requirements-dev.txt`.
- Result, measured: 16 tests passed (4.64 s). With the worker stopped, 2 of the 3 selected tests failed, which shows the tests can fail. A no-cache build from a clean checkout succeeded and matched `requirements.lock` (129 of 129).
- Overall status: not PASS. Of 15 requirements assessed: 0 PASS, 7 PARTIAL, 4 FAIL (EQ-02, EQ-04, NFR-11, PL-03), 4 UNVERIFIED. The other 248 are UNVERIFIED because they were not assessed.
- Main defects: no exact dependency pins (0 of 22), no CI or lint configuration, no request id or latency in logs, a database password containing `@` breaks the connection URL.
- Not changed: compose file, Dockerfile, `requirements.txt`, source code, SSOT, requirement documents. Eight proposed changes (F-01 to F-08) await John's approval.
- Not done: no commit.
- Work by Claude.

### 17 Nov 2026: audit findings F-01 to F-08 fixed

- John approved all eight findings and asked for no new per-requirement tests yet (a later step). None were written. Existing tests were only updated to match changed code.
- Changes: exact pins everywhere with a build-time check (`scripts/check_pins.py`), runtime trimmed to what the code uses (image 3.64 GB to 326 MB, locked packages 129 to 39), request logging with id and latency, database URL built from parts, CI workflow, ruff and mypy configuration, health check cached for 5 seconds, two draft ADRs, `CLAUDE.md` importing `Deterministic_audit.md`, new README.
- Two defects found and fixed on the way: `packaging` is an undeclared dependency of Celery's Redis transport (the worker crashed without it), and the Celery ping made every uncached `/health` take about 2.1 s.
- Result, measured: 19 test cases pass, lint, format and types clean, a planted unpinned dependency fails the build, a planted fake token fails the secret scan, `pip-audit` reports no known vulnerabilities, a password with `@ : / # ?` connects.
- Re-assessed 17 requirements: PASS 2, PARTIAL 10, FAIL 2 (EQ-03 no branch protection, PL-03), UNVERIFIED 3. Not PASS overall. Details in `audits/remediation_2026-11-17.md`.
- Not verified: the CI workflow has never run on GitHub. The repository is public and `docs/source/` is untracked but not ignored.
- Not done: no commit, no push, no change to GitHub settings, SSOT or requirements.
- Work by Claude. Approval from John.

### 18 Nov 2026: decisions, branch protection and commits

- Answers from John: both prediction points are built, with the pre-release forecast (T0) as the headline and the post-call nowcast (T1) secondary (C-17); 100 companies for December, about 20 of them removed from the index (C-18); SEC CIK as the company identifier (C-19); a TranscriptSentence entity added to the data model (C-20); the proposal PDF stays out of the public repository (C-21); ADRs 0001 and 0002 accepted (C-22); branch protection on `main` (C-23); SSOT map rows approved (C-24).
- Done: branch protection enabled and read back from the GitHub API. `docs/source/` added to `.gitignore`. `adr/` row added to the SSOT map. `TranscriptSentence` added to Product Section 11. ADRs marked Accepted. Decision log and `pipeline.md` updated. Traceability regenerated (PASS 3, PARTIAL 10, FAIL 1, UNVERIFIED 3).
- Not applied, because John has not seen exact wording: the requirement edits that follow from C-17 (D-33) and the negation and forward-guidance definitions (D-34). D-01 (supervisor agreement on the label) is unanswered and still open.
- Probe before the decisions: one request pair to SEC EDGAR for one company (Apple). The submissions data has a UTC acceptance time with seconds and an `items` field. `sic` is a single current value. EPS facts have a `filed` date. There is no Q4 EPS fact. One company only.
- Not verified: lint, format, types and tests were not re-run today because Docker Desktop was stopped. No source, test or build file changed since the last green run. The CI workflow has never run on GitHub.
- Work by Claude. Decisions by John.

### 18 Nov 2026: component requirement documents and consistency review

- Asked by John: requirements for feature engineering, the explanation agent, the database and the frontend, with each pipeline component in its own file, nothing from outside the project, and a check of all files for errors and contradictions.
- Added four draft documents in `docs/requirements/`: feature engineering (FE-01 to FE-31), explanation agent (AG-01 to AG-26), database (DB-01 to DB-17) and frontend (UX-01 to UX-11). Each requirement names where in the project it comes from. Rules that the project leaves open are marked "pending" and sit in decisions D-36 to D-39. Ideas that did not trace to the project were removed and listed in D-41.
- Errors found and fixed in earlier files: D-33 proposed a new FR-28 but FR-28 already exists (now FR-29); several documents said "three" or "four" requirement documents; Product SC-06 and DO-02 still required a vector store ADR although decision C-11 chose plain SQL; the Data document named a different membership source from pipeline.md (D-32 is open); the Data spike section said the EDGAR script was not run although a one-company probe was; the commit register lacked a720023; the traceability generator ignored any new document.
- Edited existing requirement text, listed so John can reverse any: Product FR-24 (mean sentiment over analytic sentences), Project-Wide SC-06, DO-02, DO-05, SS-03, ASM-04 and C11 wording, Data 4A.1 and the gate matrix (membership source), Data Section 12 (spike result).
- Not done: the SSOT map rows for the four documents (owner-only, proposed in D-40).
- Verified after Docker Desktop was started: stack healthy, `/health` 200, `ruff check`, `ruff format --check`, `mypy` clean, 19 tests passed. The document checker passes (checks 1 to 6) and the traceability generator gives identical output on repeated runs. The CI workflow has still never run on GitHub.
- Full list of edits to existing files: `audits/consistency_review_2026-11-18.md`.
- Work by Claude. Decisions by John.

### 18 Nov 2026: four more component documents and two owner answers

- Answers from John: the label route is his decision because Professor Goodacre does not mind which label is used, so the time-series SUE stays (C-25, closes D-01); asked which of three-class and binary suits the project (recommendation: one three-class model, D-42); authentication is a later problem (deferred, SV-15).
- Added four draft documents in `docs/requirements/`: ingestion and preparation (IG-01 to IG-22), modelling and evaluation (MD-01 to MD-23), API and serving (SV-01 to SV-16) and deployment and operations (DP-01 to DP-15). Each requirement names where in the project it comes from. Open values are in D-42 to D-45, approval and SSOT wording in D-46. The checker, the traceability generator and the README cover all twelve documents.
- Findings that shaped them: FR-01 needs three class probabilities, so a binary model would contradict it; the API only reads stored predictions (C-15), so a cloud demo needs no worker; the label has no forward-looking window, so no purging is needed in the split; Product Section 12 has an artefact-checksum error state that C-15 seemed to contradict, resolved in SV-08.
- Not done: SSOT edits (owner-only, wording in D-46). Nothing committed. Not run: any code.
- Work by Claude. Decisions by John.

### 18 Nov 2026: drift controls and numbered requirements for tests

- Asked by John: reduce every drift risk and give requirements IDs that tests can use later.
- IDs added: numbered error states ER-01 to ER-13, endpoints EP-01 to EP-09, screens SCR-01 to SCR-07, success metrics SM-01 to SM-08 (Product) and thresholds TH-01 to TH-15 (Data). Every check of every requirement now has a reference `ID-ACn` in the generated `audits/acceptance_index.md` (584 checks). Goals, non-goals, stretch objectives, market needs, conflicts and gates have no check of their own and are listed as such.
- Controls added (decision C-26): a task brief before every build task and IDs in commits and tests (Deterministic_audit.md, Drift controls; CLAUDE.md now also loads the requirements index); `audits/pending_values.md` lists the 42 requirements that cite an open decision; `@pytest.mark.req(...)` markers on tests, filled into the traceability file; `scripts/check_requirement_refs.py` and `scripts/check_commit_refs.py`; a CI job "Requirements consistency (DO-03, DO-05)" (DP-07 is now Must). Four existing tests were marked (SC-01, API-01-AC1, API-02-AC1, SP-06). Eight older tests are on a legacy list that only shrinks.
- Verified: each check was shown to fail on a planted fault (unknown reference, unmarked test, code commit without an ID, stale generated file) and to pass on the real tree. Stack healthy, ruff, format and mypy clean, 19 tests passed with unknown markers treated as errors, requirement checker and pins check pass, generator output identical on repeat runs.
- Not verified: the new CI job has not run on GitHub. `actionlint` was not re-run on the changed workflow because the image pull was blocked in this session. Making the new job a required check is a repository setting and needs John's approval.
- Work by Claude. Decisions by John.

### 19 Nov 2026: feasibility review, prediction point wording and gap fixes

- Asked by John: count the requirements, check that every feature has one, check that each can be implemented, then fix the first issue and the gaps. Result: 476 IDs, of which 376 were requirements before today. The full review is `audits/feasibility_review_2026-11-19.md` (15 issues, 8 gaps, a test class for every requirement).
- Approved by John and applied: the requirement wording that follows from C-17 (Product FR-01, FR-07, FR-18, FR-22, FR-24, ER-01, new FR-29, Data GATE-2), closing D-33 as C-27. Gap fixes G-01 to G-08 as C-28: Feature Engineering FE-32 (EDA notebook), Product EP-10 and SCR-01, five schema additions in Database Section 9, FR-28 wording, manual retraining in the Modelling document, SSOT Sections 5 and 8 (edited with John's permission), and one sentence in the Drift controls about stretch objectives.
- Two changes differ from what John was first shown, both recorded in C-28: FE-32 is Must, not Should, because the proposal lists the EDA notebook as a milestone 2 deliverable; and the non-goal NG1 was not extended, because that would rule out a later forecast for upcoming events. FR-28 carries a milder sentence instead.
- Checked against: the SSOT, the decision log, pipeline.md, and the proposal PDF (text recovered by hand from its streams, because no PDF tool is installed; the Read tool could not render it). The proposal confirms the EDA notebook deliverable and the "analyst consensus dispersion" wording. It also says the API loads the serialised model, while SV-01 and decision C-15 have the API read stored predictions. That variance is not new and is left for John.
- I-02 (sector history), approved by John and applied as C-29: SIC spike run on 18 companies (header SIC equal to today's value in every year, inconclusive, leaning negative; recorded in Data Section 12). Sector scoring is off for the December scope. Data SEC-01, SEC-02, VL-03 and VL-11 are Must if built, and the "by sector" reports in VL-02, TX-07, IG-22, TR-04, FE-20, FE-31 and EQ-09 apply only where a dated sector history exists. D-20 is closed.
- I-03 (consensus baseline), approved and applied as C-30: Market N4 reworded, and Product FR-06 shows the consensus-revision baseline in its own table on the prospective set. The proposal asks only for a tabular-only baseline, so this is an extension and is not a drift from it.
- I-04 (failure handling after C-15), approved with the warning and applied as C-31: FR-07, ER-04, new ER-14, SV-12, SV-14, UX-02 and the pipeline Step 6 sentence.
- I-05 (explanation job state), option A approved and applied as C-32: the job is the Explanation row, the API role may insert it, a unique key guarantees one job, and failure_reason and completed_at are added.
- I-06 (no alert channel), approved and applied as C-33: ER-13, SV-08, SV-12, DP-09; D-13 closed (Slack alert dropped). From now on John approved following proposals automatically when they align with the SSOT, the proposal and the other documents; each is checked first and recorded.
- I-07 to I-15 checked against the SSOT, the proposal and the other documents, and applied as C-34 to C-40: NFR-03 and NFR-04 made testable; TX-04, TX-07 and IG-22 measured against the loaded company list; FR-25 and MD-20 handle an uninformative cutoff; LB-06, VL-05, VL-06, VL-08, AE-02 and TX-04 say what happens on a miss; FR-27 limited to what the benchmark supplies; six small wording fixes; /metrics needs the token. No pending value was filled in. The SSOT corpus sentence (S&P 500, 4,000 to 5,000 events) was not edited. I-12 (people and approvals) and I-13 (42 pending values) stay with John.
- Not applied: SSOT Section 4 label route wording (D-46), because the exact sentence has not been shown to John. Issues I-06 to I-15 are open.
- Work by Claude. Decisions by John.

### 19 Nov 2026: a test for every acceptance check

- Asked by John: a test for each requirement, a requirement for each test, and the test showing the project code it exercises. Tests are written against requirements, not product features.
- Done: 597 acceptance checks (432 IDs) each have at least one test in `tests/test_req_*.py`, one file per requirement document. Every test carries `@pytest.mark.req(...)` and, where code exists, `@pytest.mark.code(...)`. The eight older tests were marked and `tests/legacy_unmarked.txt` is now empty. `scripts/requirement_tests.py` has three commands: `check` (coverage rules), `map` (requirement, test, code table) and `scaffold` (placeholder for any new acceptance check).
- Honest status: 16 checks have a real test, 2 have a test that is expected to fail because the requirement is not met yet (SC-06, SC-07), and 579 are placeholders that skip with a reason (407 not implemented, 56 blocked by an open decision, 81 need a measurement, 35 need a person). Skipped is NOT TESTED, never a pass. The test run prints the counts.
- Run with pytest 9.2.0, ruff 0.17.5 and mypy 2.4.1 (pinned versions, installed into a folder outside the repository, Python 3.14 here against 3.12 in the image): 31 passed, 2 expected failures, 0 failed, 579 skipped (not tested). `ruff check`, `ruff format --check` and `mypy` pass. The integration file `tests/test_stack_integration.py` was not run because Docker was stopped, so its five tests are NOT TESTED in this session. The repository checks skip as NEEDS REPO inside the CI test container, which holds only `src/` and `scripts/`.
- No test without a requirement: `tests/conftest.py` refuses to run the suite if a collected test has no `@pytest.mark.req(...)`. A planted unmarked test and a planted test with a made up reference were both rejected by pytest, `scripts/check_requirement_refs.py` and `scripts/requirement_tests.py check`, and removed.
- Two placeholders that duplicated checks with real tests (NFR-04-AC1, DP-01-AC1) were removed.
- Needs John: add `python3 scripts/requirement_tests.py check` to the CI requirements job (change to DP-07), and run the full CI test command once with Docker running, which also runs the integration tests.
- Work by Claude. Decisions by John.

## Waiting on John

- Feasibility review I-12 and I-13: name the independent reviewer (D-09), start the ethics application (D-16), and give the values for the 41 requirements that cite open decisions (`audits/pending_values.md`). Also whether the SSOT sentence on the corpus (S&P 500, 4,000 to 5,000 events) should be reconciled with the 100-company subset (C-35).
- D-34: approve the negation and forward-guidance definitions.
- D-35 to D-46: FinBERT checkpoint, the exact feature rules, agent values, database and frontend values, approval of the four new documents, and any of the removed candidates you want back.
- D-46: note in the next supervisor meeting action list that Professor Goodacre has no objection to the time-series label (C-25 closed D-01 on John's word; SC-07 and SS-04 ask for it in writing).
- D-32 (membership source).
- D-03 and D-26 (drop order, re-tagging the Must data requirements), needed before week 3.
- D-29: the exact submission date.
- Two small SSOT document map edits still unapproved: the prefix GATE on the data row, and a row for this log book.
