# Modelling and Evaluation Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns how the models are trained, tuned, calibrated, explained, scored and evaluated. Product Section 8 (ML-01 to ML-06), Section 8A (TR) and FR-03, FR-06, FR-10, FR-25 and FR-26 state what must hold. They do not say which task is trained, how confidence is defined, which SHAP output is used for three classes, how calibration is fitted, or how the metrics are computed. This document does.

Retraining is started by hand. There is no scheduled retrain in this version. Every retrain is a new model version and passes the Product ML-06 gate.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a value the project leaves open says "pending D-42", and it is not final until John decides D-42 in the [decision log](../decision-log.md) (Project-Wide SS-02). Research on the internet informed the choices in Section 2 and is listed in Section 8. It is not a requirement by itself.

| Already defined elsewhere | Where |
|---|---|
| Two XGBoost models, temporal split, test set read once | SSOT Section 6; Product FR-03, ML-02 |
| Baseline comparison, metric list, naive baselines | Product FR-06, TR-06 |
| Intervals, variants tried, per-year and per-sector, decile calibration | Product TR-01, TR-02, TR-04, TR-05 |
| Seeds, artefact checksum, explainer from the same artefact, report before registration, promotion gate | Product ML-01, ML-03, ML-04, ML-05, ML-06 |
| Model format | Project-Wide SP-01 |
| Calibration and precision display; global SHAP; pretraining-cutoff check | Product FR-10, FR-26, FR-25 |
| Model inventory, model card, drift monitoring | Product MR-01 to MR-06 |
| Label thresholds frozen on 2015 to 2021 | Data LB-06, VL-06 |
| Features and the feature-set version | Feature Engineering FE-01 to FE-32 |

## 2. Choices made, with the reasons

**Three classes or two.** Recommended: train one three-class model (beat, in-line, miss), and compute the beat-against-miss numbers from the same model's probabilities.

| Option | What it means | Against the project |
|---|---|---|
| A. Binary model | Train beat against miss and drop in-line events | Contradicts Product FR-01, which returns three class probabilities that sum to 1, and PG-1, SSOT Section 4 and Product FR-06 (three-class AUC). Discards the middle band and so many events. |
| B. One three-class model (recommended) | Train beat, in-line, miss. Report three-class metrics and a binary beat-against-miss AUC from the same probabilities | Matches FR-01, PG-1, the SSOT label and FR-06, which already asks for both AUCs. One training run, so one fewer variant to disclose (Product TR-02). The binary AUC lines up with the SAE-FiRE reference (Product FR-27). |
| C. Both models | Train a three-class and a separate binary model | Doubles the variants and the tuning effort. The second model adds nothing over B. |

Cost of B: with a middle band, the in-line class can dominate. FinCall-Surprise's authors report that accuracy can mislead when classes are imbalanced, so accuracy is never the headline (MD-12).

**Evidence on the tools.** Class imbalance for a multi-class XGBoost model is handled by per-row sample weights, because `scale_pos_weight` is for binary targets. Early stopping uses log loss, not accuracy. These come from secondary sources and are to be checked against the XGBoost documentation for the pinned version when the code is written.

## 3. Training

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| MD-01 | Must | The model is an XGBoost classifier with three classes (beat, in-line, miss) and the multi-class probability objective. The class order is fixed, stored in the ModelVersion record and used in every output. Output probabilities sum to 1 within rounding. | Fixture prediction has three probabilities summing to 1.00. The class order in the record matches the output columns. | SSOT Section 4, 6; Product PG-1, FR-01; Section 2 |
| MD-02 | Must | The models trained are: the tabular-only baseline, the full model at T0 (earlier calls only), and, as a Should, the full model at T1 (adds the event's own transcript). They share one split, one tuning procedure and one metric code. The T1 result is reported separately and is never called a forecast (decision C-17). | Report lists the three models with the feature-set version and prediction point of each. | SSOT Section 6; decision C-17; Product FR-06 |
| MD-03 | Must | The training split uses the announcement date: 2015 to 2021 for training, 2022 for validation, 2023 to 2024 for test, with no shuffling across years. No purging window is needed, because a label and every feature use only information dated at or before the announcement, not a forward-looking window. That claim is verified by the date tests, not assumed (Feature Engineering FE-26). | Split test confirms boundaries by announcement date. Date tests pass for all features. | Product FR-03; Data VL-04, GATE-4; Feature Engineering FE-26 |
| MD-04 | Must | Class imbalance is handled by per-row sample weights computed from the training window only. Whether weighting beats no weighting is one tuning variant, decided on the 2022 validation set. | Weights are stored with the run. Changing 2022 data leaves the weights unchanged. | Feature Engineering FE-25; Product ML-02; Section 2 |
| MD-05 | Must | Hyperparameters are tuned on the 2022 validation set only (Product ML-02). The search space and the number of trials are written down before the search starts and are the same for every model compared. Early stopping uses the 2022 log loss and counts as part of tuning. The space and trial count are pending D-42. | Search file is dated before the run. Every model has the same trial count. Test rows are not read. | Product ML-02, FR-06, TR-02; pending D-42 |
| MD-06 | Must | Missing feature values are passed to the model as missing (Feature Engineering FE-24). | A fixture with a missing value trains and predicts. | Feature Engineering FE-24 |
| MD-07 | Must | One command trains a model from a configuration file. The configuration, the data snapshot identifier, the feature-set version, the seed and the code version are stored with the run. The thread count is fixed so two runs with the same seed and snapshot give identical predictions. | Two runs give identical predictions and matching metrics (Product ML-01). | Product ML-01, FR-11 |
| MD-08 | Must | After tuning, the configuration, feature-set version and thresholds are frozen and recorded. One final job then reads the test set (Product ML-02), writes the metrics report before the model is registered (Product ML-05), and stores the model with its checksum. Nothing is refitted on the validation year, because Product FR-03 allows no row after 2021 in training. | Registration fails without the report. Access log shows one test read. | Product FR-03, ML-02, ML-03, ML-05 |
| MD-09 | Must | Models are saved in the XGBoost native format, never pickle, with a SHA-256 checksum checked on load. Artefacts live in a git-ignored folder and are listed in the ModelVersion table. | Altered artefact fails to load. Repository contains no artefact. | Project-Wide SP-01; Product ML-03; `.gitignore` |

## 4. Confidence, calibration and explanation

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| MD-10 | Must | Confidence is the probability of the predicted class after calibration. Precision at the top 20% most confident predictions ranks by that value. | Fixture confidence equals the largest calibrated probability. | Product FR-01, FR-10; Proposal 5.3 |
| MD-11 | Must | Calibration is fitted on the 2022 validation predictions and then frozen. With a few hundred events a year, a one-parameter method (temperature scaling) is recommended over isotonic regression, which needs more data to avoid overfitting. Uncalibrated and calibrated results are both reported, and each counts as a variant (Product TR-02). The method is pending D-42. | Calibration parameters are in the ModelVersion record. Both Brier scores appear in the report. | Product PG-1, FR-10, TR-02, TR-05; pending D-42 |
| MD-12 | Must | The SHAP explainer is built from the registered artefact (Product ML-04). For each prediction, the SHAP values of the predicted class's score are stored: feature name, feature value and signed value, plus the base value for that class. The array for the class actually predicted is used, not a fixed index, and the shape is checked by a test on the installed version, because the output layout differs between versions. | Fixture prediction's SHAP values plus base value equal the predicted class's raw score to 1e-4. A shape test passes. | Product FR-04, ML-04; SSOT Section 6 |
| MD-13 | Must | A feature's direction is stated relative to the predicted class: positive SHAP is "toward" that class and negative is "away from" it. For a predicted miss this is Product FR-04's "toward miss". The explanation agent's sign check uses the same rule (Explanation Agent AG-14). Pending D-42. | Fixtures for each of the three predicted classes give the expected label. | Product FR-04; Explanation Agent AG-14; pending D-42 |
| MD-14 | Must | Global importance is the mean absolute SHAP value per feature over the test predictions, using the predicted class's values, with a per-class table beside it. The directions recorded before the test read (Product FR-26) are stated for the predicted class. | Evaluation page lists every feature with its mean absolute value. | Product FR-26 |

## 5. Metrics and reporting

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| MD-15 | Must | The metric definitions are fixed in code and in the evaluation protocol before the test read: accuracy; weighted F1; three-class AUC (one against rest, macro average); binary beat-against-miss AUC from the same model, using the beat probability divided by the beat plus miss probability on events that are not in-line; Brier score as the mean over events of the squared differences across the three class probabilities; precision at top 20% as the precision of the predicted class among the 20% of events with the highest confidence; and a per-class confusion matrix. No separate binary model is trained. | Hand-calculated fixture matches each metric. | Product FR-06, FR-10; Proposal 5.3 |
| MD-16 | Must | Accuracy is never the only headline number. Per-class precision and recall and the class shares of each year are shown beside it. | Evaluation report has the per-class table. | Product FR-06; Data VL-06; Section 2 |
| MD-17 | Must | Intervals are 95% bootstrap intervals resampling by event, with a fixed seed and a stated number of resamples (proposed 1,000, pending D-42). | Interval code run twice gives identical bounds. | Product TR-01 |
| MD-18 | Must | The two naive baselines are computed on the same test rows: the majority class of the training window, and the previous event's class for the same company. Events with no previous event are listed and handled the same way for every model. | Both appear in the FR-06 table with the exclusion count. | Product TR-06, FR-06 |
| MD-19 | Must | Every model fit counts as a variant: tuning trials, weighted and unweighted, calibration options, feature-set versions and prediction points. The count and the multiple-testing method for the headline result are written down before the test read. The method is pending D-42. | Report states the count and the method, and both are dated before the test read. | Product TR-02; pending D-42 |
| MD-20 | Must | The FinBERT pretraining-cutoff check (Product FR-25) uses, for each quarter, the rank correlation between call-level net sentiment and the event's SUE, plotted with the pretraining cutoff marked. The cutoff date is decision D-22. | Per-quarter series exists with the cutoff marked. If no labelled quarter lies before the cutoff, the report says the check cannot show a jump and gives the reason. | Product FR-25; Proposal 5.4; decision D-22 |
| MD-21 | Must | Evaluation results are produced by code and stored in report tables. The evaluation endpoint reads the stored report and never recomputes. Every number shown links to a stored report row. | Number on the page equals the stored row. | Project-Wide ASM-02; Product Section 13 |

## 6. Scoring job

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| MD-22 | Must | A Celery task scores each event once its features exist, for each prediction point, and stores the Prediction with class, probabilities, calibrated confidence, the top SHAP values (MD-12), the model version and the feature-set version. A lookup reads this stored result and does not score a new transcript live. | Event with features gets one stored prediction per point. A second run adds none. | Decision C-15; Product FR-01, FR-11; Database DB-05 |
| MD-23 | Must | The API refuses to serve a prediction whose model artefact is missing or fails its checksum, and answers with the Section 12 message. Scoring itself needs the artefact only in the scoring job. | Altered artefact makes the endpoint return 503 with the Section 12 message. | Product ML-03, Section 12 |

## 7. Pending items

Choices that need John are in decision D-42: the three-class recommendation (Section 2), the class used for SHAP and direction labels (MD-13), the calibration method (MD-11), the search space and trial count (MD-05), the number of resamples (MD-17) and the multiple-testing method (MD-19). The pretraining cutoff is D-22. The T1 reporting rule is Product FR-29 (decision C-27).

## 8. Evidence read

No requirement above depends on an outside source. Read as background, mostly as summaries:
- XGBoost multi-class guides: the multi-class probability objective, sample weights for imbalance, log loss for early stopping. The official parameter documentation was not retrieved.
- SHAP documentation and guides: the layout of multi-class tree output differs between versions and between libraries, so MD-12 requires a shape test. They also say values are in raw score units, not probabilities.
- scikit-learn calibration documentation: sigmoid is safer than isotonic on small samples, isotonic suits more than about 1,000 samples, and a temperature-scaling option exists in newer versions. Whether the pinned version has it was not checked. The Brier score alone does not show calibration, which is why decile calibration (Product TR-05) is kept.
- Time-series validation guides: purging and embargo matter when labels look forward over a window. This project's label does not, which is why MD-03 needs none. The guides are blogs and one unread paper.
- FinCall-Surprise: accuracy can mislead when classes are imbalanced. Label design tables were not read.

Searches were run on 18 November 2026.
