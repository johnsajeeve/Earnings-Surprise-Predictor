# Market Requirements: LLM-Powered Earnings Surprise Predictor

Derived from the Third Year Project Proposal (2026-27), the project design notes, and research into model risk management, backtest validation, model monitoring and LLM explanation faithfulness. Updated 26 October 2026.

## 1. Purpose and Scope

This document sets out what the market needs from the Earnings Surprise Predictor, which requirements follow from those needs, and where the current proposal is not yet ready to meet them. It tests the proposal against a real use case, so the design choices in Section 4 of the proposal can be defended against more than the project's own assumptions.

The proposal states that the contribution lies in the distributed systems design and the ML methodology, with finance as the test domain. This document keeps that framing. It answers a narrower question: who would use a system like this, what they would need to trust its output, and which of those needs the design can meet within 16 weeks.

Market size is deliberately not estimated. No figure here comes from a market research report, and none should be quoted until one is found.

## 2. Target Users

| Rank | Segment | What they do today | Fit with proposal |
|---|---|---|---|
| 1 | Independent quantitative researchers and small-fund analysts | Build their own earnings signals from consensus data and filings. Already hold a consensus data licence or have university access. | High. They can judge the temporal split and SHAP output, and they need a second opinion they can inspect. |
| 2 | Equity research analysts at small or mid-sized firms | Write notes on upcoming results. Want a quick, cited read on a call. | Medium. The explanation layer fits, but the prediction is a weak input for a published view. |
| 3 | Retail investors on self-directed platforms | Read headlines and summaries, sometimes act on them. | Low. Would need investment-promotion compliance and data licensing the project does not have. |

**Recommended primary persona:** a quantitative researcher at a small fund, or an independent analyst with access to point-in-time consensus data. This person is hard to satisfy with a black-box score and easy to satisfy with a faithful, inspectable explanation. The rest of this document assumes that persona.

## 3. Competitive Landscape

Checked against each product's own published pages. Unconfirmed claims are marked.

| Product | Offer | Target user | Gap, as far as published material shows |
|---|---|---|---|
| LSEG StarMine SmartEstimate | Forecasts earnings surprises and estimate shifts. Weights analyst estimates by past accuracy and recency, and publishes a "Predicted Surprise" signal. Delivered by API, Excel, Snowflake and similar channels. | Investors, equity researchers, screening and valuation teams. | The product description does not mention earnings call transcript text as an input. It is estimate-based, not text-based. |
| Bloomberg Point-in-Time | Historical point-in-time dataset for 58,000 companies: financials, consensus, guidance and pricing. | Quantitative and research analysts, institutional investors. | A data product, not a prediction product. Customers build their own models on it. |
| AlphaSense Earnings Analysis | Cited call summaries within hours, question answering over single transcripts, grid analysis across many transcripts, and a sentiment score from -100 to 100. | Hedge funds, asset managers, private equity, investment banking. | The product page does not describe a beat/miss prediction or a per-prediction explanation tied to a model. |
| Academic baselines: Koval et al. (2023, 2024), SAE-FiRE (2025) | Research results on beat/miss prediction from transcripts. SAE-FiRE reports an XGBoost baseline with AUC around 0.67 under a chronological split. | Researchers. | None ships a system anyone can query. |

**What this means.** StarMine already sells a surprise forecast, so "predicting earnings surprises" is not the differentiator. The differentiators that survive the comparison are:

1. A text-based signal (transcript features) fused with tabular data, which StarMine's published description does not include.
2. A per-prediction explanation checked against the source transcript sentence, not only against SHAP values.
3. A system a user can query by ticker, which the academic baselines are not.

The sector-relative score (FR-16) is included as a market requirement because users compare companies within a sector. Its novelty has not been confirmed, so it should support the product rather than lead the pitch.

## 4. User Needs

| ID | Need | Why it matters to the persona |
|---|---|---|
| N1 | Get a beat, in-line or miss call with a stated confidence before or at the announcement. | The core output. Without confidence the call cannot be used for sizing or prioritising. |
| N2 | See which features drove the call, and which transcript sentences support them. | An explanation that cannot be checked is worse than none for a quantitative user. |
| N3 | Trust that historical performance is not inflated by lookahead, survivorship or selection bias. | The first question any quantitative user asks. A backtest that fails this is discarded. |
| N4 | Compare the text-augmented model with a tabular-only baseline and a consensus-only baseline. | The user needs to know whether the text adds anything before paying attention to it. |
| N5 | Get a result for a ticker without assembling data by hand. | Setup cost decides whether a tool gets used at all. |
| N6 | Know how the model was built, what it was tested on, and when it was last retrained. | Quantitative users treat undocumented models as unusable, and the reasoning is the same as in regulated model risk. |
| N7 | See how a company compares with its sector, not only in absolute terms. | Beat/miss in isolation can mislead when a whole sector beats consensus. |

## 5. Requirements

### 5.1 Functional Requirements

Priorities use MoSCoW.

| ID | Priority | Requirement | Traces to |
|---|---|---|---|
| FR-01 | Must | Given a ticker, return a class (beat, in-line or miss), class probabilities and a confidence value. | N1; Proposal 2, 4.1 |
| FR-02 | Must | Store transcript date, estimate-publication date and announcement date as separate fields for every event. | N3; Proposal 5.4 |
| FR-03 | Must | Enforce the temporal train, validation and test split in code, with an automated test that fails if any training row is dated after the cutoff. | N3; Proposal 5.3, 5.4 |
| FR-04 | Must | Return the top three SHAP features for each prediction, with signed contribution toward beat or miss. | N2; Proposal 4.3 |
| FR-05 | Must | Verify that every transcript excerpt cited by the explanation agent exists in the source document. Reject and flag any that do not. | N2; Proposal 5.5 |
| FR-06 | Must | Report the tabular-only baseline and the full model side by side on the same test set. | N4; Proposal 5.3 |
| FR-07 | Must | Handle explicitly: no transcript available, upstream API failure, and a ticker with too little history (cold start). | Proposal 7 |
| FR-08 | Must | Show a not-investment-advice notice on every prediction and explanation. | Section 6 |
| FR-09 | Should | Look up historical predictions for a ticker by date. | Proposal 6 (history endpoint) |
| FR-10 | Should | Show calibration (Brier score) and precision on the top 20% most confident predictions. | Proposal 5.3; TR-05 |
| FR-11 | Should | Store model version and feature-set version with every prediction, so results can be reproduced. | N3; MR-01 |
| FR-12 | Could | Multi-class output: large beat, small beat, in-line, small miss, large miss. | Proposal stretch objectives |
| FR-13 | Could | Historical P&L simulation from the signals. | Proposal stretch objectives |
| FR-14 | Could | Critic-and-revise loop for the explanation agent. | Proposal 5.5 (conditional); EX-02 |
| FR-15 | Must | Show the evidence base on every prediction: training window, test window, number of events used, and date of last retraining. | N6; MR-02 |
| FR-16 | Should | Show a sector-relative score: the company's standardised surprise minus the mean of its sector peers in the same quarter, divided by the peers' standard deviation. Show the peer count beside it. | N7; DR-06 |
| FR-17 | Must | Show the as-of timestamp of every input used in a prediction, so the user can see what was known at the time. | N3; FR-02 |
| FR-18 | Should | Show the SUE definition, the beat and miss thresholds in use, and the analyst estimate dispersion measure. | N6; Proposal 5.1 |
| FR-19 | Should | Compare the full model with a consensus-revision baseline built only from analyst estimate changes, the approach StarMine takes. | N4; Section 3 |

### 5.2 Non-Functional Requirements

The proposal sets no numerical targets for performance, availability or freshness. The values below are proposed and should be agreed with the supervisor before they are treated as commitments.

| ID | Area | Proposed requirement | Basis |
|---|---|---|---|
| NFR-01 | Prediction latency | Cached prediction returned within 500 ms at the 95th percentile. The explanation agent is excluded and returned asynchronously. | Reasonable for a dashboard. |
| NFR-02 | Data freshness | New transcripts ingested within 24 hours of publication. | Keeps the history endpoint useful. |
| NFR-03 | Availability | Best-effort for a demo deployment. No availability SLA. | Honest scoping for an academic deployment. |
| NFR-04 | Reproducibility | Retraining from the same data snapshot reproduces reported metrics to two decimal places. | Supports N3 and FR-11. |
| NFR-05 | Explanation latency | Full explanation within 10 seconds, or flagged as pending. | The agent makes several tool calls. |
| NFR-06 | Security | No secrets in the repository. Data-licence keys in environment variables. Demo authentication via JWT, as the proposal states. | Proposal 4 |
| NFR-07 | Accessibility | Dashboard meets WCAG 2.1 AA for colour contrast and keyboard navigation. Charts have a text or table alternative. | Institutional users and public-sector buyers expect this. |

### 5.3 Data Requirements

This is the most important section. The design depends on data that may not exist in the form the project needs. Verify each risk before week 1.

| ID | Requirement | Current plan | Assessment |
|---|---|---|---|
| DR-01 | Analyst consensus estimates and their standard deviation, as they stood **before** each announcement. | yfinance or Alpha Vantage (Proposal 5.1). | **High risk.** To my knowledge these return current estimates, not dated historical snapshots. If so, SUE cannot be computed for past events and the lookahead claim cannot be made. Check against the library documentation. |
| DR-02 | Index membership as of each date, so the universe includes companies later removed. | S&P 500, 2015-2024 (Proposal 5.1). | **Medium risk.** A static list of current constituents introduces survivorship bias. |
| DR-03 | Earnings call transcripts for the target universe. | SEC EDGAR full-text search API (Proposal 5.1). | **High risk.** Transcripts are generally published on company investor-relations sites or by data vendors, not filed with the SEC. Check this. Any dataset must be checked for licensing. |
| DR-04 | Actual EPS for each event, with announcement date. | yfinance or Alpha Vantage. | **Medium risk.** Usable for actuals, but announcement date must be checked against transcript date (FR-02). |
| DR-05 | Licence terms that allow the chosen data in a public demo. | Not addressed in the proposal. | **High risk.** Most consensus and transcript data cannot be redistributed. A public demo may need an open historical slice or the user's own key. |
| DR-06 | Point-in-time GICS sector assignment for every company and date. | Not addressed in the proposal. | **Medium risk.** Sector classifications have been revised over time (for example the 2023 GICS changes). Sector-relative scores computed with current sectors would be wrong for past quarters. |
| DR-07 | Vendor revisions recorded, with the value as first reported kept alongside any later correction. | Not addressed. | **Medium risk.** Restated actuals can leak information from after the announcement into the label. |
| DR-08 | Companies delisted or acquired during 2015-2024 included wherever their data exists. | Not addressed. | **Medium risk.** Dropping them removes the weakest performers and inflates results. |
| DR-09 | Transcript provenance: source URL and retrieval date stored with every transcript. | Not addressed. | **Low risk.** Needed for FR-05 and for showing the user where a quote came from. |
| DR-10 | Consensus estimate snapshots captured on a schedule before each announcement, so the estimate in use is known. | Not addressed. | **High risk.** If only one estimate is stored per event, the user cannot tell whether it existed before the announcement. |

**Practical route for DR-01, DR-03 and DR-10.** Check whether the university library provides I/B/E/S consensus data and transcript data through a research platform. Institutional access is the cheapest route to point-in-time data for a student project. Raise this with Professor Goodacre in the first week.

### 5.4 Trust and Evidence Requirements

These are the checks a quantitative user applies before reading any headline number.

| ID | Priority | Requirement | Traces to |
|---|---|---|---|
| TR-01 | Must | Report bootstrap confidence intervals, resampling by event, on all headline metrics. | N3; Harvey and Liu (2015) on noise in backtests |
| TR-02 | Must | Disclose the number of model variants tried and apply a multiple-testing adjustment to the headline result. | N3; Harvey and Liu (2015) |
| TR-03 | Must | Use one sealed test set (2023-2024) that is read once, for the final evaluation only. | N3; ML-02 |
| TR-04 | Should | Report performance separately for 2023 and 2024, and by sector, to show whether results are stable. | N3; Proposal 5.3 |
| TR-05 | Should | Report calibration by confidence decile, not only one Brier score. | FR-10; Proposal 5.3 |
| TR-06 | Must | Report two naive baselines: majority class, and repeating the previous quarter's surprise. | N4; FR-06 |

### 5.5 Model Risk and Governance Requirements

These requirements follow the core expectations of SR 11-7, the US supervisory guidance on model risk management. The project is not subject to that regulation. The guidance is used because it sets out what a careful reviewer expects from a deployed model.

| ID | Priority | Requirement | Traces to |
|---|---|---|---|
| MR-01 | Must | Keep a model inventory entry for each version: owner, purpose, risk tier and status. | FR-11; SR 11-7 inventory |
| MR-02 | Must | Publish a model card for each version covering objective, data, assumptions, limitations and tests. | FR-15; SR 11-7 documentation |
| MR-03 | Must | Have a reviewer who did not build the model check the evaluation before release. | SR 11-7 independent validation; ML-06 |
| MR-04 | Should | Compare predictions with realised outcomes on a rolling basis after release, not only at training time. | SR 11-7 outcomes analysis; FR-09 |
| MR-05 | Should | Monitor input feature distributions for drift, with alert thresholds set from the training baseline. | SR 11-7 ongoing monitoring; SageMaker Model Monitor data quality |
| MR-06 | Should | Monitor the rank order of top SHAP features over time and flag large changes. | SageMaker Model Monitor feature attribution drift |
| MR-07 | Must | Treat every retrain as a new model version that must pass re-evaluation before it replaces the served model. | SR 11-7 change control; ML-06 |

### 5.6 Explanation Faithfulness Requirements

The explanation layer is judged on whether its claims are supported, not on how well it reads. These requirements apply to any LLM-generated explanation.

| ID | Priority | Requirement | Traces to |
|---|---|---|---|
| EX-01 | Must | Every factual claim in an explanation links to a feature or a cited transcript sentence. | FR-05; grounded-generation checks |
| EX-02 | Must | Each claim receives a faithfulness label (supported or unsupported) with a short reason, recorded with the explanation. | Grounded-faithfulness evaluators (Arize Phoenix) |
| EX-03 | Must | The explanation discusses only features in the top-ranked SHAP set for that prediction. | Ichmoukhamedov et al. rank agreement; Section 5.5 of proposal |
| EX-04 | Must | When retrieval finds no supporting sentence, the output says so. It does not generate a rationale. | FR-05; Section 4.3 of proposal |
| EX-05 | Should | A random sample of explanations is rated by a human reviewer, and agreement with the automated labels is reported. | Section 5.5 of proposal; He and Martens (2026) |

### 5.7 Compliance and Adoption Requirements

| ID | Priority | Requirement | Traces to |
|---|---|---|---|
| CP-01 | Must | No accuracy claim appears in the product or in any write-up without a link to the evaluation page it comes from. | Section 6; TR-01 |
| CP-02 | Must | Transcript excerpts shown to users stay within the quotation limits of the licence. | DR-05; DR-09 |
| AD-01 | Should | A new user gets a first prediction within five minutes, without installing anything. | N5; NFR-01 |
| AD-02 | Must | Before first use, the user sees a short summary of what the model cannot do: no live calls, historical testing only, and the known data limits. | N3; Section 6 |

## 6. Constraints and Compliance

| Constraint | Requirement | Note |
|---|---|---|
| Investment advice | Not-investment-advice notice on every output (FR-08). | Good practice regardless of audience. |
| Financial promotion (UK) | If offered to UK retail users, financial promotion rules may apply. | Not a concern for an academic deliverable. Take advice before any non-academic release. |
| Data licences | Licensed data must not be redistributed. | See DR-05 and CP-02. |
| Data protection | Not expected to apply: no personal data about end users is stored. | Recheck if user accounts with email addresses are added. |
| Model risk regulation | SR 11-7 is not binding on this project. | Requirements in Section 5.5 are used as a quality reference only. |

## 7. Success Measures

| Measure | Target | Source |
|---|---|---|
| Full model vs tabular baseline on held-out test set (2023-2024) | Better F1 and AUC than baseline. A negative result is reported as a valid finding. | Proposal 7; FR-06 |
| Full model vs consensus-revision baseline | Reported on the same test set. | FR-19 |
| AUC on held-out test set | At least match the XGBoost baseline reported in SAE-FiRE (about 0.67). 0.70 is stretch only. | Proposal 1, 3.3 |
| Confidence intervals and multiple-testing adjustment | Reported for every headline metric. | TR-01, TR-02 |
| Brier score and precision at top 20% | Reported. No target until the baseline is known. | Proposal 5.3 |
| Sign agreement and rank agreement | Reported on a held-out sample. Target set after a pilot run. | Proposal 5.5 |
| Citation verification rate (FR-05) | 100% of cited excerpts verified, or failure flagged. | Proposal 5.5 |
| Human agreement with automated faithfulness labels (EX-05) | Reported as an agreement statistic on a sample. | Section 5.6 |
| Usability | Five test users look up one ticker and read its explanation without help. | Proposal 7; AD-01 |

The 70% directional accuracy target in the project notes is not carried forward. On a balanced beat/miss task it would exceed the best result in the proposal's own references, and the proposal does not justify it.

## 8. Scope

The submitted proposal is the build basis. The P&L feedback loop, broker execution and insider and options triangulation are excluded, as in the product requirements. These add regulatory or data scope with no supporting requirement in Section 5.

Sector-relative scoring is now included (FR-16) as a Should. Its novelty claim is not confirmed, so it is justified by user need, not by a claim that nobody else does it.

Live mid-call prediction is excluded for the reasons in DR-03 and DR-05.

## 9. Open Decisions

1. Confirm the primary persona in Section 2, or name a different one.
2. Confirm the data sources after DR-01, DR-03, DR-05, DR-06 and DR-10 are checked.
3. Agree the proposed non-functional targets in Section 5.2 with Professor Goodacre.
4. Decide whether the explanation layer or the temporal evaluation is the headline contribution. The proposal's Section 8 gives them equal weight.
5. Decide who serves as the independent reviewer for MR-03. Options are the supervisor or a peer from the course.

## 10. Sources Checked

- LSEG, StarMine SmartEstimate: https://www.lseg.com/en/data-analytics/financial-data/analytics/quantitative-analytics/starmine-smartestimates
- Bloomberg, Point-in-Time data press release: https://www.bloomberg.com/company/press/bloomberg-launches-point-in-time-data-solution-that-gives-quants-a-competitive-edge
- AlphaSense, Earnings Analysis: https://www.alpha-sense.com/solutions/earnings-analysis/
- Harvey, C. and Liu, Y., "Backtesting", Duke University working paper: https://people.duke.edu/~charvey/Research/Published_Papers/P120_Backtesting.PDF
- SR 11-7 model risk management summary: https://www.magicmirrorsecurity.com/blog/sr-11-7-model-risk-management-guidance-explained
- Amazon SageMaker Model Monitor, arXiv:2111.13657: https://arxiv.org/pdf/2111.13657
- Arize Phoenix, faithfulness evaluator: https://www.arize.com/docs/phoenix/evaluation/pre-built-metrics/faithfulness
- S&P Global, GICS sector changes: https://www.spglobal.com/spdji/en/education/article/talkingpoints-an-overview-of-sp-500-sector-indices-and-25-years-of-gics
- Project proposal, Third Year Project Proposal (2026-27), as uploaded.
- Project design notes, earnings-surprise-predictor area file, from project memory.

Points marked "to my knowledge" or "check" were not confirmed against primary documentation. The SR 11-7 and Harvey and Liu sources were read through summaries, not the primary texts.
