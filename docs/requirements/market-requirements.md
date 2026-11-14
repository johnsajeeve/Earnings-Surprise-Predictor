# Project-Wide Requirements: Delivery, Assessment, Engineering, Security, Ethics and Operations

Derived from the Third Year Project Proposal (2026-27), the project planning notes stored in project memory, and the Product, Market and Data requirement documents (26 to 30 October 2026). Research on ethics, AI-use and security references was carried out 30 October 2026.

## 1. Purpose and Scope

The three requirement documents cover what the product does, what the market needs and which data it depends on. They do not yet cover how the project is delivered, assessed, secured, governed or run.

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
| C11 | Planning notes, Week 1 | Asks for a 2 to 3 page requirements document. The four requirement documents are much longer. | ASM-04 |
| C12 | Planning notes, testing table | Backtest target of 70% accuracy and AUC above 0.70. Already removed from the product and market documents, but the notes still carry it. | Product Section 15 (no target carried forward) |
| C13 | Planning notes, Week 15 | User acceptance with "mock traders". Testing with people needs university ethics approval before recruitment. | ET-01, ET-02 |

## 3. Requirements

### 3.1 Assessment Alignment

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| ASM-01 | Must | Every functional, non-functional and data requirement traces to at least one evaluation criterion in proposal Section 7 or submission skill in Section 8. | Traceability matrix (DO-03) has no requirement without a link. | Proposal 7, 8 |
| ASM-02 | Must | Every quantitative claim in the report and demo links to a figure, table or test ID generated from code. | Claim checklist is complete before submission. | Market CP-01 |
| ASM-03 | Must | Each novelty claim is recorded with the literature check that supports it: sources reviewed and date. | Novelty register has an entry for each claim. Unverified claims in the planning notes are marked. | New. Planning notes novelty scorecard. |
| ASM-04 | Should | A two to three page summary of the four requirement documents is prepared for the Week 2 supervisor meeting. | Summary is reviewed at SS-03. | Planning notes, Week 1 |

### 3.2 Delivery and Capacity

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| PD-01 | Must | Planned effort fits available hours. Weekly planned hours, including buffer, stay at or below 20. The schedule keeps 2 to 3 weeks of buffer. | Capacity check is recorded at each milestone. | Planning notes, team capacity (C10) |
| PD-02 | Must | Every feature and milestone carries a Must, Should or Could tag. A drop order is agreed before Week 3. | Drop order is dated and approved at SS-03. | Planning notes, "If stretched" list |
| PD-03 | Must | Each milestone in proposal Section 6 has a demonstrable artefact, run from a clean environment, before it is marked complete. | Milestone checklist signed off. | Proposal 6 |
| PD-04 | Must | If a milestone slips by more than one week, the drop order from PD-02 is applied within that week and recorded. | Decision log entry exists for each slip. | New |
| PD-05 | Should | The risk register is reviewed every two weeks. Each risk has an owner, a trigger and a mitigation. | Dated review entries. | Product Section 18 |

### 3.3 Supervision and Change Control

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SS-01 | Must | Supervisor meetings are held on a fixed cadence, proposed fortnightly, with a written agenda and an action list kept after each one. | Action list exists for each meeting. | Market Section 9; Product Section 19 |
| SS-02 | Must | A decision log records each open decision with its date, owner and outcome. Every open item in the market, product and data documents appears in it. | Each item is closed or has a date. | Market 9, Product 19, Data 14 |
| SS-03 | Must | The four requirement documents are signed off by the supervisor in Week 2 (requirements freeze). | Sign-off record on file. | Product milestones, Weeks 1 to 2 |
| SS-04 | Must | After freeze, any added feature or changed non-goal needs a written change entry, a capacity check (PD-01) and supervisor agreement. | Change log is complete. | C9; Product 2.2 |

### 3.4 Scope and Architecture Consistency

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SC-01 | Must | The queue and task design follows the proposal: Celery with Redis as the broker. Kafka, Redis Streams and Cloud Tasks are used only if an architecture decision record (ADR) justifies them. | ADR exists. Deployment diagram matches the ADR. | Proposal 4.1, 4.2; C4, C5 |
| SC-02 | Must | One frontend framework is chosen by ADR (Streamlit or React). | ADR exists. Only one framework is in the repository. | Proposal 4.2; C6 |
| SC-03 | Must | Non-goals NG1 to NG5 are checked at every pull request review. Code for a non-goal is rejected. | Review checklist includes the five items. | Product 2.2; C9 |
| SC-04 | Must | No mock or synthetic data appears in any reported result. Synthetic data is used only in automated tests and is labelled as such. | Reported tables state their data source. The evaluation job refuses synthetic input. | C1; Market TR-03 |
| SC-05 | Must | Explanation quality is measured with rank agreement, sign agreement and citation verification. ROUGE and BERTScore may be reported as secondary measures only and are not pass or fail gates. | No ROUGE or BERTScore threshold exists in the evaluation harness. | Proposal 5.5; C2 |
| SC-06 | Must | The vector store for transcript sentences is chosen by ADR. The ADR records a check that the transcript licence allows hosting and embedding. | ADR exists with the licence check. | Planning notes, Week 6; Data SR-03; C8 |

### 3.5 Engineering Quality

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| EQ-01 | Must | Automated tests run in continuous integration on every pull request. A failing test blocks the merge. | Merge is blocked by a planted failing test. | Planning notes, git workflow; Proposal 8 |
| EQ-02 | Must | Lint, format and type checks run in continuous integration. | A planted style error fails the job. | Proposal 8 |
| EQ-03 | Must | The main branch accepts changes only through reviewed pull requests. Direct pushes are blocked. | Branch protection is on in the repository settings. | Planning notes, git workflow |
| EQ-04 | Must | The service builds from a clean checkout with one documented command and runs in a container. | Build succeeds on a fresh clone in a clean environment. | Planning notes, Weeks 3 and 15; Product OP-02 |
| EQ-05 | Must | Load test: 100 concurrent requests for cached predictions, with 95th percentile latency under 500 ms, run on the deployed environment. Results are reported. | Load test report exists. | Planning notes, Weeks 12 and 13; Product NFR-01 |
| EQ-06 | Must | Fault-injection tests: killing a worker mid-job, restarting the database and making Redis unavailable. Each case recovers with no duplicate or missing rows. | Three scripted tests pass. | Proposal 1 and 8 (distributed design) |
| EQ-07 | Must | Every queued task is idempotent: running it twice leaves the same database state. | Test runs each task twice and compares state. | Product FR-13 |
| EQ-08 | Should | Dependencies are scanned for known vulnerabilities in continuous integration. High-severity findings block release. | Scan job runs on every pull request. | Planning notes, Week 15 |

### 3.6 Security and Privacy

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SP-01 | Must | Model artefacts are stored and loaded only in non-executable formats: XGBoost native format or ONNX. The loader rejects pickle files. | Loader test with a pickle file fails as expected. | C7; Product ML-03 |
| SP-02 | Must | A pre-release review of the API against the OWASP API Security Top 10 covers at least: broken object-level authorisation, broken authentication, unrestricted resource consumption, security misconfiguration and unsafe consumption of external APIs. | Review checklist is signed off before release. | Planning notes, Week 15; Product API-06, API-07 |
| SP-03 | Must | The explanation agent treats transcript text as data. Instructions found in transcripts are not followed. Each claim is checked against retrieved sentences. | Test set of 20 transcript excerpts containing planted instructions: agent behaviour does not change. | OWASP LLM01 (prompt injection); Product FR-05 |
| SP-04 | Must | Transcript text is sent to a third-party LLM provider only if the transcript licence and the provider's data-use terms allow it. The terms, and the date they were checked, are recorded. | Register entry exists for each provider. | Data SR-03, DR-05; Market CP-02 |
| SP-05 | Should | Request logs hold only what operations need: request ID, ticker, latency and status. Logs are deleted after a set period, proposed at 30 days. | Log schema test. Retention job runs. | Product NFR-11; Market Section 6 |

### 3.7 Ethics, Licensing and Academic Integrity

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| ET-01 | Must | Before any user study, including the five-user usability test, the university ethics route is confirmed using the Ethics Decision Tool. Approval is obtained before recruitment. | Approval reference on file. | Proposal 7; C13. Manchester ethics page: approval routes are School or Division review, Proportionate UREC or Full UREC. |
| ET-02 | Must | Participants receive an information sheet and give consent. Identifying data is not kept beyond the approved period. | Documents on file. Retention date recorded. | C13. Information sheet requirement not stated on the ethics page: confirm with the approval route. |
| ET-03 | Must | A third-party register lists the licence and terms for every dataset, model and library used, including FinBERT weights and spaCy models. | Register is complete before the demo. | Data SR-01, SR-03; Proposal 4.2 |
| ET-04 | Must | No output or alert uses buy, sell or hold language. Every alert carries the disclaimer in FR-08. Confidence-threshold alerts are removed unless both rules are met. | Text scan of all alert templates. Disclaimer test passes. | C3; Product NG5, FR-08 |
| ET-05 | Must | The report declares AI-tool use as each assessment's guidance requires. Manchester sets an AI tier for each assignment (Prohibited, Minimal, Permitted or Required), and the tier is set by the unit lead. | Written confirmation of the tier and declaration format from the unit lead for each assessed item. | Manchester AI policy (tiers, per the EdTech Innovation Hub article). Declaration format not confirmed. |

### 3.8 Operations and Cost

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| OR-01 | Must | The PostgreSQL database is backed up daily, and a restore is tested once before the demo. Proposed targets: recovery point 24 hours, recovery time 4 hours. | Restore test log exists. | Planning notes, Cloud SQL; Product OP-03 |
| OR-02 | Must | A monthly ceiling for cloud and API spend is set before Week 3, with an alert at 80% of the ceiling. The value of the ceiling is a decision for John. | Budget alert exists in the cloud console. | Planning notes, deployment; Data DR-03 and FMP costs |
| OR-03 | Must | The demo database is separate from the evaluation dataset. Demo writes never change rows used for training or testing. | Demo service account has no write rights on the evaluation schema. | Data VL-04; Product ML-02 |

### 3.9 LLM Operations

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| AI-01 | Must | Each explanation records the prompt version, the model version and the generation settings. | All three fields are non-null on every stored explanation. | Product FR-11; Market EX-02 |
| AI-02 | Must | A fixed regression set of 50 event cases is re-run whenever the prompt or model changes. Faithfulness results must not fall below the previous version unless the drop is logged as a decision. | Regression report exists for each change. | Market EX-03, EX-04; Proposal 5.5 |
| AI-03 | Should | LLM-based metrics are reported as the mean and range across three runs, because LLM output varies between runs. | Results table shows three values per metric. | Proposal 5.5; Product Section 15 |

### 3.10 Documentation and Handover

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DO-01 | Must | A new machine can run the system from the README in under 30 minutes. The test is timed on a clean environment, ideally by someone other than the builder. | Timed run recorded. | Planning notes, Week 14; Proposal 8 |
| DO-02 | Must | Each major technology choice has an ADR: queue, frontend, vector store, model format, deployment target and LLM provider. | ADR list is complete before Week 6. | SC-01, SC-02, SC-06, SP-01 |
| DO-03 | Must | A traceability matrix maps every requirement ID to the test or evidence that proves it. | No requirement without evidence at submission. | ASM-01; Proposal 7 |
| DO-04 | Should | A runbook covers rollback, worker restart, re-ingestion of one day's data and database restore. Each step is run once in a non-production environment. | Each step has a dated run record. | Product OP-03; OR-01 |

## 4. Summary Count

| Area | Requirements | Must | Should |
|---|---|---|---|
| Assessment alignment (ASM) | 4 | 3 | 1 |
| Delivery and capacity (PD) | 5 | 4 | 1 |
| Supervision and change control (SS) | 4 | 4 | 0 |
| Scope and architecture (SC) | 6 | 6 | 0 |
| Engineering quality (EQ) | 8 | 7 | 1 |
| Security and privacy (SP) | 5 | 4 | 1 |
| Ethics and licensing (ET) | 5 | 5 | 0 |
| Operations and cost (OR) | 3 | 3 | 0 |
| LLM operations (AI) | 3 | 2 | 1 |
| Documentation (DO) | 4 | 3 | 1 |
| Total | 47 | 41 | 6 |

## 5. Decisions Needed Before Freeze

1. Confirm the ADR decisions for queue (SC-01), frontend (SC-02) and vector store (SC-06).
2. Confirm that mock data is removed from the plan for reported results (SC-04).
3. Confirm that the explanation evaluation uses the proposal's metrics (SC-05).
4. Remove the Slack confidence alert, or redesign it to meet ET-04 (C3).
5. Decide whether live streaming, insider and options, and the contrastive multi-agent system stay in scope. The product document excludes them, and the planning notes keep them (C9). A change needs SS-04.
6. Confirm the monthly spend ceiling for OR-02.
7. Confirm the ethics route for the user study with the Ethics Decision Tool (ET-01).
8. Ask the unit lead for the AI tier and declaration format for each assessed item (ET-05).

## 6. Changes Needed in Other Documents

| Document | Change |
|---|---|
| Planning notes (project memory) | Week 2 and Week 4: choose one queue design and remove Kafka or Redis Streams unless justified. Week 4: remove mock data for reported results. Week 6: record the vector store ADR. Week 9: mark live streaming as pending the SS-04 decision. Week 10: redesign or remove the Slack alert (ET-04). Testing table: replace ROUGE and BERTScore gate with SC-05 metrics. Deployment diagram: correct the Cloud Tasks and Celery relationship. Risk table: remove mock data mitigation, and replace the ROUGE mitigation. Week 15: user testing waits for ET-01. |
| Proposal | Section 4.2: resolve "Streamlit (or React)". Section 5.1: name the consensus source once IBES access is decided. |
| Architecture deck | Slide 6: add the decisions in Section 5 of this page. |

I have not edited the planning notes or the proposal. Section 6 lists the changes for you to approve.

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
