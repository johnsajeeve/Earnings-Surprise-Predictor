# Open approvals, with a recommended answer for each (26 November 2026)

For John. A recommendation is not an approval: nothing here is decided until you say so.

"Within requirements" means the recommendation can be done without changing any requirement text. **CHANGE** means a requirement or document would have to change, so it needs your explicit yes. **YOU** means only you (or your supervisor) can do it.

## Facts checked on 26 November (they shape several answers)

| Fact | How checked |
|---|---|
| yfinance returns 2012 to 2024 prices for 77 of the 80 companies still in the index and 5 of the 20 removed ones. 18 companies have no prices, 15 of them removed | Ran it for all 100 companies |
| yfinance's `Close` with `auto_adjust=False` is still split-adjusted (Apple 6 June 2014: 23.06, which is 645.57 divided by 28). It is not the raw price | Ran it |
| `^SP500TR` (total return), `^GSPC`, `SPY` and `RSP` (equal weight) are available for 2012 to 2024 from yfinance | Ran it |
| The SEC split-ratio tag lists 17 of the 18 plain share splits yfinance shows | Stored SEC data |
| `ProsusAI/finbert`: licence CC BY-NC-SA 4.0, revision `0bc2ac10dda6929bcb1f77ccc43c7ec5c424f031`. `yiyanghkust/finbert-tone`: no licence stated | Hugging Face API and model page |
| Tiingo has a free tier (500 symbols a month, internal use only). Whether it holds delisted companies on that tier is **not verified**. Financial Modeling Prep advertises a free tier (250 requests a day, personal use); its delisted price history is **not verified** | Web search, vendor and third-party pages |

## A. Needed to start Wave 1.8 (prices)

| # | Item | Recommendation | Standing |
|---|---|---|---|
| A1 | Price tables (D-38; PX-01 to PX-03; LB-05) | Two append-only tables. `price_daily`: company, date, raw close, volume, source, capture time, stored payload. `adjustment_factor`: company, ex-date, kind (split or dividend), value, source, stored payload. Raw close is rebuilt as yfinance close multiplied by the later split ratios, then checked against a second source. Adjusted series are computed when read, never stored mixed with raw. Dated split factors then also feed LB-05, with the SEC tag kept for companies without prices | Within requirements. Adds two entities to Product Section 11: **CHANGE** to that table |
| A2 | 15 removed companies with no prices | Get a free Tiingo key and test it on the 15. Where no free source has a company, store momentum and returns as unavailable with a reason (FE-24), list them, and label results as covering the priced companies | Within requirements (FE-24, SR-06 allows narrowing the scope). Key is **YOU** |
| A3 | Second source for the 20 closing prices (PX-01) | The same Tiingo key | Within requirements |
| A4 | Survivorship check (VL-05, TH-06) | Compare the universe with `^SP500TR` and with `RSP`, because an equal-weighted universe is closer to an equal-weighted index. Record TH-06 from the first run, before the validation set is read. State that missing removed companies bias this check | Within requirements |

## B. Data quality found in Wave 1.7 and the bug review

| # | Item | Recommendation | Standing |
|---|---|---|---|
| B1 | DR-27: 24 labels use EPS in the wrong scale | Exclude all 24 from training with a reviewer note. Change no stored value. Correcting them from a later filing would break the first-filed rule (LB-04) | Within requirements |
| B2 | DV-04 cut-off for "extreme" (not stated anywhere) | Flag labels above 10 in absolute size for review (33 after the scale errors). Flag only, never remove. I saw the distribution of all years when proposing it; it is a review trigger, not a model setting | Within requirements (fills a pending value) |
| B3 | TX-04 coverage 86.9% against 90% | Do what TX-04 says: report the shortfall by company and year and label results as covering the covered events. Keep the threshold. Optionally fill gaps with an Alpha Vantage free key (25 requests a day), after reading its licence | Within requirements. Key is **YOU** |
| B4 | AE-02 EPS agreement not shown | Improve the parser, add the yfinance cross-check the requirement asks for, then check the rest by hand. Keep the 200 sample and the 98% | Within requirements |
| B5 | DR-29: DV-05 says the release is on or before the call; your decision C-17 allows a call before the 8-K (8 events) | Reword DV-05: "announcement before or on transcript, except a call that precedes the 8-K filing, which C-17 allows and which is listed" | **CHANGE** to DV-05 |
| B6 | D-26: halve the audit samples? | Keep 100 and 200. Halving changes TH-08 and TH-03 | Keeping: within requirements. Halving: **CHANGE** |
| B7 | D-09: independent reviewer | A coursemate or your supervisor who did not build the data. I cannot be it | **YOU** |
| B8 | Hand audit (100 events) and boundary labels (50 calls) | Redrawn audit sheet is ready. Boundary sheet is unchanged | **YOU** |
| B9 | DR-19: companies with no EPS in the SEC data | Accept and report the gap. A yfinance EPS fallback would likely mix adjusted and GAAP figures, against AE-03 | Within requirements |

## C. Rules I built that you have not approved

| # | Item | Recommendation | Standing |
|---|---|---|---|
| C1 | D-47 (a) to (p) | Approve (a) to (j), (l), (n), (o), and (k) in its new form (SEC tag, until A1 adds price-source factors). (j), the sample standard deviation, matches the convention FE-18 already states. (m) and (p) are my own values (the one-million flag; the 100-day window, 10-day rule and excluding EPS filed before the release): approve or change | Within requirements |
| C2 | DR-16 rename rule | Approve after reading `wave-1.3/review_list.csv` | **YOU** to read |
| C3 | DR-14: `source_version` column on `raw_payload` | Approve. SR-04 asks for the source version and it is not stored today, so this closes a gap | Within requirements (schema change) |
| C4 | DR-18 and the new event columns | Update Product Section 11 to match the built tables | **CHANGE** (document follows the code, with your approval) |
| C5 | DR-10: no fallback for 8-K times | Record a scope limit: events without an SEC acceptance time are not covered | Within requirements (SR-06) |
| C6 | IG-16 sentence in Data Section 12 | Replace "(quartiles 1,008, 180 and 59 minutes)" with "(the filing came first in these; the quartiles of the lead are 59, 180 and 1,008 minutes)" | **CHANGE** (wording) |
| C7 | DR-08: CI job for the document checks | Add the job. Do not make it a required check until it has passed for a week | Within requirements |
| C8 | DR-21: your email on one web commit | Turn on GitHub's private email for future commits. Do not rewrite history: it would rewrite the branches that hold the evidence | **YOU** |

## D. Needed before Wave 2 (features)

| # | Item | Recommendation | Standing |
|---|---|---|---|
| D1 | D-35 FinBERT | `ProsusAI/finbert` at revision `0bc2ac10`. Its licence is non-commercial and share-alike: acceptable for a dissertation, stated in the register and in any demo. `finbert-tone` states no licence, so do not use it | Within requirements |
| D2 | D-36 (a) to (j) | Approve as written in the Feature Engineering document, which already words them this way. For (f) use the whole Q&A section, as the proposal says. (i) is the least-squares slope (FE-21) | Within requirements |
| D3 | D-34 negation and forward guidance | Approve the proposed rule. I will write the exact phrase list for your approval before any code | Within requirements |
| D4 | D-45 run times | 8-K check 03:30 UTC, transcript check 03:45, data gates 04:15, so they run after EDGAR stops accepting filings for the day (22:00 New York by my knowledge; I will confirm on the SEC page). The jobs only run while your PC is on, so keep the start-up catch-up | Within requirements |

## E. Later, or yours alone

- **Later, before their waves:** D-42 (before Wave 3), D-43 (before 4), D-37 and D-27 (before 5), D-39 (before 6), D-15 and D-44 (before any cloud spend). I will research each then, so the facts are current.
- **YOU, with dates that matter:** D-16 ethics application (December), D-29 exact submission date, written agreement from your supervisor to the time-series label (C-25, SC-07, SS-04; I earlier called this D-46 by mistake), D-03 drop order, D-40 approval of the component documents, D-17, D-21, D-24, D-25, the spot-check of five requirements, and the two SSOT map edits. D-02, D-04 to D-08, D-11, D-12 and D-14 are older planning confirmations for the next supervisor meeting.
- **Optional:** FMP key; D-41 additions (leave them out unless you want one).

## Where a recommendation would change a requirement or document

A1 (two entities added to Product Section 11), B5 (DV-05 wording), C4 (Section 11 update), C6 (Section 12 sentence), and B6 only if you choose to halve. Nothing else changes requirement text.
