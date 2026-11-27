# Product Requirements: LLM-Powered Earnings Surprise Predictor

Derived from the Third Year Project Proposal (2026-27) (see [SSOT](../SSOT.md)), the Market Requirements and the project design notes. Updated 26 October 2026. Revised 14 November 2026 (priorities, proposal items, sector scoring). Restructured 15 November 2026: this document now owns every requirement about what the system does, including the evaluation (TR), model governance (MR) and explanation (EX) requirements that were previously in the market document. Open questions are in the [decision log](../decision-log.md).

## 1. Problem Statement

**Framing.** As the proposal states (Sections 1 and 8), the contribution of this project is the distributed systems design and the ML methodology. Finance is the domain they are tested in. The user and market framing below is used to set testable behaviour. It does not change the contribution the dissertation claims.

Quantitative users who want to use earnings call transcripts as a signal have no tool that does three things together: returns a beat/miss prediction for a ticker, explains that prediction using evidence from the transcript itself, and shows that the historical performance is free of lookahead and selection bias.

Existing products cover parts of this. StarMine forecasts surprises from analyst estimates. AlphaSense summarises calls and scores sentiment. Academic systems predict beat/miss from transcripts but cannot be queried. The gap this product fills is the combination, as described in Section 3 of the Market Requirements.

**Evidence.** The academic baseline reports, for XGBoost on earnings calls, AUC 0.620, accuracy 0.781 and F1 0.715 on a binary beat/miss task under a chronological split. SAE-FiRE's own models reach AUC 0.657 to 0.668 (SAE-FiRE, 2025). These figures were corrected on 14 November 2026: the proposal's 0.67 is SAE-FiRE's model, not the XGBoost baseline. Their label uses analyst forecasts issued after the call, so it differs from ours (FR-27). The related work in the proposal shows that fluent explanations can cite factors the model never used (He and Martens, 2026), and Ichmoukhamedov et al. provide the rank and sign agreement metrics used to detect this. Both points justify building an evaluation harness alongside the prediction.

**Data note.** The proposal describes the corpus as public through SEC EDGAR. The Data Requirements (Section 3) show that transcripts and point-in-time consensus need licensed academic sources. The reason for the domain is unchanged: the label is measurable and the dates make lookahead testable. The change is logged as C14 in the Project-Wide Requirements.

**Label note.** The proposal defines the label against analyst consensus. No free source gives historical point-in-time consensus with a standard deviation, and the project is to be built from free sources (Data SR-09). The historical label is therefore a time-series SUE built from SEC EDGAR EPS (Data LB-01 to LB-08), the approach of Bernard and Thomas (1989), which the proposal cites. Analyst consensus is captured from now on as a prospective check. The change is logged as C19 in the Project-Wide Requirements and needs the supervisor's agreement.

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

PG-1 to PG-5 come from the proposal. PG-6 is an extension added after the proposal (Market N7). It is kept at Should priority and must not displace the proposal goals.

### 2.2 Non-Goals

These are out of scope for this version. Each one is excluded on purpose, and the reason is given.

| ID | Non-goal | Reason |
|---|---|---|
| NG1 | Live or mid-call predictions. | Needs a licensed real-time transcript feed that is not in the data plan (Data TX-04, SR-03). |
| NG2 | Trade execution, broker integration, or a live P&L loop that feeds trading results back into the model. | Adds regulatory scope with no requirement in the market analysis. The historical P&L research measure (ST-02) is separate. |
| NG3 | Insider trading or options data triangulation. | Data integration cost. Not needed for PG-1 to PG-6. |
| NG4 | Public user accounts, personalisation or saved watchlists. | Demo authentication only (JWT, API-06). The proposal does not specify authentication; JWT is added for the security review (Project-Wide SP-02). |
| NG5 | Investment advice or any claim that the output should be traded. | Not an advisory product. Notice shown on every output (FR-08). |

### 2.3 Stretch Objectives

All stretch objectives are Could. They are built only after every Must requirement passes, and nothing else depends on them.

| ID | Stretch objective | Rule | Source |
|---|---|---|---|
| ST-01 | Five-class output: large beat, small beat, in-line, small miss, large miss. | Thresholds set in EDA and frozen before the test set is read (Data VL-06). | Proposal 2 |
| ST-02 | Historical P&L simulation from the signals. | Research measure on the sealed test period only. No buy, sell or hold language (Project-Wide ET-04). | Proposal 2 |
| ST-03 | Critic-and-revise loop for the explanation agent. | Only if the core pipeline finishes early. Judged on the same metrics as the single-pass agent. | Proposal 5.5 |
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
- Given a ticker with no earlier transcript (a cold-start ticker), then the card shows "No transcript available for this ticker" and no class.

### FR-02: Date fields on every event (J3)

**Priority.** Must.

**Requirement.** Each earnings event stores transcript date, announcement date and an information date as separate fields. The information date is the estimate-publication date for events with a consensus label, and the filing date of the latest EPS used for events with a time-series label (Data LB-04).

**Acceptance criteria.**
- Given any event in the database, when its record is read, then all three date fields are present and non-null, or the event is marked incomplete. The label route is stored beside them.
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

**Priority.** Must. The consensus-revision baseline within it is Should and conditional. With the time-series label it exists only for the prospective set.

**Requirement.** The evaluation page shows the full model against the tabular-only baseline and the two naive baselines in TR-06 on the same test rows. The consensus-revision baseline (Market N4) is added only if historical estimate revisions are available (a licensed source, Data CE-01) or, for the prospective set only, from the captured snapshots; otherwise the page states that it is unavailable and why.

**Acceptance criteria.**
- Given the evaluation page loads, then every model shown has accuracy, weighted F1, three-class AUC (one-against-rest, macro average), binary AUC (beat against miss, in-line excluded), Brier score and precision at top 20%, computed on the same rows. The consensus-revision baseline, where it exists, is shown in its own table on the prospective set, with the full and tabular models re-scored on those same rows. Accuracy, weighted F1 and binary AUC follow the SAE-FiRE definitions so that tables line up with the literature.
- Given any headline metric, then TR-01 (confidence intervals) and TR-02 (variants tried) apply.
- Given the full model does not outperform a baseline, then the page states this without hiding either result.

### FR-07: Explicit edge-case handling (J1)

**Priority.** Must.

**Requirement.** The system handles missing transcripts, upstream API failures and cold-start tickers explicitly.

**Acceptance criteria.**
- Given a data source returns an error during ingestion, then the task retries and is then dead-lettered (PL-02), the run record shows the failure (PL-01), no partial event is stored (DB-13), and /health reports the ingestion status without changing its HTTP status. Predictions already stored are still served, with the warning "Data refresh failed on <date>. Showing the last stored result." in the response envelope (API-04).
- Given PostgreSQL is unavailable, then every data endpoint returns 503 "Service temporarily unavailable." with no partial result. Given Redis is unavailable, then only the explanation job endpoint returns 503, and other endpoints are unaffected.
- Given a ticker with too little history for a trailing feature (fewer than five earlier calls at T0 for the sentiment surprise, or fewer than four prior SUE values for the surprise trend), then the prediction is returned with the label "Limited history" and that feature is marked as unavailable.

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
- Given the evaluation page, then calibration by confidence decile is shown as TR-05 requires.

### FR-11: Reproducibility record (J3)

**Priority.** Should.

**Requirement.** Every stored prediction records the model version and feature-set version.

**Acceptance criteria.**
- Given a prediction is stored, then both version identifiers are present and match a registered model artefact.

### FR-12: Sector-relative scoring (J1, J3, J4)

**Priority.** Should. An extension beyond the proposal (PG-6, Market N7).

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

**Requirement.** Consensus estimates are stored as dated snapshots. This applies to the forward capture job (Data SR-10) and to any licensed consensus source adopted later; the time-series label uses no estimates. Earlier snapshots are never overwritten. A prediction uses only snapshots captured before the announcement date. Capture rules for snapshot-only sources are Data SR-08 and SR-10.

**Acceptance criteria.**
- Given a new consensus estimate arrives for an event, then a new snapshot row is added with its capture timestamp and the earlier snapshot is unchanged.
- Given a prediction for an event announced on date D, then any snapshot captured on or after D is excluded from its inputs.

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
- Given the call being scored and fewer than four calls before it, then the prediction carries the "Limited history" label (FR-07). At T0 the call being scored is the most recent earlier call.

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

**Priority.** Must (Market N6).

**Requirement.** Every prediction shows the training window, the test window, the number of training events and the date of the last retraining.

**Acceptance criteria.**
- Given any prediction card, then all four values are shown and match the ModelVersion record of the model that produced it.

### FR-22: As-of timestamps of inputs (J1, J3)

**Priority.** Must (Market N3).

**Requirement.** Every prediction records and shows the as-of timestamp of each input group: transcript, estimate snapshot, prices, fundamentals and sector context.

**Acceptance criteria.**
- Given a T0 prediction for an event with cutoff C (the earlier of the call time and the 8-K Item 2.02 acceptance time), then every stored as-of timestamp is before C. A test fails the build if any is not. A T1 prediction is labelled "post-call" and records its own transcript time, which is after C. Every other input of a T1 prediction is still before C.
- Given the prediction card, then the timestamps are visible in the same view or one click away.

### FR-23: Label definition shown (J3)

**Priority.** Should (Market N6).

**Requirement.** The evaluation page shows the label route (time-series SUE or consensus), the SUE definition, the beat and miss thresholds in use, the date they were frozen, the dispersion measure used, and the agreement between the time-series label and the consensus label on the prospective set (Data LB-08).

**Acceptance criteria.**
- Given the evaluation page, then the thresholds shown equal the frozen values recorded under Data VL-06.

### FR-24: Full proposal feature set

**Priority.** Must. Any feature dropped later is recorded in the decision log (Project-Wide SS-02).

**Requirement.** The feature matrix contains the features in proposal Sections 4.1 and 5.2. Each feature has a source tag (Data SR-02) and an as-of rule.

| Group | Feature | As-of rule | Detail |
|---|---|---|---|
| Text | Mean FinBERT positive, negative and neutral scores across all analytic sentences (Feature Engineering FE-02, FE-07) | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | FR-16 |
| Text | Sentiment trajectory: first half against second half of the call | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | |
| Text | Uncertainty score: hedge words divided by word count | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | FR-17 |
| Text | Negation frequency | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | FR-17 |
| Text | Question count in the Q&A section | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | FR-15 |
| Text | Forward-guidance ratio: sentences mentioning future quarters divided by total sentences | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | |
| Text | Q&A sentiment delta: analyst question sentiment against management answer sentiment | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | FR-15 |
| Text | Q&A-only sentiment and Q&A-only hedge-word rate | Transcript of an earlier quarter (T0); the event's own transcript (T1 only) | FR-15 |
| Text | Sentiment surprise: z-score against the trailing four quarters | Transcripts of earlier quarters (T0); also the event's own transcript (T1 only) | FR-18 |
| Tabular | Prior four-quarter EPS surprise trend, from the label's own prior SUE values | Prior events announced before D | Data LB-01 |
| Tabular | Revenue growth, gross margin, operating margin | Latest filing filed before D (Data FD-02). The current quarter's figures are not known before D. | |
| Tabular | Surprise dispersion: standard deviation of the prior 8 seasonal EPS differences (the SUE denominator). Analyst dispersion replaces it only where a consensus standard deviation exists. | EPS first filed before D | Data LB-01 |
| Tabular | Price momentum: three-month return before the announcement | Prices dated before D (Data PX-02) | |
| Sector | Sector context: peer mean SUE and peer count | Peer events announced before D | SRS-08 |

**Acceptance criteria.**
- Given the feature-set version, then every feature in the table is listed with its source tag and as-of rule, or is listed as dropped with a decision-log reference.
- Given a fixture event, then each computed feature equals a hand-calculated value.

### FR-25: FinBERT pretraining-cutoff check

**Priority.** Must (Proposal 5.4).

**Requirement.** The relationship between FinBERT sentiment and the outcome is compared for transcripts close to FinBERT's pretraining-corpus cutoff and for transcripts well after it, to look for a jump at the cutoff that would suggest the pretraining corpus overlaps with later outcomes.

**Acceptance criteria.**
- Given the evaluation report, then it contains a per-quarter series of a sentiment-only metric with the pretraining cutoff marked, and the result is stated either way. If no labelled quarter lies before the cutoff, the report says the check cannot show a jump and gives the reason (Modelling and Evaluation MD-20).

### FR-26: Global SHAP and domain consistency

**Priority.** Must (Proposal 5.3, 7).

**Requirement.** The evaluation shows global SHAP importance for the full model and checks named features against expected directions from domain knowledge (for example, a higher uncertainty score is expected to push toward miss).

**Acceptance criteria.**
- Given the evaluation page, then it shows mean absolute SHAP value for every feature.
- Given at least four named features, then their expected directions are recorded before the test set is read, and the observed direction is shown beside each. Mismatches are reported, not hidden.

### FR-27: External benchmark replication (J3)

**Priority.** Should. Research use only.

**Requirement.** The baseline pipeline is run on a published labelled benchmark, so the project has an external anchor for its numbers. The benchmark is FinCall-Surprise (2019 to 2021, IBES consensus with forecasts issued up to one month after the call), or the SAE-FiRE dataset if it becomes available. Results are reported separately, with the benchmark's own label stated, and are never mixed with the project's results.

**Acceptance criteria.**
- Given the benchmark, then the tabular-only and text-augmented baselines are run with the same features and split rules as the main model, where the benchmark supplies the inputs. Features it cannot supply are listed and left out of both models, and if it supplies no tabular input only the text model is reported and the report says so. Accuracy, weighted F1 and binary AUC are reported with intervals.
- Given the report, then the benchmark's label definition, licence (CC BY-NC-ND for transcripts; the repository is Apache-2.0) and the note that its label uses post-call forecasts are stated beside every number.
- Given any comparison with SAE-FiRE (AUC 0.620), then it is labelled as indicative, because the label, period and universe differ.
- Given the public demo, then no benchmark data is shown or redistributed (Data SR-03).

### FR-28: Limitations notice before first use

**Priority.** Must (Market N6).

**Requirement.** Before first use, the user sees a short summary of what the system cannot do: no live calls, no scoring of events that have not yet been announced, historical testing only, the label definition in use, and the known data limits.

**Acceptance criteria.**
- Given a first visit, then the notice is shown before the first prediction.
- Given any screen, then the notice can be reopened from that screen.

### FR-29: Post-call result reported separately (J3)

**Priority.** Should (decision C-17).

**Requirement.** The evaluation reports the T1 post-call result separately from the T0 forecast, labelled a nowcast, on the same split and metrics as FR-06.

**Acceptance criteria.**
- Given the evaluation page, then the T1 result is in its own table labelled "post-call nowcast, not a forecast", with the same metrics, intervals and rows as the T0 table.
- Given any headline claim, then it names T0 or T1.

## 4A. Sector-Relative Scoring Requirements

These requirements break FR-12 into its parts. They apply only if FR-12 is built. Where a requirement is marked "Must if built", FR-12 may not ship without it, because it protects the no-lookahead claim.

Definitions used in this section:
- **D**: the announcement date of the event being scored.
- **Peer**: another company in the same sector and in the S&P 500 on D.
- **Peer SUE**: the SUE of a peer's most recent eligible event (SRS-04, SRS-05).

### 4A.1 Sector Classification

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-01 | Must if built | The sector of each company on each date comes from a dated sector history. The current classification is never used for a past date. | Data VL-11: a company reclassified in 2023 shows its old sector before the change date. | Data SEC-01 |
| SRS-02 | Should | The sector level is the GICS sector, as the GICS structure stood on D. The GICS version is stored with each assignment, because the number of sectors changed during 2015 to 2024 (Real Estate was split out in 2016, Communication Services was created in 2018). | A test date in 2015 resolves to the structure in force then, and the stored version matches it. | Data SEC-01 |

### 4A.2 Peer Set

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SRS-03 | Must if built | Peers are the companies in the S&P 500 on D (point-in-time membership) whose sector on D matches the event's sector. The company itself is excluded. | Unit test on a fixed date with a known peer set passes. A company removed from the index before D is not a peer. | Data SEC-02, IM-01 |
| SRS-04 | Must if built | Each peer contributes one event: its most recent event announced strictly before D and no more than 100 days before D (proposed). Peers that announce on D or later are excluded. The window covers early reporters in a quarter, which would otherwise have almost no peers. | Test: a peer announcing on D is excluded; a peer with two events in the window contributes only the later one; a peer whose last event is 101 days before D is excluded. | Data GATE-3; Data VL-03 |
| SRS-05 | Must if built | A peer event is eligible only if its own SUE is valid under the label route in use: for the time-series label, at least 6 prior seasonal differences and a non-zero standard deviation (Data LB-02); for a consensus label, at least three estimates (Data CE-04) captured before the peer's own announcement (FR-14). Ineligible peers are counted and reported. | Test: a peer event with 5 prior seasonal differences (or two estimates, under a consensus label) is excluded and counted. | Data CE-04; FR-14 |

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
| SRS-09 | Must if built | The realised score is (event SUE minus peer mean) divided by peer standard deviation, using the peer statistics stored for D. It is computed only after the event's actual EPS is released. It is never a model input. | Feature-matrix schema test: no column is derived from the event's own SUE. Before the announcement, the API returns "Pending" for the realised score. | Market N7; FR-03 |

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
| SRS-14 | Must if built | If point-in-time sector history cannot be obtained (Data SEC-01 fails), the sector features and display are switched off, the feature-set version records this, and the gap is reported. Current sectors are never used as a substitute. | Configuration test: with sector history missing, no sector column is produced and the card shows "Sector comparison unavailable". | Data SEC-01; Section 18 |

## 4B. Explanation Requirements

The explanation layer is judged on whether its claims are supported, not on how well it reads. These requirements apply to any LLM-generated explanation. They implement need N2.

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| EX-01 | Must | Every factual claim in an explanation links to a feature or a cited transcript sentence. | A claim with no link is rejected before the explanation is stored. | FR-05; grounded-generation checks |
| EX-02 | Must | Each claim receives a faithfulness label (supported or unsupported) with a short reason, recorded with the explanation. | Every stored claim has a label and a reason. | Grounded-faithfulness evaluators (Arize Phoenix) |
| EX-03 | Must | The explanation discusses only features in the top-ranked SHAP set for that prediction. | Rank-agreement test on the evaluation sample. | Ichmoukhamedov et al.; Proposal 5.5 |
| EX-04 | Must | When retrieval finds no supporting sentence, the output says so. It does not generate a rationale. | Fixture with no matching sentence returns the no-evidence message. | FR-05; Proposal 4.3 |
| EX-05 | Should | A random sample of explanations is rated by a human reviewer, and agreement with the automated labels is reported. | Agreement statistic exists for the sample. | Proposal 5.5; He and Martens (2026) |

## 5. Non-Functional Requirements

Thresholds are proposed and are to be agreed with the supervisor (decision D-05). Withdrawn NFR numbers are listed in the README registry and are not reused.

| ID | Priority | Area | Requirement | Threshold |
|---|---|---|---|---|
| NFR-01 | Should | Latency | Cached prediction response time, 95th percentile. | Under 500 ms |
| NFR-02 | Should | Latency | Full explanation response time, 95th percentile, from request to complete status. | Under 10 s, or returned as pending |
| NFR-03 | Should | Freshness | The daily check for new transcripts (Ingestion IG-05) runs at least once in every 24 hours. Each transcript it finds is stored in that run unless a source limit defers it (IG-07). Deferrals and the latest transcript date per ticker are shown in /health (PL-03). | Check runs every 24 hours |
| NFR-04 | Must | Availability | The service reports its own health. No uptime percentage is promised for the demo. | /health returns 200 when the database, Redis and worker are healthy, and 503 when one is not |
| NFR-07 | Should | Accessibility | Dashboard meets WCAG 2.1 AA colour contrast, checked by an automated accessibility tool. Chart alternatives and keyboard operation are UI-02 and UI-05. | Automated check passes |
| NFR-08 | Could | Responsiveness | Dashboard usable at 375 px width. | No horizontal scrolling on prediction card |
| NFR-09 | Should | Batch throughput | Backfill of the full target corpus (4,000-5,000 events) on demo infrastructure. | Completes within 24 hours |
| NFR-11 | Must | Request logging | Every API request is logged with a request identifier, latency and status code. | 100% of requests |
| NFR-12 | Should | Service metrics | Latency and error rate exposed for scraping. | Available at /metrics |
| NFR-13 | Should | Time to first result | A new user gets a first prediction within five minutes, without installing anything. | Five minutes |

## 6. API Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| API-01 | Must | The OpenAPI specification is generated from code and served with the API. | Specification validates and matches every endpoint in Section 13. |
| API-02 | Must | All endpoints except /health and /metrics sit under the /v1 path prefix. | Requests to unversioned paths other than /health and /metrics return 404. |
| API-03 | Should | Every error response has the same shape: code, message and request identifier. | Contract test checks the shape for 404, 422, 401, 429 and 503. |
| API-04 | Must | Prediction endpoints return the envelope: data, warnings array and model_version. | Contract test on each prediction endpoint. |
| API-05 | Should | The history endpoint is paginated, with a default page size of 20 and a maximum of 100. | Request for 500 rows returns 100 with a next-page link. |
| API-06 | Must | Every endpoint except /health requires a JWT. This includes /metrics, which is outside /v1 only because of API-02. | Request without a token returns 401. |
| API-07 | Should | Each client is rate limited, and a limited request returns 429 with a Retry-After header. | Load test exceeding the limit returns 429 with the header present. |

## 7. Data Pipeline Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| PL-01 | Must | Scheduled ingestion jobs record start time, end time, status and row counts. | Each run produces a log row that can be queried. |
| PL-02 | Must | Failed ingestion tasks retry up to three times with exponential backoff, then move to a dead-letter queue. | Injected failure produces three retries and one dead-letter entry. |
| PL-03 | Should | Each ticker's latest transcript date is reported through /health. | Health response lists the date for a test ticker. |
| PL-04 | Must | Events missing actual EPS, or missing the EPS history the label needs (Data LB-02), are rejected, and the reason is logged. Under a consensus label, a missing estimate mean also rejects the event. | Fixture with insufficient EPS history is rejected with the logged reason. |
| PL-05 | Must | Schema changes are made only through versioned migrations. | Migration history matches the deployed schema on a clean database. |
| PL-06 | Must | Raw transcripts are stored unchanged. Cleaned text is stored in a separate column. | Hash of raw text is identical before and after cleaning. |

## 8. Machine Learning Pipeline Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| ML-01 | Must | Random seeds are fixed and recorded for every training run. Retraining from a stored data snapshot with the same seed reproduces the reported metrics to two decimal places. | Two runs with the same seed and snapshot produce identical predictions, and the metrics match to two decimal places. |
| ML-02 | Must | Hyperparameters are tuned on the 2022 validation set only. The 2023-2024 test set is read once, for final evaluation. | Access log shows test rows read only in the final evaluation job. |
| ML-03 | Must | Each model artefact is saved with its version and a SHA-256 checksum. Loading verifies the checksum. The artefact format is set by Project-Wide SP-01. | Altered artefact fails to load with a checksum error. |
| ML-04 | Must | The SHAP explainer is built from the same artefact as the served model. | Explainer and model share the artefact identifier. |
| ML-05 | Must | A training run writes its metrics report before the model is registered. | Registration fails if the report file is missing. |
| ML-06 | Must | A model is promoted to serving only after the FR-06 comparison has been run on the sealed test set and reported, and the sign-off of a reviewer who did not build the model is recorded. Every retrain is a new model version and passes the same gate before it replaces the served model. The full model does not have to beat the baselines: a negative result is valid (Proposal 7) and is shown on the evaluation page. | Promotion step checks that the comparison report and the sign-off record both exist for the new version. |

## 8A. Evaluation and Trust Requirements

These are the checks a quantitative user applies before reading any headline number. They implement need N3 and N4.

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| TR-01 | Must | Report bootstrap confidence intervals, resampling by event, on all headline metrics. | Every headline metric on the evaluation page has a 95% interval. | N3; Harvey and Liu (2015) on noise in backtests |
| TR-02 | Must | Disclose the number of model variants tried and apply a multiple-testing adjustment to the headline result. | The evaluation page states the variant count and the adjustment. | N3; Harvey and Liu (2015) |
| TR-04 | Should | Report performance separately for 2023 and 2024, and by sector where a dated sector history exists (SEC-01), to show whether results are stable. | Per-year table exists, and a per-sector table where sector history exists. | N3; Proposal 5.3 |
| TR-05 | Should | Report calibration by confidence decile, not only one Brier score. | Decile calibration plot exists. | FR-10; Proposal 5.3 |
| TR-06 | Must | Report two naive baselines: majority class, and repeating the previous quarter's surprise class. | Both appear in the FR-06 table on the same rows. | N4; FR-06 |

The sealed test set read once is ML-02.

## 8B. Model Governance and Monitoring Requirements

These follow the core expectations of SR 11-7, the US supervisory guidance on model risk management. The project is not subject to that regulation. The guidance is used because it sets out what a careful reviewer expects from a deployed model. Independent review and re-evaluation on retrain are ML-06.

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| MR-01 | Should | Keep a model inventory entry for each version: owner, purpose and status. | Every registered version has an entry. | FR-11; SR 11-7 inventory |
| MR-02 | Must | Publish a model card for each version covering objective, data, assumptions, limitations and tests. | Model card exists for every served version. | FR-21; SR 11-7 documentation |
| MR-04 | Should | Compare predictions with realised outcomes on a rolling basis after release, not only at training time. | Rolling outcome table exists. | FR-09; SR 11-7 outcomes analysis |
| MR-05 | Should | Monitor input feature distributions for drift, with alert thresholds set from the training baseline. | Drift report runs on the schedule. | SR 11-7 ongoing monitoring; SageMaker Model Monitor |
| MR-06 | Should | Monitor the rank order of top SHAP features over time and flag large changes. | Rank-change flag fires on a planted change. | SageMaker Model Monitor feature attribution drift |

## 9. User Interface Requirements

| ID | Priority | Requirement | Acceptance check |
|---|---|---|---|
| UI-01 | Could | Ticker search offers autocomplete from the universe (EP-10). | Typing two letters shows matching tickers. |
| UI-02 | Should | Every chart has a text alternative and a switch to a data table. | Automated accessibility check finds no chart without an alternative. |
| UI-03 | Must | The explanation view shows the verification status beside each citation. | Each citation in the view has a visible status. |
| UI-04 | Could | A sector comparison view shows the peers used for a prediction (SRS-12). | View lists every peer used in the calculation. |
| UI-05 | Should | All controls can be reached by keyboard, with a visible focus indicator. | Keyboard-only walkthrough completes Journey J1. |

## 10. Operations Requirements

Operations, security and engineering requirements are defined in the Project-Wide Requirements. Product-level operational thresholds are in Section 5 (NFR). The three operations requirements that were here are withdrawn: secrets handling is Project-Wide SP-06, pinned container builds are EQ-04 and the rollback drill is DO-04.

## 11. Data Model

| Entity | Key fields | Notes |
|---|---|---|
| Company | company_id, name | company_id is a permanent identifier that survives ticker changes (Data IM-03). |
| TickerHistory | company_id, ticker, valid_from, valid_to | Data IM-03. Tickers are looked up as of a date. |
| IndexMembership | company_id, valid_from, valid_to, removal_reason | One row per membership spell, so a company can leave and rejoin (Data IM-01, IM-02, IM-03). |
| SectorAssignment | company_id, gics_sector, gics_version, valid_from, valid_to | SRS-01, SRS-02; Data SEC-01. |
| EarningsEvent | event_id, company_id, transcript_id, period_end, fiscal_period, transcript_date, information_date, announcement_date, announcement_time_utc, release_accession, eps_basis, label_route, sue, sue_reason, differences_used, splits_applied, incomplete, status (included or excluded), exclusion_reason, eps_accession, eps_filed_at | FR-02; Data DV-06, DV-07, AE-03 (decision C-53). Table `earnings_event`. Built so far: the columns listed. The class `label`, derived from SUE thresholds frozen during EDA, and `consensus_label` (prospective set only) are added by the steps that create them. |
| ActualEps | event_id, version, value, basis, source, document_id, released_at | Data AE-01 to AE-04. The first-reported value is kept; corrections are new versions. |
| EstimateSnapshot | snapshot_id, company_id, event_id (nullable until the event is built), mean_estimate, low_estimate, high_estimate, std_estimate (nullable), estimate_count, eps_basis, period_label, source, source_version, captured_at, raw_payload (decision C-44) | FR-14; Data SR-10, CE-01, CE-04. Append-only. Holds the forward capture set. |
| EpsHistory | eps_id, company_id, period_start, period_end, period_kind, filing_fiscal_year, filing_fiscal_period, eps_diluted, derived (boolean), basis, form, accession, filed_at, payload_id | Data LB-01 to LB-05 (decision C-53). Table `eps_history`. One row per version: first-filed values are kept and restated values are new rows. The fiscal year and period describe the filing, not the quarter. |
| FundamentalsFiling | fundamentals_id, company_id, period_start, period_end, filing_fiscal_year, filing_fiscal_period, revenue, revenue_tag, gross_profit, operating_income, derived, form, accession, filed_at, payload_id | FR-24; Data FD-01 to FD-04 (decision C-53). Table `fundamentals_filing`. One row per version. |
| Transcript | transcript_id, company_id, ticker, fiscal_year, fiscal_quarter, call_date, call_at, source, source_ref, payload_id, release_accession, release_accepted_at, raw_text, raw_hash, cleaned_text, cleaning_rules_version, turns (speaker, role, section), segmentation_status, boundary_turn, status (kept or duplicate), call_type | PL-06, FR-05; Data SR-04, TX-01 to TX-06 (decision C-53). The event refers to its transcript. The source address and retrieval time are those of the stored payload. |
| TranscriptSection | section_id, transcript_id, kind (prepared or qa), text | FR-15. |
| TranscriptSentence | sentence_id, transcript_id, section_id, position, text, speaker, role, analytic, truncated, finbert_positive, finbert_negative, finbert_neutral, model_revision, hedge_count, negation_count, word_count | One row per sentence and FinBERT revision (decision C-68). Built so far: all fields except hedge_count, negation_count and word_count. One row per sentence, so the explanation agent retrieves the sentences behind a feature by plain SQL (decision C-11). FR-05, FR-15 to FR-17; EX-01. A forward-guidance field is added when decision D-34 settles the rule. |
| FeatureVector | event_id, feature_set_version, features (JSON), computed_at | FR-24. Tabular, text and sector features in one row per event. |
| SectorBenchmark | event_id, sector, gics_version, as_of_date, peer_event_ids (JSON), mean_sue, std_sue, peer_count, status | SRS-10. Stored with the as-of date so the no-lookahead rule can be checked. |
| ModelVersion | model_version, trained_on_from, trained_on_to, training_event_count, metrics (JSON), artefact_path, checksum, seed, retrained_at | FR-11, FR-21, ML-01, ML-03. |
| PriceDaily | price_id, company_id, ticker, price_date, close_raw, volume, source, source_version, captured_at, payload_id | Data PX-01 to PX-03 (decision C-49). The raw close only, never an adjusted one. Append-only. |
| AdjustmentFactor | factor_id, company_id, ex_date, kind (split or dividend), value, source, source_version, captured_at, payload_id | Data PX-01, LB-05 (decision C-49). A split value is the share ratio and a dividend value is the cash amount per share, as the source reports it. Append-only. |
| Prediction | prediction_id, event_id, model_version, feature_set_version, class, probabilities, confidence, input_as_of (JSON), created_at | FR-01, FR-11, FR-22. Realised outcome and realised sector score joined from EarningsEvent and SectorBenchmark. |
| Explanation | explanation_id, prediction_id, features (JSON), citations (JSON), verification_status, job_status, prompt_version, llm_model_version, generation_settings (JSON), created_at | FR-04, FR-05, FR-19; Project-Wide AI-01. |
| ClaimLabel | claim_id, explanation_id, claim_text, label, reason | EX-02. |
| IngestionRun | run_id, job_name, source, started_at, ended_at, status (running, succeeded, failed), rows_read, rows_written, error_class, task_id | PL-01; Ingestion IG-03. Table `ingestion_run` (decision C-45). |
| DeadLetter | dead_letter_id, task_name, args_hash, error_class, failed_at, attempt_count, run_id | PL-02; Ingestion IG-02. Insert only (decision C-45). |
| Quarantine | quarantine_id, source_table, row_key, reason, detail, first_seen_at, reviewer_note | Data DV-01, DV-04 (decision C-53). Rows that fail a check are listed for review and are not removed from their own table. |
| RawPayload | payload_id, source, url, retrieved_at, sha256, content_type, byte_length, body, source_version (empty where the source states none) | Database DB-11; Ingestion IG-10; Data SR-04. Insert only, one row per source, URL and hash (decisions C-45, C-51). |

## 12. Error States

| ID | Condition | User sees | System does |
|---|---|---|---|
| ER-01 | No earlier transcript for ticker (cold start) | "No transcript available for this ticker." | Logs the request; no prediction stored. |
| ER-02 | Ticker not in universe | "Ticker not in universe." (404) | Logs the request. |
| ER-03 | Invalid ticker format | "Invalid ticker format." (422) | Rejects before lookup. |
| ER-04 | Data source failure during ingestion | "Data refresh failed on <date>. Showing the last stored result." beside the stored prediction. | Retries up to three times, then dead-letters the task (PL-02); marks the run failed (PL-01); /health shows ingestion degraded; stores no partial event. |
| ER-05 | Rate limit exceeded | "Too many requests. Try again shortly." (429) | Returns Retry-After header. |
| ER-06 | Limited history | Prediction with "Limited history" label. | Marks trailing features as unavailable. |
| ER-07 | Segmentation failed | "Q&A analysis unavailable for this call." | Stores Q&A features as unavailable. |
| ER-08 | Insufficient peers | "Insufficient peers" in the sector section. | Stores sector features as unavailable (SRS-06). |
| ER-09 | Sector history unavailable | "Sector comparison unavailable." | Sector features switched off (SRS-14). |
| ER-10 | Realised sector score before announcement | "Pending." | No value computed (SRS-09). |
| ER-11 | Citation not found | Explanation marked "partially verified". | Logs the failure with prediction identifier. |
| ER-12 | Explanation job failed | "Explanation could not be generated." | Stores the failure reason and returns it with the status. |
| ER-13 | Model artefact missing or checksum mismatch | "Service temporarily unavailable." (503) | Refuses to serve; logs an error line with the request identifier and the artefact identifier, and sets the artefact check in /health to failed (SV-08). |
| ER-14 | Database or queue unavailable | "Service temporarily unavailable." (503) | Logs the request identifier; returns no partial result. |

## 13. API Surface

| ID | Method | Path | Purpose | Requirement |
|---|---|---|---|---|
| EP-01 | GET | /v1/predictions/{ticker} | Latest prediction, top three features, evidence base, input as-of times and sector context. | FR-01, FR-04, FR-21, FR-22, SRS-11, API-04 |
| EP-02 | GET | /v1/predictions/{ticker}/sector | Peer list and statistics behind the sector context and realised score. | SRS-10, SRS-12 |
| EP-03 | GET | /v1/predictions/{ticker}/explanation | Explanation with citations and verification status. | FR-04, FR-05, FR-19 |
| EP-04 | POST | /v1/predictions/{ticker}/explanation/jobs | Starts an explanation job and returns the job identifier. | FR-19 |
| EP-05 | GET | /v1/jobs/{job_id} | Status of an explanation job. | FR-19 |
| EP-06 | GET | /v1/predictions/{ticker}/history?from=&to=&page= | Past predictions with outcomes and realised sector scores. | FR-09, SRS-09, API-05 |
| EP-07 | GET | /v1/evaluation/metrics?model=full\|tabular\|majority\|previous\|consensus | Test-set metrics for a model version. | FR-06, FR-10, FR-23, FR-26 |
| EP-08 | GET | /health | Service, data freshness and ingestion status. | NFR-03, PL-03 |
| EP-09 | GET | /metrics | Service metrics for scraping. | NFR-12 |
| EP-10 | GET | /v1/universe | Tickers in the universe with company names, for ticker autocomplete. Could. | UI-01, FR-20 |

## 14. Screens

| ID | Screen | Contents | Journey | Priority |
|---|---|---|---|---|
| SCR-01 | Ticker search | Input field, submit. Autocomplete if UI-01 is built (EP-10). | J1 | Must |
| SCR-02 | Prediction card | Class, probabilities, confidence, evidence base, input as-of times, sector context (SRS-11), not-investment-advice notice, link to explanation. | J1 | Must |
| SCR-03 | Feature chart | Horizontal bars for top three SHAP features, coloured by direction, with a data table alternative. | J1, J2 | Must |
| SCR-04 | Explanation view | Each claim, its faithfulness label, the cited sentence and its verification status. | J2 | Must |
| SCR-05 | History table | Date, class, confidence, realised outcome, realised sector score, pending state, pagination. | J4 | Must |
| SCR-06 | Evaluation page | Baseline comparison table with confidence intervals, calibration plot, precision at top 20%, global SHAP, label definition, limitations notice. | J3 | Must |
| SCR-07 | Sector comparison | Peer list and statistics (SRS-12). | J1 | Could |

## 15. Success Metrics

| ID | Metric | Target | Counter-metric | Why the counter-metric matters |
|---|---|---|---|---|
| SM-01 | Full model against tabular baseline on 2023-2024 test set | F1 and AUC difference reported with 95% bootstrap intervals. No pass mark: a negative result is valid (Proposal 7). | Brier score reported beside it | A higher AUC with poor calibration misleads users about confidence. |
| SM-02 | Binary AUC (beat against miss, in-line excluded) | Reported beside the SAE-FiRE XGBoost baseline (0.620 on calls) as a reference point, not a pass mark. The label, period and universe differ, so the comparison is indicative only (FR-27). The three-class AUC is not compared with it. | Share of events excluded as in-line | Excluding the middle band makes the binary task easier. |
| SM-03 | Precision at top 20% | Reported; no target until baseline known | Coverage: share of events receiving a prediction | High precision on a small subset is not useful if most events are excluded. |
| SM-04 | Sector context coverage (SRS-13) | At least 90% of predictions have a numeric sector context (proposed) | Share showing "Insufficient peers", by year and sector | A score that is hidden for most events is not useful, so coverage must be reported beside the score. |
| SM-05 | Citation verification rate | 100% verified or flagged | Explanation length | Verifying shorter explanations is easier and could hide weak evidence. |
| SM-06 | Rank and sign agreement | Reported on held-out sample | Number of features discussed per explanation | Discussing more features raises agreement chances without raising faithfulness. |
| SM-07 | Claim faithfulness rate (EX-02) | Reported per explanation | Human agreement with automated labels (EX-05) | Automated labels that humans disagree with are not evidence of faithfulness. |
| SM-08 | Usability (five test users, after ethics approval, Project-Wide ET-01) | All complete J1 without help | Time to complete J2 | Fast completion can mean users skipped the explanation. |

## 16. Milestones

Aligned to Section 6 of the proposal. Weeks are a guide, not a commitment. Calendar targets set by the owner (end of December 2026 for the pipeline, models, API, explanation agent and evaluation; late February 2027 for submission) are in the [decision log](../decision-log.md), C-06 and C-13, and take precedence over the week numbers below. Two changes from the proposal's order are recorded: the explanation layer comes before the frontend, so the dashboard can show explanations, and the API is deployed at the hardening milestone rather than at the backend milestone.

| Weeks | Milestone | Done when |
|---|---|---|
| 1-2 | Requirements, data verification (Data Sections 4A and 12) | Label route agreed with the supervisor; free sources tested; the forward consensus capture job (Data SR-10) is running; this document agreed. |
| 3-5 | Data pipeline and feature engineering | Feature matrix stored; EDA notebook complete (Feature Engineering FE-32); SUE thresholds frozen; PL-01 to PL-06, FR-02, FR-03, FR-13 to FR-18, FR-24 tests pass; SRS-01 to SRS-08 pass if FR-12 is built. |
| 6-7 | Model development and baseline comparison | Full model and baselines trained; ML-01, ML-02, ML-05 pass; FR-06, FR-25, FR-26 and FR-27 results available. |
| 8-9 | Backend endpoints | Section 13 endpoints running; API-01 to API-07, FR-01, FR-04, FR-07, FR-09, FR-20, FR-21, FR-22 pass; SRS-09 to SRS-11 pass if FR-12 is built. |
| 10-11 | Explanation layer and citation verification | FR-05, FR-19, EX checks pass on test set; faithfulness rates reported. |
| 12-13 | Frontend and usability testing | Must screens in Section 14 live; UI-03 passes; five-user test complete if ethics approval is in place. |
| 14-15 | Hardening and deployment | The non-functional requirements in Section 5 measured and recorded; Project-Wide SP-06, EQ-04 and DO-04 pass; ML-06 sign-off recorded. |
| 16 | Write-up and presentation | Dissertation draft; demo recorded. |

## 17. Dependencies

| Dependency | Needed for | Status |
|---|---|---|
| Diluted EPS history from SEC EDGAR | FR-01 (time-series SUE label), FR-03 | Free and public. Early-period coverage and fourth-quarter derivation to check (Data LB-03). |
| Consensus snapshots, captured forward | Prospective check set (Data LB-07, LB-08), FR-14 | Free sources, current values only. Capture must start in week 1 (Data SR-10). |
| Point-in-time consensus history (optional) | A consensus label as in the proposal | Not required. Needs a licensed source (Data Section 4A.2). |
| Transcript source with licence for demo | FR-01, FR-05, FR-15 | Unverified (Data TX-04, SR-03) |
| Index membership history | FR-03 universe, SRS-03 peer set | Unverified (Data IM-01, IM-02) |
| Point-in-time GICS sector history | FR-12, SRS-01 | Unverified (Data SEC-01). If unavailable, SRS-14 applies. |
| Quarterly fundamentals with filing dates | FR-24 (revenue growth, margins) | Unverified (Data FD-01) |
| FinBERT model weights | FR-16 | Available (HuggingFace). Licence to be recorded (Project-Wide ET-03). |
| GCP project for deployment | NFR-01, NFR-04, Project-Wide DO-04 | To be set up |

## 18. Risks

| Risk | Likelihood | Impact | Mitigation |
|---|---|---|---|
| Point-in-time estimates unavailable | Certain on the free route | High | Time-series label (Data LB-01 to LB-08) with the limitation stated, a prospective consensus check, and no claim of agreement with consensus-based studies. |
| Time-series label is a weak proxy for analyst surprise | Medium | High | Report agreement on the prospective set (Data LB-08) whatever it shows. State the limitation in the evaluation page (FR-23). |
| Consensus capture starts late or has gaps | Medium | Medium | Start the job in week 1 (Data SR-10). Report gaps and flag affected events. |
| Transcript source unavailable or unlicensed | High | High | Check library access. Use a licensed fallback (Data Section 4), or restrict the demo to a historical slice. |
| Sector history wrong for past quarters | Medium | High | Use the point-in-time sector source (Data SEC-01). If unavailable, switch sector scoring off (SRS-14). Never use current sectors. |
| Early reporters have too few peers | Medium | Medium | 100-day peer window (SRS-04). Report coverage (SRS-13). |
| Fundamentals filed after the announcement leak into features | Medium | High | Use only filings filed before D (FR-24, Data FD-02). |
| FinBERT pretraining overlaps test period | Medium | High | FR-25. Report result either way. |
| Explanation agent produces unfaithful narratives | Medium | Medium | FR-05, EX-03, EX-04 and rank and sign agreement metrics. Report the rate. |
| Test set read during tuning | Low | High | ML-02 access log. Any read outside final evaluation invalidates the headline result. |
| Feature drift after release | Medium | Medium | Monitor feature distributions and top-feature rank order against the training baseline (MR-05, MR-06, Should). |
| Scope creep from design notes | High | Medium | Non-goals in Section 2.2 are fixed for this version. Stretch objectives in Section 2.3 are Could. |
| Effort exceeds 15-20 hours per week | Medium | High | Drop Could items first, then Should items, in the drop order agreed under Project-Wide PD-02. |

## 19. Open Questions

Open questions are in the [decision log](../decision-log.md). Those that concern this document: D-05 (non-functional targets), D-07 (peer window and minimum peers), D-09 (independent reviewer), D-22 (FinBERT cutoff date) and D-23 (SUE thresholds).

## 20. Sources Checked

- Plannotator, product requirements document guidance: https://docs.plannotator.ai/learn/planning/what-is-a-product-requirements-document
- Amazon SageMaker Model Monitor, arXiv:2111.13657: https://arxiv.org/pdf/2111.13657
- Arize Phoenix, faithfulness evaluator: https://www.arize.com/docs/phoenix/evaluation/pre-built-metrics/faithfulness
- Harvey, C. and Liu, Y., "Backtesting", Duke University working paper: https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF
- SR 11-7 model risk management summary: https://www.magicmirrorsecurity.com/blog/sr-11-7-model-risk-management-guidance-explained
- Project proposal, Third Year Project Proposal (2026-27), as uploaded.
- Market Requirements document, `docs/requirements/market-requirements.md`.

Points marked "to be set up" or "unverified" have not been confirmed against primary sources. The SR 11-7 and Harvey and Liu sources were read through summaries, not the primary texts. The GICS structure changes in SRS-02 (Real Estate in 2016, Communication Services in 2018) are from memory and should be checked against S&P's published history before SRS-02 is tested.
