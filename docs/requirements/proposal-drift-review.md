# Proposal Drift Review

Compares every requirement document and the architecture deck with the [SSOT](../SSOT.md), which restates the proposal and the owner's decisions. Rewritten 15 November 2026. The SSOT is a draft awaiting the owner's approval, so this review compares against the draft.

How to repeat it: run `python3 docs/tools/check_requirements.py` (structure), then read Sections 2 to 4 of this file against the SSOT (meaning).

## 1. Result

1. **The core is intact.** Every commitment in SSOT Sections 2 to 10 has a requirement (Section 2).
2. **Five deliberate variants** differ from the proposal. None is approved yet (Section 3).
3. **Capacity is the main remaining drift.** 161 of the 215 requirements outside the market document are Must, and 66 of the 70 data requirements are Must. The proposal's capacity (15 to 20 hours a week) is not shown to fit (Section 4).
4. **Structure is fixed.** No ID is defined twice. Each requirement is in the document that owns its type. Withdrawn IDs are in the README registry. A script checks this.
5. **Open items** are in the [decision log](../decision-log.md), not here.

## 2. Traceability: SSOT to requirements

| SSOT item | Defined in | Status |
|---|---|---|
| Research question (NLP against tabular baseline, negative result valid) | Product PG-2, FR-06, ML-06 | Covered |
| Ingestion pipeline and PostgreSQL schema | Product PL-01 to PL-06, FR-13, Section 11; Data SR, TX, AE, DV | Covered |
| NLP features: FinBERT, hedge words, negation, Q&A, z-score, trajectory, guidance ratio, question counts | Product FR-15 to FR-18, FR-24 | Covered |
| Tabular features: EPS surprise trend, revenue growth, margins, dispersion, momentum | Product FR-24; Data FD-01 to FD-04, PX-01 to PX-03 | Covered. Dispersion is a variant (Section 3). |
| XGBoost, tabular baseline, full model | Product FR-06, ML-01 to ML-06 | Covered |
| Split 2015-21 / 2022 / 2023-24, test set read once | Product FR-03, ML-02; Data VL-04 | Covered |
| Label: SUE with frozen thresholds | Data CE-05, LB-01 to LB-08, VL-06; Product FR-23 | Variant (Section 3) |
| Three dates stored separately | Product FR-02; Data GATE-1, TX-02, DV-05 | Variant (Section 3) |
| Target corpus: S&P 500, 2015-2024, 4,000 to 5,000 events, membership as of each date | Data TX-04, IM-01 to IM-03 | Covered |
| F1, Brier, precision at top 20%; SHAP global and local | Product FR-04, FR-06, FR-10, FR-26 | Covered |
| FinBERT pretraining-cutoff check | Product FR-25 | Covered |
| Explanation agent: top SHAP features, retrieval, synthesis | Product FR-04, FR-05, FR-19, EX-01 to EX-04 | Covered |
| Agent step 3, optional 8-K corroboration | Product ST-05 (stretch) | Covered as stretch, as the proposal calls it optional |
| Faithfulness: rank agreement, sign agreement, citation check | Product EX-03, FR-05; Project-Wide SC-05 | Covered |
| FastAPI endpoints: prediction, explanation, history | Product Section 13, API-01 to API-07 | Covered |
| Edge cases: no transcript, API failure, cold start | Product FR-07, FR-20, Section 12 | Covered |
| Frontend: ticker search, prediction card, feature chart | Product Section 14, UI-01 to UI-05 | Covered |
| Stack: Celery with Redis, FastAPI, PostgreSQL, Docker, Cloud Run | Project-Wide SC-01, SC-02, EQ-04; decision D-10 | Covered. Streamlit or React is still to be chosen. |
| Milestones 1 to 7 | Product Section 16 | Covered. Order differs (Section 3). |
| Evaluation criteria 1 to 6 | Product Section 15, FR-06, FR-26, FR-07, UI-03, EX-03 | Covered |
| Stretch: fine-tuning, five-class, P&L | Product ST-01, ST-02, ST-04 | Covered, all Could |
| Capacity 15 to 20 hours a week | Project-Wide PD-01 | Covered as a rule. Fit not shown (Section 4). |
| Ethics approval before user study | Project-Wide ET-01, ET-02 | Covered |
| Not investment advice | Product FR-08, NG5; Project-Wide ET-04 | Covered |

## 3. Deliberate variants (not yet approved)

| Variant | What differs from the proposal | Why | Decision |
|---|---|---|---|
| Label route | The historical label can be a time-series SUE from EDGAR EPS, with analyst consensus captured forward as a check. | No free source gives historical point-in-time consensus with a standard deviation, and the owner decided the primary route must be free (SSOT Section 4). | D-01 |
| Information date | The estimate-publication date becomes an information date (latest EPS filing date for the time-series label). | Follows the label route. | D-01 |
| Dispersion feature | Analyst dispersion is replaced by the dispersion of past seasonal EPS differences on the time-series route. | Follows the label route. | D-01 |
| Milestone order | The explanation layer comes before the frontend, and the API is deployed in the hardening milestone. | The dashboard can then show explanations. Recorded in Product Section 16. | D-03 |
| Data description | The proposal says the corpus is public through EDGAR. Transcripts and consensus are not. | Verified in the data research of 14 November 2026. | D-02 |

Related correction. The documents said SAE-FiRE's XGBoost baseline had AUC about 0.67. The paper's table gives 0.620 for XGBoost on earnings calls and 0.657 to 0.668 for SAE-FiRE's own models. SAE-FiRE's label also uses analyst forecasts issued up to a month after the call, and its sample is 2012 to 2014. Corrected in Product FR-06, FR-27 and Section 15.

### 3.1 What the label change means

| | Proposal label | Time-series label |
|---|---|---|
| Question answered | Did earnings beat what analysts expected? | Did earnings move more than the seasonal pattern predicts? |
| Needs | Historical consensus with standard deviation (licensed) | EPS history from SEC EDGAR (free) |
| Events 2015 to 2024 | 4,000 to 5,000 | 4,000 to 5,000 after a warm-up from about 2012 |
| Backtest | Yes | Yes |
| Comparable with SAE-FiRE and Koval et al. | Yes, apart from their post-call forecasts | No: label differs (Project-Wide ASM-06) |
| Noise | Lower | Higher: analyst forecasts are generally more accurate at short horizons (unverified secondary sources) |

Consequences for requirements: the consensus-revision baseline exists only on the forward set; peer SUE in sector scoring follows the label route; GATE-2 covers EPS first filed before the announcement; Data LB-08 reports agreement with the consensus label on the forward set. Forward-only consensus would give about 500 events from one earnings season, so no backtest and low power.

## 4. Capacity

| Document | Requirements | Must | Must if built | Should | Could |
|---|---|---|---|---|---|
| Market | 7 needs | 6 | 0 | 1 | 0 |
| Product | 91 | 50 | 8 | 29 | 4 |
| Data | 70 | 66 | 0 | 4 | 0 |
| Project-wide | 54 | 45 | 0 | 9 | 0 |

- **The proposal has 7 milestones and a lightweight dashboard.** The documents hold 215 requirements outside the market document. 161 are Must.
- **Data requirements are almost all Must (66 of 70).** Most are verification and validation checks. Large samples add work: a 100-event hand audit (VL-09), a 200-event EPS cross-check (AE-02), a 50-transcript hand label (TX-03), 30-event replays (VL-02, VL-03), and 20 canary events (VL-08).
- **Not shown:** no hours estimate exists for any milestone. PD-01 requires one, and it has not been made.
- **Mitigation in place:** PD-06 sets a drop order and sector scoring is kept with a switch-off rule (SRS-14).

Candidates to retag from Must to Should, for the owner to decide (D-26): VL-08, VL-09, AE-02, TX-03, GS-02, DV-04, VL-10 (the forward capture already satisfies it). Halving the sample sizes in VL-09 and AE-02 is the other lever.

### 4.1 Additions that are not in the proposal

| Addition | Where | Tier |
|---|---|---|
| Five gates, snapshots, point-in-time membership | Data GATE-1 to GATE-5; Product FR-02, FR-14 | Core: how the lookahead claim is made testable |
| Bootstrap intervals, variant disclosure, naive baselines | Product TR-01, TR-02, TR-06 | Keep: cheap, protect the headline result |
| Claim labels, human rating, regression set, repeat runs | Product EX-02, EX-05; Project-Wide AI-02, AI-03 | Beyond proposal Section 5.5. EX-05, AI-02, AI-03 are Should and early in the drop order. |
| Sector-relative scoring | Product FR-12, SRS-01 to SRS-14 | Owner-approved extension (SSOT Section 3A). Should. |
| Consensus-revision baseline | Product FR-06 | Should, conditional |
| External benchmark replication | Product FR-27 | Should |
| Model inventory, drift and rank monitoring | Product MR-01, MR-04 to MR-06 | Should, early in the drop order |
| Load test, runbook, restore drill | Project-Wide EQ-05, DO-04, OR-01 | Should |
| JWT authentication | Product API-06 | Not in the proposal. Added for the security review (Project-Wide SP-02). |
| Accessibility, 375 px layout, autocomplete, extra screens | Product NFR-07, NFR-08, UI-01, UI-02, UI-05 | Should or Could |

## 5. Contradictions and duplicates fixed in this review

- **Promotion rule** (Product ML-06): now needs the comparison reported, not won, because the proposal accepts a negative result.
- **AUC target:** now a binary AUC reported as a reference, with the corrected 0.620 baseline (Product FR-06, Section 15).
- **JWT:** no longer attributed to the proposal.
- **P&L simulation:** a research stretch measure only (Product ST-02).
- **Priorities:** load test, restore drill, regression set and model inventory were Must but sit in the drop order. They are now Should (Project-Wide EQ-05, OR-01, AI-02; Product MR-01).
- **Duplicates merged:** reproducibility (Product NFR-05 into ML-01), secrets (NFR-06 and OP-01 into SP-06), pinned builds (OP-02 into EQ-04), rollback (OP-03 into DO-04), test coverage (NFR-10 into EQ-09), sealed test set (TR-03 into ML-02), independent review and retrain gate (MR-03 and MR-07 into ML-06), accuracy claims (CP-01 into ASM-02), baselines and intervals (FR-06 and FR-10 now cite TR-01, TR-02, TR-05, TR-06), snapshot capture rules (FR-14 now cites Data SR-08, SR-10), source and licence registers (Project-Wide ET-03 now covers models and libraries only), keyboard accessibility (NFR-07 now cites UI-05).
- **Misplaced requirements moved:** functional and non-functional requirements out of the market document into the product document; data risks out of the market document into the data requirements; evaluation, governance and explanation requirements into the product document; compliance and adoption items to the data, product and project-wide documents. See the registry in [README.md](README.md).
- **Data document:** the gate matrix listed paid WRDS sources as preferred, which contradicted the free-first decision. It now shows the free primary route and lists paid sources as optional upgrades.
- **Open-decision lists** in four documents (with repeats) merged into one decision log.
- **Deck:** slides 3, 4 and 6 updated for the peer cutoff (strictly before the announcement), the information date and the moved IDs.

## 6. Still open

- The SSOT is a draft until the owner approves it.
- Decisions D-01 to D-26 in the [decision log](../decision-log.md). The highest priority are D-01 (label route), D-03 (drop order) and D-26 (Must tags on data requirements).
- `assessment-requirements.md` is empty (D-25).
- The deck's slide 2 does not yet mark the drift monitor, transcript index and model registry as optional, and slide 6 does not yet list the open decisions.
- The proposal and planning notes are not edited by Claude. Pending edits are in the decision log, Section 3.
- Unverified inputs behind some requirements: Bernard and Thomas (1989) scaling window; early XBRL coverage and fourth-quarter EPS derivation; free-tier estimate endpoints on Finnhub and FMP; the origin and licence of the Hugging Face transcript sets; the FinCall-Surprise LICENSE file; GICS structure changes (2016 and 2018) in Product SRS-02, written from memory.
