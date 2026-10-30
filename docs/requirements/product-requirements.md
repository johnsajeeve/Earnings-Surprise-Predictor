# Product Requirements: LLM-Powered Earnings Surprise Predictor

Derived from the Third Year Project Proposal (2026-27), the Market Requirements document (26 October 2026), and the project design notes. Updated 26 October 2026.

## 1. Problem Statement

Quantitative users who want to use earnings call transcripts as a signal have no tool that does three things together: returns a beat/miss prediction for a ticker, explains that prediction using evidence from the transcript itself, and shows that the historical performance is free of lookahead and selection bias.

Existing products cover parts of this. StarMine forecasts surprises from analyst estimates. AlphaSense summarises calls and scores sentiment. Academic systems predict beat/miss from transcripts but cannot be queried. The gap this product fills is the combination, as described in Section 3 of the Market Requirements.

**Evidence.** The academic baseline in the proposal reports an AUC around 0.67 for XGBoost under a chronological split (SAE-FiRE, 2025). The proposal's own explanation-faithfulness research (Ichmoukhamedov et al.) shows that fluent explanations can cite factors the model never used. Both points justify building an evaluation harness alongside the prediction.

## 2. Goals and Non-Goals

### 2.1 Goals

| ID | Goal | Measured by |
|---|---|---|
| G1 | Produce a beat, in-line or miss prediction for a ticker with a calibrated confidence. | Brier score, precision at top 20% (Section 15). |
| G2 | Show a text-augmented model against a tabular-only baseline on the same test set. | F1 and AUC difference on 2023-2024 held-out data. |
| G3 | Explain each prediction with features and transcript sentences that can be checked. | Rank agreement, sign agreement and citation verification rate. |
| G4 | Prevent lookahead and survivorship bias from entering training or evaluation. | Automated test suite passes; FR-03, FR-14 and FR-15 hold. |
| G5 | Serve predictions through an API and a dashboard a user can run without setup. | Deployed endpoint and dashboard; usability test (Section 15). |
| G6 | Score each prediction relative to its sector, not only in absolute terms. | FR-12 acceptance criteria pass; share of predictions with sufficient peers reported. |

### 2.2 Non-Goals

These are out of scope for this version. Each one is excluded on purpose, and the reason is given.

| ID | Non-goal | Reason |
|---|---|---|
| NG1 | Live or mid-call predictions. | Needs a licensed real-time transcript feed that is not in the data plan (DR-03, DR-05 in the Market Requirements). |
| NG2 | Trade execution or broker integration. | Adds regulatory scope with no requirement in the market analysis. |
| NG3 | Insider trading or options data triangulation. | Data integration cost. Not needed for G1 to G6. |
| NG4 | Public user accounts, personalisation or saved watchlists. | Demo authentication only, as the proposal states. |
| NG5 | Investment advice or any claim that the output should be traded. | Not an advisory product. Notice shown on every output (FR-08). |

## 3. Users and Journeys

Primary persona: quantitative researcher or independent analyst with point-in-time consensus data access (Section 2 of the Market Requirements).

**Journey J1: Look up a ticker.** The user enters a ticker and sees the latest prediction, its confidence, the sector-relative score, and the top three features that drove it.

**Journey J2: Check an explanation.** The user opens the explanation for a prediction and sees each claim with its faithfulness label, and the transcript sentence it cites. The user can open the source sentence in context.

**Journey J3: Review historical performance.** The user opens the evaluation page and compares the full model with the tabular baseline and the consensus-revision baseline, including calibration, the evidence base and per-date results. The user can see which predictions were made before the announcement date.

**Journey J4: Look up history.** The user selects a ticker and date range and sees past predictions alongside the realised outcome.

## 4. Functional Requirements

Each requirement is written as a user-visible behaviour or system behaviour with acceptance criteria. Acceptance criteria state the starting condition, the action and the expected result.

### FR-01: Prediction lookup (J1)

**Requirement.** Given a ticker, the system returns the class, class probabilities, confidence and top three features.

**Acceptance criteria.**
- Given a ticker with a stored transcript and feature vector, when the user submits the ticker, then the prediction card shows the class, the three class probabilities summing to 1.00 within rounding, a confidence value, and three features.
- Given the same ticker submitted twice without new data, then the same prediction is returned both times.
- Given a ticker with no transcript, then the card shows "No transcript available for this ticker" and no class.

### FR-02: Date fields on every event (J3)

**Requirement.** Each earnings event stores transcript date, estimate-publication date and announcement date as separate fields.

**Acceptance criteria.**
- Given any event in the database, when its record is read, then all three date fields are present and non-null, or the event is marked incomplete.
- Given a transcript dated after its announcement, then the event is flagged for review and excluded from training.

### FR-03: Temporal split enforcement (J3)

**Requirement.** Training uses 2015-2021, validation uses 2022, and test uses 2023-2024. No row dated after a split's cutoff enters that split's training data.

**Acceptance criteria.**
- Given the training pipeline runs, when any training row has a date after 31 December 2021, then the pipeline fails with an error naming the row.
- Given the test suite runs, then a test confirms the split boundaries against the feature matrix.

### FR-04: Feature attribution (J1, J2)

**Requirement.** Each prediction returns the top three SHAP features by absolute value, with signed contribution toward beat or miss.

**Acceptance criteria.**
- Given a prediction, when the explanation is requested, then three features are returned in descending absolute SHAP value.
- Given a feature with a positive SHAP value for miss, then its direction is labelled "toward miss".

### FR-05: Citation verification (J2)

**Requirement.** Every transcript excerpt cited by the explanation agent is checked for exact presence in the source document.

**Acceptance criteria.**
- Given an explanation citing a sentence, when the source transcript is checked, then the sentence is present verbatim, or the citation is removed and the explanation is marked "partially verified".
- Given a citation that cannot be found, then the failure is logged with the prediction identifier.

### FR-06: Baseline comparison (J3)

**Requirement.** The evaluation page shows the tabular-only baseline, the consensus-revision baseline and the full model on the same test set.

**Acceptance criteria.**
- Given the evaluation page loads, then all three models show F1, AUC, Brier score and precision at top 20%, computed on the same rows.
- Given the full model does not outperform a baseline, then the page states this without hiding either result.

### FR-07: Explicit edge-case handling (J1)

**Requirement.** The system handles missing transcripts, upstream API failures and cold-start tickers explicitly.

**Acceptance criteria.**
- Given an upstream API returns an error, then the response has status 503, a message naming the failed source, and no partial prediction.
- Given a ticker with fewer than four prior quarters of history, then the prediction is returned with the label "Limited history" and the trailing-average feature is marked as unavailable.

### FR-08: Disclaimer (all journeys)

**Requirement.** Every prediction and explanation displays a notice that it is not investment advice.

**Acceptance criteria.**
- Given any prediction or explanation is shown, then the notice appears in the same view, not behind a link.

### FR-09: History lookup (J4)

**Requirement.** The user selects a ticker and date range and sees past predictions with the realised outcome.

**Acceptance criteria.**
- Given a ticker and a range covering four events, then four rows are returned, each showing the prediction date, class, confidence and realised outcome.
- Given a prediction whose outcome is not yet known, then the outcome field shows "Pending".

### FR-10: Calibration display (J3)

**Requirement.** The evaluation page shows calibration and precision on the most confident predictions.

**Acceptance criteria.**
- Given the evaluation page, then a calibration plot and the precision at top 20% value are displayed for the test set.

### FR-11: Reproducibility record (J3)

**Requirement.** Every stored prediction records the model version and feature-set version.

**Acceptance criteria.**
- Given a prediction is stored, then both version identifiers are present and match a registered model artefact.

### FR-12: Sector-relative score (J1, J3)

**Requirement.** Each prediction includes a sector-relative score: the event's standardised unexpected earnings (SUE) minus the mean SUE of S&P 500 peers in the same GICS sector and quarter, divided by the standard deviation of those peer SUE values. It shows how far a company beat or missed its sector, not only the market as a whole.

**Acceptance criteria.**
- Given a prediction, when the prediction card is shown, then the sector-relative score appears with the sector name and the number of peer events used.
- Given a sector and quarter with fewer than five peer events, then the score is shown as "Insufficient peers" and no numeric value is displayed.
- Given a prediction for an event announced on date D, when the sector statistics are computed, then only peer events announced on or before D are used.
- Given the training pipeline runs, then sector statistics for training rows are computed only from training-window events (FR-03 applies).

### FR-13: Idempotent transcript ingestion

**Requirement.** Re-running an ingestion job does not create duplicate transcripts, including after a partial failure.

**Acceptance criteria.**
- Given the same filing is ingested twice, then exactly one transcript row exists for it.
- Given an ingestion job fails halfway and is re-run, then the final row count equals the count of a clean run.

### FR-14: Estimate snapshots kept as captured

**Requirement.** Consensus estimates are stored as dated snapshots. Earlier snapshots are never overwritten. A prediction uses only snapshots captured before the announcement date.

**Acceptance criteria.**
- Given a new consensus estimate arrives for an event, then a new snapshot row is added with its capture timestamp and the earlier snapshot is unchanged.
- Given a prediction for an event announced on date D, then any snapshot captured after D is excluded from its inputs.

### FR-15: Prepared remarks and Q&A segmentation

**Requirement.** Each transcript is split into prepared remarks and the Q&A section. Q&A features are computed only from the Q&A section.

**Acceptance criteria.**
- Given a transcript with a recognised Q&A marker, then prepared and Q&A sections are stored separately.
- Given no Q&A marker is found, then the event is flagged "Segmentation failed" and the Q&A features are stored as unavailable, not as zero.

### FR-16: Sentence-level sentiment scoring

**Requirement.** FinBERT scores are computed per sentence in batches and stored. A transcript is rescored only when the transcript or the FinBERT version changes.

**Acceptance criteria.**
- Given a transcript is already scored with the current FinBERT version, when the batch runs, then no sentence is rescored.
- Given the FinBERT version changes, then every affected transcript is rescored and the old scores are retained with their version.

### FR-17: Linguistic uncertainty features

**Requirement.** Hedge-word ratio and negation frequency are computed with spaCy, using the word lists defined in the feature set.

**Acceptance criteria.**
- Given a fixture transcript with a known hedge-word count, then the uncertainty score equals hedge count divided by word count to four decimal places.
- Given a transcript with zero words, then the feature is stored as unavailable and no division is attempted.

### FR-18: Sentiment surprise z-score

**Requirement.** The current quarter's sentiment is expressed as a z-score against the company's trailing four-quarter average.

**Acceptance criteria.**
- Given four prior quarters of scores, then the z-score equals (current minus the mean of the four) divided by their standard deviation.
- Given the standard deviation of the four prior quarters is zero, then the feature is stored as unavailable, not as infinity.
- Given fewer than four prior quarters, then the prediction carries the "Limited history" label (FR-07).

### FR-19: Asynchronous explanation

**Requirement.** An explanation request returns a job identifier immediately. The explanation is generated in the background.

**Acceptance criteria.**
- Given an explanation request, then the API returns a job identifier within 500 ms and the job status is pending.
- Given the job completes, then the status changes to complete and the explanation is retrievable by identifier.
- Given the job fails, then the failure reason is stored and returned with the status.

### FR-20: Ticker validation

**Requirement.** Tickers are validated before any lookup.

**Acceptance criteria.**
- Given a ticker not in the universe for any date in the dataset, then the response is 404 with the message "Ticker not in universe".
- Given a ticker with characters outside letters, digits, dot or hyphen, or longer than ten characters, then the response is 422 with the message "Invalid ticker format".

## 5. Non-Functional Requirements

Thresholds are proposed. They are to be agreed with the supervisor (Section 9 of the Market Requirements).

| ID | Area | Requirement | Threshold |
|---|---|---|---|
| NFR-01 | Latency | Cached prediction response time, 95th percentile. | Under 500 ms |
| NFR-02 | Latency | Full explanation response time, 95th percentile, from request to complete status. | Under 10 s, or returned as pending |
| NFR-03 | Freshness | New transcripts available after publication. | Within 24 hours |
| NFR-04 | Availability | Demo deployment uptime. | Best effort; no SLA |
| NFR-05 | Reproducibility | Retraining from a stored snapshot reproduces reported metrics. | Same to two decimal places |
| NFR-06 | Security | No secrets in source control. Data-licence keys in environment variables. | Checked in CI |
| NFR-07 | Accessibility | Dashboard meets WCAG 2.1 AA for colour contrast and keyboard navigation. | Automated check passes |
| NFR-08 | Responsiveness | Dashboard usable at 375 px width. | No horizontal scrolling on prediction card |
| NFR-09 | Batch throughput | Backfill of the full target corpus (4,000-5,000 events) on demo infrastructure. | Completes within 24 hours |
| NFR-10 | Test coverage | Line coverage on feature engineering, split logic and sector normalisation. | At least 80% |
| NFR-11 | Request logging | Every API request is logged with a request identifier, latency and status code. | 100% of requests |
| NFR-12 | Service metrics | Latency and error rate exposed for scraping. | Available at /metrics |

## 6. API Requirements

| ID | Requirement | Acceptance check |
|---|---|---|
| API-01 | The OpenAPI specification is generated from code and served with the API. | Specification validates and matches every endpoint in Section 13. |
| API-02 | All endpoints sit under the /v1 path prefix. | Requests to unversioned paths return 404. |
| API-03 | Every error response has the same shape: code, message and request identifier. | Contract test checks the shape for 404, 422, 401, 429 and 503. |
| API-04 | Prediction endpoints return the envelope: data, warnings array and model_version. | Contract test on each prediction endpoint. |
| API-05 | The history endpoint is paginated, with a default page size of 20 and a maximum of 100. | Request for 500 rows returns 100 with a next-page link. |
| API-06 | Every endpoint except /health requires a JWT. | Request without a token returns 401. |
| API-07 | Each client is rate limited, and a limited request returns 429 with a Retry-After header. | Load test exceeding the limit returns 429 with the header present. |

## 7. Data Pipeline Requirements

| ID | Requirement | Acceptance check |
|---|---|---|
| PL-01 | Scheduled ingestion jobs record start time, end time, status and row counts. | Each run produces a log row that can be queried. |
| PL-02 | Failed ingestion tasks retry up to three times with exponential backoff, then move to a dead-letter queue. | Injected failure produces three retries and one dead-letter entry. |
| PL-03 | Each ticker's latest transcript date is reported through /health. | Health response lists the date for a test ticker. |
| PL-04 | Events missing actual EPS or the estimate mean are rejected, and the reason is logged. | Fixture with a missing estimate is rejected with the logged reason. |
| PL-05 | Schema changes are made only through versioned migrations. | Migration history matches the deployed schema on a clean database. |
| PL-06 | Raw transcripts are stored unchanged. Cleaned text is stored in a separate column. | Hash of raw text is identical before and after cleaning. |

## 8. Machine Learning Pipeline Requirements

| ID | Requirement | Acceptance check |
|---|---|---|
| ML-01 | Random seeds are fixed and recorded for every training run. | Two runs with the same seed and snapshot produce identical predictions. |
| ML-02 | Hyperparameters are tuned on the 2022 validation set only. The 2023-2024 test set is read once, for final evaluation. | Access log shows test rows read only in the final evaluation job. |
| ML-03 | Each model artefact is saved with its version and a SHA-256 checksum. Loading verifies the checksum. | Altered artefact fails to load with a checksum error. |
| ML-04 | The SHAP explainer is built from the same artefact as the served model. | Explainer and model share the artefact identifier. |
| ML-05 | A training run writes its metrics report before the model is registered. | Registration fails if the report file is missing. |
| ML-06 | A model is promoted to serving only after the FR-06 comparison passes and a reviewer's sign-off is recorded. | Promotion step checks for the sign-off record. |

## 9. User Interface Requirements

| ID | Requirement | Acceptance check |
|---|---|---|
| UI-01 | Ticker search offers autocomplete from the universe. | Typing two letters shows matching tickers. |
| UI-02 | Every chart has a text alternative and a switch to a data table. | Automated accessibility check finds no chart without an alternative. |
| UI-03 | The explanation view shows the verification status beside each citation. | Each citation in the view has a visible status. |
| UI-04 | A sector comparison view shows the ticker's sector-relative score against its peers in the same quarter. | View lists every peer used in the calculation. |
| UI-05 | All controls can be reached by keyboard, with a visible focus indicator. | Keyboard-only walkthrough completes Journey J1. |

## 10. Operations Requirements

| ID | Requirement | Acceptance check |
|---|---|---|
| OP-01 | Secrets are read from environment variables or a secret manager. None appear in source control. | Secret scanner passes in CI. |
| OP-02 | Container images are built in CI with all dependencies pinned to exact versions. | Build fails if a dependency is unpinned. |
| OP-03 | The service can be rolled back to the previous revision within 10 minutes. | Rollback drill completed and timed during week 15. |

## 11. Data Model

| Entity | Key fields | Notes |
|---|---|---|
| Company | ticker, name, sector, index_membership_from, index_membership_to | Membership dates support DR-02. Sector history supports DR-06. |
| EarningsEvent | event_id, ticker, transcript_date, estimate_date, announcement_date, sue, label | FR-02. Label derived from SUE thresholds set during EDA. |
| EstimateSnapshot | snapshot_id, event_id, mean_estimate, std_estimate, captured_at | FR-14. Append-only. |
| Transcript | transcript_id, event_id, source_url, retrieved_at, raw_text, cleaned_text, raw_hash | PL-06, FR-05, DR-09. |
| TranscriptSection | section_id, transcript_id, kind (prepared or qa), text | FR-15. |
| FeatureVector | event_id, feature_set_version, features (JSON), computed_at | Tabular and text features in one row per event. |
| SectorBenchmark | sector, quarter, mean_sue, std_sue, peer_count, computed_as_of | FR-12. Stored with the as-of date so the no-lookahead criterion can be checked. |
| ModelVersion | model_version, trained_on_from, trained_on_to, metrics (JSON), artefact_path, checksum, seed | FR-11, ML-01, ML-03. |
| Prediction | prediction_id, ticker, event_id, model_version, class, probabilities, confidence, created_at | Realised outcome joined from EarningsEvent. |
| Explanation | explanation_id, prediction_id, features (JSON), citations (JSON), verification_status, job_status, created_at | FR-04, FR-05, FR-19. |
| ClaimLabel | claim_id, explanation_id, claim_text, label, reason | EX-02 in the Market Requirements. |
| IngestionRun | run_id, job_name, started_at, ended_at, status, row_counts | PL-01. |

## 12. Error States

| Condition | User sees | System does |
|---|---|---|
| No transcript for ticker | "No transcript available for this ticker." | Logs the request; no prediction stored. |
| Ticker not in universe | "Ticker not in universe." (404) | Logs the request. |
| Invalid ticker format | "Invalid ticker format." (422) | Rejects before lookup. |
| Upstream API failure | "Data source unavailable. Try again later." (503) | Retries on the next scheduled run; no partial prediction. |
| Rate limit exceeded | "Too many requests. Try again shortly." (429) | Returns Retry-After header. |
| Limited history | Prediction with "Limited history" label. | Marks trailing features as unavailable. |
| Segmentation failed | "Q&A analysis unavailable for this call." | Stores Q&A features as unavailable. |
| Citation not found | Explanation marked "partially verified". | Logs the failure with prediction identifier. |
| Explanation job failed | "Explanation could not be generated." | Stores the failure reason and returns it with the status. |
| Model artefact missing or checksum mismatch | "Service temporarily unavailable." (503) | Refuses to serve; raises an alert. |

## 13. API Surface

| Method | Path | Purpose | Requirement |
|---|---|---|---|
| GET | /v1/predictions/{ticker} | Latest prediction, top three features and sector-relative score. | FR-01, FR-04, FR-12, API-04 |
| GET | /v1/predictions/{ticker}/explanation | Explanation with citations and verification status. | FR-04, FR-05, FR-19 |
| POST | /v1/predictions/{ticker}/explanation/jobs | Starts an explanation job and returns the job identifier. | FR-19 |
| GET | /v1/jobs/{job_id} | Status of an explanation job. | FR-19 |
| GET | /v1/predictions/{ticker}/history?from=&to=&page= | Past predictions with outcomes. | FR-09, API-05 |
| GET | /v1/evaluation/metrics?model=full\|tabular\|consensus | Test-set metrics for a model version. | FR-06, FR-10 |
| GET | /health | Service, data freshness and ingestion status. | NFR-03, PL-03 |
| GET | /metrics | Service metrics for scraping. | NFR-12 |

## 14. Screens

| Screen | Contents | Journey |
|---|---|---|
| Ticker search | Input field with autocomplete, submit, recent lookups. | J1 |
| Prediction card | Class, probabilities, confidence, sector-relative score with peer count, not-investment-advice notice, link to explanation. | J1 |
| Feature chart | Horizontal bars for top three SHAP features, coloured by direction, with a data table alternative. | J1, J2 |
| Explanation view | Each claim, its faithfulness label, the cited sentence and its verification status. | J2 |
| Sector comparison | Ticker's sector-relative score against peers in the same quarter, with the peer list. | J1 |
| History table | Date, class, confidence, realised outcome, pending state, pagination. | J4 |
| Evaluation page | Three-model comparison table, calibration plot, precision at top 20%, evidence base, limitations notice. | J3 |

## 15. Success Metrics

| Metric | Target | Counter-metric | Why the counter-metric matters |
|---|---|---|---|
| AUC on 2023-2024 test set | At least match SAE-FiRE baseline (about 0.67) | Brier score must not worsen against the baseline | A higher AUC with poor calibration misleads users about confidence. |
| Precision at top 20% | Reported; no target until baseline known | Coverage: share of events receiving a prediction | High precision on a small subset is not useful if most events are excluded. |
| Sector-relative score coverage (FR-12) | At least 90% of predictions show a numeric score | Share showing "Insufficient peers" | A score that is hidden for most events is not useful, so coverage must be reported beside the score. |
| Citation verification rate | 100% verified or flagged | Explanation length | Verifying shorter explanations is easier and could hide weak evidence. |
| Rank and sign agreement | Reported on held-out sample | Number of features discussed per explanation | Discussing more features raises agreement chances without raising faithfulness. |
| Claim faithfulness rate (EX-02) | Reported per explanation | Human agreement with automated labels (EX-05) | Automated labels that humans disagree with are not evidence of faithfulness. |
| Usability (five test users) | All complete J1 without help | Time to complete J2 | Fast completion can mean users skipped the explanation. |

## 16. Milestones

Aligned to Section 6 of the proposal. Weeks are a guide, not a commitment.

| Weeks | Milestone | Done when |
|---|---|---|
| 1-2 | Requirements, data verification (DR-01, DR-03, DR-05, DR-06, DR-10) | Data sources confirmed in writing; this document agreed. |
| 3-5 | Data pipeline and feature engineering | Feature matrix stored; EDA notebook complete; PL-01 to PL-06, FR-02, FR-03, FR-13 to FR-18 tests pass. |
| 6-7 | Model development and baseline comparison | Baseline, consensus and full models trained; ML-01, ML-02, ML-05 pass; evaluation page data available (FR-06). |
| 8-9 | Backend endpoints | Section 13 endpoints deployed; API-01 to API-07, FR-01, FR-04, FR-07, FR-09, FR-12, FR-20 pass. |
| 10-11 | Explanation layer and citation verification | FR-05, FR-19, EX checks pass on test set; faithfulness rates reported. |
| 12-13 | Frontend and usability testing | Section 14 screens live; UI-01 to UI-05 pass; five-user test complete. |
| 14-15 | Hardening and deployment | NFR-01 to NFR-12 measured and recorded; OP-01 to OP-03 pass. |
| 16 | Write-up and presentation | Dissertation draft; demo recorded. |

## 17. Dependencies

| Dependency | Needed for | Status |
|---|---|---|
| Point-in-time consensus estimates (snapshots) | FR-01 (SUE labels), FR-03, FR-14 | Unverified (DR-01, DR-10) |
| Transcript source with licence for demo | FR-01, FR-05, FR-15 | Unverified (DR-03, DR-05) |
| Index membership history | FR-03 universe, FR-12 peer set | Unverified (DR-02) |
| Point-in-time GICS sector history | FR-12 | Unverified (DR-06) |
| FinBERT model weights | FR-16 | Available (HuggingFace) |
| GCP project for deployment | NFR-01, NFR-04, OP-03 | To be set up |

## 18. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Point-in-time estimates unavailable | High | High | Confirm in week 1. Fall back to a documented, reduced label definition with the limitation stated. |
| Transcript source unavailable or unlicensed | High | High | Check library access. Use a public open dataset with licence checked, or restrict the demo to a historical slice. |
| Sector history wrong for past quarters | Medium | High | Use the point-in-time sector source (DR-06). Report the sector-relative score as unavailable where history is missing. |
| FinBERT pretraining overlaps test period | Medium | High | Sanity check at pretraining boundary (proposal 5.4). Report result either way. |
| Explanation agent produces unfaithful narratives | Medium | Medium | FR-05, EX-03, EX-04 and rank and sign agreement metrics. Report the rate. |
| Test set read during tuning | Low | High | ML-02 access log. Any read outside final evaluation invalidates the headline result. |
| Feature drift after release | Medium | Medium | Monitor feature distributions and top-feature rank order against the training baseline. |
| Scope creep from design notes | High | Medium | Non-goals in Section 2.2 are fixed for this version. |
| Effort exceeds 15-20 hours per week | Medium | High | Drop items in proposal stretch objectives first. |

## 19. Open Questions

| Question | Owner | Needed by |
|---|---|---|
| Are point-in-time consensus estimates accessible through the university? | John, with Professor Goodacre | Week 1 |
| Which transcript source is licensed for the demo? | John | Week 1 |
| Is point-in-time GICS sector history available? | John | Week 1 |
| Are the NFR thresholds in Section 5 acceptable to the supervisor? | John, with Professor Goodacre | Week 2 |
| Is the explanation layer or the temporal evaluation the headline contribution? | John, with Professor Goodacre | Week 2 |
| Who performs the independent review in ML-06? | John, with Professor Goodacre | Week 2 |
| What is the SUE threshold for beat and miss? | John, from EDA | Week 4 |

## 20. Sources Checked

- Plannotator, product requirements document guidance: https://docs.plannotator.ai/learn/planning/what-is-a-product-requirements-document
- Amazon SageMaker Model Monitor, arXiv:2111.13657: https://arxiv.org/pdf/2111.13657
- Arize Phoenix, faithfulness evaluator: https://www.arize.com/docs/phoenix/evaluation/pre-built-metrics/faithfulness
- Harvey, C. and Liu, Y., "Backtesting", Duke University working paper: https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF
- SR 11-7 model risk management summary: https://www.magicmirrorsecurity.com/blog/sr-11-7-model-risk-management-guidance-explained
- Project proposal, Third Year Project Proposal (2026-27), as uploaded.
- Market Requirements document, dated 26 October 2026, saved to project as claude/market-requirements.md.

Points marked "to be set up" or "unverified" have not been confirmed against primary sources. The SR 11-7 and Harvey and Liu sources were read through summaries, not the primary texts.
