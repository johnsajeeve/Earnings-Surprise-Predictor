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
| f4503db | 19 Nov 2026 | Feasibility review fixes (C-27 to C-40) and a test for every acceptance check |
| Next commit | 21 Nov 2026 | Reversible requirement, test and code matrix |

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

### 21 Nov 2026: reversible test matrix

- Asked by John: a reversible requirement, test and code matrix, with the check text fingerprinted, run results from pytest, and test to code links measured by coverage.
- Done: `scripts/test_matrix.py` (build, verify, accept, trace, results). `audits/test_matrix.json` and `.md` are generated and committed, with three views of one relationship: check to tests, test to checks and code, code to tests and checks. The markers on the tests are the only place the relationship is written. `tests/requirement_checks.lock` fingerprints the wording of all 597 checks. `coverage==7.17.4` was added to `requirements-dev.txt` and a coverage section to `pyproject.toml` (dynamic context per test function). `test-results/` and `.coverage` are ignored by git. CI: the requirements job runs `build` before the generated-files diff and `verify` after the reference check. README and Deterministic_audit rules 5 and 6 describe it.
- Verified: pytest 38 passed, 2 expected failures, 0 failed, 579 not tested (integration file not run, Docker stopped). ruff, ruff format and mypy pass. A planted reword of FR-01-AC2 and a swap of the two FR-04 criteria made `verify` fail and were restored. A measured run merged 13 PASS, 2 known FAIL, 56 BLOCKED and 526 NOT TESTED checks from the unit tests and showed where declared code and executed code differ.
- Limits: coverage cannot attribute code that runs at import time, and tests that only read files execute no project code, so declared and measured code differ for them. The measured report is not committed and has not run in CI. The CI change has not run on GitHub.
- Work by Claude. Decisions by John.

### 23 Nov 2026: implementation plan, audit ledger and Wave 0.1

- Asked by John: an implementation plan in phases, waves and steps with the best lifecycle method and testing at every level, a deterministic audit file to stop drift and fabricated claims, and then to start building.
- Done: `docs/implementation-plan.md` (plan-driven phases, weekly waves, test-first steps, three gates); `audits/implementation_audit.md` (accountability rules, gate commands, drift register, ledger); `audits/plan_coverage.txt` and `scripts/check_plan_coverage.py` (each of the 480 requirements mapped to one wave, each wave has a ledger row, a PASS needs an evidence file). Two gap reviews changed the plan: 95 uncited Must requirements, three missing waves, overlapping phases, class thresholds placed before the EDA, and checks mapped to waves that could not test them.
- Wave 0.1 (in progress): regression baseline measured (25 passed and 599 skipped in the CI-style run, 42 passed and 580 skipped in the full-repository run, 0 failed). Spikes on real data: call time against 8-K time (call stamps are US Eastern with daylight saving, decision C-42), EDGAR EPS depth (9 of 10 companies), consensus from yfinance, removed-company transcript coverage (126 of 230), FinBERT speed (14.7 to 28.3 sentences a second). Source register (7 datasets, all primary entries cost zero) and ADR 0004 (label route). Five placeholder tests became real checks (SR-01, SR-09, TH-14, OR-02, SC-07); a planted bad register row made them fail.
- Decisions by John: C-41 (plan approved, December target kept), C-42 (call-time zone), C-43 (register placement, ADR 0004, Section 12 wording, D-32 and D-19 closed).
- Limits: SR-06 fails (no fallback for the announcement time, and no fallback tested). SC-07 is partial without the supervisor's written agreement. D-35 stays open: the weights of `ProsusAI/finbert` are CC BY-NC-SA 4.0. The stack was rebuilt over running containers, not from a clean volume. The second bulk-file observation, the Finnhub, FMP and Alpha Vantage spikes and the independent phase audit are not done.
- Work by Claude. Decisions by John.

### 23 Nov 2026: Wave 0.2, database foundation

- Asked by John: start with whichever of Waves 0.2 and 0.3 is better. Wave 0.3 (forward consensus capture) loses data every day it waits, but it needs a migration, so the database slice came first. John approved (C-44): Alembic and yfinance as runtime dependencies, the role, pool and time-out values, a changed EstimateSnapshot, and embedded Celery beat.
- Done: Alembic migrations (`earnings.migrate`, one-shot `migrate` compose service, migration 0001 company with the ten-digit CIK as key); roles `earnings_migrator`, `earnings_worker` (no delete) and `earnings_api` (read only), none a superuser; pools of 5 plus 5, statement time-outs 10, 120 and 300 s; a test database built from nothing each session; `load_companies` task, safe to run twice. D-38 narrowed to the tables not yet approved.
- Verified: full-repository pytest 60 passed, 3 expected failures, 0 failed (47 passed before); CI-style run 42 passed, 0 failed; ruff, ruff format and mypy pass; planted faults in the role grants and a time-out made the role tests fail; no earlier passing test regressed.
- Limits: DB-02 is partial (no agent role until Wave 5.1). DB-04 and DB-05 only cover the company table so far. The wave is not run on GitHub Actions and not audited independently. All role passwords are in every service's environment (acceptable locally).
- Work by Claude. Decisions by John.

### 23 Nov 2026: Wave 0.3, forward consensus capture

- Asked by John: do Wave 0.3 first if it is better. It was the time-critical one, so Wave 0.2's database slice was built first and 0.3 followed straight after. John chose 22:30 UTC, with a catch-up capture when the worker starts and today has no snapshot.
- Done: migration 0002 (`estimate_snapshot`, append-only for the worker role, nothing before 23 Nov 2026 00:00 UTC, one row per company, source, period and UTC day); `earnings.consensus` (capture, gap report, catch-up check); the `capture_consensus` task and the daily beat in the worker; a list of 10 companies. The first real capture ran by itself when the worker started: 10 of 10 companies stored, 12 seconds.
- Verified: full-repository pytest 69 passed, 3 expected failures, 0 failed; CI-style 51 passed; ruff, format and mypy pass; planted faults in the migration made the SR-08 tests fail; no earlier passing test regressed.
- Limits: the job has run on one day, so SR-10 stays partial until real runs on later days. The 22:30 run has not happened yet. Capture only runs while Docker and the PC are on. Ten companies only. XOM left out until the CIK question (DR-06) is settled.
- Work by Claude. Decisions by John.

### 23 Nov 2026: earlier-wave fixes, then Wave 1.1 (task framework and EDGAR client)

- Asked by John: resolve the open issues of the earlier waves, then start Wave 1.1. John approved (C-45): three new tables (`ingestion_run`, `dead_letter`, `raw_payload`), the retry and queue values, deferring the Alpha Vantage client until a key exists, and requiring the sixth CI check.
- Earlier waves: the question of five or six required checks was settled by reading the repository settings (five required, the sixth job was not); the sixth is now required. A clean clone built from an empty volume in a separate Compose project reaches healthy services and passes the CI-style tests (EQ-04). The project database was untouched.
- Wave 1.1 done: retries (3, backoff from 30 s to 300 s, jitter) with a dead-letter table; run records for every task; late acknowledgement; a rate limiter shared through Redis (8 requests a second against the SEC limit of 10); an EDGAR client that refuses to send without the contact, sends it only to sec.gov hosts and never logs it; raw payloads stored as received and parsed offline; one schedule file; a late-job report. First real slice: five companies fetched through the queue, 25.9 MB stored.
- Verified: full-repository pytest 94 passed, 3 expected failures, 0 failed (69 before); CI-style 76 passed; ruff, format and mypy pass; three injected faults made 7 tests fail; no earlier passing test regressed.
- Limits: Wave 1.1 is partial. Alpha Vantage limit and counter deferred, the worker-kill test is for Wave 7.1, the other three scheduled jobs and the event flag come with their waves, and the retry waits were tested eagerly, not in real time. Not run on GitHub Actions.
- Work by Claude. Decisions by John.

### 23 Nov 2026: Finnhub, storage rules (Wave 1.2), branch pushed, Phase 0 audit started

- Asked by John: place the Finnhub key in the file for keys, finish the leftovers of earlier waves, push the branch, start Wave 1.2, make sure the auditing works, and log it.
- Key: stored in the git-ignored `.env` as `FINNHUB_API_KEY`, never printed. A scan of every tracked file and the whole git history found it nowhere. It is not passed into the containers, because no code uses it.
- Finnhub spike (leftover of Wave 0.1): the free key gets 403 on the quarterly estimate endpoint (0 of 5 tickers) and `/stock/earnings` returns only the last 4 quarters, so it cannot be a forward consensus source and cannot pass VL-12's five-year test. Its terms allow personal use only and forbid redistribution. Recorded in the source register as optional, not adopted; the yfinance fallback is now recorded as failed.
- Wave 1.2 done: the worker cannot update or delete any append-only table, with a test that the list and the database agree; an as-of read that returns only versions strictly before the date; half-open validity ranges with overlap refused by the database, for ticker history and index membership; a hash check of stored payloads (5 real payloads, 0 mismatches). While building it I found that the migration history table was writable by the worker and API roles, and closed that.
- Plan change: DB-11-AC1 moved to Wave 1.4, DB-12 to 2.4, DB-13 to 1.6 and DB-14 to 1.7, because their checks need tables or data that come later. Coverage map and plan edited together and the coverage check passes.
- Verified: full-repository pytest 105 passed, 3 expected failures, 0 failed (94 before); CI-style 87 passed; ruff, format and mypy pass; two off-by-one faults in the as-of read and the validity boundary made tests fail; no earlier passing test regressed.
- Pushed `build/wave-0-1` to GitHub (CI runs only on a pull request, so nothing has run there yet).
- Auditing: an independent agent audit of Phase 0 was started in an isolated clone, given only requirement IDs. A new section of the audit file lists the time-gated checks that cannot be run yet (the 22:30 UTC capture, the second look at the SEC bulk files, the real retry waits).
- Limits: SR-04 lacks a source version column (DR-14, needs John). DB-08 and DB-09 cover only the tables that exist. The 22:30 UTC capture, the second capture day and the bulk-file check are still to happen.
- Work by Claude. Decisions by John.

### 23 Nov 2026: independent audit of Phase 0 and the fixes it led to

- Asked by John: make sure the auditing works. A fresh agent audited Phase 0 (Waves 0.1 to 0.3) in an isolated clone with its own Docker project, given only the requirement IDs and the repository, not my evidence or claims. Its report is in `audits/evidence/phase-0-independent.md`.
- What it found, with my response: the worker could change the migration history table (already closed in Wave 1.2, re-probed live); I had cited 22:30 UTC as approved when I had not recorded John's answer in the decision log (now C-46); the SR-06 test accepted "not tested" as a result (tightened); the connection pool test followed its own constants (approved values now pinned); the schema test only compared migrations with themselves (now every column and the deployed database); a freshly started stack called Yahoo with no off switch (now behind `CAPTURE_CATCH_UP`, off by default, on in John's `.env`); the application roles could connect to the `postgres` database (revoked); the capture task did not report gaps (now logs them); the start date was duplicated in the code and the migration (a test ties them).
- Not fixed, stated: the database enforces only a lower bound on `captured_at` (DR-15); the register's Yahoo and Hugging Face facts are still "not read" or "unknown"; the source-version column (DR-14); the 20 repo-reading tests skipped in CI (DR-08).
- Verified after the fixes: full-repository pytest 111 passed, 3 expected failures, 0 failed; CI-style 93 passed; ruff, format and mypy pass.
- Result: Phase 0 is PARTIAL (the lower status of the auditor and me stands). John's own spot-check of five requirements has not happened.
- Work by Claude, audit by an independent agent. Decisions by John.

### 23 Nov 2026: pull request opened, Wave 1.3 (universe and identifiers)

- Asked by John: open the pull request, start Wave 1.3, and never delete working branches that hold commits. Pull request #3 is open against `build/docker-skeleton` (it is stacked on the still-open #2); no branch was or will be deleted, and that rule is saved to memory.
- John decided (C-47): companies whose CIK changed are excluded and logged (XOM, new Disney, Baker Hughes and others), Wikipedia's history table is a secondary source for names and removal reasons only, and the 100 companies are chosen with seed 2031 (80 current, 20 removed with at least one per year).
- Done: four real source files stored as received; parsers that read them offline; exact-name matching with a review list; a rename rule for renamed tickers; the selection; a job that loads 5 or 100 companies from a list file, safe to repeat; 100 companies, their ticker histories and index membership loaded into the project database; the daily capture widened to 89 companies.
- Found by checking the real data, not the tests: the first matcher accepted `BBT` as "Beacon Financial Corp" (a reused ticker) and linked two renames on one day wrongly, and the first rename rule linked 301 tickers, many wrongly. Each was fixed and the links were read by hand.
- Results: the company count at each year-end is 499 to 503 against the nominal 500 (tickers 502 to 506, the difference is share classes); all ten known renames give one continuous history; every year has a removed company with a date and reason.
- Verified: full-repository pytest 125 passed, 3 expected failures, 0 failed (111 before); CI-style 106 passed; ruff, format and mypy pass; faults in the matching rules made 4 tests fail; no earlier test regressed.
- Limits: 431 of 1,209 tickers have no CIK (62 of the 230 removed ones); the rename rule is beyond the written method and needs John's confirmation (DR-16); removal reasons are Wikipedia's wording; the list was not checked company by company by a person.
- Work by Claude. Decisions by John.

### 24 Nov 2026: Wave 1.4 finished, inspection of Waves 0.1 to 1.4

- Asked by John: finish what was left of Wave 1.4, inspect everything built so far against the requirements and their tests, then commit, push and move on.
- Wave 1.4 (financial data): EPS history and fundamentals stored as every version a filing reported, append-only, with as-of and first-filed reads (a filing dated on or after the prediction date is not visible); derived quarters flagged, using the year minus the nine-month figure so a share split does not break them; earnings-release 8-K parsing and the earlier-of-call-and-filing cutoff; backfill of the 100 companies (15,834 EPS rows, 14,555 fundamentals rows). A rebuild from the stored payload gives identical table hashes.
- Real data findings: Apple's fiscal 2014 Q1 EPS was first filed at 14.50 and restated to 2.07 after the split; 98 of 100 companies have EPS, and 67 have the 10 pre-2015 quarters LB-02 needs; Visa and Danaher have none in SEC's API. The company selection was found to contain two old registrants with the same name and one company with no SEC facts; the check was tightened and three companies were replaced.
- Found on 24 Nov: the worker's start-up catch-up failed after a restart because PostgreSQL was still recovering (now a retried task), and 3 of 89 captures failed on Yahoo timeouts (now one more attempt). The second capture day exists (24 Nov, from the catch-up); the 22:30 UTC schedule has still not been seen firing. The SEC bulk files were refreshed between 21 and 24 Nov.
- Inspection (`audits/evidence/inspection-2026-11-24.md`, generated from the matrix): in Waves 0.1 to 1.4, 42 checks are real, 2 are expected failures and 12 are not tested. Checks that could not be tested in the wave they were assigned to (transcripts, events, the demo bundle) were moved to the waves that can test them. New tests: every registered task must have a run-twice test (EQ-07), the Section 12 spike result (IG-16), no table keyed on a ticker (DB-04).
- Verified: full-repository pytest 145 passed, 3 expected failures, 0 failed; CI-style 124 passed; ruff, format and mypy pass; faults in the as-of read and the derivation made 4 tests fail.
- Limits: prices wait for John's table approval (Wave 1.8); values are not yet checked against the filings (Wave 1.7); the columns of the two new tables extend Product Section 11 (DR-18).
- Work by Claude. Decisions by John.

### 24 Nov 2026: second independent audit (Waves 0.1 to 1.4) and the fixes

- Asked by John: finish Wave 1.4, inspect everything built against the requirements and tests, commit and push, then move on. A second fresh agent audited the work in an isolated clone (`audits/evidence/phase-1-independent.md`).
- What it found, and what was done: my selection of the 100 companies broke decision C-47, because four companies that joined the index in 2025 or 2026 had been chosen as "in the index at 31 December 2024" (my error; fixed, the list was re-drawn, the tables rebuilt from the stored payloads, and the new companies fetched); some removal reasons described the company that was added (now marked); the superuser password was in every container (the worker no longer has it and an unused superuser URL is gone; the api service keeps it for the CI test job); the fiscal-period columns described the filing, not the period (renamed); and several tests were weaker than they looked (the count test recomputed nothing, the guards that drop test databases were untested, the approved selection values and the start-day gap were not pinned). It also found 4 mutations missed out of 41; each now has a test that fails under it.
- Not fixed, stated: the rules I added in Waves 1.3 and 1.4 that were never approved are listed as D-47 for John; the membership file can carry a current ticker for years when another was used (DR-20); John's email address is the Author header of one commit made through the GitHub website (DR-21); the Section 12 text prints the gap quartiles as magnitudes and needs John to approve a correction.
- Verified: full-repository pytest 154 passed, 3 expected failures, 0 failed; CI-style 133 passed; ruff, format and mypy pass. The real-data coverage is better with the corrected list: 94 companies have pre-2015 EPS and 79 of them have the 10 quarters LB-02 needs.
- Work by Claude, audit by an independent agent. Decisions by John.

### 25 Nov 2026: Wave 1.5 (transcripts) resumed, Docker stopped

- Asked by John: finish what was left of the previous session. State at the start: the Hugging Face file was downloaded in full (1,824,805,388 bytes, 33,362 calls, size checked; the checksum check ran inside the download function), and the module, client, migration 0007 and a first test draft were written but never run.
- Blocked: Docker Desktop was not running (the engine pipe was missing; I could not find its executable to start it). Everything that needs the stack is therefore NOT RUN: the real-data scan, migration 0007, all tests, ruff, mypy, the 100-company load and the review sheet.
- Done without Docker: schema test expectations for the two new tables (`tests/test_req_product.py`), the transcript tests corrected for the loader date window (the Apple release fixture is 2025 and later), a stray import and the longest lines in `src/earnings/transcripts.py` tidied, the ledger row W1.5 set to IN PROGRESS, D-47 item (i) added for the new columns and rules, evidence file `audits/evidence/wave-1.5.md` started with every claim marked NOT RUN.
- Still missing: the real-row excerpt fixture `tests/fixtures/hf_transcript_excerpts.json` (needs the scan), so `tests/test_transcripts.py` cannot pass yet.
- Work by Claude. Decisions by John.

### 25 Nov 2026: audit of Waves 0.1 to 1.5 (static)

- Asked by John: audit what is implemented, check requirements and tests, and keep the gaps as items to add later today. Result in `audits/evidence/audit-2026-11-25.md`. Docker was down, so no test was run: only the host consistency checks (all pass) and a read of the test matrix.
- Result: 61 of 597 acceptance checks have a real test; waves 1.2 and 1.3 have no open checks, 0.1 to 0.3, 1.1 and 1.4 have 1 to 5 each, and Wave 1.5 has 28 open (code not run yet). The generated traceability file is stale as a status record (17 assessed). Ten items to finish later today are listed in the audit file.
- Work by Claude, not independent.

### 25 Nov 2026: Wave 1.5 (transcripts) built and run

- Docker came back. Rebuilt the stack, applied migration 0007, scanned the 33,362 real calls, cut a real-excerpt fixture, fixed the tests and lint, ran 10 mutation checks (2 survived at first, tests added, all killed), loaded the 100 companies, ran it twice (same counts), drew the 50-call review sheet.
- Results: full tests 170 passed, 0 failed; CI-style 149 passed; ruff, format, mypy clean. 3,183 calls loaded, 138 unlinked, 27 with no boundary, 7 companies with no transcript (list in the evidence file).
- Needs John: label the 50 calls in `audits/evidence/wave-1.5/boundary_review_sheet.md` (kept local, not in git); the first one looks wrong to me (DR-23). D-45 run time for the daily transcript check. D-47 item (i).
- Work by Claude, not independently audited yet.

### 25 Nov 2026: Wave 1.6 task brief written

- Wave 1.5 committed (`3bd426a`) and pushed. Leftovers of 1.5 are listed at the end of the brief. Brief for Wave 1.6 (events and time-series SUE) is `audits/evidence/wave-1.6-task-brief.md`; no build work started because drift control 2 says John sees the brief first. Three points need John: event table columns, what one event is, and where split factors come from (LB-05).
- Work by Claude. Decisions by John.

### 25 Nov 2026: Wave 1.6 (events and time-series SUE) built and run

- Brief approved by John. Built the SUE (`label.py`), the event table (migration 0008) and the build, snapshot, coverage and size functions (`events.py`). 12 new label and event tests, 13 mutation checks (all killed after one added test). Full tests 182 passed, CI-style 161 passed, 0 failed; lint and types clean.
- Real result: the label is available for 2,619 of 3,183 events (82%); the rest lack EPS data (DR-26). Transcripts exist for 91% of releases of companies still in the index and 59% of companies that left it (DR-25). Database 677 MB measured, about 3.6 GB estimated for 500 companies.
- Needs John: D-47 (j) sample standard deviation, (k) inferred splits until the price tables are approved, (l) event columns; DR-25 and DR-26.
- Work by Claude, not independently audited yet.

## Waiting on John

Decisions and actions only John can take, as of 24 November 2026. Each has a requirement or decision reference. The blocking ones come first.

**Blocks the next waves**
- **Price tables (Wave 1.8, PX-01 to PX-03):** approve a daily price table and a dated split and dividend factor table. Product Section 11 lists neither. Without them prices cannot be stored. Removed companies will have no yfinance prices.
- **D-45, run times for three more scheduled jobs:** the daily transcript check, the daily 8-K Item 2.02 check and the daily data gates (IG-05). The capture job is set at 22:30 UTC.
- **D-35, FinBERT checkpoint:** needed before Wave 2.1. `ProsusAI/finbert` weights are CC BY-NC-SA 4.0 (non-commercial, share-alike). Accept it or name another.
- **D-34 and D-36, feature rules:** negation, forward guidance, trajectory, question count and the rest (needed before Wave 2.2).
- **D-18, transcript source and demo design:** the Hugging Face set says MIT and "research and educational use only" and names no origin. Needed before Wave 1.5.

**Needs a decision, work can continue**
- **Wave 1.6 task brief:** read `audits/evidence/wave-1.6-task-brief.md` and approve it or change it (three points).
- **Boundary review (TX-03, IG-18, TH-02):** label the 50 calls in `audits/evidence/wave-1.5/boundary_review_sheet.md` (write `correct` or `wrong` after each arrow) and give the sheet back. 95% or more must be correct.
- **D-47, rules I built that you have not approved:** the rename rule, the selection checks, the Q4 and cumulative derivations, the revenue tag order, the table columns, how reasons that name another company are stored, and the capture list. List and reasons are in the decision log. A second independent audit found these were not recorded as decisions.
- **DR-21:** your email address is the Author of one commit made through the GitHub website, so it is visible in the public history. Leave it, or use a no-reply address from now on. Changing history is your call.
- **IG-16 wording:** the Section 12 text shows the gap quartiles as 1,008, 180 and 59 minutes, which are magnitudes of negative values (the filing came first). Approve a corrected sentence.
- **DR-18 (schema detail):** the columns of `eps_history` and `fundamentals_filing` extend Product Section 11. Approve and I update Section 11.
- **DR-16:** confirm the rename rule (a ticker that ends the day another starts, with no index change recorded by Wikipedia, is the same company). All 21 links were read by hand. Read the review list in `audits/evidence/wave-1.3/review_list.csv`, which is the quickest way to catch wrong matches.
- **DR-14:** add a nullable `source_version` column to `raw_payload` (Data SR-04 asks for it).
- **DR-10:** name a fallback source for the 8-K announcement time, or accept a stated scope limit (SR-06).
- **DR-19:** accept that Visa and Danaher have no EPS history in the SEC data and some companies have gaps, or ask for a fallback source (yfinance earnings dates).
- **DR-08:** whether to add a CI job for the 20 checks that read documents and skip in the CI test job.
- **D-46:** record in the next supervisor meeting that Professor Goodacre agrees to the time-series label (C-25, SC-07, SS-04 ask for it in writing).
- **Spot-check:** pick five requirements of Waves 0.1 to 1.4 and check them against the evidence. This is the last step to close the Phase 0 gate.
- **FMP free key:** only if you want the optional second consensus-source test.

**Planning, still open**
- D-03 drop order and D-26 re-tagging the data requirements; D-29 the exact submission date; D-42, D-43, D-37, D-39 and D-27 (provider and budget) before Waves 3, 4, 5, 6; D-16 the ethics application (apply in December); D-21 the library enquiry; D-09 the independent reviewer; D-15 the cloud spend ceiling.
- Feasibility review I-12 and I-13, D-25 (assessment requirements), D-40 and D-46 (approve the eight component requirement documents).
- Two small SSOT document map edits still unapproved: the prefix GATE on the data row, and a row for this log book.
