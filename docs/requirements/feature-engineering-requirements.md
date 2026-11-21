# Feature Engineering Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns the detail of how the feature matrix is built: text preparation, FinBERT scoring, linguistic features, tabular features, assembly and versioning. The proposal (Section 5.2) lists the features and Product FR-24 lists them with as-of rules, but neither says how each one is computed. This document fills those gaps, using only the project's own documents.

Every requirement below has a "Traces to" entry naming the part of the project it comes from: the proposal, the SSOT, an existing requirement, a decision, or [pipeline.md](../architecture/pipeline.md). A requirement that fixes an exact rule the project documents leave open says "rule pending D-36". The rule is then not final until John decides D-36 in the [decision log](../decision-log.md) (Project-Wide SS-02). Ideas that do not trace to the project are not requirements. They are listed in decision D-41.

It does not restate requirements that exist elsewhere. It cites them.

| Already defined elsewhere | Where |
|---|---|
| Segmentation into prepared remarks and Q&A | Product FR-15; Data TX-03, TX-06 |
| Sentence-level FinBERT, rescoring rule | Product FR-16 |
| Hedge and negation features | Product FR-17 |
| Sentiment surprise z-score | Product FR-18 |
| The feature table with as-of rules, and surprise and consensus dispersion | Product FR-24 |
| FinBERT pretraining-cutoff check | Product FR-25 |
| Label (SUE) construction | Data LB-01 to LB-08 |
| Fundamentals, prices | Data FD-01 to FD-04, PX-01 to PX-03 |
| Sector context features | Product SRS-08 |
| Raw and cleaned text storage | Product PL-06 |
| Date gates and feature replay | Data GATE-1 to GATE-5, VL-02 |

## 2. Definitions used in this document

- **Analytic sentence:** a sentence that is not operator speech or safe-harbour boilerplate (FE-02).
- **Word count:** the number of spaCy tokens that are neither punctuation nor whitespace (FE-12).
- **Net sentiment:** FinBERT positive probability minus negative probability, for a sentence or averaged over a call.
- **T0, T1:** the two prediction points in decision C-17 (pipeline.md Section 2.3). T0 is before the release and uses earlier calls only. T1 adds the event's own transcript.
- **Unavailable:** stored as NULL with a reason code. Never zero, never a filled-in average (Product FR-15, FR-17, FR-18).

## 3. Text preparation

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| FE-01 | Must | Each cleaned transcript is split into sentences with spaCy. The spaCy package version and model name are recorded in the feature-set version (FE-28). The same input gives the same sentences in the same order, and each gets a stable `sentence_id` and a `position`. | A fixture transcript with a known sentence count gives that count. Two runs give identical rows. | Proposal 4.1; Product Section 11 (TranscriptSentence); pipeline.md Step 3 |
| FE-02 | Must | Operator turns and the safe-harbour (forward-looking statements) paragraph are marked non-analytic and excluded from every text feature. The mark is stored on the sentence. Reason: those paragraphs are dense in words such as "may" and "could", so counting them would change the uncertainty score for a reason unrelated to what management said. The detection rule is pending D-36. | A fixture call with a safe-harbour paragraph has the same hedge count with and without that paragraph. | Proposal 5.2 (uncertainty score); Product FR-17; rule pending D-36 |
| FE-03 | Must | Every stored sentence text is an exact substring of the stored cleaned text, and cleaning rules are listed and versioned. This is what lets a citation be checked against the source (Product FR-05). | A test finds each sentence in the cleaned text by exact match. | Product PL-06, FR-05 |
| FE-04 | Must | Where speaker roles are missing (Data TX-06), features that need them are stored as unavailable with the reason "no speaker roles". Features that do not need roles are still computed. | Fixture without roles: Q&A sentiment delta is unavailable, mean sentiment is present. | Product FR-15; Data TX-06 |

## 4. FinBERT scoring

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| FE-05 | Must | The FinBERT checkpoint is named exactly, with its revision, and each stored score carries that version (Product FR-16). The model runs in inference mode. It is not fine-tuned in the core scope (SSOT Section 3, stretch). The licence of the weights is recorded in the third-party register (Project-Wide ET-03). The choice of checkpoint is decision D-35. | Score rows have a non-null model revision. Register entry exists. | Product FR-16; SSOT Section 3; Project-Wide ET-03; decision D-35 |
| FE-06 | Must | FinBERT accepts a limited number of tokens per input. A sentence longer than the limit is cut explicitly, the row is flagged `truncated`, and the flagged share is reported (FE-31). It is never cut silently. This is needed because the proposal scores sentence by sentence (Product FR-16) and the model has a fixed input size. | A fixture sentence over the limit is flagged. The truncated share is in the feature report. | Proposal 4.1; Product FR-16 |
| FE-07 | Must | The call-level score for each class is the unweighted mean of that class's sentence probabilities over analytic sentences. This narrows Product FR-24's "across all sentences" to analytic sentences (FE-02). Product FR-24 is edited to match (change entry in the consistency review). | Hand-calculated fixture matches to four decimals. | Proposal 5.2; Product FR-24 |
| FE-08 | Must | Sentiment trajectory is the mean net sentiment of the second half of the analytic sentences minus the mean of the first half, with halves split by sentence position. The middle sentence of an odd count goes to the first half. With fewer than 4 analytic sentences the feature is unavailable. Rule pending D-36. | Hand-calculated fixture matches. Fixture with 3 sentences is unavailable. | Proposal 5.2 (sentiment trajectory); Product FR-24; rule pending D-36 |
| FE-09 | Should | FinBERT scoring speed on the owner's CPU is measured and recorded: sentences per second, and the projected hours for the 100-company subset and for the full corpus. | Benchmark record exists with the hardware stated. | Decision C-08, C-18; Product NFR-09 |

## 5. Linguistic features

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| FE-10 | Must | Hedge words are matched against the Loughran and McDonald uncertainty list (decision C-14). The list file, its source and its retrieval date are stored in the repository and recorded in the feature-set version. A token is counted once. Matching is on the lower-cased token, or on the lemma if the list holds base forms only. The form used is recorded with the list version. The proposal's examples include "believe". Whether "believe" is on that list is unverified and is part of D-34. | Fixture sentences with known hedge counts match. List version is in the feature-set version. | Proposal 5.2; Decision C-14; Product FR-17 |
| FE-11 | Must | The licence of the word list is checked and recorded before it is committed to the public repository. | Register entry exists. | Project-Wide ET-03 |
| FE-12 | Must | Word count is the number of spaCy tokens that are neither punctuation nor whitespace. The same word count is the denominator for every ratio. Uncertainty score and negation frequency use the word count of analytic sentences only. Rule pending D-36. | Fixture with a known word count. | Product FR-17 ("divided by word count"); rule pending D-36 |
| FE-13 | Must | The negation rule is the one approved under decision D-34. The count per sentence is stored with the rule version. Call-level negation frequency is the negation count divided by the word count. | Fixture sentences with known negation counts match. | Proposal 4.1 (negation frequency); Product FR-17; Decision D-34 |
| FE-14 | Must | Each sentence has a stored forward-guidance flag, set by the rule approved under D-34. The ratio is flagged analytic sentences divided by analytic sentences, and is unavailable when there are none. | Fixture with 4 flagged of 20 gives 0.2000. | Proposal 5.2 (forward guidance ratio); Product FR-24; Decision D-34 |
| FE-15 | Must | Question count is the number of Q&A sentences from analyst turns that end with a question mark. Without speaker roles it is the number of Q&A sentences that end with a question mark, and the row is flagged "no roles". Rule pending D-36. | Fixture Q&A with 5 questions gives 5. | Proposal 4.1 (question counts); Product FR-24; rule pending D-36 |
| FE-16 | Must | Q&A-only sentiment and Q&A-only hedge rate use the Q&A section as a whole, as the proposal says. Whether to use management turns only is part of D-36. | Fixture matches a hand calculation. | Proposal 5.2; Product FR-15, FR-24; rule pending D-36 |
| FE-17 | Must | Q&A sentiment delta is the mean net sentiment of analyst question sentences minus the mean net sentiment of management answer sentences. It is unavailable when either side has no sentences. | Fixture matches. Fixture with no analyst turns is unavailable. | Proposal 5.2; Product FR-15, FR-24 |

## 6. Cross-call and tabular features

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| FE-18 | Must | Sentiment surprise (Product FR-18) uses net sentiment, the sample standard deviation (n minus 1) of the four prior calls, and only calls of the same company dated before the prediction cutoff. At T0 it is the most recent earlier call against the four calls before it (pipeline.md Section 2.3). Rule pending D-36. | Hand-calculated fixture matches. | Proposal 5.2; Product FR-18; pipeline.md 2.3; rule pending D-36 |
| FE-19 | Must | Revenue growth is the change from the same fiscal quarter one year earlier, divided by that earlier revenue, from filings filed before D (Data FD-01, FD-02). It is unavailable if the earlier revenue is missing or not positive. Rule pending D-36. | Fixture matches. | Proposal 5.2; Data FD-01, FD-02; rule pending D-36 |
| FE-20 | Must | Gross margin is gross profit divided by revenue, and operating margin is operating income divided by revenue. A company that does not report gross profit has gross margin stored as unavailable, not zero. The unavailable share is reported by year, and by sector where a dated sector history exists (SEC-01). | Fixture company without gross profit is unavailable. | Proposal 5.2; Data FD-01 |
| FE-21 | Must | Prior four-quarter surprise trend is the least-squares slope of the four most recent prior SUE values in time order. All four must be valid, otherwise it is unavailable and the prediction carries "Limited history" (Product FR-07). Each prior SUE is the value as it stood before D (Data LB-04). Rule pending D-36. | Fixture with rising SUEs gives a positive slope. Fixture with three prior values is unavailable. | Proposal 5.2; Product FR-24, FR-07; Data LB-04; rule pending D-36 |
| FE-22 | Must | Price momentum is the return over the 63 trading days ending at the last close before the announcement session, using one price basis only (Data PX-03). With fewer than 63 prior trading days it is unavailable. Rule pending D-36. | Fixture matches. A planted future price has no effect (Data PX-02). | Proposal 5.2; Data PX-02, PX-03; rule pending D-36 |

Surprise dispersion and analyst consensus dispersion are defined in Product FR-24 and Data LB-01 and are not defined again here.

## 7. Prediction point, missing values and leakage

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| FE-23 | Must | Every feature in the registry (FE-27) is tagged T0, T1 or both. A feature computed from the event's own transcript is tagged T1 only. A T0 feature vector contains none of them. At T0 the text features are those of the most recent earlier call of the same company, with that call's date stored beside them. This is the reading of pipeline.md Section 2.3 ("Calls from earlier quarters only") and decision C-27 confirms it. | A T0 vector built for a planted event has no column derived from its own transcript. | Decision C-17, C-27; pipeline.md 2.3 |
| FE-24 | Must | Unavailable values are stored as NULL with a reason code. The model is given missing values as missing, and nothing is imputed at storage time. Any imputation used in training is recorded in the feature-set version. | Fixture with a NULL feature trains and predicts without error on the pinned XGBoost version. No stored zero stands for "missing". | Product FR-15, FR-17, FR-18 |
| FE-25 | Must | Any transformation that learns a value from data (a clip limit, a scaler, a bin edge) is fitted on the 2015 to 2021 window only, and the fitted value is stored and frozen. | Test: changing 2023 data leaves every fitted value unchanged. | Product FR-03; Data GATE-4, VL-06 |
| FE-26 | Must | Each feature has a test in which a record dated on or after its cutoff is planted and the feature value does not change. Together with Data VL-02 this covers every feature. | One passing test per registry entry. | Proposal 5.4; Data GATE-2, VL-02; Product FR-22 |

## 8. Assembly, versioning and reporting

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| FE-27 | Must | A feature registry lists, for every feature: name, group, definition, unit, source tag (Data SR-02), as-of rule, prediction-point tag (FE-23), missing-value rule and code version. Product FR-24's table is its starting content, and FR-24's own check (every feature listed with a source tag and as-of rule) applies to it. | Registry file exists and every column of the feature matrix has an entry. | Product FR-24; Data SR-02 |
| FE-28 | Must | The feature-set version is a hash of the registry, the code version, the FinBERT revision, the spaCy model, the word-list version and the negation and guidance rule versions. Changing any one gives a new version. Recomputing with the same inputs gives the same version and the same values to 1e-6. | Test changes each component in turn and sees a new version. Two runs are identical. | Product FR-11, FR-24; Data DV-08 |
| FE-29 | Must | Computing features is idempotent: rows are written once per event and feature-set version, never duplicated. Failed events are retried and logged like ingestion jobs. | Re-running a batch leaves the row count unchanged. | Product FR-13, PL-01, PL-02 |
| FE-30 | Must | The feature set is frozen before the test set is read. A feature added or changed afterwards is a new variant and is counted under Product TR-02. | The feature-set version in the test-read log equals the frozen version. | Product ML-02, TR-02; Data GATE-4 |
| FE-31 | Should | A feature report is produced for each feature-set version: count, unavailable share by year, and by sector where a dated sector history exists (SEC-01), truncated share (FE-06), and mean and standard deviation per year, using the training window for any statistic that informs a decision. The training-window distribution is stored as the baseline for drift monitoring. | Report exists and the baseline is stored. | Proposal 6 (feature matrix and EDA deliverable); Product MR-05 |
| FE-32 | Must | An EDA notebook is committed and runs from a clean checkout against the stored data. It shows class shares per year, the SUE threshold choice and the unavailable share of each feature, and it uses only 2015 to 2021 rows for any decision it informs (threshold choice, clip limits). | The notebook executes without error in the project container. A planted 2023 row does not change the thresholds it proposes. | Proposal 6 and SSOT Section 9 (milestone 2 deliverable); Data LB-06, VL-06; FE-25, FE-31 |

## 9. Evidence read

No requirement above depends on an outside source. These were read as background, mostly as abstracts or summaries, and none is treated as proof:
- Loughran and McDonald (2011) on finance word lists. The list file was not opened.
- Studies and notes on splitting long text for BERT-family models. They support the truncation flag. They do not set an aggregation rule, so the aggregation rules here come from the proposal's wording.
- Bernard and Thomas (1989, 1990) via secondary sources. The eight-quarter window in Data LB-01 was not confirmed and should be checked against the original papers.

Searches were run on 18 November 2026.
