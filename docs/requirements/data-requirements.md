# Data Requirements: Verification and Validation

Derived from the Market Requirements and Product Requirements (26 October 2026, revised 14 November 2026), the architecture deck (slides 3 and 4), and source research carried out 30 October 2026.

## 1. Purpose and Scope

This page sets out the data the predictor depends on, which source can supply each dataset, and the checks that prove the data passes the five gates in the architecture deck.

It covers seven datasets: earnings call transcripts, actual EPS, pre-announcement consensus, index membership, sector classification, share prices and quarterly fundamentals (added 14 November 2026, because the proposal's tabular features in Section 5.2 need them).

For each dataset it sets:
- which sources are acceptable, and whether each one passes the gates;
- verification requirements: is the data correct, complete and consistently formatted?
- validation requirements: does the data hold up under the lookahead gates?

A dataset may build the label or the features only when its source passes every gate that depends on it (SR-02). A source that fails a gate can still support development or cross-checks, if its licence allows.

## 2. Gates Used on This Page

| Gate | Rule | Origin |
|---|---|---|
| GATE-1 | Three dates stored separately for every event: transcript, estimate publication and announcement. | Deck slide 4, gate 1; Product FR-02 |
| GATE-2 | Consensus estimates used are those captured before the announcement. | Deck slide 4, gate 2; Product FR-14 |
| GATE-3 | The peer set and the universe are as they stood on the event date. | Deck slide 4, gate 3; Product SRS-03 to SRS-08 |
| GATE-4 | The split is enforced in code and the test set is read once. | Deck slide 4, gate 4; Product FR-03 |
| GATE-5 | Data is signed off and its provenance recorded before release. | Deck slide 4, gate 5, adapted from model sign-off to data sign-off |

## 3. Bottom Line

1. **No free source gives historical point-in-time consensus, and no low-cost source has been proven to.** yfinance returns Yahoo's current estimates. Financial Modeling Prep (FMP) states that it keeps no revision history. Two low-cost vendors, Alpha Vantage ($49.99 a month) and EODHD (from £49.99 a month), return one estimate beside each past actual, but neither documents whether that estimate is the consensus as it stood before the announcement, and neither returns the standard deviation of estimates that the proposal's SUE needs. Snapshots collected from now on cannot backfill 2015 to 2024.
2. **I/B/E/S via WRDS is still the preferred route to historical point-in-time consensus with a standard deviation, and it is restricted at Manchester.** The library FAQ says IBES via WRDS is available "for AMBS Accounting and Finance researchers only". The only other routes found with documented point-in-time history are S&P Capital IQ Estimates and Intrinio's Zacks surprises, which are enterprise products with no public price. This blocks GATE-2 for the label as the proposal defines it. It needs a decision now, not in week 1 of the build.
3. **For transcripts, S&P Capital IQ Transcripts via WRDS is the strongest licensed source found, and Alpha Vantage is the best low-cost source.** The library FAQ names no eligibility limit for Capital IQ Transcripts. That is not the same as confirming access for a Computer Science student. Alpha Vantage's transcript endpoint covers "any quarter since 2010Q1" with speaker, title and content for each turn, which also helps Q&A separation (TX-06). Its demo-use licence is unverified.
4. **For membership and prices, CRSP via WRDS is the preferred source, and EODHD's S&P Global feed is the best low-cost source for membership.** The library FAQ confirms CRSP holds the full history of S&P 500 constituents. Eligibility is unverified. EODHD sells an S&P index constituents add-on (£29.99 a month) with dated additions and removals, taken from S&P Global. EODHD's terms limit it to personal, non-commercial use.
5. **Yahoo-derived data cannot go into a public demo.** yfinance's README states that Yahoo's API is "intended for personal use only". The GitHub index file checked also takes its data from Yahoo Finance. Tiingo is limited to internal and personal use unless it is licensed.
6. **The public demo cannot rely on most licensed data.** It needs one of two designs: a historical demo slice built from redistributable data, or a bring-your-own-key design where the user supplies their own licensed credentials.
7. **The proposal's plan to take transcripts from SEC EDGAR is not sound.** Some issuers file transcripts as 8-K exhibits, but coverage is not systematic. This corrects Market DR-03.
8. **yfinance is not good enough for the label or for a public demo.** It scrapes Yahoo's calendar page and returns current estimates, its history depth is set by Yahoo, it has no standard deviation of estimates, and Yahoo limits the API to personal use. Use it for development and cross-checks only.
9. **The proposal's SUE needs a standard deviation of analyst estimates that most low-cost sources do not return.** If I/B/E/S access fails, the label has to change to a time-series SUE (CE-05), which is a change from proposal Section 5.1 and needs a change entry (Project-Wide SS-04).

## 4. Source Assessment

| Source | Dataset | Historical point-in-time? | Access for this project | Licence for public demo | Verdict |
|---|---|---|---|---|---|
| I/B/E/S via WRDS | Historical consensus and actuals | Yes. Standard research dataset with dated estimates. Revision handling to be confirmed from WRDS documentation (not read). | Restricted at Manchester to AMBS Accounting and Finance researchers. | Academic use only. | Preferred for consensus if access is granted. |
| LSEG Refinitiv Workspace | Consensus, transcripts, some historical estimate data | Unverified | Manchester has Workspace access per the library FAQ. | Unverified | Check whether dated historical estimates can be exported in bulk. |
| S&P Capital IQ Transcripts via WRDS | Earnings call transcripts | Transcripts carry event dates. First-publication timestamps unverified. | WRDS. Library FAQ states no eligibility limit. Coverage given as about 10,600 companies (FAQ) and about 8,000 (WRDS page). | Academic use only. | Preferred transcript source, subject to access and a segmentation test. |
| Refinitiv Advanced Events Search | Transcripts | Yes, by event | Manchester library access. Export is by PDF, Word or text; batch export needs a Windows tool. | Unverified | Fallback for small manual samples only. Not suitable for the pipeline. |
| FMP transcripts | Transcripts | Event-dated. Coverage of about 8,200 companies and 200,000 or more transcripts, from 10+ years by quarter. | Paid. Transcripts are included only in the Ultimate plan: $139 per month, or $99 per month billed annually. | Unverified | Commercial fallback if WRDS access fails. Check licence before paying. |
| FMP estimates | Consensus | No. Returns the current consensus only and states it has no revision history. | Paid plan | Unverified | Fails Gate 2 for backtesting. Usable forward-only from a start date. |
| yfinance | Consensus (current), recent EPS history, prices | No for estimates. `earnings_estimate` reads Yahoo's current estimates. `get_earnings_dates` scrapes Yahoo's calendar web page (default 12 rows, maximum 100) and returns an estimate and a reported EPS per past date, but nothing says the estimate is the pre-announcement value. No standard deviation of estimates. Depth of `earnings_history` is set by Yahoo. | Free, no key. Unofficial. | Fails: "intended for personal use only" under Yahoo's API terms. | Development and cross-checks only. Not suitable for the label. |
| Alpha Vantage EARNINGS and EARNINGS_ESTIMATES | Quarterly reported EPS, estimated EPS, surprise, report date and time; estimate average, high, low and analyst count | Unverified. The documentation does not say whether `estimatedEPS` is the consensus before the announcement. EARNINGS returns reported date, reported EPS, estimated EPS, surprise and report time (before or after market) per quarter, with demo history from 1996. EARNINGS_ESTIMATES has the average, high, low, analyst count and revision values at 7, 30, 60 and 90 days, but no standard deviation and no as-of timestamp. A three-point check on one ticker found past estimates close to the 30 and 60 day values, which suggests a near-announcement estimate. That is inconclusive. | Free key limited to 25 requests a day. Paid plans from $49.99 a month. Neither endpoint carries a premium label in the documentation. | Unverified | Candidate for the label only if the pre-announcement test (VL-12) passes and CE-05 is accepted. Otherwise cross-check only. |
| Alpha Vantage EARNINGS_CALL_TRANSCRIPT | Earnings call transcripts | Event-dated by quarter. First-publication timestamps unverified. | "Any quarter since 2010Q1". Each turn has speaker, title, content and a sentiment string. Same key and limits as above. | Unverified | Best low-cost transcript candidate. Run the segmentation test (TX-03) and a coverage test (TX-04) on 50 S&P 500 names before paying. |
| EODHD earnings and fundamentals history | Reported EPS, consensus estimate, surprise per quarter; estimate trends with analyst count | Unverified. The documentation stores the estimate beside the actual and does not say when the estimate was taken. Fields: report date, fiscal period end, before or after market, actual, estimate. No standard deviation. History "back to the 1990s" for major US companies. | Fundamentals plan from £49.99 a month (annual billing) or £59.99 monthly. EOD prices are a separate plan. | Personal use only. EODHD's terms prohibit redistribution and display. | Same status as Alpha Vantage: candidate only if VL-12 passes. |
| EODHD S&P Dow Jones Indices historical constituents | S&P 500 membership with dated additions and removals | Yes, dated additions and removals. Source is S&P Global under a direct contract. History for the S&P 500 "in 1957" per the product page. | Add-on from £29.99 a month. | Personal use only. | Best low-cost membership source found. Check it against 10 known removals (IM-02) before use. |
| Wikipedia revision history, or the `index-constitution` package | S&P 500 membership, rebuilt from revisions | Approximate. A practitioner method rebuilds past lists from the page's revision history. The package reads Wikipedia and maps old tickers to current names. The author of the method notes messy tables and a CIK column only from 2014. | Free. Package is MIT-licensed. | The licence of the underlying Wikipedia text is not stated on the pages read. | Free fallback for membership only. Must pass IM-01 and IM-02 checks. |
| S&P Capital IQ Estimates | Point-in-time consensus | Yes. Advertised as point-in-time history without look-ahead bias, with North American history from 1999. | Enterprise product. No public price found. Not available through WRDS to this project as far as is known. | Licensed | Strong on the data, but out of reach unless the university holds it. Ask the library. |
| Intrinio Zacks EPS surprises | Pre-release mean estimate, surprise, estimate count and standard deviation | Yes per the product page, with 20 or more years of history. | Enterprise only. No history in default plans. No public price found. | Licensed | Only vendor found that lists the standard deviation and count with history. Ask for a quote only if I/B/E/S fails. |
| FinCall-Surprise (research dataset, GitHub) | 2,688 labelled calls, 2019 to 2021 | No. The label uses the mean of forecasts issued within one month after the call, so it includes post-call revisions. | Free. Repository is Apache-2.0; the paper is CC BY 4.0. Transcripts were scraped mainly from Seeking Alpha. | Upstream transcript rights not covered by those licences. | Development and pipeline testing only. Its labels must not be used in the project's results (Project-Wide SC-04). |
| SEC EDGAR | Filing dates, 8-K press releases with EPS, some 8-K transcript exhibits | Yes, by filing date | Free and public | Public record | Use for announcement dates and actual-EPS cross-checks. Not a systematic transcript source. |
| SEC EDGAR XBRL company facts / Compustat via WRDS | Quarterly revenue, gross profit, operating income | EDGAR: yes, each fact carries the filing date (to be verified on a sample). Compustat: report date fields unverified. | EDGAR free and public. Compustat: WRDS eligibility unverified. | EDGAR: public record. Compustat: academic use only. | EDGAR preferred. Use only values from filings filed before the announcement (FD-02). |
| CRSP via WRDS | Index membership, prices | Yes for membership (full history of S&P 500 constituents per the IESE FAQ). | WRDS. A tutorial states CRSP requires a subscription. Eligibility at Manchester unverified. | Academic use only. | Preferred for membership and prices, subject to access. |
| Compustat via WRDS | Index lists by date range, GICS fields | Lists can be built for a date range (IESE FAQ). Whether GICS history is stored by date is unverified. | WRDS. Eligibility unverified. | Academic use only. | Candidate for sector history. Verify the field history first. |
| Datastream | Monthly index membership | Yes, monthly series | Manchester has Datastream per the library FAQ. | Unverified | Fallback for membership. |
| Tiingo | Daily prices | Yes | Free tier available. Basic and Power accounts are for internal and personal use only. | Redistribution prohibited without a licence. Email Tiingo for a licence. | Internal development only. |
| GitHub `fja05680/dow-sp500-100-years` | Described as S&P 500 membership history | No. The file checked is a daily index-level series from 1927, sourced from Yahoo Finance. Membership is not confirmed. | Free, MIT licence on the repository. | Inherits Yahoo's personal-use restriction through its data source. | Do not use for membership unless the constituent data is verified. |

## 5. Gate Pass Matrix

| Dataset | Gates | Preferred source | Status | Blocker |
|---|---|---|---|---|
| Transcripts | GATE-1, GATE-4 | Capital IQ Transcripts via WRDS | Conditional | WRDS eligibility. Segmentation untested. |
| Transcripts (fallback 1) | GATE-1, GATE-4 | Alpha Vantage EARNINGS_CALL_TRANSCRIPT | Conditional | Licence for demo. Segmentation and coverage untested. |
| Transcripts (fallback 2) | GATE-1, GATE-4 | FMP Ultimate | Conditional | Cost and licence |
| Actual EPS | GATE-1 | 8-K Exhibit 99.1 from SEC EDGAR, cross-checked against Capital IQ or IBES | Conditional | Primary-document parsing not built |
| Pre-announcement consensus | GATE-2 | I/B/E/S via WRDS | Conditional | Manchester eligibility |
| Consensus (fallback 1) | GATE-2 | Alpha Vantage or EODHD per-quarter estimates, with a time-series SUE (CE-05) | Conditional | Must pass the pre-announcement test VL-12. No standard deviation, so the label definition changes. |
| Consensus (fallback 2) | GATE-2 | yfinance, Alpha Vantage ESTIMATES or FMP snapshots captured daily | Fails for backtest. Usable only forward from the capture start date. | No historical data |
| Index membership | GATE-3 | CRSP via WRDS | Conditional | WRDS eligibility |
| Index membership (fallback 1) | GATE-3 | EODHD S&P historical constituents | Conditional | Personal-use licence. Check against known removals. |
| Index membership (fallback 2) | GATE-3 | Datastream monthly series, or Wikipedia revision history | Conditional | Series codes not yet checked. Wikipedia route is approximate. |
| Sector history | GATE-3 | Compustat via WRDS | Unverified | GICS field history not checked |
| Sector (fallback) | GATE-3 | SIC codes from EDGAR | Fails unless historical SIC is verified | EDGAR company records are believed to hold only the current code. To verify. |
| Prices | GATE-4 (momentum feature) | CRSP via WRDS | Conditional | WRDS eligibility |
| Fundamentals | GATE-1, GATE-2 | SEC EDGAR XBRL company facts | Conditional | Filing-date handling not built. Restatements to check. |
| Prices (fallback) | GATE-4 | Tiingo | Internal development only | Licence |

## 6. Source Requirements

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| SR-01 | Must | Every dataset has a named source, licence, access route and access date recorded in a source register before ingestion starts. | Register has one row per dataset, each with a licence and a dated access check. | GATE-5 | Market DR-05 |
| SR-02 | Must | A dataset builds the label or any feature only if its source passes every gate that depends on it. | Every feature column carries a source tag. An untagged column fails the build. | GATE-1 to GATE-4 | Product FR-02 |
| SR-03 | Must | Data in the public demo must be redistributable under its licence, or supplied by the user's own credentials. | Demo bundle manifest lists each source and its licence. Any personal-use source fails the check. | GATE-5 | Market DR-05, CP-02 |
| SR-04 | Must | Raw responses are stored unchanged with retrieval time, source name and source version. | Hash of each stored raw file matches the hash recorded at retrieval. | GATE-5 | Product PL-06 |
| SR-05 | Must | Eligibility for every WRDS dataset is requested in week 1 and confirmed in writing by the end of week 2 (before week 3 starts). If any answer is no, the fallback in SR-06 is chosen at the week 2 supervisor meeting. | Written confirmation from the library or supervisor is on file, or a dated refusal with the fallback decision recorded. | GATE-5 | Market DR-01, DR-03; Product Section 16 (weeks 1 to 2) |
| SR-06 | Must | Every Must dataset has a documented fallback source, and the fallback passes the same tests or the project scope is narrowed. | Register lists a fallback per dataset and records the test result for it. | GATE-5 | Market DR-01 |
| SR-07 | Should | Scraped sources are used only in development, with request logs kept and rate limits respected. | Request log exists. No scraped source appears in the demo bundle. | GATE-5 | Section 4 |
| SR-08 | Must | Snapshot-only sources are stored only as timestamped captures from the start date. They are never backfilled into historical rows. | Test rejects any row for a snapshot source whose capture time is missing or earlier than the start date. | GATE-2 | Product FR-14 |

## 7. Dataset Requirements

### 7.1 Earnings Call Transcripts

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| TX-01 | Must | Each transcript has a company identifier linked to a permanent identifier, the event date and the call type. | 100% of rows have all three fields. Rows missing one are rejected and logged. | GATE-1 | Product FR-02 |
| TX-02 | Must | A transcript is dated on or after its announcement, within a window of one trading day. | Violations are zero, or each violation is listed with a reason. | GATE-1 | Product FR-02 |
| TX-03 | Must | The split between prepared remarks and Q&A is accurate. | On a hand-labelled sample of 50 transcripts, at least 95% of boundaries are correct. | GATE-5 | Product FR-15 |
| TX-04 | Must | At least 90% of target events, S&P 500 2015 to 2024, have a transcript. | Coverage report lists every missing company and quarter. | GATE-3 | Market DR-03 |
| TX-05 | Must | Where two transcripts exist for one event, the one with the earliest first-publication time is kept and the other is stored as a rejected duplicate. Uniqueness of the event key is tested by DV-03. | Given two transcripts for one event, the earlier is kept. DV-03 passes. | GATE-1 | Product FR-13 |
| TX-06 | Should | Speaker and role labels are kept, so analyst questions and management answers can be separated. | Sample of 20 transcripts has labels on every turn. | GATE-1 | Product FR-15 |

### 7.2 Actual EPS

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| AE-01 | Must | Each actual EPS value is linked to a primary document (8-K Exhibit 99.1 or a licensed vendor record) and its release date. | Every event has a document identifier and a release date. | GATE-1 | Market DR-04 |
| AE-02 | Must | Actual EPS from two independent sources agrees within 0.5%, or the difference is explained. | At least 98% agreement on a sample of 200 events. | GATE-1 | Market DR-04 |
| AE-03 | Must | The EPS basis (GAAP or adjusted) is recorded and used consistently for both the actual and the consensus. | Basis field is populated and has one value per dataset. Test in VL-07. | GATE-2 | Product FR-01 |
| AE-04 | Must | The first reported actual is kept. Later corrections are stored as new versions. | After a simulated correction, the first-reported value is unchanged. | GATE-5 | Market DR-07 |

### 7.3 Pre-Announcement Consensus

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| CE-01 | Must | Consensus mean and standard deviation are stored with the time they were captured. Every capture time is before the announcement. | Zero rows where capture time is on or after announcement. | GATE-2 | Market DR-01, DR-10 |
| CE-02 | Must | No historical consensus is inferred from a current value. Where only current values exist, the project starts capturing on a dated schedule from the start date. | Test VL-01 passes. SR-08 test passes. | GATE-2 | Product FR-14 |
| CE-03 | Must | Consensus is on the same basis as the actual EPS it is compared with. | Basis test VL-07 passes. | GATE-2 | Product FR-01 |
| CE-04 | Must | Events with fewer than three estimates are excluded from the label and the exclusion count is reported. The standard deviation is undefined below that count. | Exclusion count is reported per year. | GATE-2 | Proposal 5.1 (SUE) |
| CE-05 | Must | If I/B/E/S access fails and no source returns the standard deviation of estimates, the label uses a time-series SUE: the surprise (actual minus estimate) divided by the standard deviation of that company's surprises over its previous eight quarters, using only events announced before D. Companies with fewer than six prior quarters are excluded and counted. This replaces the proposal's definition and is recorded as a change entry (Project-Wide SS-04). The two definitions are never mixed in one dataset. | Test: a planted surprise dated D or later does not enter the denominator. The label definition is stored with the dataset version and shown on the evaluation page (Product FR-23). | GATE-2 | Proposal 5.1; Product FR-23 |

### 7.4 Index Membership

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| IM-01 | Must | Membership is stored with start and end dates for every company. The universe on each date matches the index membership on that date. | At sampled year-ends, company count matches the published count within 5, and differences are explained. | GATE-3 | Market DR-02 |
| IM-02 | Must | Companies that were removed, delisted or acquired during 2015 to 2024 are included, each with its last trading date and removal reason. | Each year in the period has at least one such company. Each record has a removal date and reason. | GATE-3 | Market DR-08 |
| IM-03 | Must | Ticker changes and identifier changes are linked through a permanent identifier, so a company's history is continuous. | Join on the permanent identifier produces one continuous history for ten known renames. | GATE-3 | Market DR-02 |

### 7.5 Sector Classification

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| SEC-01 | Must | Sector is assigned as it stood on the event date, from a dated history. The current classification is never used for past events. | Test VL-11: a company reclassified in 2023 shows its old sector before the change date. | GATE-3 | Market DR-06 |
| SEC-02 | Must | The peer set for sector scoring includes only companies that are in the universe on date D, have a known sector on D, and have announced before D (Product SRS-03, SRS-04). The company itself is excluded. | Unit test on a fixed date with a known peer set passes. | GATE-3 | Product SRS-03, SRS-04 |

### 7.6 Share Prices

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| PX-01 | Must | Split and dividend adjustments are stored separately from the raw price, with dated adjustment factors. | 20 sampled announcement-day closes match a second source. | GATE-4 | Market DR-04 |
| PX-02 | Must | Momentum features use only prices dated before the announcement. Outcome returns use only prices from the announcement onwards. | Test with a planted future price shows it is excluded. | GATE-4 | Product FR-03 |
| PX-03 | Must | Adjusted and unadjusted prices are never mixed in one series. yfinance returns dividend-adjusted prices by default. | Series-type check fails any series containing both. | GATE-4 | Section 4 |

### 7.7 Quarterly Fundamentals

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| FD-01 | Must | Revenue, gross profit and operating income are stored per company and fiscal quarter, each with the form type, the filing date and the source. Revenue growth, gross margin and operating margin are computed from these. | Every row has a filing date. A sample of 20 values matches the filing. | GATE-1 | Proposal 5.2; Product FR-24 |
| FD-02 | Must | A prediction for an event announced on date D uses only fundamentals from filings filed before D. The current quarter's figures are used only if their filing date is before D; otherwise the latest earlier quarter is used. | Test with a planted filing dated D or later shows it is excluded. | GATE-2 | Product FR-24 |
| FD-03 | Must | The first-filed value is kept. Restated values are stored as new versions with their own filing dates, and only versions filed before D are visible to a prediction. | After a simulated restatement, a prediction before the restatement date is unchanged. | GATE-5 | AE-04 |
| FD-04 | Should | Fiscal periods are mapped to the same calendar quarters as the events (DV-06), including companies with non-calendar fiscal years. | Mapping test passes on the five non-calendar companies used in DV-06. | GATE-1 | DV-06 |

## 8. Verification Requirements

Verification asks whether the data is correct, complete and consistently formatted.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| DV-01 | Must | Every table matches its versioned schema. Rows that fail are quarantined, not dropped. | Quarantine count is reported per run. | GATE-5 | Product PL-05 |
| DV-02 | Must | Null rates are measured for each field, and each field has a maximum. | The three date fields have zero nulls. Other fields are within the thresholds in Section 11. | GATE-1 | Product FR-02 |
| DV-03 | Must | Each event is unique on company, fiscal quarter and announcement date. | Uniqueness check passes on every load. | GATE-1 | Product FR-13 |
| DV-04 | Must | Extreme values are flagged for a person to review, not removed automatically. | Flagged rows have a reviewer note before the dataset is signed off. | GATE-5 | Market DR-07 |
| DV-05 | Must | Date order holds: capture before announcement, announcement before or on transcript, and release before the price window. | Date-order test on every load reports zero violations. | GATE-1, GATE-2 | Product FR-02 |
| DV-06 | Must | Fiscal periods are mapped to calendar quarters, including companies with non-calendar fiscal years. | Mapping test passes on five known non-calendar companies. | GATE-1 | Product FR-02 |
| DV-07 | Must | Announcement times are converted to UTC and mapped to the correct trading day. Releases after the close are dated to the next session. | Test covers a pre-open and an after-close release, both mapped correctly. | GATE-1, GATE-4 | Product FR-03 |
| DV-08 | Must | Re-running ingestion on the same raw snapshot produces identical tables. | Table hashes match between two runs. | GATE-5 | Product NFR-05 |

## 9. Validation Requirements

Validation asks whether the data holds up under the gates. Each test is written so that it can fail.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| VL-01 | Must | Planted-future estimate: a synthetic estimate captured one day after an announcement is inserted. | The pipeline excludes it. Any leaked row fails the build. | GATE-2 | Market TR-03 |
| VL-02 | Must | Feature replay: for 30 events, rebuild each feature vector (text, tabular, fundamentals and sector features) using only data dated before the announcement. | Rebuilt vectors match stored vectors. Any mismatch is a leak and fails the build. | GATE-1, GATE-2, GATE-3 | Product FR-03 |
| VL-03 | Must | Peer-set replay: for 30 predictions, recompute the sector benchmark using only peers whose most recent event was announced strictly before D (Product SRS-04). | Recomputed values match stored values. | GATE-3 | Product SRS-03 to SRS-08 |
| VL-04 | Must | Split and seal: row counts and date ranges match the split definitions. The test set is read only in the final evaluation job. | Access log shows test rows read once. | GATE-4 | Product FR-03, ML-02 |
| VL-05 | Must | Survivorship check: the universe contains delisted names in every year, and the universe's average return is compared with an independent index return for the same period. | A persistent gap above a threshold set in Section 11 is investigated and recorded. | GATE-3 | Market DR-08 |
| VL-06 | Must | Label balance and threshold freeze: class shares are reported per year. The SUE cut-offs are set during EDA and frozen before the test set is read. | No class is below 10% in any year (proposed threshold). Any change after the freeze is logged. | GATE-4 | Proposal 5.1 |
| VL-07 | Must | Basis check: 50 sampled events are checked for the same EPS basis in actual and consensus. | Zero mismatches, or every mismatch is corrected and logged. | GATE-2 | AE-03, CE-03 |
| VL-08 | Must | Known-event canary: 20 widely reported earnings surprises from public records are in the dataset with the expected class. | 20 of 20 correct, or each miss is investigated. | GATE-5 | Product FR-01 |
| VL-09 | Must | Hand audit: 100 randomly sampled events are checked against their primary documents. | Error rate at or below 2%. | GATE-5 | Market N3 (trust in the data) |
| VL-10 | Must | Snapshot trial: for 20 tickers, the chosen snapshot source is captured daily for four weeks. Past-dated values are checked for change. | Results are recorded. Any change to a past-dated value rules out that source for backfill. This test is the only way to establish whether yfinance, FMP or Alpha Vantage's estimates endpoint change past-dated values. Alpha Vantage's documentation was read on 14 November 2026 and does not say. FMP's pages could not be read (HTTP 403). | GATE-2 | SR-08 |
| VL-11 | Must | Sector history check: companies reclassified in 2023 are checked against the published list of changes. | Every sampled company shows the sector that applied on its event date. | GATE-3 | SEC-01 |
| VL-12 | Must | Pre-announcement estimate test: for any source that stores one estimate beside each past actual (Alpha Vantage, EODHD, yfinance), compare its stored estimate with the consensus quoted in the company's own 8-K press release or a dated news item, for 30 events across at least 10 sectors and 5 years. | At least 28 of 30 estimates agree within 1 cent or 1%, and none is a value revised after the announcement. Otherwise the source cannot build the label. | GATE-2 | CE-01, CE-02 |

## 10. Data Governance

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| GS-01 | Must | Each dataset version has a sign-off record. The reviewer did not build the dataset. Checks passed and known gaps are listed. | Sign-off exists before the dataset is used in training. | GATE-5 | Market MR-03 |
| GS-02 | Must | Each dataset has a data card: source, licence, coverage, date range, transformations and known gaps. | Data card exists for every dataset version. | GATE-5 | Market MR-02 |

## 11. Thresholds

These are proposed values. They should be agreed with Professor Goodacre before they are treated as commitments.

| Measure | Proposed threshold | Requirement |
|---|---|---|
| Transcript coverage, target events | At least 90% | TX-04 |
| Segmentation accuracy, 50-transcript sample | At least 95% | TX-03 |
| Actual EPS agreement across two sources, 200-event sample | At least 98% within 0.5% | AE-02 |
| Consensus minimum estimate count | 3 | CE-04 |
| Index company count at sampled year-ends | Within 5 of published count | IM-01 |
| Survivorship gap | To be set after the first comparison run | VL-05 |
| Minimum share of any class per year | 10% | VL-06 |
| Hand-audit error rate, 100 events | At most 2% | VL-09 |
| Snapshot trial length | 4 weeks, 20 tickers, daily | VL-10 |
| Pre-announcement estimate test | 28 of 30 events agree within 1 cent or 1% | VL-12 |
| Time-series SUE history | At least 6 prior quarters, 8-quarter window | CE-05 |
| Null rate on the three date fields | 0% | DV-02 |

## 12. Week-One Experiments

Some source pages could not be read (FMP, Finnhub and the EODHD constituents blog), and no vendor documents when its estimates were taken, so these tests should run before any build work relies on them.

| Experiment | What it settles | Owner |
|---|---|---|
| Ask the library, and if needed the supervisor, whether a Computer Science student can get IBES via WRDS. | Whether the label can use point-in-time consensus. | John, with Professor Goodacre |
| Confirm WRDS access for Capital IQ Transcripts, CRSP and Compustat. | Whether the transcript, membership and sector routes are open. | John, with the library |
| Start the snapshot trial (VL-10) on 20 tickers. | Whether yfinance, Alpha Vantage or FMP keep past values unchanged. | John |
| Pull Alpha Vantage EARNINGS and EARNINGS_CALL_TRANSCRIPT for 10 tickers with a free key (25 requests a day). | History depth per ticker, and whether transcripts are complete for 2015 to 2024. Field names and the 25-a-day free limit are already read from the documentation. | John |
| Run `get_earnings_dates` for 10 tickers over 2019 to 2024. | Depth of past-event coverage and whether reported EPS matches the 8-K. | John |
| Run the pre-announcement estimate test (VL-12) on Alpha Vantage, EODHD and yfinance for 30 events. | Whether any low-cost source can build the label, and whether the time-series SUE (CE-05) is needed. | John |
| Ask the library whether the university holds S&P Capital IQ Estimates or an Intrinio or Zacks licence. | Whether a point-in-time consensus with standard deviation exists outside I/B/E/S. | John |
| Pull 20 events from 8-K Exhibit 99.1 and check the release dates. | Whether AE-01 can be met from primary documents. | John |

## 13. Changes Needed in Earlier Documents

Status 14 November 2026: the Market, Product and Project-Wide documents have been updated for every row in the table below except the proposal and deck rows, which are still waiting for your approval.

| Document | Item | Change |
|---|---|---|
| Market requirements | DR-01 (consensus) | Status confirmed as high risk. FMP has no history and yfinance is current-only. The only route is IBES, which is restricted. |
| Market requirements | DR-03 (transcripts) | Change the source from SEC EDGAR to Capital IQ via WRDS, or FMP as fallback. The SEC route is partial. |
| Market requirements | DR-05 (licence) | Add yfinance (personal use only), Tiingo (internal use only) and the GitHub index file (inherits Yahoo terms). |
| Market requirements | DR-06 (sector) | Add Compustat as the candidate source. Field history still to verify. |
| Product requirements | FR-14 (snapshots) | Add the rule that snapshot sources start from a capture date and cannot backfill (SR-08). Start capture early if IBES access is refused. |
| Proposal | Section 5.1 (data sources) | Replace the EDGAR transcript route, and name the consensus source once access is decided. |
| Architecture deck | Slide 6 (decisions) | Add the IBES access decision and the transcript source as decisions before week 1. |

The Proposal and the deck have not been edited. Those changes are listed for you to approve.

## 14. Open Decisions

1. Can a Computer Science student get IBES via WRDS at Manchester? If not, is there an approved route through the supervisor?
2. If IBES is refused, which of three options applies: (a) a low-cost source that passes VL-12 with the time-series SUE (CE-05), which keeps the 2015 to 2024 backtest but changes the label definition; (b) an enterprise licence; or (c) a forward-only label with no backtest over 2015 to 2024?
3. Which paid transcript fallback is worth paying for: Alpha Vantage (from $49.99 a month) or FMP Ultimate ($99 to $139 a month)? Both have unverified demo licences. FMP's pages could not be read on 14 November 2026.
4. Does the public demo use a historical slice or a bring-your-own-key design (SR-03)?
5. Which thresholds in Section 11 does Professor Goodacre accept?
6. Which fundamentals source is used: EDGAR XBRL company facts (free, filing dates per fact) or Compustat (WRDS eligibility unverified)? Needed by week 1 (FD-01).
7. What monthly spend ceiling covers the low-cost route? It is about $50 for Alpha Vantage plus £50 to £80 for EODHD (fundamentals and the constituents add-on), before any prices plan (Project-Wide OR-02).

## 15. Sources Checked

| Source | What was checked | Status |
|---|---|---|
| Manchester library FAQ on IBES historical forecast data: https://manchester-uk.libanswers.com/teaching-and-learning/faq/250332 | IBES access restriction and Workspace or Datastream coverage | Read |
| Manchester library FAQ on earnings call transcripts: https://manchester-uk.libanswers.com/teaching-and-learning/faq/193007 | Capital IQ Transcripts coverage, Refinitiv export limits | Read |
| WRDS Capital IQ Transcripts page: https://wrds-www.wharton.upenn.edu/pages/grid-items/capital-iq-transcripts/ | Coverage of about 8,000 companies | Read |
| yfinance README: https://github.com/ranaroussi/yfinance | Yahoo affiliation, personal-use statement, dividend adjustment default | Read |
| yfinance 1.7.0 source, downloaded from PyPI | `get_earnings_dates` scrapes Yahoo's calendar page. `earnings_estimate` reads the current-estimates module. `earnings_history` reads the history module. | Read in source code |
| Alpha Vantage premium and documentation pages | Free-tier limit, EARNINGS and EARNINGS_ESTIMATES behaviour | Not accessible. Blocked from this environment. |
| Alpha Vantage EARNINGS summary, macroption.com: https://www.macroption.com/alpha-vantage-fundamental-data/ | EARNINGS includes estimates and surprise. Field names and history depth not confirmed. | Secondary summary read |
| FMP earnings call transcripts page: https://site.financialmodelingprep.com/datasets/earnings-call-transcripts | Coverage, JSON delivery, Ultimate plan pricing | Read |
| FMP estimate drift article: https://site.financialmodelingprep.com/education/calendar/build-an-earnings-revision-pressure-signal-estimate-drift-monitor | No revision history. Users must store snapshots. | Read |
| Tiingo documentation: https://www.tiingo.com/documentation/general | Internal and personal use only. Redistribution needs a licence. | Read |
| WRDS page on downloading S&P 500 constituents: https://wrds-www.wharton.upenn.edu/pages/grid-items/downloading-the-sp-500-constituents/ | CRSP subscription required. Table names not given. | Read |
| IESE library FAQ on index constituents: https://manchester-uk.libanswers.com/teaching-and-learning/faq/193109 | The FAQ is from IESE Business School, not Manchester. It lists CRSP and Compustat via WRDS, and Datastream monthly membership. | Read |
| GitHub `fja05680/dow-sp500-100-years`: https://github.com/fja05680/dow-sp500-100-years | MIT licence. File is an index-level series from Yahoo Finance. Membership not confirmed. | Read |
| SEC 8-K search results | Some issuers file transcripts as 8-K exhibits. | Search result titles only. Documents not opened. |
| SSGA note on 2023 GICS changes: https://www.ssga.com/us/en/individual/insights/2023-gics-changes-companies-impacted-and-what-you-need-to-know | Planned as the reference list for VL-11 | Title seen in search. Not read. |

| Alpha Vantage documentation and premium page: https://www.alphavantage.co/documentation/ and https://www.alphavantage.co/premium/ | EARNINGS, EARNINGS_ESTIMATES and EARNINGS_CALL_TRANSCRIPT fields, free limit of 25 requests a day, prices from $49.99 a month, transcripts since 2010Q1 | Read 14 November 2026. Timing of estimates not stated. |
| EODHD earnings calendar and fundamentals pages: https://eodhd.com/financial-apis/calendar-upcoming-earnings-ipos-and-splits | Earnings and trends fields, history, plan prices | Read 14 November 2026. Timing of estimates not stated. |
| EODHD S&P constituents product page: https://eodhd.com/financial-apis/sp-and-dow-jones-indices-historical-constituents-data-api | Source, endpoints and add-on price | Read 14 November 2026. The blog page returned 404. |
| EODHD licence pages: https://eodhd.com/financial-apis/terms-conditions and https://eodhd.com/financial-apis/commercial-vs-personal-license-use | Personal use only, no redistribution | Read 14 November 2026 |
| FinCall-Surprise: https://arxiv.org/html/2510.03965v1 and https://github.com/Tizzzzy/FinCall-Surprise | Date range, label definition, licences, transcript sources | Read 14 November 2026. LICENSE file not opened. |
| Koval, Andrews and Yan (2023): https://aclanthology.org/2023.findings-acl.520 | Dataset source and licence | Abstract only. PDF text could not be extracted. The FinCall-Surprise paper says the Koval resources are "not fully open source", which is not verified here. |
| SEC EDGAR API overview: https://www.sec.gov/search-filings/edgar-application-programming-interfaces | No key needed; 10 requests a second; declared user agent | Read 14 November 2026. Per-fact fields (filing date, fiscal period) not confirmed on the page. |
| `index-constitution` on PyPI: https://pypi.org/project/index-constitution/ and riazarbi, S&P 500 constituent lists: https://riazarbi.github.io/quant/backtesting-sp500-constituent-history | Wikipedia-based membership, MIT licence, caveats | Read 14 November 2026 |
| Search results only, not opened: S&P Capital IQ Estimates, Intrinio Zacks EPS surprises (https://intrinio.com/products/eps-surprises), LSEG transcripts, Finnhub, FirstRate Data | Point-in-time claims and coverage | Vendor marketing. Not verified. Finnhub's documentation pages loaded empty. |

Points not verified: FMP plans and endpoints (pages blocked); Finnhub; the timing of every low-cost vendor's stored estimate (VL-12 settles it); the licence of Alpha Vantage data for a public demo; yfinance history depth; I/B/E/S revision handling and whether it stores a standard deviation per announcement; Compustat GICS history; the claim that EDGAR holds only current SIC codes; the Refinitiv Workspace estimate history; the Datastream series codes; and all licence terms marked "unverified" in Section 4.
