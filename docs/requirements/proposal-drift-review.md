# Proposal Drift Review

Compares every requirement document and the architecture deck against the Third Year Project Proposal (2026-27). Reviewed 14 November 2026.

Documents compared:
- Product requirements (current branch)
- Market requirements, **taken from commit `c5230be`**. Commit `aaaeac7` overwrote the file with a copy of the project-wide document.
- Data requirements
- Project-wide requirements
- Architecture deck (6 slides)

Drift means one of four things:
1. Something the proposal commits to has no requirement.
2. A requirement contradicts the proposal.
3. Scope has grown beyond what the proposal's capacity supports.
4. The documents disagree with each other.

Later extensions are allowed. They must not displace core work, and they must be tagged so they can be dropped.

## 1. Bottom Line

1. **The core is intact.** The documents keep all of the following from the proposal:
   - the research question
   - the 2015–21 / 2022 / 2023–24 split
   - SUE labelling with thresholds frozen during EDA
   - FinBERT, spaCy and XGBoost
   - the tabular baseline
   - F1, Brier and precision at the top 20%
   - the single-pass agent, judged on rank agreement, sign agreement and citation checks
   - the stack: FastAPI, Celery, Redis, PostgreSQL, Docker and Cloud Run
2. **Several proposal commitments have no requirement** (Section 2). The most serious is the tabular features. Revenue growth, gross margin and operating margin have no data source in any document.
3. **Three requirements contradict the proposal** (Section 3):
   - Promoting a model needs a comparison that "passes", but the proposal accepts a negative result.
   - The AUC target compares a three-class model with a binary benchmark.
   - JWT authentication is said to come from the proposal. It does not.
4. **Scope has grown far beyond the proposal.** The documents hold about 215 requirements:
   - 116 are tagged Must.
   - The 59 product requirements carry no priority at all, which in practice means Must.
   - The proposal describes 7 milestones.

   The project-wide rule PD-01 caps planned effort at 20 hours a week. The current Must set does not fit under that cap (Section 4).
5. **The documents disagree with each other** (Section 5):
   - Market and product requirements reuse the same IDs (FR-xx, NFR-xx) for different things.
   - SC-01 means two different things.
   - G1 to G6 are product goals, and G1 to G5 are also data gates.

## 2. Proposal Commitments With No Requirement

| # | Proposal item | Proposal section | Where it went | Action |
|---|---|---|---|---|
| P1 | Tabular features: revenue growth, gross margin, operating margin | 5.2 | No fundamentals dataset in the data document. Its six datasets are transcripts, actual EPS, consensus, membership, sector and prices. | Add a seventh dataset: quarterly fundamentals, with a point-in-time filing date (EDGAR XBRL company facts or Compustat). Add source, verification and G1/G2 checks. The value is only known from the 10-Q filing date, which can fall after the announcement. |
| P2 | Prior four-quarter EPS surprise trend and analyst dispersion as features | 5.2 | Implied by the actual EPS and consensus data. No feature requirement. | Add a tabular feature requirement that names all five proposal features and their cutoff dates. |
| P3 | Text features: sentiment trajectory (first half against second half), forward-guidance ratio, Q&A sentiment delta, question counts (4.1) | 5.2, 4.1 | Not in the product requirements. Only FR-15 to FR-18 exist: segmentation, FinBERT, hedges and negation, and the z-score. | Add one requirement listing the full proposal feature set, or record the dropped features in the decision log. |
| P4 | Agent step 3: an optional tool call checking a later 8-K for corroborating or contradicting information | 4.3 | Dropped silently. Not in the deck (slide 5) or the EX requirements. | Decide: drop it and log the decision, or keep it as Could. If kept, explanations must label post-announcement evidence, and the deck's cutoff note (slide 3) must say that the cutoff applies to predictions, not to evidence in explanations. |
| P5 | FinBERT pretraining-cutoff sanity check | 5.4 | Only a risk row in the product requirements, Section 18. No ID and no acceptance check. | Add a Must requirement: compare score-to-outcome accuracy before and after the FinBERT pretraining cutoff, and report the result either way. |
| P6 | SHAP explanations consistent with domain knowledge (for example, high uncertainty leads to worse outcomes) | 7 | No requirement. | Add a Should requirement: global SHAP direction for 3 to 5 named features against expected signs, reported in the evaluation. |
| P7 | SHAP used for global feature importance | 5.3 | Only local (top-three) SHAP is required. | Add global SHAP to the evaluation page requirements (FR-06 or FR-10). |
| P8 | Stretch: fine-tune a model on financial transcripts | 2 | Not mentioned anywhere. | List it as Could, after the other stretch items. |
| P9 | Stretch: five-class output, and the P&L backtest | 2 | Only in the old market document, as Could (FR-12 and FR-13). Missing from the product requirements. | Carry both into the product requirements as Could. See C5 for the P&L conflict. |

## 3. Contradictions With the Proposal

| # | Where | Conflict | Fix |
|---|---|---|---|
| C1 | Product ML-06; deck slide 4, gate 5 | A model is served only after "the FR-06 comparison passes". The proposal (Section 7) says a negative result, where NLP adds nothing, is a valid finding. If "passes" means "beats the baseline", a valid outcome blocks the demo. | Define "passes" as: the comparison has run on the sealed test set and been reported, and the reviewer has signed off. Winning is not required. |
| C2 | Product Section 15; market Section 7 | The AUC target is "at least match SAE-FiRE (about 0.67)". SAE-FiRE is a binary beat/miss task. This project has three classes. A three-class AUC is not comparable, and the proposal treats SAE-FiRE as a reference point, not a target ("falling short ... would say something"). | Report a binary beat-against-miss AUC (in-line excluded) as the comparison with SAE-FiRE, and mark it as a reference, not a pass mark. |
| C3 | Market NFR-06; product NG4 | Both say JWT and demo authentication are "as the proposal states". The proposal does not mention authentication. | Remove the attribution. Keep JWT as a requirement traced to the security work (SP-02), not to the proposal. |
| C4 | Data document, Section 3; proposal Sections 1, 5.1 and 8 | The proposal's case rests on a public corpus ("published openly through SEC EDGAR"; "the corpus is public"). The data document shows transcripts and consensus must come from licensed WRDS sources. The data change is correct, but the proposal's justification no longer holds as written. | Record a change entry (SS-04). Reword the submission justification: the label and lookahead checks are the point, and the corpus is licensed academic data. |
| C5 | Market FR-13 (Could) against market Section 8 and product NG5; project-wide ET-04 | The proposal lists the P&L backtest as a stretch goal. The market document lists it as Could, and then says in Section 8 that it is excluded. A P&L figure also sits close to the "no buy, sell or hold language" rule. | Decide once. If kept, frame it as a research measure on historical data, with no trade language. |
| C6 | Product problem statement and goals | They frame the product around a market user and a competitor gap. The proposal (Sections 1 and 8) says the contribution is the distributed systems design and the ML method, with finance as the test domain. The market document keeps that framing; the product document does not. | Add one line to the product problem statement restating the proposal's framing, so the dissertation does not drift toward a product pitch. |

## 4. Scope and Capacity Drift

### 4.1 Size

| Document | Requirements | Must | Should | Could | No priority |
|---|---|---|---|---|---|
| Product | 59 | 0 | 0 | 0 | 59 |
| Market (`c5230be`) | 58 | 25 | 13 | 3 | 17 (needs, NFR and DR tables) |
| Data | 51 | 49 | 2 | 0 | 0 |
| Project-wide | 47 | 41* | 6* | 0 | 0 |

\*The document's own summary gives 41 and 6. A raw text count finds 42 and 7, because "Must" and "Should" also appear in other table cells.

Two of the documents' own rules are broken here:
- PD-02 requires a Must, Should or Could tag on every feature. The product document has none.
- PD-01 caps planned effort at 20 hours a week.

The proposal has 7 milestones and a "lightweight" dashboard. The product milestone plan (Section 16) gives no time to the data validation work, which includes:
- hand-labelling 50 transcripts
- a 100-event hand audit
- a 200-event EPS cross-check
- a 4-week snapshot trial
- 30-event replays

It also gives no time to the project-wide process work: ADRs, a traceability matrix, a novelty register, an OWASP review, a runbook and restore drills.

### 4.2 Additions Not in the Proposal

Each addition is placed in a tier. "Core" means the proposal needs it. "Keep" means it is cheap and strengthens the proposal's own claims. "Drop order" means it should be tagged Could and dropped first if a milestone slips (PD-04).

| Addition | Where | Tier | Reason |
|---|---|---|---|
| Five gates, three dates, estimate snapshots, point-in-time membership, sealed test set | Deck slide 4; FR-02, FR-03, FR-14; data G1 to G5 | Core | This is how the proposal's central claim (no lookahead) is made testable. |
| Q&A segmentation, z-score, hedge and negation | FR-15 to FR-18 | Core | Named in proposal 5.2. |
| Async explanation jobs, history endpoint, edge cases, ticker validation | FR-07, FR-09, FR-19, FR-20 | Core | Proposal 6 and 7. |
| Bootstrap CIs, naive baselines, multiple-testing disclosure | Market TR-01, TR-02, TR-06 | Keep | Cheap, and they protect the headline result. Missing from the product document: add them. |
| EX-01, EX-03, EX-04; citation verification; prompt-injection test (SP-03) | Market, project-wide | Keep | Directly support proposal 5.5. |
| CI tests, lint, branch protection, one-command container build, SP-01 (no pickle) | Project-wide EQ-01 to EQ-04, SP-01 | Keep | Low cost and expected for a systems project. |
| Fault-injection and idempotency tests | EQ-06, EQ-07 | Keep | Evidence for the distributed-systems claim (proposal 8). |
| Ethics approval before user testing | ET-01, ET-02 | Keep (required) | University rule, not optional. |
| **Sector-relative score** | Product G6, FR-12, UI-04, sector screen, SectorBenchmark entity; data sector classification IDs, VL-03, VL-11; deck | **Drop order: first** | Not in the proposal. Market rated it Should, but product made it a goal with a 90% coverage target. It depends on point-in-time GICS history, which is unverified (DR-06). Retag as Could. |
| **Consensus-revision baseline (StarMine-style)** | Product FR-06 (third model, required) | **Drop order: first** | Not in the proposal; market rated it Should. It needs historical estimate revisions, the same blocked I/B/E/S dependency. Tag Could. Make FR-06 require only the tabular baseline and the two naive baselines. |
| Drift monitor, outcome tracking, SHAP rank drift | Deck slide 2; MR-04 to MR-06 | Drop order | Not in the proposal. Useful, but post-deployment work. Tag Could and remove from the core diagram, or draw it dashed. |
| Model registry, model inventory, per-version model card | Deck slide 2; MR-01, MR-02, MR-07 | Reduce | Keep one model card and a checksum (ML-03). Drop the inventory and risk tiers. |
| Per-claim LLM faithfulness labels, human rating, 50-case regression set, three-run reporting | EX-02, EX-05, AI-02, AI-03 | Drop order | Beyond proposal 5.5 (rank, sign, citation). It adds an LLM-as-judge component. Keep AI-01 (record prompt and model version). |
| Transcript vector index / vector store | Deck slide 2; SC-06 | Reduce | The proposal's retrieval is feature-driven (for example, the highest hedge-density Q&A sentences). That can be plain SQL over scored sentences, with no embeddings and no licence question. Make the vector store Could. |
| 100-concurrent load test, OWASP review, backup restore drill, runbook, budget alert, CDN, Cloud Logging | EQ-05, SP-02, OR-01, DO-04, OR-02, deck slide 6 | Reduce | Keep the budget alert (cost safety) and one rollback drill. Tag the rest Should or Could. |
| WCAG 2.1 AA, 375 px layout, autocomplete, seven screens | NFR-07, NFR-08, UI-01 to UI-05, product Section 14 | Reduce | The proposal promises a lightweight dashboard: search, prediction card and feature chart. Keep those three, plus the explanation view and evaluation page. Tag the rest Could. |
| Data validation sample sizes | Data TX-03 (50), VL-09 (100), AE-02 (200), VL-02 and VL-03 (30) | Reduce | Halve the sample sizes as a proposal for the supervisor, or move the larger samples to Should. |
| ADRs, traceability matrix, novelty register | DO-02, DO-03, ASM-03 | Keep, but light | One page each. Do not let them become deliverables in their own right. |

## 5. Inconsistencies Between Documents

| # | Problem | Fix |
|---|---|---|
| I1 | `market-requirements.md` on this branch is a byte-identical copy of `project-wide-requirements.md`. The real market document exists only in commit `c5230be`. `assessment-requirements.md` is empty. | Restore from `c5230be`. Add or remove the assessment document. |
| I2 | Market and product use the same IDs for different requirements. Market FR-12 is the five-class output (Could); product FR-12 is the sector score. Market FR-16 is the sector score; product FR-16 is FinBERT. Market NFR-05 is explanation latency; product NFR-05 is reproducibility. Other documents cite "Product FR-xx" or bare "FR-xx" inconsistently. | Prefix the IDs (MKT-FR, PRD-FR) or renumber the market FRs. Product is the build reference. |
| I3 | SC-01 means "sector history" in the data document and "queue design" in the project-wide document. | Rename the data IDs to SEC-01 and SEC-02. |
| I4 | G1 to G6 are product goals; G1 to G5 are data gates. | Rename the gates to GATE-1 to GATE-5. |
| I5 | Market FR-15 (evidence base, Must), FR-17 (as-of timestamp of every input, Must) and FR-18 (show the SUE definition and thresholds) have no product requirement. They appear only loosely in the evaluation-page screen list. | Add them to the product document, or record them as dropped. FR-17 is cheap and supports the no-lookahead claim. |
| I6 | Milestone order. The proposal puts the frontend before the agent. The product document puts the explanation layer (weeks 10–11) before the frontend (weeks 12–13), and deploys the API in weeks 14–15 rather than at the backend milestone. | Acceptable, but record it as a change from the proposal. |

## 6. Recommended Actions

1. Restore the market document from `c5230be` (I1).
2. Add the missing proposal items P1 to P7 to the product and data documents. P1 (the fundamentals dataset) is the only one with a data-access risk.
3. Fix contradictions C1 to C3 now. They are wording changes. Put C4 and C5 in the decision log for the supervisor.
4. Add MoSCoW tags to every product requirement. Apply the tiers in Section 4.2. Record the drop order (PD-02), with the sector score and the consensus-revision baseline first.
5. Update the deck: draw the drift monitor, the transcript index and the model registry as optional, and add the decisions in project-wide Section 5 to slide 6.
6. Resolve the ID collisions (I2 to I4) before building the traceability matrix (DO-03). Otherwise the matrix inherits them.

None of the requirement documents, the proposal or the deck have been changed. This page lists the changes for approval.

## 7. Fix Status (14 November 2026)

| Item | Status | Where |
|---|---|---|
| I1 market document restored | Done | `market-requirements.md` restored from `c5230be`, then revised. `assessment-requirements.md` is still empty. |
| P1 fundamentals | Done | Product FR-24; Data FD-01 to FD-04 |
| P2, P3 full feature set | Done | Product FR-24 |
| P4 agent 8-K step | Done as stretch | Product ST-05 |
| P5 FinBERT cutoff check | Done | Product FR-25 |
| P6, P7 SHAP checks | Done | Product FR-26 |
| P8, P9 stretch objectives | Done | Product Section 2.3 (ST-01 to ST-05) |
| C1 promotion rule | Done | Product ML-06; Project-Wide C16 |
| C2 AUC target | Done | Product FR-06 and Section 15; Market Section 7 |
| C3 JWT attribution | Done | Product NG4; Market MNFR-06 |
| C4 public corpus wording | Logged | Project-Wide C14 and ASM-05. The proposal text itself is unchanged. |
| C5 P&L conflict | Done | Market Section 8; Product NG2 and ST-02 |
| C6 framing | Done | Product Section 1 |
| I2 to I4 ID collisions | Done | MFR/MNFR prefixes, GATE-1 to GATE-5, SEC-01/02, PG-1 to PG-6. A script finds no duplicate definitions and no undefined references. |
| I5 evidence base, as-of times, label definition | Done | Product FR-21, FR-22, FR-23 |
| Capacity: MoSCoW tags | Done | Every product requirement now has a priority. Drop order in Project-Wide PD-06. |
| Capacity: reducing scope | Partly | Several items are retagged Could or Should. Nothing was deleted. The supervisor must approve the drop order. |
| Sector-relative scoring | Kept and broken down | Product FR-12 and SRS-01 to SRS-14 (Section 4A) |
| Deck | Partly | Slides 3 and 4 peer wording aligned. Slide 6 decisions and the optional boxes on slide 2 are not changed. |
| Proposal and planning notes | Not changed | Listed in Project-Wide Section 6 |
