# Decision Log

The one place for open and closed decisions and for pending edits to documents outside the repository. It replaces the separate "open decisions" lists that were in the market, product, data and project-wide documents (Project-Wide SS-02).

The SSOT ([SSOT.md](SSOT.md)) holds what is fixed. This log holds what is not yet fixed. Claude may update this log. Claude does not change the SSOT.

Last updated: 15 November 2026 (owner answers on dates, hardware, hosting, LLM, retrieval and reminders).

## 1. Closed decisions (made by the owner)

| ID | Decision | Date | Where it applies |
|---|---|---|---|
| C-01 | The proposal is the scope baseline. Extensions are allowed, but overall capacity and scope stay at the proposal's level. | 14 Nov 2026 | SSOT Section 3A; Project-Wide PD-01, PD-02, PD-06 |
| C-02 | Sector-relative scoring is kept, as an extension, and broken into its own set of requirements. | 14 Nov 2026 | SSOT Section 3A; Product FR-12, SRS-01 to SRS-14 |
| C-03 | The primary data route must be free. Sources from any country are acceptable. A forward-only design is acceptable if the alternatives are worse. | 14 Nov 2026 | SSOT Section 4; Data SR-09, Section 4A |
| C-04 | The SSOT is owner-only. Claude asks permission before any edit to it. | 15 Nov 2026 | SSOT rules |
| C-05 | Each requirement is defined in exactly one document, by type: market, product, data, project-wide. | 15 Nov 2026 | SSOT Section 12; requirements README |
| C-06 | By the end of December 2026 the pipeline, models, API, explanation agent and evaluation are finished. Christmas week is buffer. | 15 Nov 2026 | Delivery plan; D-28 defines what is in scope |
| C-07 | Hosting: a locally runnable Docker build first, then Cloud Run if time allows. | 15 Nov 2026 | Product Section 16 (hardening milestone); Project-Wide EQ-04 |
| C-08 | Build on the owner's own PC. The owner installs Docker. Models such as FinBERT are downloaded locally. CPU first; a GPU may be added later. | 15 Nov 2026 | Data and NLP pipeline sizing |
| C-09 | Explanation agent: the working default is one hosted LLM API with a small spend cap. The provider and budget are finalised later (D-27). | 15 Nov 2026 | Project-Wide SP-04, AI-01 |
| C-10 | The SEC EDGAR User-Agent contact is the owner's email. It is set through an environment variable and is never committed to the repository. | 15 Nov 2026 | Data Section 4A.1 |
| C-11 | Retrieval for the explanation agent is plain SQL over per-sentence feature scores in PostgreSQL, not a vector store. | 15 Nov 2026 | Project-Wide SC-06; Product FR-05, EX-01 |
| C-12 | Week-one data spikes (small throwaway tests of the data sources) may be run from the working environment, and their results written into the data requirements. | 15 Nov 2026 | Data Section 12 |
| C-13 | Final submission is probably late February 2027. January and February are for Cloud Run deployment, frontend polish, the usability study, the dissertation write-up and final touches. | 15 Nov 2026 | Delivery plan; D-29 asks for the exact date |

## 2. Open decisions

| ID | Decision needed | Owner | Needed by | Related requirements |
|---|---|---|---|---|
| D-01 | **Label route.** The working plan is a time-series SUE from free EDGAR EPS, with consensus captured forward as a check (the owner agreed to proceed on 14 Nov 2026). It changes the proposal's label, so the supervisor must agree. Alternatives: a licensed consensus label, or a forward-only consensus label (about 500 events, no backtest). | John, with Professor Goodacre | Week 2 | Data CE-05, LB-01 to LB-08; Project-Wide C19, SC-07, ASM-06 |
| D-02 | Approve rewording the proposal's data description (the corpus is not public through EDGAR; the route is free sources, with licensed sources optional). | John | Week 2 | Project-Wide C14, ASM-05 |
| D-03 | Approve the drop order (the sequence in PD-06) and tag every feature Must, Should or Could. | John, with Professor Goodacre | Before week 3 | Project-Wide PD-02, PD-06, SS-03 |
| D-04 | Confirm the primary persona (quantitative researcher or independent analyst), or name another. | John | Week 2 | Market Section 2 |
| D-05 | Agree the non-functional targets (latency, freshness and the rest). | John, with Professor Goodacre | Week 2 | Product Section 5 |
| D-06 | Agree the data thresholds (coverage, segmentation accuracy, agreement rates, class balance and the rest). | John, with Professor Goodacre | Week 2 | Data Section 11 |
| D-07 | Agree the sector peer window (100 days) and minimum peer count (5). | John, with Professor Goodacre | Week 2 | Product SRS-04, SRS-06 |
| D-08 | Decide whether the explanation layer or the temporal evaluation is the headline contribution. The proposal gives them equal weight. | John, with Professor Goodacre | Week 2 | Market Section 3 |
| D-09 | Name the independent reviewer who signs off each model release. | John, with Professor Goodacre | Week 2 | Product ML-06 |
| D-10 | Record ADRs for the queue (Celery with Redis, or justify another) and the frontend (Streamlit or React; recommended Streamlit for capacity). Retrieval is decided (C-11). | John | Frontend: before the MVP dashboard. Queue: Week 6 | Project-Wide SC-01, SC-02, DO-02 |
| D-11 | Confirm mock data is removed from the plan for reported results. | John | Week 2 | Project-Wide SC-04 |
| D-12 | Confirm explanation quality is judged by rank agreement, sign agreement and citation checks, not by ROUGE or BERTScore thresholds. | John | Week 2 | Project-Wide SC-05 |
| D-13 | Remove the Slack confidence alert, or redesign it to meet ET-04. | John | Week 2 | Project-Wide C3, ET-04 |
| D-14 | Decide whether live streaming, insider and options data, and the contrastive multi-agent system stay out of scope. The product requirements exclude them and the planning notes keep them. A change needs a change entry. | John, with Professor Goodacre | Week 2 | Product NG1 to NG3; Project-Wide C9, SS-04 |
| D-15 | Set a ceiling for cloud hosting spend. Data spend is zero (C-03). | John | Before week 3 | Project-Wide OR-02 |
| D-16 | Confirm the ethics route for the user study with the university Ethics Decision Tool, before recruiting anyone. Apply in December: the study is planned for January or February, and approval can take weeks. | John | Apply in December | Project-Wide ET-01, ET-02 |
| D-17 | Ask the unit lead for the AI tier and declaration format for each assessed item. | John | Week 2 | Project-Wide ET-05 |
| D-18 | Choose the free transcript sources, and whether the public demo uses a historical slice or a bring-your-own-key design. Check the origin and licence of the Hugging Face transcript sets. If free sources fail, decide on a paid fallback (Alpha Vantage from $49.99 a month, or FMP Ultimate at $99 to $139). | John | Week 2 | Data SR-03, TX-04, TX-07, Section 4A |
| D-19 | Choose the fundamentals source (EDGAR XBRL company facts is free and is the working choice). | John | Week 1 | Data FD-01 |
| D-20 | Find a free point-in-time GICS sector history, or accept that sector scoring is switched off. | John | Week 2 | Data SEC-01; Product SRS-14 |
| D-21 | Send the library enquiry for I/B/E/S, Capital IQ Transcripts, CRSP and other institutional sources, and ask the supervisor about sponsorship. These are optional upgrades. | John | Week 1 | Data SR-05; `requirements/library-enquiry-draft.md` |
| D-22 | Find FinBERT's pretraining-corpus cutoff date. | John | Week 4 | Product FR-25 |
| D-23 | Set the beat, in-line and miss thresholds from the training window in EDA, then freeze them. | John | Week 4 | Data LB-06, VL-06 |
| D-24 | Read the FinCall-Surprise LICENSE file before using it for the benchmark replication. | John | Before week 6 | Product FR-27 |
| D-25 | Write the assessment requirements document, or remove it. It is empty today. | John | Week 2 | `requirements/assessment-requirements.md` |
| D-26 | Re-tag data requirements. 66 of 70 are Must, which is not a priority order. Candidates for Should: VL-08, VL-09, AE-02, TX-03, GS-02, DV-04, VL-10. Also consider halving the sample sizes in VL-09 and AE-02. | John, with Professor Goodacre | Before week 3 | Data Section 11; Project-Wide PD-01, PD-02, PD-06; `requirements/proposal-drift-review.md` Section 4 |
| D-27 | Choose the LLM provider, monthly budget and licence check for sending transcript text to a third party. Working default: one hosted API with a small cap (C-09). The owner asked to be reminded. | John | Before building the explanation agent | Project-Wide SP-04, AI-01, DO-02 |
| D-28 | Confirm the scope for the end of December. Proposed: Docker Compose (PostgreSQL, Redis, Celery worker, FastAPI); EDGAR EPS and Hugging Face transcripts for a subset of companies, widened if time allows; time-series label; FinBERT, hedge-word, negation and Q&A features; baseline and full XGBoost on the temporal split with SHAP; prediction and explanation endpoints; the explanation agent with citation checks and the faithfulness harness; the evaluation page with intervals and baselines; a minimal Streamlit card. Not by December: sector scoring (extension), Cloud Run, the usability study. Also start the forward consensus capture job in the first week. | John | This week | Product Section 16; Data SR-10 |
| D-29 | Give the exact final submission date. The owner said late February 2027 (C-13). Capacity: from 15 November to 31 December is about 6.5 weeks, roughly 100 to 130 hours at 15 to 20 hours a week, for work the 16-week plan spreads over about 13 weeks (milestones 1 to 6). To late February is about 15 weeks, roughly 225 to 300 hours in total. The December scope will not fit every Must requirement. D-26 (re-tagging the 66 Must data requirements) and D-03 (drop order) are therefore needed before week 3. | John | This week | Project-Wide PD-01, PD-03, PD-06 |
| D-30 | Decide where the proposal PDF and planning notes go. Recommended: `docs/source/`, not the requirements folder, because they are sources, not requirements. If the repository is public, they become public. This also needs one new row in the SSOT document map, which only the owner edits. | John | This week | SSOT Section 12 |

## 3. Pending edits to documents outside the repository

These documents are not edited by Claude. Each row is a change for the owner to approve.

| Document | Change | Reason |
|---|---|---|
| Proposal | Section 4.2: resolve "Streamlit (or React)". | D-10 |
| Proposal | Section 5.1: replace the EDGAR transcript route; name the free sources; replace the consensus-based label with the working label route if approved. | D-01, D-02 |
| Proposal | Sections 1, 3.1 and 8: reword "public corpus". | D-02 |
| Proposal | Section 3.3: the SAE-FiRE sentence can be read as an XGBoost AUC of about 0.67. The paper reports 0.620 for XGBoost on earnings calls and 0.657 to 0.668 for SAE-FiRE's own models. | Correction, 14 Nov 2026 |
| Planning notes | Weeks 2 and 4: one queue design (no Kafka or Redis Streams unless justified). Week 4: no mock data in reported results. Week 6: vector store ADR. Week 9: live streaming pending D-14. Week 10: redesign or remove the Slack alert. Testing table: replace the ROUGE and BERTScore gate. Deployment diagram: correct the Cloud Tasks and Celery relationship. Risk table: remove the mock-data mitigation and the ROUGE mitigation. Week 15: user testing waits for D-16. Testing table: remove the 70% accuracy and AUC above 0.70 targets. | Project-Wide C1 to C13 |
| Deck, slide 2 | Draw the drift monitor, transcript index and model registry as optional. | PD-06 |
| Deck, slide 6 | List the decisions in Section 2 above. | D-01 to D-30 |

## 4. Reminders for the owner

Claude surfaces these at the trigger, without being asked. They are also saved in Claude's memory.

| Reminder | Trigger | Related |
|---|---|---|
| Install Docker under WSL2. | Before any database or container work. | C-08 |
| Create free accounts and keys: Hugging Face (token), Alpha Vantage (free key), and later a GCP project. Share them through environment variables, never in the repository. | Hugging Face and Alpha Vantage before ingestion; GCP before Cloud Run. | Data Section 4A.1 |
| Choose the LLM provider, budget and licence check. | Before building the explanation agent. | D-27 |
| Add the proposal PDF and planning notes to the repository (or decide not to). | This week. | D-30 |
| Provide the assessment criteria from the unit, or decide to remove the empty assessment document. | When you have them, and before the requirements freeze. | D-25 |
| Send the library enquiry for optional institutional data, and ask the supervisor about sponsorship. | Week 1. | D-21 |
| Apply for ethics approval for the usability study. | December. | D-16 |
