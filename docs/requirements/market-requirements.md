# Market Requirements: LLM-Powered Earnings Surprise Predictor

Derived from the Third Year Project Proposal (2026-27) (see [SSOT](../SSOT.md)) and the project design notes. Updated 26 October 2026. Restructured 15 November 2026.

**What this document holds.** Who would use the system, what competitors offer, what the market needs (N1 to N7), and the constraints that follow. It does not define functional, non-functional, data, trust, governance or explanation requirements. Those are defined once, in the document that owns them, and Section 5 shows where each market need is implemented. IDs that were defined here before 15 November 2026 are listed as withdrawn in the README registry.

## 1. Purpose and Scope

This document sets out what the market needs from the Earnings Surprise Predictor and where the current proposal is not yet ready to meet those needs. It tests the proposal against a real use case, so the design choices in Section 4 of the proposal can be defended against more than the project's own assumptions.

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
| Academic baselines: Koval et al. (2023, 2024), SAE-FiRE (2025) | Research results on beat/miss prediction from transcripts. SAE-FiRE reports an XGBoost baseline with AUC 0.620, accuracy 0.781 and F1 0.715 on earnings calls, under a chronological split and a consensus label that uses analyst forecasts issued after the call. Its own models reach AUC 0.657 to 0.668 on calls (corrected 14 November 2026). | Researchers. | None ships a system anyone can query. |

**What this means.** StarMine already sells a surprise forecast, so "predicting earnings surprises" is not the differentiator. The differentiators that survive the comparison are:

1. A text-based signal (transcript features) fused with tabular data, which StarMine's published description does not include.
2. A per-prediction explanation checked against the source transcript sentence, not only against SHAP values.
3. A system a user can query by ticker, which the academic baselines are not.

The sector-relative score (Product FR-12) is included because users compare companies within a sector (N7). Its novelty has not been confirmed, so it should support the product rather than lead the pitch.

## 4. Market Requirements (User Needs)

Each need is a market requirement. The last column names the requirements that implement it, in the document that owns them.

| ID | Need | Why it matters to the persona | Implemented by |
|---|---|---|---|
| N1 | Get a beat, in-line or miss call with a stated confidence before or at the announcement. | The core output. Without confidence the call cannot be used for sizing or prioritising. | Product FR-01, FR-10, NFR-01 |
| N2 | See which features drove the call, and which transcript sentences support them. | An explanation that cannot be checked is worse than none for a quantitative user. | Product FR-04, FR-05, EX-01 to EX-05 |
| N3 | Trust that historical performance is not inflated by lookahead, survivorship or selection bias. | The first question any quantitative user asks. A backtest that fails this is discarded. | Product FR-02, FR-03, FR-22, ML-02, TR-01 to TR-06; Data GATE-1 to GATE-5, IM-02, VL-01 to VL-12 |
| N4 | Compare the text-augmented model with a tabular-only baseline and a consensus-only baseline. | The user needs to know whether the text adds anything before paying attention to it. | Product FR-06, TR-06 |
| N5 | Get a result for a ticker without assembling data by hand. | Setup cost decides whether a tool gets used at all. | Product FR-01, FR-20, NFR-13 |
| N6 | Know how the model was built, what it was tested on, and when it was last retrained. | Quantitative users treat undocumented models as unusable, and the reasoning is the same as in regulated model risk. | Product FR-11, FR-21, FR-23, FR-28, MR-02 |
| N7 | See how a company compares with its sector, not only in absolute terms. | Beat/miss in isolation can mislead when a whole sector beats consensus. | Product FR-12, SRS-01 to SRS-14 |

## 5. Implementation Map

Market needs by priority. The proposal's core objectives (SSOT Section 3) are the Must items. Extensions are Should or Could.

| Priority | Need | Origin |
|---|---|---|
| Must | N1, N2, N3, N4, N5, N6 | Proposal Sections 2, 4, 5 and 7 (N6 follows from the evaluation criteria) |
| Should | N7 | Owner-approved extension (SSOT Section 3A) |

Constraints that apply to every need are in Section 6.

## 6. Constraints and Compliance

| Constraint | Requirement | Note |
|---|---|---|
| Investment advice | Not-investment-advice notice on every output (Product FR-08). | Good practice regardless of audience. |
| Financial promotion (UK) | If offered to UK retail users, financial promotion rules may apply. | Not a concern for an academic deliverable. Take advice before any non-academic release. |
| Data licences | Licensed data must not be redistributed. | See Data SR-03 and SR-11. |
| Data protection | Not expected to apply: no personal data about end users is stored. | Recheck if user accounts with email addresses are added. |
| Model risk regulation | SR 11-7 is not binding on this project. | The model governance requirements (Product MR-01 to MR-06) use it as a quality reference only. |

## 7. Success Measures

Success measures are defined once, in Product Requirements Section 15. The project does not carry forward the 70% directional-accuracy target from the project notes. On a balanced beat/miss task it would exceed the best result in the proposal's own references, and the proposal does not justify it.

## 8. Scope

The proposal is the build basis (SSOT). Exclusions are in Product Requirements Section 2.2 and stretch objectives in Section 2.3. Two market-driven points:

- Sector-relative scoring is an extension for N7. Its novelty claim is not confirmed, so it is justified by user need, not by a claim that nobody else does it.
- A historical P&L simulation is a proposal stretch objective. It is reported only as a research measure, with no buy, sell or hold language.

## 9. Open Decisions

Open decisions are in the [decision log](../decision-log.md). Those that concern this document: D-04 (primary persona) and D-08 (headline contribution).

## 10. Sources Checked

- LSEG, StarMine SmartEstimate: https://www.lseg.com/en/data-analytics/financial-data/analytics/quantitative-analytics/starmine-smartestimates
- Bloomberg, Point-in-Time data press release: https://www.bloomberg.com/company/press/bloomberg-launches-point-in-time-data-solution-that-gives-quants-a-competitive-edge
- AlphaSense, Earnings Analysis: https://www.alpha-sense.com/solutions/earnings-analysis/
- Refinitiv, StarMine SmartEstimate performance (vendor-published, not independently replicated): https://www.refinitiv.com/perspectives/market-insights/starmine-smartestimate-20-years-of-outperformance/
- SAE-FiRE, arXiv 2505.14420: https://arxiv.org/html/2505.14420v2
- Project proposal, Third Year Project Proposal (2026-27), as uploaded.
- Project design notes, earnings-surprise-predictor area file, from project memory.

Competitor claims come from each vendor's own pages. StarMine's hit rates are vendor-reported. The StarMine, Bloomberg and AlphaSense pages were read through summaries, not the primary documents.
