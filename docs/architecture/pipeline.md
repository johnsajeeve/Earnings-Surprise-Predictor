# Pipeline Architecture: From Data to Dashboard

Written 16 November 2026 for John. It describes how the whole system fits together, step by step, with the components each step needs. It follows the [SSOT](../SSOT.md) and the requirement documents. It does not define requirements: each step cites the requirement IDs that do. Where the existing documents are silent or disagree, the step says so and points to a decision in the [decision log](../decision-log.md).

The slide deck in this folder shows the same system as diagrams. This file is the text version with the detail.

## 1. The system in one picture

```
 SOURCES               INGEST            STORE               PREPARE
 -------               ------            -----               -------
 Hugging Face calls ─┐                                    ┌─ split call: prepared remarks / Q&A
 EDGAR XBRL EPS     ─┤                                    ├─ split into sentences (spaCy)
 EDGAR 8-K 2.02     ─┼► Celery tasks ─► PostgreSQL ──────►├─ build label (time-series SUE)
 EDGAR fundamentals ─┤  (Redis queue)   raw + dated rows  ├─ attach index membership + sector
 yfinance prices    ─┤  + validation                      └─ date gates (as-of checks)
 membership, sector ─┤
 consensus snapshots ┘ (forward only, check set)
                                  │
                                  ▼
 FEATURES                    MODEL                          SERVE
 --------                    -----                          -----
 FinBERT per sentence ─┐     temporal split                 FastAPI
 hedge, negation,      │     train 2015-21                  GET  /v1/predictions/{ticker}
 guidance, Q&A         ├──►  validate 2022          ──►     POST /v1/predictions/{ticker}/explanation/jobs
 tabular (EPS trend,   │     test 2023-24, read once        GET  /v1/jobs/{job_id}
 margins, momentum)    │     XGBoost baseline vs full       GET  /health
 sector context        ┘     SHAP, F1, Brier, top-20%             │
 → feature matrix in DB      → model version record              ▼
                                                          EXPLANATION AGENT ──► STREAMLIT UI
                                                          top SHAP → SQL → LLM    ticker, card,
                                                          → citation check        factors, evidence
```

Two modes of running:
- **Batch (offline):** ingestion, preparation, features, training, evaluation. Runs on a schedule or by hand.
- **On demand (online):** a ticker lookup reads a stored prediction (decision C-15). The explanation runs as a background job because it calls an LLM (FR-19).

## 2. The prediction point: when is the prediction made?

This was not settled in the documents. It decides which inputs are allowed, so it comes first.

### 2.1 What the research found (16 November 2026)

| Question | Finding | Status |
|---|---|---|
| Does the Hugging Face transcript set carry a call time? | Yes. The card lists `date` as "Earnings call date in YYYY-MM-DD HH:MM:SS format", plus integer `year` (fiscal year) and `quarter` (1 to 4). Sample values include a time of day, for example 2020-11-23 16:30:00. | Read on the dataset card and viewer. |
| Does the card say what that time means? | No. It does not say whether it is the scheduled start, the actual start or a placeholder. The card names no transcript provider. The only origin hint is `company_id`, described as a "Capital IQ Company identifier". | Unverified. Must be tested against EDGAR (section 2.3). |
| Is there a free, authoritative time for the earnings release? | Yes, probably. The earnings press release is normally filed on an 8-K under Item 2.02, usually as Exhibit 99.1. The SEC states EDGAR records an acceptance time as HHMMSS in Eastern time. | The header format is on the SEC FAQ. That Item 2.02 and Exhibit 99.1 are the usual place is from third-party guides, not SEC text. The field format inside the data.sec.gov JSON is unverified. |
| Is the acceptance time the moment the news became public? | Not necessarily. A company can issue the release over a news wire and file the 8-K later. This is my inference, not something the sources state. | Treat the acceptance time as a late bound, not the exact release time. |
| Does the literature settle the question? | No source read answers it directly. One paper says press releases usually come first and are more widely disseminated than the call. If a call follows the release, its text contains information the market already had. That is again an inference from the sources. | Open. |

### 2.2 The conflict in the existing documents

These existing requirements cannot all hold:

| Requirement | Says |
|---|---|
| Data TX-02, Product FR-02 | A transcript is dated on or after its announcement, within one trading day. |
| Data GATE-2, Product FR-22 | Every input to the label and the features is dated before the announcement, and a test fails the build if any stored as-of timestamp is not before D. |
| Product FR-01 | A ticker with no transcript gets no class. This reads as if the transcript of the event being predicted is required. |
| Product FR-24 | Text features have the as-of rule "Transcript". |

If the text features come from the call for the same quarter, that call happens on or after the announcement, so FR-22 and GATE-2 fail by construction. If they come from earlier calls, FR-22 holds and FR-01 needs its wording changed. The SSOT does not say which. Logged as decision D-31, closed as C-17.

### 2.3 Design (decision C-17, 18 November 2026)

Use one feature store where every input carries an as-of time, and define two prediction points. John chose option C on 18 November 2026: both points are built and T0 is the headline. The requirement wording that follows is decision D-33, which is not yet approved, so FR-01, FR-22, FR-24 and GATE-2 still read as before.

| | T0: pre-release forecast (headline) | T1: post-call nowcast (secondary, tagged Should) |
|---|---|---|
| Cutoff | The earlier of the call time and the 8-K Item 2.02 acceptance time. This is the conservative choice, because the release can come before the filing. | After the call has ended. |
| Text inputs | Calls from earlier quarters only. The sentiment surprise is the last call against the four before it. | Adds the call for the event itself. |
| Tabular inputs | Latest filing filed before the cutoff, prices before the cutoff, prior EPS surprises, sector peers that announced earlier (FR-24 as written). | Same. |
| What it claims | A true forecast of a label not yet public. Meets the SSOT's no-lookahead criterion with no caveat. | The label is already public when the call happens, so this tests whether the call text agrees with the surprise. It is reported separately and not called a forecast. |
| FR-22 and GATE-2 | Hold as written. | Fail as written. They would need an exception that is stated and tested. |

Why T0 is the headline: it is the only version that satisfies the evaluation criterion "no lookahead bias" (SSOT Section 10, item 2) and the existing FR-22 without exceptions. It costs little to add T1 later, because it is the same pipeline with a later cutoff.

Effect on the explanation agent: at T0 the cited sentences come from the previous call, so the card shows that call's date beside each quote.

Effect on the research question: the text may carry less signal at T0. The SSOT says a negative result is a valid finding.

Spike to run first (data decision C-12 allows it; needs `SEC_USER_AGENT` set): for 50 events, compare the Hugging Face call time with the 8-K Item 2.02 acceptance time. Report how often the call precedes the filing and by how much.

## 3. Steps, with the components each one needs

### Step 0. Infrastructure

Docker Compose with four services: PostgreSQL, Redis, a Celery worker and FastAPI (C-07, C-08). CPU only at first. Secrets such as the SEC contact and API keys come from environment variables, never the repository (C-10).

Components: `docker-compose.yml`, one image for the app, a `.env.example` without values, migrations.

### Step 1. Ingestion

One Celery task per source, each with retries, rate limits and a raw-response log.

| Data | Source | Notes |
|---|---|---|
| Call transcripts | Hugging Face `kurry/sp500_earnings_transcripts` | 33,362 rows, 685 symbols, 2005 to May 2025 (card figures). The card says MIT and also "for research and educational use only". Origin unnamed. Some rows have empty `content`. Not for the public demo (Data 4A.1). |
| Forward transcripts | Alpha Vantage, free key | From June 2025. 25 requests a day. |
| Actual EPS, fundamentals | SEC EDGAR XBRL company facts | No key. Maximum 10 requests a second. A User-Agent with a contact is required. Bulk files `companyfacts.zip` and `submissions.zip` exist and are recompiled nightly. |
| Announcement time | EDGAR 8-K Item 2.02 | See section 2. |
| Prices | yfinance | Personal use only. Dividend-adjusted by default (PX-03). |
| Membership, sector | See section 4. | |
| Consensus | yfinance snapshots, forward only | Check set, not the label (LB-07, LB-08). Start in week one (SR-10). |

Components: a client per source, a user-agent setting, a retry and backoff helper, a raw-payload table or folder for audit.

### Step 2. Storage

PostgreSQL holds raw and derived data. The key rule is that every row carries the date it became knowable. Entities already named in the product requirements: TickerHistory, EarningsEvent (with transcript, information and announcement dates, `announcement_time_utc`), EstimateSnapshot (append only), SectorAssignment, SectorBenchmark and ModelVersion. Also needed: transcripts, a per-sentence table with each feature score, fundamentals and prices.

The per-sentence table matters most. The agent later retrieves evidence by plain SQL over it (C-11).

### Step 3. Preparation

1. **Identify the event.** Link a transcript to a company, fiscal quarter and announcement, using the SEC CIK as the permanent identifier (decision C-19) so ticker changes do not break history (IM-03, DV-06, FD-04). One transcript per event; the earliest first publication wins (TX-05).
2. **Convert times.** Announcement times go to UTC and are mapped to the right trading day. A release after the close belongs to the next session (DV-07).
3. **Split the call** into prepared remarks and Q&A, and label speakers where possible (TX-03, TX-06). Target at least 95% correct boundaries on 50 hand-checked calls.
4. **Split into sentences** with spaCy.
5. **Build the label.** Time-series SUE: this quarter's diluted EPS minus the same quarter a year earlier, divided by the standard deviation of the previous 8 seasonal differences, using first-filed values and split-adjusted shares (LB-01 to LB-05). Fourth-quarter EPS is derived and flagged (LB-03). Beat, in-line and miss thresholds are set on 2015 to 2021 only and then frozen (LB-06, D-23). This label route is pending the supervisor (D-01).
6. **Run the date gates.** GATE-1 to GATE-5 as tests that fail the build.

### Step 4. Feature engineering

All features are in FR-24. Each has a source tag and an as-of rule. How each is computed is in the [Feature Engineering requirements](../requirements/feature-engineering-requirements.md). Storage rules are in the [Database requirements](../requirements/database-requirements.md), the agent in the [Explanation Agent requirements](../requirements/explanation-agent-requirements.md) and the dashboard in the [Frontend requirements](../requirements/frontend-requirements.md). These four documents are drafts until decision D-40 is approved.

- **Text (per sentence, then per call):** FinBERT positive, negative and neutral (FR-16); hedge-word rate and negation (FR-17); Q&A sentiment delta and Q&A-only rates (FR-15); sentiment trajectory; guidance ratio; sentiment surprise against the trailing four calls (FR-18).
- **Hedge list:** the Loughran and McDonald uncertainty word list (C-14).
- **Tabular:** prior four-quarter surprise trend, revenue growth, gross and operating margin from the latest filing before the cutoff (FD-02), surprise dispersion, three-month price momentum (PX-02).
- **Sector context (extension):** peer mean SUE and peer count, only if sector history exists (SRS-08).

Output: one row per event in the feature matrix, tagged with a feature-set version. Components: a FinBERT runner (batched, CPU), a spaCy pipeline, the word lists, a feature registry that records source tag and as-of rule.

### Step 5. Modelling and evaluation

- Two XGBoost models: tabular-only baseline and full model with text features.
- Split by time: train 2015 to 2021, validate 2022, test 2023 to 2024, no shuffling across years. The test set is read once and the code enforces it (GATE-4, FR-03).
- Metrics: F1, Brier score, precision on the 20% most confident predictions, with confidence intervals. SHAP for global and per-prediction importance.
- Extra checks: the FinBERT pretraining-cutoff comparison (D-22), a class-balance report per year, and, on the check set, agreement between the SUE label and the consensus label (LB-08).
- Output: a ModelVersion record per trained model, with data and feature-set versions.

### Step 6. Serving

FastAPI loads the model and reads stored features and predictions. Endpoints are in the Product Requirements: prediction lookup, explanation job, job status, health. Failure cases are explicit: no prior transcript (cold start), upstream API failure, unknown ticker (FR-01 and the edge-case requirement). Every prediction shows the as-of time of each input group (FR-22).

### Step 7. Explanation agent

1. Take the 2 to 3 highest-magnitude SHAP features of a stored prediction.
2. For each, run SQL over the per-sentence table to fetch the sentences that produced the score.
3. Optionally check a later 8-K (SSOT Section 7, step 3).
4. Send the evidence to one hosted LLM with a spend cap (C-09, D-27) and ask for a short rationale citing sentence identifiers.
5. Run the faithfulness harness: rank agreement and sign agreement with SHAP, and a check that every cited sentence exists in the source document. Reported on a held-out sample.

The agent only explains a decision already made. It does not touch features or training. Runs as a Celery job (FR-19).

### Step 8. Frontend

Streamlit (C-16). One page: ticker box, prediction card with class, probabilities and confidence, as-of times, key factors beside the explanation and its evidence, and the not-investment-advice notice. An evaluation page shows model against baseline.

### Step 9. Hardening and deployment

Local Docker build is the first target. Cloud Run, polish and the usability study come in January and February (C-07, C-13). The usability study needs ethics approval first (D-16).

## 4. Membership and sector sources (researched 16 November 2026)

### 4.1 Index membership

Why it matters: without dated membership the universe is today's constituents, which flatters results (survivorship bias). Data IM-01 to IM-03 and TX-07 set the checks.

| Candidate | What it is | Strengths | Limits | Verdict |
|---|---|---|---|---|
| `fja05680/sp500` (GitHub) | Dated snapshots of S&P 500 members since 1996, plus a ticker start and end file | MIT licence. Includes companies that left. | Built from the book download *Trading Evolved* (1996 to 2019), then Wikipedia changes. The author says Wikipedia shows only "Selected Changes", some early symbols may be missing, and the list is not always 500 names. Keyed by ticker, so renames need handling (IM-03). | Primary candidate. |
| `Johnbrick123/sp500-data` (GitHub) | Membership intervals, daily prices for current and delisted names, rename list | Free. Survivorship-free by design. Refreshed on weekdays. | No licence stated. Pre-1996 data rests on CRSP. Prices come from Yahoo and Tiingo. The README's own limits include yfinance being an unofficial scraper. | Cross-check and development only until the licence is clear. |
| Wikipedia "Selected changes" table | Current list plus changes | Free and the base for both repos above | Incomplete by the editors' own labelling. The Johnbrick README says the live page dropped its change table in mid-2026, so scraping it may now fail. That claim is from the README and was not tested. | Not the primary route. |
| EODHD S&P constituents add-on | From S&P Global, dated additions and removals | Good quality | £29.99 a month. Personal, non-commercial terms. | Paid. Only if the free route fails IM-01. |
| CRSP via WRDS | Full constituent history | Best quality | Eligibility at Manchester unverified (D-21). | Optional upgrade. |

Recommended route: build the universe from `fja05680/sp500`, test it against IM-01 (company count within 5 of the published count at sampled year-ends) and IM-02 (removed companies present each year), and use `sp500-data` as a second opinion. Disagreements are listed, not hidden. Logged as D-32.

### 4.2 Sector history (and is it essential?)

Sector-relative scoring is an extension beyond the proposal, kept by your decision C-02 and tagged Should, so it is dropped first if a milestone slips. It is not part of the core objectives. If it fails, the core project is unaffected (SRS-14 switches it off).

What was found:

| Option | Finding |
|---|---|
| Free point-in-time GICS history | Not found. The searches returned current-only lists (for example Kaggle and `datasets/s-and-p-500-companies`). The official history from S&P Global is a paid product, listed on the Databricks Marketplace as covering active and inactive classifications from 1985. |
| GICS history inside the membership repos | No. Neither `fja05680/sp500` nor `Johnbrick123/sp500-data` mentions sectors. |
| Ken French industry groups (12 and 48) | Free, widely used, defined from four-digit SIC codes, with downloadable definition files (`Siccodes12.zip`, `Siccodes48.zip`). French assigns each stock each June from its SIC code at that time, which is point-in-time. His SIC inputs come from Compustat and CRSP, which are paid, so his assignments cannot be reproduced for free. Only the SIC-to-industry mapping is free. The zip contents were not opened. |
| SIC code from SEC EDGAR | The only free route with a plausible dated history. The submissions API page does not mention a SIC field, and the pages that would say whether filing headers carry SIC as at the filing date returned 404. It is unverified. From general knowledge, EDGAR filing headers include a SIC line, but that has not been checked here. |

Proposed route (D-20, pending John):
1. Run a spike on 20 companies: download old and new 10-K or 8-K headers and see whether SIC is present and whether it differs across dates.
2. If SIC is dated per filing, map it to Fama-French 12 groups and use those as the sector level. This needs wording changes in Product SRS-02, SRS-10 and the SectorAssignment entity, which now say GICS. John approves any such change.
3. If not, sector scoring is switched off under SRS-14, and the project proceeds without it.

Known limit of the SIC route: SIC is coarser and older than GICS, so peer groups differ from what finance practice calls a sector. State it in the dissertation.

## 5. Working defaults (not yet requirements)

| Item | Default | Source |
|---|---|---|
| Company subset for December | 100 companies, about 20 of them removed from the index, widened if time allows. | Decision C-18. |
| Prediction lookup | Read a stored prediction for the latest event. No live transcript scoring. | C-15 |
| Frontend | Streamlit | C-16 |
| Hedge words | Loughran and McDonald uncertainty list | C-14 |

## 6. What this file changes in the other documents

Nothing in the SSOT or the requirements has been edited. Changes made:
- Decision log: new closed decisions C-14 to C-16, new open decisions D-31 and D-32, and a research note added to D-18 and D-20. (D-31 was closed on 18 November 2026 as C-17.)
- Logbook: one entry.

One proposed addition for John to approve: a row in the SSOT document map for `architecture/pipeline.md`. Only the owner edits the SSOT.

## 7. Still open

- D-33: approve the requirement wording that follows from decision C-17 (T0 headline, T1 secondary).
- D-34: approve the negation and forward-guidance definitions.
- D-20: approve the SIC spike, and approve the wording change if it works.
- D-32: approve `fja05680/sp500` as the membership route.
- Set `SEC_USER_AGENT` so the EDGAR spikes (EPS, announcement time, SIC) can run.
- The December company subset is decided (C-18). FinBERT speed on this PC is still unmeasured.
