# Single Source of Truth (SSOT)

**Project:** LLM-Powered Earnings Surprise Predictor
**Owner:** John. Only the owner edits this file.
**Status:** DRAFT for the owner's approval. Drafted by Claude from the Third Year Project Proposal (2026-27) and the owner's instructions in this working session. Once the owner approves it, it is frozen.

## Rules for this file

1. **Only the owner changes this file.** Claude does not edit it. If Claude thinks a change is needed, Claude asks for permission first and shows the exact wording it proposes.
2. **This file wins.** Every other document (requirements, deck, decision log, notes) must agree with it. If any document disagrees, that document is corrected, not this file.
3. **Drift check.** Before and after any change to the requirements or deck, Claude compares the change with this file. If the change drifts from it, Claude goes back to this file and corrects the other document, or asks the owner to decide.
4. **Open items live in the decision log**, not here. Anything not yet decided by the owner is in [decision-log.md](decision-log.md).
5. **This file holds only what is fixed:** the proposal's commitments and the owner's decisions. Detailed requirements live in the requirement documents (Section 12).

## 1. Identity

- Title: LLM-Powered Earnings Surprise Predictor. A distributed ML systems project: event-driven data pipelines, NLP feature engineering and explainable ensemble models applied to financial text.
- University of Manchester, Department of Computer Science, BSc Computer Science, 2026-27. Supervisor: Professor Goodacre.
- The contribution is the distributed systems design and the ML methodology. Finance is the test domain.

## 2. Research question

Does incorporating NLP-derived features from unstructured text (FinBERT sentiment scores, linguistic uncertainty signals) measurably improve classification accuracy over a tabular-only baseline, when evaluated under a strict temporal train/test split that eliminates lookahead bias?

A negative result, where NLP adds no signal, is a valid finding.

## 3. Objectives

**Core (committed):**
1. A data pipeline that ingests earnings call transcripts and financial data and stores them in a structured PostgreSQL schema.
2. NLP features from transcripts: a pre-trained financial sentiment model and linguistic uncertainty detection (hedge-word frequency, negation patterns).
3. An XGBoost ensemble over text and tabular features, evaluated against a tabular-only baseline with strict temporal splits.
4. A FastAPI backend serving predictions on demand with feature-importance explanations.
5. An agentic explanation layer: a single-pass LLM agent that takes a prediction and its SHAP attributions, picks the most influential features, retrieves the transcript passages behind each, and writes a rationale grounded in that evidence. It is judged on faithfulness to the SHAP values, not on fluency.
6. A lightweight frontend dashboard: ticker input, beat/miss prediction with confidence, and key explanatory factors.

**Stretch (only after the core is done):** fine-tune a model on financial transcripts; five-class output (large beat, small beat, in-line, small miss, large miss); historical backtesting (P&L). A critic-and-revise loop for the agent is added only if the core pipeline finishes early.

## 3A. Extensions added by the owner

Extensions are allowed. Scope and capacity must stay at the proposal's level, so every extension is tagged Should or Could and is dropped first if a milestone slips.

- **Sector-relative scoring** is kept (owner decision, 14 November 2026). It is an extension beyond the proposal. It is broken into its own set of requirements (Product Requirements Section 4A).

## 4. Data and label

- Target corpus: S&P 500 companies, 2015-2024, about 4,000 to 5,000 earnings events, with index membership as of each date.
- **Label (proposal definition):** standardised unexpected earnings, SUE = (Actual EPS - Mean analyst estimate) / Standard deviation of analyst estimates. Beat and miss use a fixed SUE threshold (for example above +1 and below -1), with in-line as the middle band. The exact cutoff is tuned during exploratory analysis to keep classes reasonably balanced.
- Three dates are stored separately for every event: transcript date, estimate-publication date and announcement date, so lookahead can be checked directly.
- **Owner decision, 14 November 2026:** the primary data route must be free. Sources from any country are acceptable (not only Manchester's). A forward-only design is acceptable if the alternatives are worse.
- **Working label route (pending supervisor approval):** where licensed point-in-time analyst consensus is not available, the historical label is a time-series SUE built from actual EPS (the Bernard and Thomas approach), with analyst consensus captured forward as a check. The owner agreed to proceed on 14 November 2026. It changes the proposal's label, so it stays marked pending until the supervisor agrees. See decision D-01.

## 5. Features (from the proposal)

**Text, per transcript:** FinBERT mean positive, negative and neutral scores; sentiment trajectory (first half against second half); uncertainty score (hedge words divided by word count); forward-guidance ratio; Q&A sentiment delta; sentiment surprise (z-score against the company's trailing four-quarter average); Q&A-only sentiment and hedge-word rate.

**Tabular, per company-quarter:** prior four-quarter EPS surprise trend; revenue growth; gross and operating margin; surprise dispersion (the standard deviation of the prior 8 seasonal EPS differences on the time-series label route; analyst consensus dispersion where a consensus standard deviation exists); price momentum (three-month return before the announcement). Question counts and negation frequency are also computed (proposal Section 4.1).

## 6. Model, split and evaluation

- Two XGBoost models: tabular-only baseline, and the full model with NLP features.
- Split: train 2015-2021, validation 2022, held-out test 2023-2024, no shuffling across years. The test set is read once.
- Metrics: F1, calibration (Brier score), precision at top 20% most confident predictions. SHAP for global importance and per-prediction explanations.
- Lookahead checks: the three date columns; and a sanity check that compares FinBERT scores near its pretraining cutoff with scores well after it, looking for an accuracy jump at the boundary.
- Explanation layer evaluation (Ichmoukhamedov et al.): rank agreement, sign agreement, and a check that every cited transcript excerpt exists in the source document. Rates are reported on a held-out sample.

## 7. Agent design (proposal Section 4.3)

1. Select the 2 to 3 highest-magnitude SHAP features.
2. For each, retrieve the transcript sentences responsible.
3. Optionally check corroborating or contradicting public information, such as a later 8-K filing.
4. Synthesise a short rationale that cites the retrieved evidence.

The agent only explains a decision the model has already made. It does not touch feature selection or training.

## 8. Technology stack

| Layer | Technology |
|---|---|
| Data ingestion | Python, requests, SEC EDGAR API, yfinance |
| Database | PostgreSQL |
| Task queue | Celery + Redis |
| Backend API | FastAPI |
| Text ML | FinBERT (HuggingFace Transformers) |
| NLP features | spaCy |
| Tabular ML | XGBoost, scikit-learn |
| Explainability | SHAP |
| Frontend | Streamlit |
| Infrastructure | Docker, GCP Cloud Run |

## 9. Milestones

| # | Milestone | Deliverable |
|---|---|---|
| 1 | Data pipeline: ingestion, PostgreSQL schema, Celery workers | Running pipeline, populated database with 2+ years of data |
| 2 | Feature engineering: FinBERT, spaCy, tabular features | Feature matrix in the database, EDA notebook |
| 3 | Model development: baseline, full model, temporal evaluation, SHAP | Trained models, evaluation report comparing baseline and full |
| 4 | Backend: prediction, SHAP explanation and history endpoints | Deployed API with documented endpoints |
| 5 | Frontend: ticker search, prediction card, feature chart | Working web UI demo |
| 6 | Agentic explanation layer with retrieval tools and faithfulness harness | Working agent endpoint; faithfulness rate reported on held-out predictions |
| 7 | Write-up | Final dissertation draft |

## 10. Evaluation criteria

1. Does the NLP-augmented model beat the tabular baseline on F1 and other metrics on the held-out test set?
2. Is the temporal split implemented correctly, with no lookahead bias?
3. Are SHAP explanations consistent with domain knowledge (for example, high uncertainty language correlates with worse outcomes)?
4. Does the system handle edge cases: no transcript, API failures, cold-start tickers?
5. Is the frontend usable, and does it surface the explanation beside the prediction?
6. Is the explanation layer faithful to the SHAP attributions, not just fluent?

## 11. Capacity and ethics

- Capacity: 15 to 20 hours a week (planning notes). Planned effort must fit, with a schedule buffer.
- Any user study (including the five-user usability test) needs university ethics approval before recruitment.
- Not investment advice. No buy, sell or hold language.

## 12. Document map

| Document | Holds | Does not hold |
|---|---|---|
| SSOT.md (this file) | Fixed project truth | Detailed requirements, open items |
| decision-log.md | Open and closed decisions, pending edits to the proposal, notes and deck | Requirements |
| requirements/market-requirements.md | Users, competitors, market needs (N), constraints | Functional, data or engineering requirements |
| requirements/product-requirements.md | What the system does: FR, SRS, EX, NFR, API, UI, PL, ML, TR, MR | Data sources, delivery process |
| requirements/data-requirements.md | Data sources, licences, label construction, verification and validation: SR, TX, AE, CE, LB, IM, SEC, PX, FD, DV, VL, GS | Product behaviour |
| requirements/project-wide-requirements.md | Delivery, assessment, supervision, engineering, security, ethics, operations, LLM operations, documentation: ASM, PD, SS, SC, EQ, SP, ET, OR, AI, DO | Product behaviour |
| requirements/README.md | Index, ID registry, withdrawn IDs | Requirements |
| requirements/proposal-drift-review.md | Comparison of the documents with this file | Requirements |
| architecture/earnings-predictor-architecture.pptx | Architecture and workflow diagrams | Requirements |
| architecture/pipeline.md | Step-by-step pipeline, components per step, source research summaries | Requirements |
| adr/ | Architecture decision records, one file per decision | Requirements |

A requirement is defined in exactly one document. Other documents cite its ID.
