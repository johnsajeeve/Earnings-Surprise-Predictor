# Project-Wide Requirements: Delivery, Assessment, Engineering, Security, Ethics and Operations

Derived from the Third Year Project Proposal (2026-27) (see [SSOT](../SSOT.md)), the project planning notes stored in project memory, and the Product, Market and Data requirement documents. Research on ethics, AI-use and security references was carried out 30 October 2026. Restructured 15 November 2026: engineering, security and operations requirements that were in the product document (secrets, container builds, rollback, test coverage) now live here. Open decisions are in the [decision log](../decision-log.md).

## 1. Purpose and Scope

The product, market and data requirement documents cover what the product does, what the market needs and which data it depends on. They do not cover how the project is delivered, assessed, secured, governed or run. Eight component documents added on 18 November 2026 (feature engineering, explanation agent, database, frontend, ingestion and preparation, modelling and evaluation, API and serving, and deployment and operations, awaiting approval under decisions D-40 and D-46) hold the detail for those pipeline steps.

This page sets those requirements. It covers ten areas:

- assessment alignment (ASM)
- delivery and capacity (PD)
- supervision and change control (SS)
- scope and architecture consistency (SC)
- engineering quality (EQ)
- security and privacy (SP)
- ethics, licensing and academic integrity (ET)
- operations and cost (OR)
- LLM operations (AI)
- documentation and handover (DO)

Section 2 lists conflicts between the planning notes and the requirements already agreed. Those conflicts are resolved by requirements in Section 3, but several need a decision from you and Professor Goodacre before they can close.

## 2. Conflicts to Resolve First

| ID | Where the conflict is | What conflicts | Resolved by |
|---|---|---|---|
| C1 | Planning notes, Week 4 and risk table | Notes say to use mock transcript data if real data is unavailable. Results built on mock data cannot support a backtest claim. | SC-04 |
| C2 | Planning notes, testing table and risk table | Explanation quality is judged by ROUGE or BERTScore above 0.7. The proposal (Section 5.5) judges faithfulness by rank agreement, sign agreement and citation verification. Overlap with a reference text is not faithfulness to SHAP values. | SC-05 |
| C3 | Planning notes, Week 10 | Alerts to Slack when confidence exceeds 80%. An alert like this reads as a trading signal, which conflicts with NG5 and FR-08. | ET-04 |
| C4 | Planning notes, deployment diagram | Diagram places Celery workers behind Cloud Tasks. Cloud Tasks is a separate managed service. The proposal's stack is Celery with Redis as the broker. | SC-01, DO-02 |
| C5 | Planning notes, Weeks 2 and 4 | Mentions Kafka and Redis Streams. Neither is in the proposal stack, and the notes do not choose one. | SC-01 |
| C6 | Proposal Section 4.2 and planning notes, Week 11 | Proposal says "Streamlit (or React)". Notes say React. | SC-02 |
| C7 | Planning notes, Week 2 | Model serving in pickle or ONNX format. Pickle files can execute code when loaded. | SP-01 |
| C8 | Planning notes, Week 6 | Vector store choice left open (Pinecone, Weaviate or FAISS). Transcript text is licensed. | SC-06 |
| C9 | Planning notes, Weeks 7, 8 and 9, and "Keep" list | Contrastive multi-agent system, insider and options agent, and live streaming are in the plan. The product document excludes them as non-goals (NG1, NG3). | SC-03, SS-04 |
| C10 | Planning notes, team capacity | Assumes 25 hours a week for 400 hours, then says the realistic figure is 15 to 20 hours a week. The scope in the notes does not fit either figure with a buffer. | PD-01, PD-02 |
| C11 | Planning notes, Week 1 | Asks for a 2 to 3 page requirements document. The requirement documents are much longer. | ASM-04 |
| C12 | Planning notes, testing table | Backtest target of 70% accuracy and AUC above 0.70. Already removed from the product and market documents, but the notes still carry it. The proposal treats SAE-FiRE's 0.67 as a reference, not a pass mark. | Product Section 15 (binary AUC reported as a reference; no target) |
| C13 | Planning notes, Week 15 | User acceptance with "mock traders". Testing with people needs university ethics approval before recruitment. | ET-01, ET-02 |
| C14 | Proposal Sections 1, 5.1 and 8 against Data Requirements Section 3 | The proposal calls the corpus public and available through SEC EDGAR, and justifies the project partly on that. Transcripts and point-in-time consensus actually need licensed academic sources (WRDS) with restricted demo use. | SS-04 (change entry), ASM-05 |
| C15 | Proposal Section 5.2 against Product and Data documents | Revenue growth, gross margin and operating margin had no requirement and no data source. | Product FR-24; Data FD-01 to FD-04 |
| C16 | Proposal Section 7 against Product ML-06 | Promotion to serving required the baseline comparison to "pass". The proposal accepts a negative result as valid. | Product ML-06 (reworded 14 November) |
| C17 | Proposal Section 3.3 against Product Section 15 | The AUC target compared a three-class AUC with SAE-FiRE's binary AUC. | Product FR-06 and Section 15 (binary AUC as a reference only) |
| C20 | Product and Market documents against SAE-FiRE (arXiv 2505.14420, Table 2) | The documents said the XGBoost baseline had AUC about 0.67. The table gives 0.620 for XGBoost on conference calls. 0.67 belongs to SAE-FiRE's own models (0.657 to 0.668). The SAE-FiRE label also uses post-call analyst forecasts and a 2012 to 2014 sample. | Corrected in Product FR-06, FR-27 and Section 15, and Market Section 7 (14 November 2026) |
| C18 | Product and Market documents | Same ID used for different requirements (for example FR-12, FR-16 and SC-01, and the product goals G1 to G6 against the data gates G1 to G5, now PG-1 to PG-6 and GATE-1 to GATE-5). | DO-05 |
| C19 | Proposal Section 5.1 against the free-source decision (14 November 2026) | The proposal labels events by the surprise against analyst consensus, standardised by the standard deviation of estimates. No free source gives historical point-in-time consensus, and the project is to use free sources. The label becomes a time-series SUE from EDGAR EPS (Data LB-01 to LB-08), with consensus captured forward as a check. Consequences are in `proposal-drift-review.md`, Section 8. | SC-07, ASM-06, SS-04 |

## 3. Requirements

### 3.1 Assessment Alignment

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| ASM-01 | Must | Every functional, non-functional and data requirement traces to at least one evaluation criterion in proposal Section 7 or submission skill in Section 8. | Traceability matrix (DO-03) has no requirement without a link. | Proposal 7, 8 |
| ASM-02 | Must | Every quantitative claim in the report and demo links to a figure, table or test ID generated from code. No accuracy claim appears in the product or any write-up without a link to the evaluation page it comes from. | Claim checklist is complete before submission. | Market N3 |
| ASM-03 | Must | Each novelty claim is recorded with the literature check that supports it: sources reviewed and date. | Novelty register has an entry for each claim. Unverified claims in the planning notes are marked. | New. Planning notes novelty scorecard. |
| ASM-04 | Should | A two to three page summary of the requirement documents is prepared for the Week 2 supervisor meeting. | Summary is reviewed at SS-03. | Planning notes, Week 1 |
| ASM-05 | Must | Where the data route differs from the proposal's description (licensed academic sources rather than public EDGAR), the dissertation states the difference and the reason, and the submission justification is worded to match. | Change entry exists (SS-04). The methodology section cites it. | C14; Proposal 1, 5.1, 8 |
| ASM-06 | Must | The dissertation states that the label is a time-series SUE and not a surprise against analyst consensus, reports its agreement with the consensus label on the prospective set, and does not compare its AUC with consensus-based studies (SAE-FiRE, Koval et al.) as if the labels were the same. Every quantitative claim names the label route. | Methodology section and results tables name the route. Claim checklist (ASM-02) has a label-route column. | C19; Data LB-08 |

### 3.2 Delivery and Capacity

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| PD-01 | Must | Planned effort fits available hours. Weekly planned hours, including buffer, stay at or below 20. The schedule keeps 2 to 3 weeks of buffer. | Capacity check is recorded at each milestone. | Planning notes, team capacity (C10) |
| PD-02 | Must | Every feature and milestone carries a Must, Should or Could tag. A drop order is agreed before Week 3. | Drop order is dated and approved at SS-03. | Planning notes, "If stretched" list |
| PD-03 | Must | Each milestone in proposal Section 6 has a demonstrable artefact, run from a clean environment, before it is marked complete. | Milestone checklist signed off. | Proposal 6 |
| PD-04 | Must | If a milestone slips by more than one week, the drop order from PD-02 is applied within that week and recorded. | Decision log entry exists for each slip. | New |
| PD-05 | Should | The risk register is reviewed every two weeks. Each risk has an owner, a trigger and a mitigation. | Dated review entries. | Product Section 18 |
| PD-06 | Must | The drop order agreed under PD-02 is applied in this sequence unless the supervisor agrees otherwise: stretch objectives ST-01 to ST-05; Could items (sector comparison view SRS-12, autocomplete, 375 px layout); the consensus-revision baseline; drift monitoring, SHAP rank monitoring and the model inventory (Product MR-01, MR-04 to MR-06); LLM extras (Product EX-05; AI-02, AI-03); the load test, runbook and restore drill (EQ-05, DO-04, OR-01); then the other Should items. Sector-relative scoring (Product FR-12, SRS-01 to SRS-14) is kept, as the owner decided, but every SRS item marked "Must if built" must pass or the feature is switched off (SRS-14). Proposal-derived Must items are never dropped. | Dated drop-order list approved at SS-03. | C10; Proposal 6; SSOT Section 3A |

### 3.3 Supervision and Change Control

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SS-01 | Must | Supervisor meetings are held on a fixed cadence, proposed fortnightly, with a written agenda and an action list kept after each one. | Action list exists for each meeting. | Decision log |
| SS-02 | Must | The decision log (`docs/decision-log.md`) records each open decision with its date, owner and outcome. Every open decision in any requirement document appears in it and nowhere else. | Each item is closed or has a date. No requirement document holds its own open-decision list. | Decision log |
| SS-03 | Must | The requirement documents (market, product, data and project-wide, and the eight component documents once approved under D-40 and D-46) are signed off by the supervisor in Week 2 (requirements freeze). | Sign-off record on file. | Product milestones, Weeks 1 to 2 |
| SS-04 | Must | After freeze, any added feature or changed non-goal needs a written change entry, a capacity check (PD-01) and supervisor agreement. | Change log is complete. | C9; Product 2.2 |

### 3.4 Scope and Architecture Consistency

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SC-01 | Must | The queue and task design follows the proposal: Celery with Redis as the broker. Kafka, Redis Streams and Cloud Tasks are used only if an architecture decision record (ADR) justifies them. | ADR exists. Deployment diagram matches the ADR. | Proposal 4.1, 4.2; C4, C5 |
| SC-02 | Must | One frontend framework is chosen by ADR (Streamlit or React). | ADR exists. Only one framework is in the repository. | Proposal 4.2; C6 |
| SC-03 | Must | Non-goals NG1 to NG5 are checked at every pull request review. Code for a non-goal is rejected. | Review checklist includes the five items. | Product 2.2; C9 |
| SC-04 | Must | No mock or synthetic data appears in any reported result. Synthetic data is used only in automated tests and is labelled as such. Real benchmark data (FinCall-Surprise, Product FR-27) is reported separately, labelled with its own label definition. | Reported tables state their data source. The evaluation job refuses synthetic input. | C1; Data VL-01 |
| SC-05 | Must | Explanation quality is measured with rank agreement, sign agreement and citation verification. ROUGE and BERTScore may be reported as secondary measures only and are not pass or fail gates. | No ROUGE or BERTScore threshold exists in the evaluation harness. | Proposal 5.5; C2 |
| SC-06 | Must | Retrieval of transcript sentences is plain SQL over per-sentence scores (decision C-11), so no vector store is built. An ADR records that choice and its reason. If a vector store is ever added, the ADR also records a check that the transcript licence allows hosting and embedding. | ADR exists with the licence check. | Planning notes, Week 6; C8; Data SR-03 |
| SC-07 | Must | The label route (time-series SUE, or consensus where a licensed source exists) is chosen by ADR at the end of week 2 and recorded with the supervisor's agreement. The two routes are never mixed in one training set. | ADR exists. A test fails if events with different label routes are in one training set (Data CE-05). | C19; Data CE-05 |

### 3.5 Engineering Quality

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| EQ-01 | Must | Automated tests run in continuous integration on every pull request. A failing test blocks the merge. | Merge is blocked by a planted failing test. | Planning notes, git workflow; Proposal 8 |
| EQ-02 | Must | Lint, format and type checks run in continuous integration. | A planted style error fails the job. | Proposal 8 |
| EQ-03 | Must | The main branch accepts changes only through reviewed pull requests. Direct pushes are blocked. | Branch protection is on in the repository settings. | Planning notes, git workflow |
| EQ-04 | Must | The service builds from a clean checkout with one documented command and runs in a container. Dependencies are pinned to exact versions, and the build fails if one is unpinned. | Build succeeds on a fresh clone in a clean environment. A planted unpinned dependency fails the build. | Planning notes, Weeks 3 and 15 |
| EQ-05 | Should | Load test: 100 concurrent requests for cached predictions run on the deployed environment, checked against the latency target in Product NFR-01. Results are reported. | Load test report exists. | Planning notes, Weeks 12 and 13; Product NFR-01 |
| EQ-06 | Must | Fault-injection tests: killing a worker mid-job, restarting the database and making Redis unavailable. Each case recovers with no duplicate or missing rows. | Three scripted tests pass. | Proposal 1 and 8 (distributed design) |
| EQ-07 | Must | Every queued task is idempotent, including ingestion (Product FR-13): running it twice leaves the same database state. | Test runs each task twice and compares state. | Product FR-13 |
| EQ-08 | Should | Dependencies are scanned for known vulnerabilities in continuous integration. High-severity findings block release. | Scan job runs on every pull request. | Planning notes, Week 15 |
| EQ-09 | Must | Line coverage on feature engineering, split logic and sector scoring is at least 80%. | Coverage report in continuous integration. | Product ML-02, FR-03, SRS-01 to SRS-14 |

### 3.6 Security and Privacy

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SP-01 | Must | Model artefacts are stored and loaded only in non-executable formats: XGBoost native format or ONNX. The loader rejects pickle files. | Loader test with a pickle file fails as expected. | C7; Product ML-03 |
| SP-02 | Must | A pre-release review of the API against the OWASP API Security Top 10 covers at least: broken object-level authorisation, broken authentication, unrestricted resource consumption, security misconfiguration and unsafe consumption of external APIs. | Review checklist is signed off before release. | Planning notes, Week 15; Product API-06, API-07 |
| SP-03 | Must | The explanation agent treats transcript text as data. Instructions found in transcripts are not followed. Each claim is checked against retrieved sentences. | Test set of 20 transcript excerpts containing planted instructions: agent behaviour does not change. | OWASP LLM01 (prompt injection); Product FR-05 |
| SP-04 | Must | Transcript text is sent to a third-party LLM provider only if the transcript licence and the provider's data-use terms allow it. The terms, and the date they were checked, are recorded. | Register entry exists for each provider. | Data SR-03, SR-11 |
| SP-05 | Should | Request logs contain only the fields in Product NFR-11 and the requested ticker. Logs are deleted after a set period, proposed at 30 days. | Log schema test. Retention job runs. | Product NFR-11; Market Section 6 |
| SP-06 | Must | No secrets are stored in source control. Data-source keys and credentials are read from environment variables or a secret manager. A secret scanner runs in continuous integration. | Secret scanner passes. A planted key fails the job. | Planning notes, deployment |

### 3.7 Ethics, Licensing and Academic Integrity

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| ET-01 | Must | Before any user study, including the five-user usability test, the university ethics route is confirmed using the Ethics Decision Tool. Approval is obtained before recruitment. | Approval reference on file. | Proposal 7; C13. Manchester ethics page: approval routes are School or Division review, Proportionate UREC or Full UREC. |
| ET-02 | Must | Participants receive an information sheet and give consent. Identifying data is not kept beyond the approved period. | Documents on file. Retention date recorded. | C13. Information sheet requirement not stated on the ethics page: confirm with the approval route. |
| ET-03 | Must | A third-party register lists the licence and terms of every model and library used, including FinBERT weights and spaCy models. Datasets are recorded in the source register (Data SR-01). | Register is complete before the demo. | Data SR-01; Proposal 4.2 |
| ET-04 | Must | No output or alert uses buy, sell or hold language. Every alert carries the disclaimer in FR-08. Confidence-threshold alerts are removed unless both rules are met. | Text scan of all alert templates. Disclaimer test passes. | C3; Product NG5, FR-08 |
| ET-05 | Must | The report declares AI-tool use as each assessment's guidance requires. Manchester sets an AI tier for each assignment (Prohibited, Minimal, Permitted or Required), and the tier is set by the unit lead. | Written confirmation of the tier and declaration format from the unit lead for each assessed item. | Manchester AI policy (tiers, per the EdTech Innovation Hub article). Declaration format not confirmed. |

### 3.8 Operations and Cost

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| OR-01 | Should | The PostgreSQL database is backed up daily, and a restore is tested once before the demo. Proposed targets: recovery point 24 hours, recovery time 4 hours. | Restore test log exists. | Planning notes, Cloud SQL |
| OR-02 | Must | The default monthly ceiling for cloud and API spend is zero for data, because the primary data route is free (Data SR-09). Any paid source or cloud spend needs a ceiling and a budget alert at 80% of it, set before it is bought. Cloud hosting spend ceiling is a decision for John. | Source register shows zero cost for every primary-route source. Budget alert exists before any spend. | Planning notes, deployment; Data SR-09 |
| OR-03 | Must | The demo database is separate from the evaluation dataset. Demo writes never change rows used for training or testing. | Demo service account has no write rights on the evaluation schema. | Data VL-04; Product ML-02 |

### 3.9 LLM Operations

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AI-01 | Must | Each explanation records the prompt version, the model version and the generation settings. | All three fields are non-null on every stored explanation. | Product FR-11; Product EX-02 |
| AI-02 | Should | A fixed regression set of 50 event cases is re-run whenever the prompt or model changes. Faithfulness results must not fall below the previous version unless the drop is logged as a decision. | Regression report exists for each change. | Product EX-03, EX-04; Proposal 5.5 |
| AI-03 | Should | LLM-based metrics are reported as the mean and range across three runs, because LLM output varies between runs. | Results table shows three values per metric. | Proposal 5.5; Product Section 15 |

### 3.10 Documentation and Handover

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DO-01 | Must | A new machine can run the system from the README in under 30 minutes. The test is timed on a clean environment, ideally by someone other than the builder. | Timed run recorded. | Planning notes, Week 14; Proposal 8 |
| DO-02 | Must | Each major technology choice has an ADR: queue, frontend, sentence retrieval method (decision C-11), model format, deployment target, LLM provider and label route. | ADR list is complete before Week 6. | SC-01, SC-02, SC-06, SC-07, SP-01 |
| DO-03 | Must | A traceability matrix maps every requirement ID to the test or evidence that proves it. | No requirement without evidence at submission. | ASM-01; Proposal 7 |
| DO-04 | Should | A runbook covers rollback to the previous revision within 10 minutes, worker restart, re-ingestion of one day's data and database restore. Each step is run once in a non-production environment, and the rollback is timed. | Each step has a dated run record. | OR-01 |
| DO-05 | Must | Requirement IDs are unique across the requirement documents. Market functional and non-functional IDs use the MFR and MNFR prefixes; data gates are GATE-1 to GATE-5; data sector requirements are SEC-01 and SEC-02; product goals are PG-1 to PG-6; stretch objectives are ST-01 to ST-05; sector scoring is SRS-01 to SRS-14; the component documents use the prefixes FE (feature engineering), AG (explanation agent), DB (database), UX (frontend), IG (ingestion and preparation), MD (modelling and evaluation), SV (API and serving) and DP (deployment and operations). | A script lists every ID defined in the documents and reports no duplicate definition. | C18; DO-03 |

## 4. Summary Count

| Area | Requirements | Must | Should |
|---|---|---|---|
| Assessment alignment (ASM) | 6 | 5 | 1 |
| Delivery and capacity (PD) | 6 | 5 | 1 |
| Supervision and change control (SS) | 4 | 4 | 0 |
| Scope and architecture (SC) | 7 | 7 | 0 |
| Engineering quality (EQ) | 9 | 7 | 2 |
| Security and privacy (SP) | 6 | 5 | 1 |
| Ethics and licensing (ET) | 5 | 5 | 0 |
| Operations and cost (OR) | 3 | 2 | 1 |
| LLM operations (AI) | 3 | 1 | 2 |
| Documentation (DO) | 5 | 4 | 1 |
| Total | 54 | 45 | 9 |

## 5. Decisions Needed Before Freeze

Open decisions are in the [decision log](../decision-log.md), Section 2. Those that concern this document: D-02, D-03, D-11 to D-17.

## 6. Changes Needed in Other Documents

Pending edits to the proposal, planning notes and deck are in the [decision log](../decision-log.md), Section 3. They are for the owner to approve. Claude does not edit the proposal or the planning notes.

## 7. Sources Checked

| Source | What was checked | Status |
|---|---|---|
| Third Year Project Proposal (2026-27), uploaded PDF | Sections 4, 5, 6, 7, 8 and 9 | Read |
| Planning notes, earnings-surprise-predictor area file, project memory | Week plan, team capacity, testing, deployment, risk, git workflow, deliverables | Read |
| Product, Market and Data requirement documents, project | Requirement IDs, non-goals, open decisions | Read (authored in this session) |
| Manchester ethical approval page: https://www.manchester.ac.uk/research/environment/governance/ethics/approval/ | Approval routes: School or Division review, Proportionate UREC, Full UREC. Supervisors are not named as approvers. | Read |
| EdTech Innovation Hub, Manchester four-tier AI policy: https://www.edtechinnovationhub.com/news/university-of-manchester-adopts-four-tier-ai-policy-for-student-assessments | Tiers: Prohibited, Minimal, Permitted, Required. Set per assignment by the unit lead. | Read. Declaration format not stated. The policy document itself (documents.manchester.ac.uk, DocID 79331) was not opened. |
| OWASP API Security Top 10 (2023), via Barracuda write-up: https://blog.barracuda.com/2023/03/17/owasp-top-10-api-security-risks-2023 | Risk names, including broken object-level authorisation and unrestricted resource consumption | Secondary source. The OWASP page was blocked. Check numbering against OWASP. |
| OWASP Top 10 for LLM Applications, via Coalfire write-up: https://coalfire.com/the-coalfire-blog/owasp-top-10-for-large-language-model-applications | LLM01 prompt injection, LLM02 insecure output handling | Secondary source describing the 2023 edition. The OWASP page was blocked. Check whether the current edition has the same numbering. |
| Python documentation, pickle: https://docs.python.org/3/library/pickle.html | Warning that unpickling untrusted data can run arbitrary code | Not read. Page was blocked. The warning is from memory. Check the current wording before citing it. |

Points not verified: the OWASP numbering and current edition; the wording of the Python pickle warning; the Manchester AI declaration format and tier process; whether an information sheet is required for the approval route that applies to this project.
