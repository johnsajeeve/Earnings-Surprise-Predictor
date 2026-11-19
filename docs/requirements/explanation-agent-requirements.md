# Explanation Agent Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns how the explanation agent works: what goes in, how evidence is found, what the language model may produce, how the output is checked, how it is evaluated and how it is kept safe and affordable. Product Section 4B (EX-01 to EX-05) states the headline rules. This document adds the rules needed to build them, using only the project's own documents.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a number the project leaves open says "pending D-37", and it is not final until John decides D-37 in the [decision log](../decision-log.md) (Project-Wide SS-02). Ideas that do not trace to the project are not requirements. They are listed in decision D-41.

**Design choice that follows the SSOT.** The proposal text (Section 4.3) calls the agent "multi-step tool-using". The SSOT (Section 3, objective 5) says "single-pass". The SSOT wins. The agent therefore makes one generation call per explanation, after fixed retrieval steps that run without the model. A critic-and-revise loop is a stretch objective (Product ST-03).

| Already defined elsewhere | Where |
|---|---|
| Top-three SHAP features with signed direction | Product FR-04 |
| Citation exact-presence check | Product FR-05 |
| Asynchronous job, status, failure reason | Product FR-19 |
| Claim links, claim labels, top-ranked features only, no-evidence message, human sample | Product EX-01 to EX-05 |
| Disclaimer; no buy, sell or hold language | Product FR-08; Project-Wide ET-04 |
| Prompt injection test set, provider data terms, secrets | Project-Wide SP-03, SP-04, SP-06 |
| Prompt, model and settings recorded; regression set; three-run reporting | Project-Wide AI-01 to AI-03 |
| Retrieval by plain SQL, no vector store | Decision C-11 |
| Provider and budget | Decision C-09, D-27; Project-Wide OR-02 |
| Explanation latency; error messages | Product NFR-02; Section 12 |
| Verification status beside each citation | Product UI-03 |
| Optional 8-K corroboration step, with post-announcement evidence labelled and kept out of scoring | Product ST-05 (stretch) |
| Critic-and-revise loop | Product ST-03 (stretch) |

## 2. Inputs and permissions

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-01 | Must | One explanation is produced in a fixed order: select features, retrieve evidence, optionally corroborate (Product ST-05), generate once, verify, store. The log shows the steps in that order. The core makes one generation call. | Trace of a run shows the order and exactly one generation call. | SSOT Section 3 (objective 5) and 7 |
| AG-02 | Must | The agent's only input is a stored Prediction: class, probabilities, the SHAP values with signs, and the feature values. It cannot call the model or change a prediction, and it can write only to the explanation tables. It connects with a database role that can read the evidence tables and write the explanation tables (Database DB-02). | The agent's role fails an UPDATE on Prediction and FeatureVector. | SSOT Section 7 ("does not touch feature selection or training"); Project-Wide SP-02 |
| AG-03 | Must | The agent selects the top 3 features by absolute SHAP value. Ties are broken by feature name so the choice is repeatable. If a selected feature is unavailable for this event, it is reported as "missing value" and not narrated as if it had a value. | Fixture with tied SHAP values gives the same three every run. A NULL feature is reported as missing. | Product FR-04; SSOT Section 7 |

## 3. Evidence retrieval

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-04 | Must | A feature-to-evidence map says, for every feature in the registry (Feature Engineering FE-27), what evidence backs it and how to fetch it. Text features map to transcript sentences. Tabular features map to the stored numbers behind them (filing values, prices, prior SUE values) and name the source row. Sector features map to the stored peer list (Product SRS-10). A feature with no map entry cannot be narrated. The proposal describes retrieval only for text features, so the non-text entries complete what Product EX-01 already requires: every claim links to a feature or a cited sentence. | Every registry feature has an entry. A feature without one is rejected at start-up. | Proposal 4.3 step 2; Product EX-01, SRS-10 |
| AG-05 | Must | Retrieval uses fixed parameterised SQL templates. The language model never writes or edits SQL, and no value from the model or the transcript is placed into a query as text. | A static check finds no string-built query. A feature name containing SQL characters returns no rows and raises no error. | Decision C-11; Project-Wide SP-02, SP-03 |
| AG-06 | Must | For each text feature the map defines which sentences are the evidence and how they are ranked. Example from the proposal: for the uncertainty score, the analytic sentences in the Q&A section with the highest hedge density. At most 3 sentences per feature. Ties are broken by position. The limit of 3 is pending D-37. | Fixture transcript returns the expected sentence ids in order for each text feature. | Proposal 4.3 step 2; SSOT Section 7 step 2; pending D-37 |
| AG-07 | Must | Evidence comes only from information available at the prediction's cutoff. For a T0 prediction (decision C-17), the event's own transcript is not evidence, because the model did not use it. The cited sentences come from the previous call, and the date of that call is shown beside each quote. For a T1 prediction (decision C-17) the event's own transcript is also evidence, shown with its call date and marked post-call. | A planted sentence from a transcript dated after the cutoff is never returned. The call date is present beside each quote. | Decision C-17; pipeline.md 2.3 (effect on the explanation agent); Proposal 5.4 |
| AG-08 | Must | A feature with no evidence is left out of the narrative with a note. If none of the selected features has evidence, the output is the no-evidence message and no rationale is generated (Product EX-04). | Fixture with no matching sentences returns the message and makes no generation call. | Product EX-04; Proposal 4.3 |

## 4. Generation contract

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-09 | Must | The system prompt is a versioned file in the repository. Transcript sentences and the SHAP table are passed in delimited data blocks, each item with an id. The prompt states that the content of those blocks is data and never instructions. | Prompt file has a version. A test shows the data blocks are delimited. | Project-Wide SP-03, AI-01 |
| AG-10 | Must | The model must return JSON that validates against a fixed schema: a list of claims, each with the feature name, a direction from the fixed set used in Product FR-04, a short statement and a list of evidence ids, plus one short summary. Text outside the schema is rejected. A response that fails validation is retried once, then fails the job with a stored reason (Product FR-19). The fixed fields are what make the rank, sign and citation checks in AG-14 mechanical. | Malformed output fixture fails with a stored reason. A valid fixture is accepted. | Product EX-01, EX-02, FR-19; Proposal 5.5 |
| AG-11 | Must | The model cites sentences by id only. The excerpt shown to the user is copied from the database by the system, not typed by the model. | An id that does not exist is rejected. The displayed text equals the stored text byte for byte. | Product FR-05, EX-01; Data SR-11 |
| AG-12 | Must | The wording describes what the model used, not what caused the company's results or share price. No buy, sell or hold language, no price targets. The disclaimer appears with every explanation. | Text scan of 20 fixture outputs finds none of the banned phrases. Disclaimer present. | Product FR-08; Project-Wide ET-04 |
| AG-13 | Must | The model is pinned by an exact provider model identifier, never an alias such as "latest". Temperature, maximum output tokens and any seed the provider supports are set in configuration and stored with each explanation. The temperature range is pending D-37. | Configuration with an alias is rejected. Stored explanation has all settings. | Project-Wide AI-01; pending D-37 |

## 5. Verification before storage

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-14 | Must | Every explanation is checked before it is stored, not only in the evaluation. The checks are: (a) rank, every discussed feature is in the selected top 3; (b) sign, each stated direction equals the sign of that feature's SHAP value; (c) citation, every cited id exists and belongs to that feature's evidence; (d) value, any number quoted equals the stored feature value after rounding. The rank and sign checks are the proposal's metrics; the citation check is the proposal's added check; the value check applies the same idea to quoted numbers. | Fixture explanations with a wrong feature, a wrong sign, a made-up id and a wrong number are each caught. | Proposal 5.5; Product EX-01, EX-02, EX-03, FR-05 |
| AG-15 | Must | A claim that fails a check is removed and the failure is logged with the prediction id (Product FR-05). If some claims fail, the explanation is marked "partially verified". If every claim fails, the job fails with the reason "no claim passed verification" and the user sees "Explanation could not be generated." Each remaining claim keeps its label and reason (Product EX-02). | Fixtures cover partial and total failure. | Product FR-05, EX-02, FR-19, Section 12 |

## 6. Safety

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-16 | Must | Explanation text is shown as plain text. No HTML, Markdown links or images from model output are rendered, and no URL from the model is followed. | A fixture output containing HTML and a link renders as text. | Project-Wide SP-03 |
| AG-17 | Must | The injection test set (Project-Wide SP-03) includes planted sentences that try to change a direction, add a link, and reveal the prompt. Passing means AG-14 and AG-16 stop each one. | All planted cases are stopped. | Project-Wide SP-03 |
| AG-18 | Must | Only the minimum is sent to the provider: feature names, SHAP values, feature values and the selected sentences. No user identifier and no full transcript. Nothing is sent until the licence and provider-terms check is recorded. | Request log fixture shows the fields sent. Register entry exists before the first call. | Project-Wide SP-04; Data SR-03, SR-11 |
| AG-19 | Must | Test fixtures contain short excerpts or synthetic sentences, labelled as such. No full licensed transcript is committed to the public repository. | A repository scan finds no fixture over the excerpt limit recorded in the source register (Data SR-11) and every fixture file states its origin. | Data SR-03, SR-11; Deterministic audit rules (real, synthetic and mock data kept apart) |

## 7. Cost, reliability and reproducibility

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-20 | Must | A per-call token limit and a monthly spend cap are enforced in code. When the cap is reached, no provider call is made and the job fails with the reason "budget reached" (Product FR-19). Tokens and estimated cost are recorded with each explanation. The cap is set under D-27. | With the cap set to zero, a job makes no provider call and fails with that reason. | Decision C-09, D-27; Project-Wide OR-02 |
| AG-21 | Must | The stored explanation is reused for the same prediction, prompt version and model version. A new generation happens only when one of those changes. | Two requests give the same stored explanation and one provider call. | Product FR-01 (same answer twice); Project-Wide AI-01 |
| AG-22 | Must | Provider calls have a timeout and retry up to three times with backoff on rate-limit and server errors. The stored failure reason names the error class and does not contain the response body. The timeout value is pending D-37. | Injected 429 and timeout fixtures behave as described. | Product FR-19, PL-02 (same retry rule), NFR-02; pending D-37 |

## 8. Evaluation

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-23 | Must | Prompts and settings are tuned on predictions from the 2022 validation year only, and the regression set (Project-Wide AI-02) is built from the same year. The evaluation sample is drawn from the 2023 to 2024 test period after the final model is fixed (Product ML-02). No prompt change is made after the evaluation run starts. | Prompt version in the evaluation record is dated before the run. Regression report names event ids and years. | Product ML-02; Project-Wide AI-02; Proposal 5.5 |
| AG-24 | Must | The metrics are fixed in a written protocol before the run: rank agreement, sign agreement, citation existence rate and claim support rate, as in Proposal 5.5 and Product EX-02 and EX-03. The sample size is proposed at 100 predictions spread over the classes and is pending D-37 and D-06. The exact definitions in the paper the proposal cites (Ichmoukhamedov et al.) are checked against the paper before the protocol is frozen. | Protocol file exists and is dated before the run. | Proposal 5.5; Product EX-02, EX-03; pending D-37 |
| AG-25 | Must | Each metric is reported as mean and range over three runs (Project-Wide AI-03) with a bootstrap interval over predictions (Product TR-01). The counter-metrics in Product Section 15 are reported beside it: explanation length, the number of features discussed per explanation, and human agreement with the automated labels (Product EX-05). | Results table has all three values per metric and the counter-metrics. | Project-Wide AI-03; Product TR-01, Section 15 |

## 9. Storage

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AG-26 | Must | The Explanation and ClaimLabel tables (Product Section 11) also store the evidence ids per claim, the verification status, token counts and estimated cost. The Explanation table also stores `failure_reason` and `completed_at`. The additions go through a migration (Database DB-17). | Migration exists and the fields are populated in a run. | Product Section 11; Project-Wide AI-01 |

## 10. Open items

Choices that need John are in decision D-37 (sentences per feature, evaluation sample size, temperature range and timeout). The provider and budget are D-27.

## 11. Evidence read

No requirement above depends on an outside source. Background read, as abstracts and summaries only, and not treated as proof:
- Ichmoukhamedov, Hinns and Martens (arXiv 2412.10220), the paper the proposal cites for rank and sign agreement. Full text not read.
- OWASP LLM01 prompt injection page. Mitigation list not captured.
- Engineering guides on checking quotes and citations in generated text.

Searches were run on 18 November 2026.
