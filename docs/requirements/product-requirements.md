# Product Requirements: LLM-Powered Earnings Surprise Predictor

Derived from the Third Year Project Proposal (2026-27), the Market Requirements document (26 October 2026), and the project design notes. Updated 26 October 2026. Revised 14 November 2026 to remove contradictions with the proposal, add the proposal items that had no requirement, add priorities, and break sector-relative scoring into its parts (Section 4A). The review behind these changes is in `proposal-drift-review.md`.

## 1. Problem Statement

**Framing.** As the proposal states (Sections 1 and 8), the contribution of this project is the distributed systems design and the ML methodology. Finance is the domain they are tested in. The user and market framing below is used to set testable behaviour. It does not change the contribution the dissertation claims.

Quantitative users who want to use earnings call transcripts as a signal have no tool that does three things together: returns a beat/miss prediction for a ticker, explains that prediction using evidence from the transcript itself, and shows that the historical performance is free of lookahead and selection bias.

Existing products cover parts of this. StarMine forecasts surprises from analyst estimates. AlphaSense summarises calls and scores sentiment. Academic systems predict beat/miss from transcripts but cannot be queried. The gap this product fills is the combination, as described in Section 3 of the Market Requirements.

**Evidence.** The academic baseline in the proposal reports an AUC around 0.67 for XGBoost on a binary beat/miss task under a chronological split (SAE-FiRE, 2025). The related work in the proposal shows that fluent explanations can cite factors the model never used (He and Martens, 2026), and Ichmoukhamedov et al. provide the rank and sign agreement metrics used to detect this. Both points justify building an evaluation harness alongside the prediction.

**Data note.** The proposal describes the corpus as public through SEC EDGAR. The Data Requirements (Section 3) show that transcripts and point-in-time consensus need licensed academic sources. The reason for the domain is unchanged: the label is measurable and the dates make lookahead testable. The change is logged as C14 in the Project-Wide Requirements.

## 2. Goals, Non-Goals and Stretch Objectives

### 2.1 Goals

| ID | Goal | Measured by |
|---|---|---|
| PG-1 | Produce a beat, in-line or miss prediction for a ticker with a calibrated confidence. | Brier score, precision at top 20% (Section 15). |
| PG-2 | Show a text-augmented model against a tabular-only baseline on the same test set. | F1 and AUC difference on 2023-2024 held-out data, with confidence intervals. A negative result is a valid outcome (Proposal 7). |
| PG-3 | Explain each prediction with features and transcript sentences that can be checked. | Rank agreement, sign agreement and citation verification rate. |
| PG-4 | Prevent lookahead and survivorship bias from entering training or evaluation. | FR-02, FR-03, FR-14 and SRS-04 hold, and the Data Requirements validation tests VL-01 to VL-05 pass. |
| PG-5 | Serve predictions through an API and a dashboard a user can run without setup. | Deployed endpoint and dashboard; usability test (Section 15). |
| PG-6 | Place each prediction in its sector context, without using information from after the announcement. | SRS-01 to SRS-14 pass; coverage reported (SRS-13). |

PG-1 to PG-5 come from the proposal. PG-6 is an extension added after the proposal (Market MFR-16). It is kept at Should priority and must not displace the proposal goals.

### 2.2 Non-Goals

These are out of scope for this version. Each one is excluded on purpose, and the reason is given.

| ID | Non-goal | Reason |
|---|---|---|
| NG1 | Live or mid-call predictions. | Needs a licensed real-time transcript feed that is not in the data plan (DR-03, DR-05 in the Market Requirements). |
| NG2 | Trade execution, broker integration, or a live P&L loop that feeds trading results back into the model. | Adds regulatory scope with no requirement in the market analysis. The historical P&L research measure (ST-02) is separate. |
| NG3 | Insider trading or options data triangulation. | Data integration cost. Not needed for PG-1 to PG-6. |
| NG4 | Public user accounts, personalisation or saved watchlists. | Demo authentication only (JWT, API-06). The proposal does not specify authentication; JWT is added for the security review (Project-Wide SP-02). |
| NG5 | Investment advice or any claim that the output should be traded. | Not an advisory product. Notice shown on every output (FR-08). |

### 2.3 Stretch Objectives

All stretch objectives are Could. They are built only after every Must requirement passes, and nothing else depends on them.

| ID | Stretch objective | Rule | Source |
|---|---|---|---|
| ST-01 | Five-class output: large beat, small beat, in-line, small miss, large miss. | Thresholds set in EDA and frozen before the test set is read (Data VL-06). | Proposal 2; Market MFR-12 |
| ST-02 | Historical P&L simulation from the signals. | Research measure on the sealed test period only. No buy, sell or hold language (Project-Wide ET-04). | Proposal 2; Market MFR-13 |
| ST-03 | Critic-and-revise loop for the explanation agent. | Only if the core pipeline finishes early. Judged on the same metrics as the single-pass agent. | Proposal 5.5; Market MFR-14 |
| ST-04 | Fine-tune a sentiment model on financial transcripts. | Trained on training-window transcripts only (FR-03). Compared with off-the-shelf FinBERT. | Proposal 2 |
| ST-05 | Agent corroboration step: a tool call that checks a later 8-K filing for corroborating or contradicting information. | Evidence dated after the announcement is labelled "post-announcement" in the explanation. It is never used by the model, and it is excluded from rank and sign agreement scoring. | Proposal 4.3 (step 3, described as optional) |

## 3. Users and Journeys

Primary persona: quantitative researcher or independent analyst with point-in-time consensus data access (Section 2 of the Market Requirements).

**Journey J1: Look up a ticker.** The user enters a ticker and sees the latest prediction, its confidence, the top three features that drove it, and its sector context (SRS-11).

**Journey J2: Check an explanation.** The user opens the explanation for a prediction and sees each claim with its faithfulness label, and the transcript sentence it cites. The user can open the source sentence in context.

**Journey J3: Review historical performance.** The user opens the evaluation page and compares the full model with the baselines in FR-06, including calibration, the evidence base and per-date results. The user can see which predictions were made before the announcement date.

**Journey J4: Look up history.** The user selects a ticker and date range and sees past predictions alongside the realised outcome and, where available, the realised sector-relative score (SRS-09).

## 4. Functional Requirements

Each requirement is written as a user-visible behaviour or system behaviour with acceptance criteria. Acceptance criteria state the starting condition, the action and the expected result. Priorities use MoSCoW, as Project-Wide PD-02 requires.

### FR-01: Prediction lookup (J1)

**Priority.** Must.

**Requirement.** Given a ticker, the system returns the class, class probabilities, confidence and top three features.

**Acceptance criteria.**
- Given a ticker with a stored transcript and feature vector, when the user submits the ticker, then the prediction card shows the class, the three class probabilities summing to 1.00 within rounding, a confidence value, and three features.
- Given the same ticker submitted twice without new data, then the same prediction is returned both times.
- Given a ticker with no transcript, then the card shows "No transcript available for this ticker" and no class.

### FR-02: Date fields on every event (J3)

**Priority.** Must.

**Requirement.** Each earnings event stores transcript date, estimate-publication date and announcement date as separate fields.

**Acceptance criteria.**
- Given any event in the database, when its record is read, then all three date fields are present and non-null, or the event is marked incomplete.
- Given a transcript dated after its announcement by more than the window in Data TX-02, then the event is flagged for review and excluded from training.

### FR-03: Temporal split enforcement (J3)

**Priority.** Must.

**Requirement.** Training uses 2015-2021, validation uses 2022, and test uses 2023-2024. No row dated after a split's cutoff enters that split's training data.

**Acceptance criteria.**
- Given the training pipeline runs, when any training row has a date after 31 December 2021, then the pipeline fails with an error naming the row.
- Given the test suite runs, then a test confirms the split boundaries against the feature matrix.

### FR-04: Feature attribution (J1, J2)

**Priority.** Must.

**Requirement.** Each prediction returns the top three SHAP features by absolute value, with signed contribution toward beat or miss.

**Acceptance criteria.**
- Given a prediction, when the explanation is requested, then three features are returned in descending absolute SHAP value.
- Given a feature with a positive SHAP value for miss, then its direction is labelled "toward miss".

### FR-05: Citation verification (J2)

**Priority.** Must.

**Requirement.** Every transcript excerpt cited by the explanation agent is checked for exact presence in the source document.

**Acceptance criteria.**
- Given an explanation citing a sentence, when the source transcript is checked, then the sentence is present verbatim, or the citation is removed and the explanation is marked "partially verified".
- Given a citation that cannot be found, then the failure is logged with the prediction identifier.

### FR-06: Baseline comparison (J3)

**Priority.** Must. The consensus-revision baseline within it is Should and conditional.

**Requirement.** The evaluation page shows the full model against the tabular-only baseline and two naive baselines (majority class, and repeating the previous quarter's surprise class) on the same test rows. The consensus-revision baseline (Market MFR-19) is added only if historical estimate revisions are available (I/B/E/S, Data CE-01); otherwise the page states that it is unavailable and why.

**Acceptance criteria.**
- Given the evaluation page loads, then every model shown has F1, three-class AUC (one-against-rest, macro average), binary AUC (beat against miss, in-line excluded), Brier score and precision at top 20%, computed on the same rows.
- Given any headline metric, then it is shown with a 95% bootstrap confidence interval, resampling by event (Market TR-01).
- Given the evaluation page, then the number of model variants tried before the final evaluation is stated (Market TR-02).
- Given the full model does not outperform a baseline, then the page states this without hiding either result.

### FR-07: Explicit edge-case handling (J1)

**Priority.** Must.

**Requirement.** The system handles missing transcripts, upstream API failures and cold-start tickers explicitly.

**Acceptance criteria.**
- Given an upstream API returns an error, then the response has status 503, a message naming the failed source, and no partial prediction.
- Given a ticker with fewer than four prior quarters of history, then the prediction is returned with the label "Limited history" and the trailing-average feature is marked as unavailable.

### FR-08: Disclaimer (all journeys)

**Priority.** Must.

**Requirement.** Every prediction and explanation displays a notice that it is not investment advice.

**Acceptance criteria.**
- Given any prediction or explanation is shown, then the notice appears in the same view, not behind a link.

### FR-09: History lookup (J4)

**Priority.** Must (the history endpoint is a proposal milestone deliverable).

**Requirement.** The user selects a ticker and date range and sees past predictions with the realised outcome.

**Acceptance criteria.**
- Given a ticker and a range covering four events, then four rows are returned, each showing the prediction date, class, confidence and realised outcome.
- Given a prediction whose outcome is not yet known, then the outcome field shows "Pending".

### FR-10: Calibration display (J3)

**Priority.** Must. Calibration by decile is Should.

**Requirement.** The evaluation page shows calibration and precision on the most confident predictions.

**Acceptance criteria.**
- Given the evaluation page, then a calibration plot and the precision at top 20% value are displayed for the test set.
- Given the evaluation page, then calibration is also shown by confidence decile (Market TR-05).

### FR-11: Reproducibility record (J3)

**Priority.** Should.

**Requirement.** Every stored prediction records the model version and feature-set version.

**Acceptance criteria.**
- Given a prediction is stored, then both version identifiers are present and match a registered model artefact.

### FR-12: Sector-relative scoring (J1, J3, J4)

**Priority.** Should. An extension beyond the proposal (PG-6, Market MFR-16).

**Requirement.** Each prediction is placed in its sector context. Sector-relative scoring is made of two separate outputs, and the requirements for each part are in Section 4A:
- **Sector context** (before the announcement): how the company's sector peers have surprised in their most recent reported quarter. It can be a model feature and can be shown with a prediction.
- **Realised sector-relative score** (after the announcement): the event's own SUE minus the peer mean, divided by the peer standard deviation. It uses the company's own actual EPS, which is the outcome being predicted, so it is never a model input and is never shown before the announcement.

**Acceptance criteria.** SRS-01 to SRS-14 pass.

### FR-13: Idempotent transcript ingestion

**Priority.** Must.

**Requirement.** Re-running an ingestion job does not create duplicate transcripts, including after a partial failure.

**Acceptance criteria.**
- Given the same transcript is ingested twice, then exactly one transcript row exists for it.
- Given an ingestion job fails halfway and is re-run, then the final row count equals the count of a clean run.

### FR-14: Estimate snapshots kept as captured

**Priority.** Must.

**Requirement.** Consensus estimates are stored as dated snapshots. Earlier snapshots are never overwritten. A prediction uses only snapshots captured before the announcement date. Sources that only return current values are captured from a start date and are never backfilled into earlier events (Data SR-08).

**Acceptance criteria.**
- Given a new consensus estimate arrives for an event, then a new snapshot row is added with its capture timestamp and the earlier snapshot is unchanged.
- Given a prediction for an event announced on date D, then any snapshot captured on or after D is excluded from its inputs.
- Given a snapshot-only source, then no row exists with a capture time earlier than that source's capture start date.

### FR-15: Prepared remarks and Q&A segmentation

**Priority.** Must.

**Requirement.** Each transcript is split into prepared remarks and the Q&A section. Q&A features are computed only from the Q&A section.

**Acceptance criteria.**
- Given a transcript with a recognised Q&A marker, then prepared and Q&A sections are stored separately.
- Given no Q&A marker is found, then the event is flagged "Segmentation failed" and the Q&A features are stored as unavailable, not as zero.

### FR-16: Sentence-level sentiment scoring

**Priority.** Must.

**Requirement.** FinBERT scores are computed per sentence in batches and stored. A transcript is rescored only when the transcript or the FinBERT version changes.

**Acceptance criteria.**
- Given a transcript is already scored with the current FinBERT version, when the batch runs, then no sentence is rescored.
- Given the FinBERT version changes, then every affected transcript is rescored and the old scores are retained with their version.

### FR-17: Linguistic uncertainty features

**Priority.** Must.

**Requirement.** Hedge-word ratio and negation frequency are computed with spaCy, using the word lists defined in the feature set.

**Acceptance criteria.**
- Given a fixture transcript with a known hedge-word count, then the uncertainty score equals hedge count divided by word count to four decimal places.
- Given a transcript with zero words, then the feature is stored as unavailable and no division is attempted.

### FR-18: Sentiment surprise z-score

**Priority.** Must.

**Requirement.** The current quarter's sentiment is expressed as a z-score against the company's trailing four-quarter average.

**Acceptance criteria.**
- Given four prior quarters of scores, then the z-score equals (current minus the mean of the four) divided by their standard deviation.
- Given the standard deviation of the four prior quarters is zero, then the feature is stored as unavailable, not as infinity.
- Given fewer than four prior quarters, then the prediction carries the "Limited history" label (FR-07).

### FR-19: Asynchronous explanation

**Priority.** Must.

**Requirement.** An explanation request returns a job identifier immediately. The explanation is generated in the background.

**Acceptance criteria.**
- Given an explanation request, then the API returns a job identifier within 500 ms and the job status is pending.
- Given the job completes, then the status changes to complete and the explanation is retrievable by identifier.
- Given the job fails, then the failure reason is stored and returned with the status.

### FR-20: Ticker validation

**Priority.** Must.

**Requirement.** Tickers are validated before any lookup.

**Acceptance criteria.**
- Given a ticker not in the universe for any date in the dataset, then the response is 404 with the message "Ticker not in universe".
- Given a ticker with characters outside letters, digits, dot or hyphen, or longer than ten characters, then the response is 422 with the message "Invalid ticker format".

### FR-21: Evidence base on every prediction (J1, J3)

**Priority.** Must (Market MFR-15).

**Requirement.** Every prediction shows the training window, the test window, the number of training events and the date of the last retraining.

**Acceptance criteria.**
- Given any prediction card, then all four values are shown and match the ModelVersion record of the model that produced it.

### FR-22: As-of timestamps of inputs (J1, J3)

**Priority.** Must (Market MFR-17).

**Requirement.** Every prediction records and shows the as-of timestamp of each input group: transcript, estimate snapshot, prices, fundamentals and sector context.

**Acceptance criteria.**
- Given a prediction for an event announced on date D, then every stored as-of timestamp is before D. A test fails the build if any is not.
- Given the prediction card, then the timestamps are visible in the same view or one click away.

### FR-23: Label definition shown (J3)

**Priority.** Should (Market MFR-18).

**Requirement.** The evaluation page shows the SUE definition, the beat and miss thresholds in use, the date they were frozen, and the dispersion measure used.

**Acceptance criteria.**
- Given the evaluation page, then the thresholds shown equal the frozen values recorded under Data VL-06.

### FR-24: Full proposal feature set

**Priority.** Must. Any feature dropped later is recorded in the decision log (Project-Wide SS-02).

**Requirement.** The feature matrix contains the features in proposal Sections 4.1 and 5.2. Each feature has a source tag (Data SR-02) and an as-of rule.

| Group | Feature | As-of rule | Detail |
|---|---|---|---|
| Text | Mean FinBERT positive, negative and neutral scores across all sentences | Transcript | FR-16 |
| Text | Sentiment trajectory: first half against second half of the call | Transcript | |
| Text | Uncertainty score: hedge words divided by word count | Transcript | FR-17 |
| Text | Negation frequency | Transcript | FR-17 |
| Text | Question count in the Q&A section | Transcript | FR-15 |
| Text | Forward-guidance ratio: sentences mentioning future quarters divided by total sentences | Transcript | |
| Text | Q&A sentiment delta: analyst question sentiment against management answer sentiment | Transcript | FR-15 |
| Text | Q&A-only sentiment and Q&A-only hedge-word rate | Transcript | FR-15 |
| Text | Sentiment surprise: z-score against the trailing four quarters | Transcript and prior events | FR-18 |
| Tabular | Prior four-quarter EPS surprise trend | Prior events announced before D | |
| Tabular | Revenue growth, gross margin, operating margin | Latest filing filed before D (Data FD-02). The current quarter's figures are not known before D. | |
| Tabular | Analyst consensus dispersion (standard deviation of estimates) | Snapshot captured before D | FR-14 |
| Tabular | Price momentum: three-month return before the announcement | Prices dated before D (Data PX-02) | |
| Sector | Sector context: peer mean SUE and peer count | Peer events announced before D | SRS-08 |

**Acceptance criteria.**
- Given the feature-set version, then every feature in the table is listed with its source tag and as-of rule, or is listed as dropped with a decision-log reference.
- Given a fixture event, then each computed feature equals a hand-calculated value.

### FR-25: FinBERT pretraining-cutoff check

**Priority.** Must (Proposal 5.4).

**Requirement.** The relationship between FinBERT sentiment and the outcome is compared for transcripts close to FinBERT's pretraining-corpus cutoff and for transcripts well after it, to look for a jump at the cutoff that would suggest the pretraining corpus overlaps with later outcomes.

**Acceptance criteria.**
- Given the evaluation report, then it contains a per-quarter series of a sentiment-only metric with the pretraining cutoff marked, and the result is stated either way.

### FR-26: Global SHAP and domain consistency

**Priority.** Must (Proposal 5.3, 7).

**Requirement.** The evaluation shows global SHAP importance for the full model and checks named features against expected directions from domain knowledge (for example, a higher uncertainty score is expected to push toward miss).

**Acceptance criteria.**
- Given the evaluation page, then it shows mean absolute SHAP value for every feature.
- Given at least four named features, then their expected directions are recorded before the test set is read, and the observed direction is shown beside each. Mismatches are reported, not hidden.

## 4A. Sector-Relative Scoring Requirements

These requirements break FR-12 into its parts. They apply only if FR-12 is built. Where a requirement is marked "Must if built", FR-12 may not ship without it, because it protects the no-lookahead claim.

Definitions used in this section:
- **D**: the announcement date of the event being scored.
- **Peer**: another company in the same sector and in the S&P 500 on D.
- **Peer SUE**: the SUE of a peer's most recent eligible event (SRS-04, SRS-05).

### 4A.1 Sector Classification

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-01 | Must if built | The sector of each company on each date comes from a dated sector history. The current classification is never used for a past date. | Data VL-11: a company reclassified in 2023 shows its old sector before the change date. | Data SEC-01; Market DR-06 |
| SRS-02 | Should | The sector level is the GICS sector, as the GICS structure stood on D. The GICS version is stored with each assignment, because the number of sectors changed during 2015 to 2024 (Real Estate was split out in 2016, Communication Services was created in 2018). | A test date in 2015 resolves to the structure in force then, and the stored version matches it. | Market DR-06 |

### 4A.2 Peer Set

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-03 | Must if built | Peers are the companies in the S&P 500 on D (point-in-time membership) whose sector on D matches the event's sector. The company itself is excluded. | Unit test on a fixed date with a known peer set passes. A company removed from the index before D is not a peer. | Data SEC-02, IM-01 |
| SRS-04 | Must if built | Each peer contributes one event: its most recent event announced strictly before D and no more than 100 days before D (proposed). Peers that announce on D or later are excluded. The window covers early reporters in a quarter, which would otherwise have almost no peers. | Test: a peer announcing on D is excluded; a peer with two events in the window contributes only the later one; a peer whose last event is 101 days before D is excluded. | Data GATE-3; Data VL-03 |
| SRS-05 | Must if built | A peer event is eligible only if its own SUE is valid: at least three estimates (Data CE-04), with snapshots captured before the peer's own announcement (FR-14). Ineligible peers are counted and reported. | Test: a peer event with two estimates is excluded and counted. | Data CE-04; FR-14 |

### 4A.3 Peer Statistics

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-06 | Must if built | At least five eligible peers are needed. Below that, the status is "Insufficient peers", no numeric value is shown, and the sector features are stored as unavailable, not as zero. | Fixture with four eligible peers returns "Insufficient peers" and unavailable features. | Former FR-12 |
| SRS-07 | Should | Peer mean and sample standard deviation of peer SUE are computed after clipping each peer SUE at the 1st and 99th percentiles of the training-window SUE distribution. The clip limits are frozen with the SUE thresholds (Data VL-06). If the standard deviation is zero, the score is unavailable. | Test with a planted extreme peer SUE shows it is clipped. Clip limits match the frozen record. | Data VL-06; FR-03 |

### 4A.4 Sector Context (Before the Announcement)

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-08 | Should | Sector context features (peer mean SUE and peer count, from SRS-03 to SRS-07) enter the feature matrix with the as-of date of D. They are recorded in the feature-set version. | Data VL-03 peer-set replay matches for 30 predictions. A planted peer event dated D does not change the feature. | FR-24; Data VL-03 |

### 4A.5 Realised Sector-Relative Score (After the Announcement)

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-09 | Must if built | The realised score is (event SUE minus peer mean) divided by peer standard deviation, using the peer statistics stored for D. It is computed only after the event's actual EPS is released. It is never a model input. | Feature-matrix schema test: no column is derived from the event's own SUE. Before the announcement, the API returns "Pending" for the realised score. | Market MFR-16; FR-03 |

### 4A.6 Storage and Audit

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-10 | Must if built | One SectorBenchmark row is stored per event, with the sector, GICS version, as-of date, the list of peer event identifiers used, the peer mean, standard deviation, count and status. | Recomputing the statistics from the stored peer list reproduces the stored values. | Section 11; FR-22 |

### 4A.7 Display

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-11 | Should | The prediction card shows the sector name and peer count. Before the announcement it shows the sector context, labelled "Sector peers already reported". After the announcement it also shows the realised score, labelled "Realised sector-relative surprise". "Insufficient peers" is shown where SRS-06 applies. | UI test covers all three states. | J1; Section 14 |
| SRS-12 | Could | A sector comparison view lists every peer used, with its event date and SUE, and the company's realised score once known. | The view lists exactly the peers stored under SRS-10. | UI-04 |

### 4A.8 Coverage and Fallback

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-13 | Should | The share of predictions with a numeric sector context is reported per year and per sector. Proposed target: at least 90%. | Coverage table exists in the evaluation report. | Section 15 |
| SRS-14 | Must if built | If point-in-time sector history cannot be obtained (Data SEC-01 fails), the sector features and display are switched off, the feature-set version records this, and the gap is reported. Current sectors are never used as a substitute. | Configuration test: with sector history missing, no sector column is produced and the card shows "Sector comparison unavailable". | Market DR-06; Section 18 |

## 5. Non-Functional Requirements

Thresholds are proposed. They are to be agreed with the supervisor (Section 9 of the Market Requirements).

| ID | Priority | Area | Requirement | Threshold |
|---|---|---|---|---|
| NFR-01 | Should | Latency | Cached prediction response time, 95th percentile. | Under 500 ms |
| NFR-02 | Should | Latency | Full explanation response time, 95th percentile, from request to complete status. | Under 10 s, or returned as pending |
| NFR-03 | Should | Freshness | New transcripts available after publication. | Within 24 hours |
| NFR-04 | Must | Availability | Demo deployment uptime. | Best effort; no SLA |
| NFR-05 | Must | Reproducibility | Retraining from a stored snapshot reproduces reported metrics. | Same to two decimal places |
| NFR-06 | Must | Security | No secrets in source control. Data-licence keys in environment variables. | Checked in CI |
| NFR-07 | Should | Accessibility | Dashboard meets WCAG 2.1 AA for colour contrast and keyboard navigation. | Automated check passes |
| NFR-08 | Could | Responsiveness | Dashboard usable at 375 px width. | No horizontal scrolling on prediction card |
| NFR-09 | Should | Batch throughput | Backfill of the full target corpus (4,000-5,000 events) on demo infrastructure. | Completes within 24 hours |
| NFR-10 | Must | Test coverage | Line coverage on feature engineering, split logic and sector scoring. | At least 80% |
| NFR-11 | Must | Request logging | Every API request is logged with a request identifier, latency and status code. | 100% of requests |
| NFR-12 | Should | Service metrics | Latency and error rate exposed for scraping. | Available at /metrics |

## 6. API Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| API-01 | Must | The OpenAPI specification is generated from code and served with the API. | Specification validates and matches every endpoint in Section 13. |
| API-02 | Must | All endpoints except /health and /metrics sit under the /v1 path prefix. | Requests to unversioned paths other than /health and /metrics return 404. |
| API-03 | Should | Every error response has the same shape: code, message and request identifier. | Contract test checks the shape for 404, 422, 401, 429 and 503. |
| API-04 | Must | Prediction endpoints return the envelope: data, warnings array and model_version. | Contract test on each prediction endpoint. |
| API-05 | Should | The history endpoint is paginated, with a default page size of 20 and a maximum of 100. | Request for 500 rows returns 100 with a next-page link. |
| API-06 | Must | Every endpoint except /health requires a JWT. | Request without a token returns 401. |
| API-07 | Should | Each client is rate limited, and a limited request returns 429 with a Retry-After header. | Load test exceeding the limit returns 429 with the header present. |

## 7. Data Pipeline Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| PL-01 | Must | Scheduled ingestion jobs record start time, end time, status and row counts. | Each run produces a log row that can be queried. |
| PL-02 | Must | Failed ingestion tasks retry up to three times with exponential backoff, then move to a dead-letter queue. | Injected failure produces three retries and one dead-letter entry. |
| PL-03 | Should | Each ticker's latest transcript date is reported through /health. | Health response lists the date for a test ticker. |
| PL-04 | Must | Events missing actual EPS or the estimate mean are rejected, and the reason is logged. | Fixture with a missing estimate is rejected with the logged reason. |
| PL-05 | Must | Schema changes are made only through versioned migrations. | Migration history matches the deployed schema on a clean database. |
| PL-06 | Must | Raw transcripts are stored unchanged. Cleaned text is stored in a separate column. | Hash of raw text is identical before and after cleaning. |

## 8. Machine Learning Pipeline Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| ML-01 | Must | Random seeds are fixed and recorded for every training run. | Two runs with the same seed and snapshot produce identical predictions. |
| ML-02 | Must | Hyperparameters are tuned on the 2022 validation set only. The 2023-2024 test set is read once, for final evaluation. | Access log shows test rows read only in the final evaluation job. |
| ML-03 | Must | Each model artefact is saved with its version and a SHA-256 checksum, in XGBoost native format or ONNX (Project-Wide SP-01). Loading verifies the checksum. | Altered artefact fails to load with a checksum error. |
| ML-04 | Must | The SHAP explainer is built from the same artefact as the served model. | Explainer and model share the artefact identifier. |
| ML-05 | Must | A training run writes its metrics report before the model is registered. | Registration fails if the report file is missing. |
| ML-06 | Must | A model is promoted to serving only after the FR-06 comparison has been run on the sealed test set and reported, and a reviewer's sign-off is recorded. The full model does not have to beat the baselines: a negative result is valid (Proposal 7) and is shown on the evaluation page. | Promotion step checks that the comparison report and the sign-off record both exist. |

## 9. User Interface Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| UI-01 | Could | Ticker search offers autocomplete from the universe. | Typing two letters shows matching tickers. |
| UI-02 | Should | Every chart has a text alternative and a switch to a data table. | Automated accessibility check finds no chart without an alternative. |
| UI-03 | Must | The explanation view shows the verification status beside each citation. | Each citation in the view has a visible status. |
| UI-04 | Could | A sector comparison view shows the peers used for a prediction (SRS-12). | View lists every peer used in the calculation. |
| UI-05 | Should | All controls can be reached by keyboard, with a visible focus indicator. | Keyboard-only walkthrough completes Journey J1. |

## 10. Operations Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| OP-01 | Must | Secrets are read from environment variables or a secret manager. None appear in source control. | Secret scanner passes in CI. |
| OP-02 | Must | Container images are built in CI with all dependencies pinned to exact versions. | Build fails if a dependency is unpinned. |
| OP-03 | Should | The service can be rolled back to the previous revision within 10 minutes. | Rollback drill completed and timed during week 15. |

## 11. Data Model

| Entity | Key fields | Notes |
|---|---|---|
| Company | company_id, name | company_id is a permanent identifier that survives ticker changes (Data IM-03). |
| TickerHistory | company_id, ticker, valid_from, valid_to | Data IM-03. Tickers are looked up as of a date. |
| IndexMembership | company_id, valid_from, valid_to, removal_reason | One row per membership spell, so a company can leave and rejoin (Data IM-01, IM-02; Market DR-02, DR-08). |
| SectorAssignment | company_id, gics_sector, gics_version, valid_from, valid_to | SRS-01, SRS-02; Market DR-06. |
| EarningsEvent | event_id, company_id, fiscal_period, transcript_date, estimate_date, announcement_date, announcement_time_utc, eps_basis, sue, label | FR-02; Data DV-06, DV-07, AE-03. Label derived from SUE thresholds frozen during EDA. |
| ActualEps | event_id, version, value, basis, source, document_id, released_at | Data AE-01 to AE-04. The first-reported value is kept; corrections are new versions. |
| EstimateSnapshot | snapshot_id, event_id, mean_estimate, std_estimate, estimate_count, source, captured_at | FR-14; Data CE-01, CE-04. Append-only. |
| FundamentalsFiling | company_id, fiscal_period, form, filed_at, revenue, gross_profit, operating_income, source, version | FR-24; Data FD-01 to FD-04. |
| Transcript | transcript_id, event_id, source, source_url, retrieved_at, raw_text, cleaned_text, raw_hash | PL-06, FR-05, Market DR-09. |
| TranscriptSection | section_id, transcript_id, kind (prepared or qa), text | FR-15. |
| FeatureVector | event_id, feature_set_version, features (JSON), computed_at | FR-24. Tabular, text and sector features in one row per event. |
| SectorBenchmark | event_id, sector, gics_version, as_of_date, peer_event_ids (JSON), mean_sue, std_sue, peer_count, status | SRS-10. Stored with the as-of date so the no-lookahead rule can be checked. |
| ModelVersion | model_version, trained_on_from, trained_on_to, training_event_count, metrics (JSON), artefact_path, checksum, seed, retrained_at | FR-11, FR-21, ML-01, ML-03. |
| Prediction | prediction_id, event_id, model_version, feature_set_version, class, probabilities, confidence, input_as_of (JSON), created_at | FR-01, FR-11, FR-22. Realised outcome and realised sector score joined from EarningsEvent and SectorBenchmark. |
| Explanation | explanation_id, prediction_id, features (JSON), citations (JSON), verification_status, job_status, prompt_version, llm_model_version, generation_settings (JSON), created_at | FR-04, FR-05, FR-19; Project-Wide AI-01. |
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
| Insufficient peers | "Insufficient peers" in the sector section. | Stores sector features as unavailable (SRS-06). |
| Sector history unavailable | "Sector comparison unavailable." | Sector features switched off (SRS-14). |
| Realised sector score before announcement | "Pending." | No value computed (SRS-09). |
| Citation not found | Explanation marked "partially verified". | Logs the failure with prediction identifier. |
| Explanation job failed | "Explanation could not be generated." | Stores the failure reason and returns it with the status. |
| Model artefact missing or checksum mismatch | "Service temporarily unavailable." (503) | Refuses to serve; raises an alert. |

## 13. API Surface

| Method | Path | Purpose | Requirement |
|---|---|---|---|
| GET | /v1/predictions/{ticker} | Latest prediction, top three features, evidence base, input as-of times and sector context. | FR-01, FR-04, FR-21, FR-22, SRS-11, API-04 |
| GET | /v1/predictions/{ticker}/sector | Peer list and statistics behind the sector context and realised score. | SRS-10, SRS-12 |
| GET | /v1/predictions/{ticker}/explanation | Explanation with citations and verification status. | FR-04, FR-05, FR-19 |
| POST | /v1/predictions/{ticker}/explanation/jobs | Starts an explanation job and returns the job identifier. | FR-19 |
| GET | /v1/jobs/{job_id} | Status of an explanation job. | FR-19 |
| GET | /v1/predictions/{ticker}/history?from=&to=&page= | Past predictions with outcomes and realised sector scores. | FR-09, SRS-09, API-05 |
| GET | /v1/evaluation/metrics?model=full\|tabular\|majority\|previous\|consensus | Test-set metrics for a model version. | FR-06, FR-10, FR-23, FR-26 |
| GET | /health | Service, data freshness and ingestion status. | NFR-03, PL-03 |
| GET | /metrics | Service metrics for scraping. | NFR-12 |

## 14. Screens

| Screen | Contents | Journey | Priority |
|---|---|---|---|
| Ticker search | Input field, submit, recent lookups. Autocomplete if UI-01 is built. | J1 | Must |
| Prediction card | Class, probabilities, confidence, evidence base, input as-of times, sector context (SRS-11), not-investment-advice notice, link to explanation. | J1 | Must |
| Feature chart | Horizontal bars for top three SHAP features, coloured by direction, with a data table alternative. | J1, J2 | Must |
| Explanation view | Each claim, its faithfulness label, the cited sentence and its verification status. | J2 | Must |
| History table | Date, class, confidence, realised outcome, realised sector score, pending state, pagination. | J4 | Must |
| Evaluation page | Baseline comparison table with confidence intervals, calibration plot, precision at top 20%, global SHAP, label definition, limitations notice. | J3 | Must |
| Sector comparison | Peer list and statistics (SRS-12). | J1 | Could |

## 15. Success Metrics

| Metric | Target | Counter-metric | Why the counter-metric matters |
|---|---|---|---|
| Full model against tabular baseline on 2023-2024 test set | F1 and AUC difference reported with 95% bootstrap intervals. No pass mark: a negative result is valid (Proposal 7). | Brier score reported beside it | A higher AUC with poor calibration misleads users about confidence. |
| Binary AUC (beat against miss, in-line excluded) | Reported beside the SAE-FiRE XGBoost baseline (about 0.67) as a reference point, not a pass mark. SAE-FiRE is binary, so the three-class AUC is not compared with it. | Share of events excluded as in-line | Excluding the middle band makes the binary task easier. |
| Precision at top 20% | Reported; no target until baseline known | Coverage: share of events receiving a prediction | High precision on a small subset is not useful if most events are excluded. |
| Sector context coverage (SRS-13) | At least 90% of predictions have a numeric sector context (proposed) | Share showing "Insufficient peers", by year and sector | A score that is hidden for most events is not useful, so coverage must be reported beside the score. |
| Citation verification rate | 100% verified or flagged | Explanation length | Verifying shorter explanations is easier and could hide weak evidence. |
| Rank and sign agreement | Reported on held-out sample | Number of features discussed per explanation | Discussing more features raises agreement chances without raising faithfulness. |
| Claim faithfulness rate (EX-02) | Reported per explanation | Human agreement with automated labels (EX-05) | Automated labels that humans disagree with are not evidence of faithfulness. |
| Usability (five test users, after ethics approval, Project-Wide ET-01) | All complete J1 without help | Time to complete J2 | Fast completion can mean users skipped the explanation. |

## 16. Milestones

Aligned to Section 6 of the proposal. Weeks are a guide, not a commitment. Two changes from the proposal's order are recorded: the explanation layer comes before the frontend, so the dashboard can show explanations, and the API is deployed at the hardening milestone rather than at the backend milestone.

| Weeks | Milestone | Done when |
|---|---|---|
| 1-2 | Requirements, data verification (Market DR-01, DR-03, DR-05, DR-06, DR-10; Data SR-05) | Data sources confirmed in writing; this document agreed. |
| 3-5 | Data pipeline and feature engineering | Feature matrix stored; EDA notebook complete; SUE thresholds frozen; PL-01 to PL-06, FR-02, FR-03, FR-13 to FR-18, FR-24 tests pass; SRS-01 to SRS-08 pass if FR-12 is built. |
| 6-7 | Model development and baseline comparison | Full model and baselines trained; ML-01, ML-02, ML-05 pass; FR-06, FR-25 and FR-26 results available. |
| 8-9 | Backend endpoints | Section 13 endpoints running; API-01 to API-07, FR-01, FR-04, FR-07, FR-09, FR-20, FR-21, FR-22 pass; SRS-09 to SRS-11 pass if FR-12 is built. |
| 10-11 | Explanation layer and citation verification | FR-05, FR-19, EX checks pass on test set; faithfulness rates reported. |
| 12-13 | Frontend and usability testing | Must screens in Section 14 live; UI-03 passes; five-user test complete if ethics approval is in place. |
| 14-15 | Hardening and deployment | NFR-01 to NFR-12 measured and recorded; OP-01 to OP-03 pass; ML-06 sign-off recorded. |
| 16 | Write-up and presentation | Dissertation draft; demo recorded. |

## 17. Dependencies

| Dependency | Needed for | Status |
|---|---|---|
| Point-in-time consensus estimates (snapshots) | FR-01 (SUE labels), FR-03, FR-14 | Unverified (Market DR-01, DR-10; Data SR-05) |
| Transcript source with licence for demo | FR-01, FR-05, FR-15 | Unverified (Market DR-03, DR-05) |
| Index membership history | FR-03 universe, SRS-03 peer set | Unverified (Market DR-02) |
| Point-in-time GICS sector history | FR-12, SRS-01 | Unverified (Market DR-06). If unavailable, SRS-14 applies. |
| Quarterly fundamentals with filing dates | FR-24 (revenue growth, margins) | Unverified (Data FD-01) |
| FinBERT model weights | FR-16 | Available (HuggingFace). Licence to be recorded (Project-Wide ET-03). |
| GCP project for deployment | NFR-01, NFR-04, OP-03 | To be set up |

## 18. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Point-in-time estimates unavailable | High | High | Confirm in week 1. Fall back to a documented, reduced label definition with the limitation stated. |
| Transcript source unavailable or unlicensed | High | High | Check library access. Use a licensed fallback (Data Section 4), or restrict the demo to a historical slice. |
| Sector history wrong for past quarters | Medium | High | Use the point-in-time sector source (Market DR-06). If unavailable, switch sector scoring off (SRS-14). Never use current sectors. |
| Early reporters have too few peers | Medium | Medium | 100-day peer window (SRS-04). Report coverage (SRS-13). |
| Fundamentals filed after the announcement leak into features | Medium | High | Use only filings filed before D (FR-24, Data FD-02). |
| FinBERT pretraining overlaps test period | Medium | High | FR-25. Report result either way. |
| Explanation agent produces unfaithful narratives | Medium | Medium | FR-05, EX-03, EX-04 and rank and sign agreement metrics. Report the rate. |
| Test set read during tuning | Low | High | ML-02 access log. Any read outside final evaluation invalidates the headline result. |
| Feature drift after release | Medium | Medium | Monitor feature distributions and top-feature rank order against the training baseline (Market MR-05, MR-06, Should). |
| Scope creep from design notes | High | Medium | Non-goals in Section 2.2 are fixed for this version. Stretch objectives in Section 2.3 are Could. |
| Effort exceeds 15-20 hours per week | Medium | High | Drop Could items first, then Should items, in the drop order agreed under Project-Wide PD-02. |

## 19. Open Questions

| Question | Owner | Needed by |
|---|---|---|
| Are point-in-time consensus estimates accessible through the university? | John, with Professor Goodacre | Week 1 |
| Which transcript source is licensed for the demo? | John | Week 1 |
| Is point-in-time GICS sector history available? | John | Week 1 |
| Which fundamentals source gives filing dates (EDGAR XBRL or Compustat)? | John | Week 1 |
| Are the NFR thresholds in Section 5 acceptable to the supervisor? | John, with Professor Goodacre | Week 2 |
| Are the sector peer window (100 days, SRS-04) and minimum peer count (5, SRS-06) acceptable? | John, with Professor Goodacre | Week 2 |
| Is the explanation layer or the temporal evaluation the headline contribution? | John, with Professor Goodacre | Week 2 |
| Who performs the independent review in ML-06? | John, with Professor Goodacre | Week 2 |
| What is FinBERT's pretraining-corpus cutoff date (FR-25)? | John | Week 4 |
| What is the SUE threshold for beat and miss? | John, from EDA | Week 4 |

## 20. Sources Checked

- Plannotator, product requirements document guidance: https://docs.plannotator.ai/learn/planning/what-is-a-product-requirements-document
- Amazon SageMaker Model Monitor, arXiv:2111.13657: https://arxiv.org/pdf/2111.13657
- Arize Phoenix, faithfulness evaluator: https://www.arize.com/docs/phoenix/evaluation/pre-built-metrics/faithfulness
- Harvey, C. and Liu, Y., "Backtesting", Duke University working paper: https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF
- SR 11-7 model risk management summary: https://www.magicmirrorsecurity.com/blog/sr-11-7-model-risk-management-guidance-explained
- Project proposal, Third Year Project Proposal (2026-27), as uploaded.
- Market Requirements document, `docs/requirements/market-requirements.md`.

Points marked "to be set up" or "unverified" have not been confirmed against primary sources. The SR 11-7 and Harvey and Liu sources were read through summaries, not the primary texts. The GICS structure changes in SRS-02 (Real Estate in 2016, Communication Services in 2018) are from memory and should be checked against S&P's published history before SRS-02 is tested.
