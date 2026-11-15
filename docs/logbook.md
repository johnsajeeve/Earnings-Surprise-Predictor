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
| Next commit | 15 Nov 2026 | |

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

## Waiting on John

- Set `SEC_USER_AGENT` so the EDGAR spike can run.
- Exact submission date (D-29).
- Permission for two small edits to the SSOT document map: add the prefix GATE to the data row, and add a row for this log book.
