# Data Requirements: Verification and Validation

Derived from the Product Requirements, the architecture deck (slides 3 and 4), the [SSOT](../SSOT.md) and source research carried out 30 October and 14 November 2026. Restructured 15 November 2026: this document owns the data requirements that were previously listed as DR-01 to DR-10 in the market document. Open decisions are in the [decision log](../decision-log.md).

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
| GATE-1 | Three dates stored separately for every event: transcript date, announcement date and information date. The information date is the estimate-publication date for consensus events and the filing date of the latest EPS used for time-series events. | Deck slide 4, gate 1; Product FR-02 |
| GATE-2 | Every input to the label and the features is dated before the announcement. For the time-series label this means EPS first filed before the announcement. For any consensus used, it means the estimate captured before the announcement. For a T0 prediction every input is dated before the cutoff C (the earlier of the call time and the 8-K Item 2.02 acceptance time). A T1 prediction also uses the event's own transcript and is reported separately (Product FR-29). | Deck slide 4, gate 2; LB-04; Product FR-14, FR-22 |
| GATE-3 | The peer set and the universe are as they stood on the event date. | Deck slide 4, gate 3; Product SRS-03 to SRS-08 |
| GATE-4 | The split is enforced in code and the test set is read once. | Deck slide 4, gate 4; Product FR-03 |
| GATE-5 | Data is signed off and its provenance recorded before release. | Deck slide 4, gate 5, adapted from model sign-off to data sign-off |

## 3. Bottom Line

1. **No free source gives historical point-in-time consensus, and no low-cost source has been proven to.** yfinance returns Yahoo's current estimates. Financial Modeling Prep (FMP) states that it keeps no revision history. Two low-cost vendors, Alpha Vantage ($49.99 a month) and EODHD (from £49.99 a month), return one estimate beside each past actual, but neither documents whether that estimate is the consensus as it stood before the announcement, and neither returns the standard deviation of estimates that the proposal's SUE needs. Snapshots collected from now on cannot backfill 2015 to 2024.
2. **I/B/E/S via WRDS is the best licensed route to historical point-in-time consensus with a standard deviation, and it is restricted at Manchester.** The library FAQ says IBES via WRDS is available "for AMBS Accounting and Finance researchers only". The only other routes found with documented point-in-time history are S&P Capital IQ Estimates and Intrinio's Zacks surprises, which are enterprise products with no public price. This blocks GATE-2 for the label as the proposal defines it, which is why the primary route does not depend on it (item 10).
3. **For transcripts, S&P Capital IQ Transcripts via WRDS is the strongest licensed source found, and Alpha Vantage is the best low-cost source.** The library FAQ names no eligibility limit for Capital IQ Transcripts. That is not the same as confirming access for a Computer Science student. Alpha Vantage's transcript endpoint covers "any quarter since 2010Q1" with speaker, title and content for each turn, which also helps Q&A separation (TX-06). Its demo-use licence is unverified.
4. **For membership and prices, CRSP via WRDS is the best licensed source, and EODHD's S&P Global feed is the best low-cost source for membership.** The library FAQ confirms CRSP holds the full history of S&P 500 constituents. Eligibility is unverified. EODHD sells an S&P index constituents add-on (£29.99 a month) with dated additions and removals, taken from S&P Global. EODHD's terms limit it to personal, non-commercial use.
5. **Yahoo-derived data cannot go into a public demo.** yfinance's README states that Yahoo's API is "intended for personal use only". The GitHub index file checked also takes its data from Yahoo Finance. Tiingo is limited to internal and personal use unless it is licensed.
6. **The public demo cannot rely on most licensed data.** It needs one of two designs: a historical demo slice built from redistributable data, or a bring-your-own-key design where the user supplies their own licensed credentials.
7. **The proposal's plan to take transcripts from SEC EDGAR is not sound.** Some issuers file transcripts as 8-K exhibits, but coverage is not systematic. This corrects the transcript route in proposal Section 5.1.
8. **yfinance is not good enough for the label or for a public demo.** It scrapes Yahoo's calendar page and returns current estimates, its history depth is set by Yahoo, it has no standard deviation of estimates, and Yahoo limits the API to personal use. Use it for development and cross-checks only.
9. **The proposal's SUE needs a standard deviation of analyst estimates that no free source returns.**
10. **Decision 14 November 2026: the primary route is free and not tied to Manchester.** Data from any country is acceptable, and no paid or institutional source is required. Because no free source gives historical point-in-time consensus, the historical label is a time-series SUE built from actual EPS in SEC EDGAR (LB-01 to LB-08), the standard approach of Bernard and Thomas (1989), which the proposal already cites. Analyst consensus is captured from now on for a prospective check set. This changes the label defined in proposal Section 5.1 (Project-Wide C19, SS-04). A licensed consensus source (Section 4A, ranks 2 to 4) can replace the label later if it becomes available.

## 4. Source Assessment

| Source | Dataset | Historical point-in-time? | Access for this project | Licence for public demo | Verdict |
|---|---|---|---|---|---|
| I/B/E/S via WRDS | Historical consensus and actuals | Yes. Manchester holds "IBES Historical Estimates" with Detail History and Summary History (library FAQ, updated 28 October 2024). Summary History is a monthly snapshot of consensus statistics; Detail History is a dated record of individual analyst forecasts, from which a consensus before any date can be rebuilt. Both include the standard deviation or the individual forecasts it needs. The rules for choosing between them are in CE-06. | "Available for AMBS Accounting and Finance researchers only." Request by email to the Teaching, Learning and Students team (uml.teachingandlearning@manchester.ac.uk), subject "IBES via WRDS request access". A WRDS account is also needed (self-registration, activated within about one working day). | Academic use only. | Best licensed option for consensus (optional upgrade, SR-05). Enquiry drafted in `library-enquiry-draft.md`. |
| LSEG Refinitiv Workspace and Datastream | Some I/B/E/S coverage, transcripts, some historical estimate data | Unverified | The library FAQ says there is "some coverage in Datastream and Workspace" for I/B/E/S and that the WRDS version is much larger. Workspace licences are limited and reset on the 1st of each month. Datastream runs as an Excel add-in on library PCs. No depth or bulk-export limit is stated. | Unverified | Ask whether dated historical estimates with standard deviation can be exported in bulk. Likely too limited for 4,000 to 5,000 events. |
| S&P Capital IQ Transcripts via WRDS | Earnings call transcripts | Transcripts carry event dates. First-publication timestamps unverified. | WRDS. Library FAQ states no eligibility limit. Coverage given as about 10,600 companies (FAQ) and about 8,000 (WRDS page). | Academic use only. | Best licensed transcript source (optional upgrade), subject to access and a segmentation test. |
| Refinitiv Advanced Events Search | Transcripts | Yes, by event | Manchester library access. Export is by PDF, Word or text; batch export needs a Windows tool. | Unverified | Fallback for small manual samples only. Not suitable for the pipeline. |
| FMP transcripts | Transcripts | Event-dated. Coverage of about 8,200 companies and 200,000 or more transcripts, from 10+ years by quarter. | Paid. Transcripts are included only in the Ultimate plan: $139 per month, or $99 per month billed annually. | Unverified | Commercial fallback if WRDS access fails. Check licence before paying. |
| FMP estimates | Consensus | No. Returns the current consensus only and states it has no revision history. | Paid plan | Unverified | Fails Gate 2 for backtesting. Usable forward-only from a start date. |
| yfinance | Consensus (current), recent EPS history, prices | No for estimates. `earnings_estimate` reads Yahoo's current estimates. `get_earnings_dates` scrapes Yahoo's calendar web page (default 12 rows, maximum 100) and returns an estimate and a reported EPS per past date, but nothing says the estimate is the pre-announcement value. No standard deviation of estimates. Depth of `earnings_history` is set by Yahoo. | Free, no key. Unofficial. | Fails: "intended for personal use only" under Yahoo's API terms. | Development and cross-checks only. Not suitable for the label. |
| Alpha Vantage EARNINGS and EARNINGS_ESTIMATES | Quarterly reported EPS, estimated EPS, surprise, report date and time; estimate average, high, low and analyst count | Unverified. The documentation does not say whether `estimatedEPS` is the consensus before the announcement. EARNINGS returns reported date, reported EPS, estimated EPS, surprise and report time (before or after market) per quarter, with demo history from 1996. EARNINGS_ESTIMATES has the average, high, low, analyst count and revision values at 7, 30, 60 and 90 days, but no standard deviation and no as-of timestamp. A three-point check on one ticker found past estimates close to the 30 and 60 day values, which suggests a near-announcement estimate. That is inconclusive. | Free key limited to 25 requests a day. Paid plans from $49.99 a month. Neither endpoint carries a premium label in the documentation. | Unverified | Candidate for a vendor-estimate label only if the pre-announcement test (VL-12) passes and the supervisor accepts a label with no standard deviation (CE-05). Otherwise cross-check only. |
| Alpha Vantage EARNINGS_CALL_TRANSCRIPT | Earnings call transcripts | Event-dated by quarter. First-publication timestamps unverified. | "Any quarter since 2010Q1". Each turn has speaker, title, content and a sentiment string. Same key and limits as above. | Unverified | Best low-cost transcript candidate. Run the segmentation test (TX-03) and a coverage test (TX-04) on 50 S&P 500 names before paying. |
| EODHD earnings and fundamentals history | Reported EPS, consensus estimate, surprise per quarter; estimate trends with analyst count | Unverified. The documentation stores the estimate beside the actual and does not say when the estimate was taken. Fields: report date, fiscal period end, before or after market, actual, estimate. No standard deviation. History "back to the 1990s" for major US companies. | Fundamentals plan from £49.99 a month (annual billing) or £59.99 monthly. EOD prices are a separate plan. | Personal use only. EODHD's terms prohibit redistribution and display. | Same status as Alpha Vantage: candidate only if VL-12 passes. |
| EODHD S&P Dow Jones Indices historical constituents | S&P 500 membership with dated additions and removals | Yes, dated additions and removals. Source is S&P Global under a direct contract. History for the S&P 500 "in 1957" per the product page. | Add-on from £29.99 a month. | Personal use only. | Best low-cost membership source found. Check it against 10 known removals (IM-02) before use. |
| Wikipedia revision history, or the `index-constitution` package | S&P 500 membership, rebuilt from revisions | Approximate. A practitioner method rebuilds past lists from the page's revision history. The package reads Wikipedia and maps old tickers to current names. The author of the method notes messy tables and a CIK column only from 2014. | Free. Package is MIT-licensed. | The licence of the underlying Wikipedia text is not stated on the pages read. | Free fallback for membership only. Must pass IM-01 and IM-02 checks. |
| S&P Capital IQ Estimates | Point-in-time consensus | Yes. Advertised as point-in-time history without look-ahead bias, with North American history from 1999. | Enterprise product. No public price found. Not available through WRDS to this project as far as is known. | Licensed | Strong on the data, but out of reach unless the university holds it. Ask the library. |
| Intrinio Zacks EPS surprises | Pre-release mean estimate, surprise, estimate count and standard deviation | Yes per the product page, with 20 or more years of history. | Enterprise only. No history in default plans. No public price found. | Licensed | Only vendor found that lists the standard deviation and count with history. Ask for a quote only if I/B/E/S fails. |
| Zacks historical data (zackspro.com) | Earnings surprises, daily consensus estimates, detailed broker estimates | Documented fields include "Consensus on Report Date", "Standard Dev. of Consensus", "Number of Estimates" and "Adjustment to Actual". Earnings surprises from 1994; quarterly daily consensus from 1982. Zacks adjusts estimates for non-recurring items, so its consensus can differ from other providers (WRDS one-sheet, via search result). | Priced by contacting a Zacks representative. WRDS carries Zacks generally, but the Manchester library FAQs list only IBES as an estimates product. | Licensed | Best documented match to the proposal's SUE outside I/B/E/S. Ask the library whether Manchester holds Zacks on WRDS. EPS basis must be checked (AE-03). |
| Benzinga earnings calendar (also sold through Massive, formerly Polygon) | Estimate, actual, surprise, revenue estimate | Unverified. Fields are `eps_est`, `eps`, `eps_surprise`. The documentation has no statement on when the estimate is captured and holds an `updated` timestamp only, so an estimate can be overwritten. No estimate count and no standard deviation. History from 30 April 2010 on the Massive endpoint. | Included in select Massive plans. No price found. | Not stated | Same status as Alpha Vantage and EODHD: candidate only if VL-12 passes. |
| Hugging Face `kurry/sp500_earnings_transcripts` | 33,362 transcripts, 685 companies, 2005 to 2025 | Call date and time per transcript. Speaker turns are in `structured_content`. Prepared remarks and Q&A are not split into fields. No EPS or estimate fields. | Free download. Source of the transcripts is not named. The `company_id` field is a Capital IQ identifier, which suggests (not confirmed) that the text came from Capital IQ Transcripts. Some records are empty. | The card says "MIT" and "For research and educational use only". Rights in the underlying transcripts are not addressed. | Useful for development and for testing the segmenter. Not for a public demo, and not for reported results until the origin and licence are confirmed (SR-03, Project-Wide ET-03). |
| STRUX transcripts (Motley Fool, 2017 to 2024) | 11,950 transcripts, 869 companies, with prepared remarks and Q&A separated | Call date present. Labels are 30-day post-earnings price moves, not EPS surprise. | Free. | CC BY-NC-ND 4.0: no commercial use and no derivatives. Motley Fool's own terms may also apply. | Development only. Cannot build the project's label. |
| FinCall-Surprise (research dataset, GitHub) | 2,688 labelled calls, 2019 to 2021 | No. The label uses the mean of forecasts issued within one month after the call, so it includes post-call revisions. | Free. Repository is Apache-2.0; the paper is CC BY 4.0. Transcripts were scraped mainly from Seeking Alpha, and the transcript licence is non-commercial. | Upstream transcript rights are not covered by those licences. | External benchmark replication only (Product FR-27): results reported separately with its label stated. Not used for training, not mixed with project results, and not shown in the public demo (SR-03). |
| SEC EDGAR | Filing dates, 8-K press releases with EPS, some 8-K transcript exhibits | Yes, by filing date | Free and public | Public record | Use for announcement dates and actual-EPS cross-checks. Not a systematic transcript source. |
| SEC EDGAR XBRL company facts / Compustat via WRDS | Quarterly diluted EPS, revenue, gross profit, operating income | EDGAR: yes, each fact carries the filing date (to be verified on a sample). Compustat: report date fields unverified. | EDGAR free and public. Compustat: WRDS eligibility unverified. | EDGAR: public record. Compustat: academic use only. | EDGAR preferred. Use only values from filings filed before the announcement (FD-02). |
| CRSP via WRDS | Index membership, prices | Yes for membership (full history of S&P 500 constituents per the IESE FAQ). | WRDS. A tutorial states CRSP requires a subscription. Eligibility at Manchester unverified. | Academic use only. | Best licensed source for membership and prices (optional upgrade), subject to access. |
| Compustat via WRDS | Index lists by date range, GICS fields | Lists can be built for a date range (IESE FAQ). Whether GICS history is stored by date is unverified. | WRDS. Eligibility unverified. | Academic use only. | Candidate for sector history. Verify the field history first. |
| Datastream | Monthly index membership | Yes, monthly series | Manchester has Datastream per the library FAQ. | Unverified | Fallback for membership. |
| Tiingo | Daily prices | Yes | Free tier available. Basic and Power accounts are for internal and personal use only. | Redistribution prohibited without a licence. Email Tiingo for a licence. | Internal development only. |
| GitHub `fja05680/dow-sp500-100-years` | Described as S&P 500 membership history | No. The file checked is a daily index-level series from 1927, sourced from Yahoo Finance. Membership is not confirmed. | Free, MIT licence on the repository. | Inherits Yahoo's personal-use restriction through its data source. | Do not use for membership unless the constituent data is verified. |

## 4A. Source Plan

Decision 14 November 2026: any source from any country is acceptable, the primary route must be free, and a forward-only design is acceptable if the alternatives are worse. Free means no subscription and no purchase. Free keys with request limits are allowed. Optional paid or institutional sources are upgrades, never dependencies (SR-09).

### 4A.1 Primary route (free)

| Dataset | Source | How it is used | Main risk |
|---|---|---|---|
| Actual EPS and the EPS history for the label | SEC EDGAR XBRL company facts (diluted EPS), with the 8-K Item 2.02 filing date as the announcement date | Time-series SUE label (LB-01 to LB-08) | Fourth-quarter EPS is not filed directly and has to be derived (LB-03). Early-period coverage must be checked. |
| Transcripts, historical | Hugging Face `kurry/sp500_earnings_transcripts` (2005 to May 2025) | Text features | Origin and licence unclear. Likely current-constituent bias, so delisted companies may be missing (TX-07). Not for the public demo. |
| Transcripts, forward | Alpha Vantage EARNINGS_CALL_TRANSCRIPT on a free key (25 requests a day) | Events from June 2025 onward | The free limit allows about 500 transcripts in 20 days. Licence for demo unverified. |
| Consensus, forward | Daily snapshots from yfinance, and Finnhub or FMP free tiers if a test call shows they return estimates | Prospective check set (LB-07, LB-08) | Current values only. No standard deviation. Personal-use terms. |
| Index membership | Candidates: `fja05680/sp500` (MIT), cross-checked against `Johnbrick123/sp500-data`; Wikipedia revision history or the `index-constitution` package as fallback. The choice is decision D-32, still open (pipeline.md Section 4.1). | Universe and peer set | Approximate. Must pass IM-01 and IM-02. |
| Prices | yfinance, free | Momentum feature and outcome returns | Personal-use terms. Dividend-adjusted by default (PX-03). |
| Fundamentals | SEC EDGAR XBRL company facts | Revenue growth and margins | Filing-date handling (FD-02). |
| Sector history | To be found. Free point-in-time GICS history has not been located. | Sector scoring | If none is found, sector scoring is switched off (Product SRS-14). |

### 4A.2 Optional upgrades (not required)

| Upgrade | What it adds | Condition |
|---|---|---|
| I/B/E/S, Capital IQ Transcripts and CRSP via WRDS | A consensus label with standard deviation, licensed transcripts, membership and prices | Eligibility. Manchester limits I/B/E/S to AMBS Accounting and Finance researchers. Enquiry drafted in `library-enquiry-draft.md`. |
| Zacks earnings surprises | Consensus on report date, standard deviation, estimate count from 1994 | Price and access unknown. |
| Alpha Vantage, EODHD or Benzinga estimates | An estimate beside each past actual | Only if VL-12 passes. Not free. No standard deviation. |
| Forward-only consensus label | The proposal's definition, without a backtest | Last resort. It gives about 500 events in one earnings season, too few for the proposal's split. |

If an upgrade becomes available, the label route is re-decided by ADR (Project-Wide SC-07). Two routes are never mixed in one training set.

**Development and benchmark data.** FinCall-Surprise may be used for an external benchmark replication (Product FR-27), reported separately and labelled with its own post-call consensus definition. STRUX and similar sets may be used to build and test the pipeline. Neither set is used for training the project's models, mixed with project results, or shown in the public demo (SR-03, Project-Wide SC-04).

## 5. Gate Pass Matrix

Status of each dataset against the gates it depends on. The primary route is the free route in Section 4A.1. Optional upgrades are in Section 4A.2 and never a dependency (SR-09).

| Dataset | Gates | Primary source (free) | Status | Blocker | Optional upgrade |
|---|---|---|---|---|---|
| Actual EPS | GATE-1 | SEC EDGAR XBRL diluted EPS and 8-K Item 2.02 filing dates | Conditional | Fourth-quarter derivation, early-period coverage and press-release parsing untested (LB-03) | Compustat or I/B/E/S actuals |
| Earnings surprise label | GATE-2 | Time-series SUE from EDGAR EPS (LB-01 to LB-06) | Conditional. Decided by the owner (C-25). Weaker than a consensus label. | Untested warm-up and restatement handling | Consensus label from I/B/E/S via WRDS, Zacks or a vendor that passes VL-12 |
| Consensus (forward check) | GATE-2 | Daily snapshots from yfinance, Finnhub or FMP free tiers, from the start date (SR-10) | Usable only forward. Fails for a backtest. | Current values only, no standard deviation, personal-use terms | Historical consensus from a licensed source |
| Transcripts | GATE-1, GATE-4 | Hugging Face `kurry/sp500_earnings_transcripts` for history; Alpha Vantage free key going forward | Conditional | Origin and licence of the Hugging Face set; survivorship in coverage (TX-07); Alpha Vantage free limit of 25 requests a day; segmentation untested | Capital IQ Transcripts via WRDS; FMP Ultimate |
| Index membership | GATE-3 | Candidates in Section 4A.1 (decision D-32 open); Wikipedia revision history or the `index-constitution` package as fallback | Conditional | Approximate. Must pass IM-01 and IM-02. | CRSP via WRDS; EODHD S&P Global constituents |
| Sector history | GATE-3 | None found. EDGAR SIC codes fail unless historical SIC is verified. | Unverified | No free point-in-time GICS source located, and the SIC spike of 19 November 2026 showed no dated history (decision C-29). If none, sector scoring is switched off (Product SRS-14). | Compustat via WRDS (GICS field history unchecked) |
| Prices | GATE-4 | yfinance (development and research only) | Conditional | Personal-use terms; adjusted prices by default (PX-03) | CRSP via WRDS; EODHD end-of-day prices |
| Fundamentals | GATE-1, GATE-2 | SEC EDGAR XBRL company facts | Conditional | Filing-date handling not built; restatements to check (FD-02, FD-03) | Compustat via WRDS |

## 6. Source Requirements

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| SR-01 | Must | Every dataset has a named source, licence, access route and access date recorded in a source register before ingestion starts. | Register has one row per dataset, each with a licence and a dated access check. | GATE-5 | Market Section 6 (data licences) |
| SR-02 | Must | A dataset builds the label or any feature only if its source passes every gate that depends on it. | Every feature column carries a source tag. An untagged column fails the build. | GATE-1 to GATE-4 | Product FR-02 |
| SR-03 | Must | Data in the public demo must be redistributable under its licence, or supplied by the user's own credentials. | Demo bundle manifest lists each source and its licence. Any personal-use source fails the check. | GATE-5 | Market Section 6 (data licences); SR-11 |
| SR-04 | Must | Raw responses are stored unchanged with retrieval time, source name and source version. | Hash of each stored raw file matches the hash recorded at retrieval. | GATE-5 | Product PL-06 |
| SR-05 | Should | If an optional institutional source is wanted (I/B/E/S, Capital IQ, CRSP via WRDS), the request is sent in week 1 and a written answer or dated refusal is on file by the end of week 2. The primary route does not wait for it. | Written answer or dated refusal on file, or a decision log entry that no request was made. | GATE-5 | Proposal 5.1; Product Section 16 |
| SR-06 | Must | Every Must dataset has a documented fallback source, and the fallback passes the same tests or the project scope is narrowed. The primary route (Section 4A.1) counts as the fallback for any optional source. | Register lists a fallback per dataset and records the test result for it. | GATE-5 | Proposal 5.1 |
| SR-07 | Should | Scraped sources are used only in development, with request logs kept and rate limits respected. | Request log exists. No scraped source appears in the demo bundle. | GATE-5 | Section 4 |
| SR-08 | Must | Snapshot-only sources are stored only as timestamped captures from the start date. They are never backfilled into historical rows. | Test rejects any row for a snapshot source whose capture time is missing or earlier than the start date. | GATE-2 | Product FR-14 |
| SR-09 | Must | Every source in the primary route is free: no subscription and no purchase. Free keys with request limits are allowed. Paid or institutional sources are optional upgrades only, and no Must requirement depends on one. Sources from any country are acceptable. | Source register has a cost column, and every primary-route entry shows zero. | GATE-5 | Project-Wide OR-02 |
| SR-10 | Must | A forward capture job records consensus snapshots for every company in the universe from the start date until each announcement, and keeps running through the project. Each snapshot stores the source, capture time and fields returned. | Job log shows a successful daily run. A gap of more than 3 consecutive days is reported and the affected events are flagged. | GATE-2 | SR-08; Product FR-14 |
| SR-11 | Must | Transcript excerpts shown to users stay within the quotation limit of the source's licence. The limit is recorded in the source register. | A test fails any displayed excerpt longer than the recorded limit. | GATE-5 | SR-03; Product FR-05 |

## 7. Dataset Requirements

### 7.1 Earnings Call Transcripts

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| TX-01 | Must | Each transcript has a company identifier linked to a permanent identifier, the event date and the call type. | 100% of rows have all three fields. Rows missing one are rejected and logged. | GATE-1 | Product FR-02 |
| TX-02 | Must | A transcript is dated on or after its announcement, within a window of one trading day. | Violations are zero, or each violation is listed with a reason. | GATE-1 | Product FR-02 |
| TX-03 | Must | The split between prepared remarks and Q&A is accurate. | On a hand-labelled sample of 50 transcripts, at least 95% of boundaries are correct. | GATE-5 | Product FR-15 |
| TX-04 | Must | At least 90% of target events have a transcript. Target events are the 2015 to 2024 earnings events of the companies on the loaded company list (Ingestion IG-21): the 100-company subset in the December scope (decision C-18), and the S&P 500 if the list is widened. If coverage is below 90%, the shortfall is reported by company and year, and results are labelled as covering the covered events (TX-07, SR-06). | Coverage report lists every missing company and quarter. | GATE-3 | Proposal 5.1 (target corpus) |
| TX-05 | Must | Where two transcripts exist for one event, the one with the earliest first-publication time is kept and the other is stored as a rejected duplicate. Where the source gives no first-publication time, the one with the earliest call time is kept, and a tie goes to the lower source identifier. Uniqueness of the event key is tested by DV-03. | Given two transcripts for one event, the earlier is kept. DV-03 passes. | GATE-1 | Product FR-13 |
| TX-06 | Should | Speaker and role labels are kept, so analyst questions and management answers can be separated. | Sample of 20 transcripts has labels on every turn. | GATE-1 | Product FR-15 |
| TX-07 | Must | Transcript coverage bias is measured and reported: the share of target events (TX-04) with a transcript, by year, by sector where a dated sector history exists (SEC-01), and separately for companies that left the index during 2015 to 2024. If delisted companies are missing, the limitation is stated and results are labelled as covering surviving companies. | Coverage table by year, survivor status and, where sector history exists, sector exists. | GATE-3 | TX-04; IM-02 |

### 7.2 Actual EPS

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| AE-01 | Must | Each actual EPS value is linked to a primary filing: the 10-Q or 10-K XBRL fact, or the 8-K Exhibit 99.1 press release. The announcement date is the filing date of the 8-K Item 2.02 release, and the value's own filing date is stored separately. | Every event has a document identifier, an announcement date and an EPS filing date. | GATE-1 | Proposal 5.1 |
| AE-02 | Must | Actual EPS from the press release (8-K) agrees with the XBRL value within 0.5%, or the difference is explained. A second free source (yfinance) is used as a further cross-check, on the same EPS basis (AE-03). A difference that is only a basis difference is listed separately and not counted as disagreement. | At least 98% agreement on a sample of 200 events. | GATE-1 | Proposal 5.1 |
| AE-03 | Must | The EPS basis (GAAP or adjusted) is recorded and used consistently for both the actual and the consensus. | Basis field is populated and has one value per dataset. Test in VL-07. | GATE-2 | Product FR-01 |
| AE-04 | Must | The first reported actual is kept. Later corrections are stored as new versions. | After a simulated correction, the first-reported value is unchanged. | GATE-5 | Proposal 5.4 |

### 7.3 Pre-Announcement Consensus (prospective set, or any licensed upgrade)

These requirements apply to every use of analyst consensus: the forward capture set (SR-10, LB-07) and any licensed source adopted later. They do not apply to the time-series label in Section 7.3A, which uses no analyst estimates.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| CE-01 | Must | Consensus mean, and its standard deviation where the source returns one, are stored with the time they were captured. Every capture time is before the announcement. | Zero rows where capture time is on or after announcement. | GATE-2 | Proposal 5.4; Product FR-14 |
| CE-02 | Must | No historical consensus is inferred from a current value. Where only current values exist, the project starts capturing on a dated schedule from the start date. | Test VL-01 passes. SR-08 test passes. | GATE-2 | Product FR-14 |
| CE-03 | Must | Consensus is on the same basis as the actual EPS it is compared with. | Basis test VL-07 passes. | GATE-2 | Product FR-01 |
| CE-04 | Must | Where a consensus standard deviation is used, events with fewer than three estimates are excluded from the label and the exclusion count is reported. The standard deviation is undefined below that count. | Exclusion count is reported per year. | GATE-2 | Proposal 5.1 (SUE) |
| CE-05 | Must | The label route is chosen once per dataset version. Route A (consensus, as in the proposal) needs a licensed point-in-time source with standard deviation. Route B (time-series SUE, Section 7.3A) is used when no such source is available. The route is recorded in the data card and shown on the evaluation page (Product FR-23). Routes are never mixed in one training set. | Dataset version has a label_route value. A test fails if events with different routes are in one training set. | GATE-2 | Proposal 5.1; Project-Wide SC-07, C19 |
| CE-06 | Must if I/B/E/S is adopted | When I/B/E/S is the source, the consensus for an event announced on date D is the last Summary History statistical period dated before D, or a consensus rebuilt from Detail History using only forecasts dated before D. The choice is made once, recorded in the data card, and not mixed. The number of days between the consensus date and D is stored for every event. Consensus older than 35 days (proposed) is flagged and its share is reported per year. | Test: a planted forecast dated D or later is excluded. Report shows the age distribution of consensus values. | GATE-2 | Proposal 5.4; CE-01 |

### 7.3A Earnings Surprise Label (Route B, time-series SUE)

Route B follows Bernard and Thomas (1989), which the proposal cites, and uses no analyst estimates. Expected EPS for a quarter is the EPS of the same quarter one year earlier. The window and the minimum history below are proposed values to agree with the supervisor. The exact scaling in the 1989 paper was not read and must be checked before the dissertation cites it.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| LB-01 | Must | For an event in fiscal quarter q announced on date D, SUE = (EPS(q) minus EPS(q minus 4 quarters)) divided by the standard deviation of the previous 8 seasonal differences. EPS is diluted EPS from XBRL. The prior 8 differences use only quarters whose EPS was first filed before D. | Fixture company with a hand-calculated SUE matches to four decimal places. | GATE-2 | Proposal 5.1; Bernard and Thomas (1989) |
| LB-02 | Must | At least 6 prior seasonal differences are needed (10 quarters of EPS history). Events with less are excluded from the label, counted and reported per year. A standard deviation of zero gives an unavailable label, not infinity. | Exclusion count reported per year. Zero-variance fixture returns unavailable. | GATE-2 | Product FR-18 (same rule) |
| LB-03 | Must | The EPS series per company is built from XBRL facts by fiscal period. Fourth-quarter EPS is derived as full-year EPS minus the first three quarters and is marked "derived". The error from changing share counts is measured on a sample of 20 companies by comparing derived values with the fourth-quarter figures in their press releases. | Derived values are flagged. Sample comparison is reported, with differences above 1% listed. | GATE-1 | AE-01, AE-02 |
| LB-04 | Must | History values are the first-filed values, not later restated comparatives. A prediction for D sees only EPS first filed before D. | Test with a planted restatement filed after D shows the original value is used. | GATE-2 | AE-04 |
| LB-05 | Must | EPS history is put on a common share basis using dated split factors known before D, so a split between q minus 4 and q does not create a false surprise. | Test on a company with a split inside the window gives the same SUE as the unsplit series. | GATE-2 | PX-01 |
| LB-06 | Must | Class thresholds (beat, in-line, miss) are set during EDA on the 2015 to 2021 training window only and frozen before the validation and test sets are read. Class shares are reported per year, and no class is below 10% in any year (proposed). A year with a class below 10% is listed with its shares and the likely cause, and the frozen thresholds are not changed because of it. | Frozen threshold record exists. Class shares table exists. | GATE-4 | VL-06 |
| LB-07 | Must | For events announced after the capture start date (SR-10), a consensus-based label is also computed: (actual EPS minus mean consensus) divided by the absolute mean consensus. It has no standard deviation because no free source returns one. The actual EPS used is the figure the same source reports beside its consensus, so both are on the same basis (usually adjusted), and the basis is recorded (AE-03, VL-07). Its thresholds are frozen separately. It is never used for training Route B models. | Prospective table has both labels per event. Thresholds are recorded. | GATE-2 | Proposal 5.1; CE-01 |
| LB-08 | Must | The agreement between the Route B label and the consensus-based label is reported on the prospective set: confusion matrix, rank correlation and the share of events where the two disagree on beat against miss. The result is stated as a limitation of the label whatever it shows. | Report exists with all three measures and the event count. | GATE-5 | Project-Wide ASM-06 |


### 7.4 Index Membership

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| IM-01 | Must | Membership is stored with start and end dates for every company. The universe on each date matches the index membership on that date. | At sampled year-ends, company count matches the published count within 5, and differences are explained. | GATE-3 | Proposal 5.1 |
| IM-02 | Must | Companies that were removed, delisted or acquired during 2015 to 2024 are included, each with its last trading date and removal reason. | Each year in the period has at least one such company. Each record has a removal date and reason. | GATE-3 | Proposal 5.1 |
| IM-03 | Must | Ticker changes and identifier changes are linked through a permanent identifier, so a company's history is continuous. | Join on the permanent identifier produces one continuous history for ten known renames. | GATE-3 | Proposal 5.1 |

### 7.5 Sector Classification

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| SEC-01 | Must if built | Sector is assigned as it stood on the event date, from a dated history. The current classification is never used for past events. | Test VL-11: a company reclassified in 2023 shows its old sector before the change date. | GATE-3 | Product SRS-01 |
| SEC-02 | Must if built | The peer set for sector scoring includes only companies that are in the universe on date D, have a known sector on D, and have announced before D (Product SRS-03, SRS-04). The company itself is excluded. | Unit test on a fixed date with a known peer set passes. | GATE-3 | Product SRS-03, SRS-04 |

### 7.6 Share Prices

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| PX-01 | Must | Split and dividend adjustments are stored separately from the raw price, with dated adjustment factors. | 20 sampled announcement-day closes match a second source. | GATE-4 | Proposal 5.2 |
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
| DV-04 | Must | Extreme values are flagged for a person to review, not removed automatically. | Flagged rows have a reviewer note before the dataset is signed off. | GATE-5 | Proposal 5.4 |
| DV-05 | Must | Date order holds: capture before announcement, announcement before or on transcript, and release before the price window. | Date-order test on every load reports zero violations. | GATE-1, GATE-2 | Product FR-02 |
| DV-06 | Must | Fiscal periods are mapped to calendar quarters, including companies with non-calendar fiscal years. | Mapping test passes on five known non-calendar companies. | GATE-1 | Product FR-02 |
| DV-07 | Must | Announcement times are converted to UTC and mapped to the correct trading day. Releases after the close are dated to the next session. | Test covers a pre-open and an after-close release, both mapped correctly. | GATE-1, GATE-4 | Product FR-03 |
| DV-08 | Must | Re-running ingestion on the same raw snapshot produces identical tables. | Table hashes match between two runs. | GATE-5 | Product ML-01 |

## 9. Validation Requirements

Validation asks whether the data holds up under the gates. Each test is written so that it can fail.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| VL-01 | Must | Planted-future estimate: a synthetic estimate captured one day after an announcement is inserted. | The pipeline excludes it. Any leaked row fails the build. | GATE-2 | Product FR-14 |
| VL-02 | Must | Feature replay: for 30 events, rebuild each feature vector (text, tabular and fundamentals features, and sector features if Product FR-12 is built) using only data dated before the announcement. | Rebuilt vectors match stored vectors. Any mismatch is a leak and fails the build. | GATE-1, GATE-2, GATE-3 | Product FR-03 |
| VL-03 | Must if built | Peer-set replay: for 30 predictions, recompute the sector benchmark using only peers whose most recent event was announced strictly before D (Product SRS-04). | Recomputed values match stored values. | GATE-3 | Product SRS-03 to SRS-08 |
| VL-04 | Must | Split definitions: row counts and date ranges of the training, validation and test sets match the split definitions. Reading the test set once is ML-02. | Counts and date ranges match the definitions. | GATE-4 | Product FR-03, ML-02 |
| VL-05 | Must | Survivorship check: the universe contains delisted names in every year, and the universe's average return is compared with an independent index return for the same period. | A persistent gap above a threshold set in Section 11 is investigated and recorded. TH-06 is set from the first comparison run and recorded in the decision log before the validation set is read. | GATE-3 | Proposal 5.1 |
| VL-06 | Must | Label balance and threshold freeze: class shares are reported per year. The SUE cut-offs are set during EDA and frozen before the test set is read. | No class is below 10% in any year (proposed threshold), or each year below it is listed with its shares. Any change after the freeze is logged. | GATE-4 | Proposal 5.1 |
| VL-07 | Must | Basis check: 50 sampled events are checked for the same EPS basis in actual and consensus. | Zero mismatches, or every mismatch is corrected and logged. | GATE-2 | AE-03, CE-03 |
| VL-08 | Must | Known-event canary: 20 widely reported earnings releases from public records are in the dataset. For each, the stored EPS values match the public record, and the stored class equals the class computed by hand from LB-01 on those values. A disagreement with the headline consensus surprise is expected on some events and is counted in the LB-08 report, not treated as an error. | 20 of 20 stored EPS values match the record and 20 of 20 classes match the hand calculation, or each miss is investigated. | GATE-5 | Product FR-01 |
| VL-09 | Must | Hand audit: 100 randomly sampled events are checked against their primary documents. | Error rate at or below 2%. | GATE-5 | Market N3 (trust in the data) |
| VL-10 | Must | Snapshot trial, which the first four weeks of the forward capture job (SR-10) satisfy: for 20 tickers, the chosen snapshot source is captured daily for four weeks. Past-dated values are checked for change. | Results are recorded. Any change to a past-dated value rules out that source for backfill. This test is the only way to establish whether yfinance, FMP or Alpha Vantage's estimates endpoint change past-dated values. Alpha Vantage's documentation was read on 14 November 2026 and does not say. FMP's pages could not be read (HTTP 403). | GATE-2 | SR-08 |
| VL-11 | Must if built | Sector history check: companies reclassified in 2023 are checked against the published list of changes. | Every sampled company shows the sector that applied on its event date. | GATE-3 | SEC-01 |
| VL-12 | Must if a vendor estimate source is adopted | Pre-announcement estimate test: for any source that stores one estimate beside each past actual (Alpha Vantage, EODHD, yfinance), compare its stored estimate with the consensus quoted in the company's own 8-K press release or a dated news item, for 30 events across at least 10 sectors and 5 years. | At least 28 of 30 estimates agree within 1 cent or 1%, and none is a value revised after the announcement. Otherwise the source cannot build the label. | GATE-2 | CE-01, CE-02 |

## 10. Data Governance

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| GS-01 | Must | Each dataset version has a sign-off record. The reviewer did not build the dataset. Checks passed and known gaps are listed. | Sign-off exists before the dataset is used in training. | GATE-5 | Product ML-06 |
| GS-02 | Must | Each dataset has a data card: source, licence, coverage, date range, transformations and known gaps. | Data card exists for every dataset version. | GATE-5 | Product MR-02 |

## 11. Thresholds

These are proposed values. They should be agreed with Professor Goodacre before they are treated as commitments.

| ID | Measure | Proposed threshold | Requirement |
|---|---|---|---|
| TH-01 | Transcript coverage, target events | At least 90% | TX-04 |
| TH-02 | Segmentation accuracy, 50-transcript sample | At least 95% | TX-03 |
| TH-03 | Actual EPS agreement across two sources, 200-event sample | At least 98% within 0.5% | AE-02 |
| TH-04 | Consensus minimum estimate count | 3 | CE-04 |
| TH-05 | Index company count at sampled year-ends | Within 5 of published count | IM-01 |
| TH-06 | Survivorship gap | To be set after the first comparison run | VL-05 |
| TH-07 | Minimum share of any class per year | 10% | VL-06 |
| TH-08 | Hand-audit error rate, 100 events | At most 2% | VL-09 |
| TH-09 | Snapshot trial length | 4 weeks, 20 tickers, daily | VL-10 |
| TH-10 | Pre-announcement estimate test | 28 of 30 events agree within 1 cent or 1% | VL-12 |
| TH-11 | Time-series SUE history | At least 6 prior seasonal differences, 8-difference window | LB-01, LB-02 |
| TH-12 | Derived fourth-quarter EPS error | Differences above 1% listed | LB-03 |
| TH-13 | Label agreement (Route B against consensus) | Reported; no pass mark | LB-08 |
| TH-14 | Free-source cost | Zero | SR-09 |
| TH-15 | Null rate on the three date fields | 0% | DV-02 |

## 12. Week-One Experiments

Some source pages could not be read (FMP, Finnhub and the EODHD constituents blog), and no vendor documents when its estimates were taken, so these tests should run before any build work relies on them.

| Experiment | What it settles | Owner |
|---|---|---|
| Send the library enquiry in `library-enquiry-draft.md` (I/B/E/S, Capital IQ Transcripts, CRSP, Zacks, Capital IQ Estimates, LSEG Workspace). Also ask the supervisor whether the department can sponsor I/B/E/S access. | Whether the label can use point-in-time consensus. | John, with Professor Goodacre |
| Confirm WRDS access for Capital IQ Transcripts, CRSP and Compustat. | Whether the transcript, membership and sector routes are open. | John, with the library |
| Start the snapshot trial (VL-10) on 20 tickers. | Whether yfinance, Alpha Vantage or FMP keep past values unchanged. | John |
| Pull Alpha Vantage EARNINGS and EARNINGS_CALL_TRANSCRIPT for 10 tickers with a free key (25 requests a day). | History depth per ticker, and whether transcripts are complete for 2015 to 2024. Field names and the 25-a-day free limit are already read from the documentation. | John |
| Run `get_earnings_dates` for 10 tickers over 2019 to 2024. | Depth of past-event coverage and whether reported EPS matches the 8-K. | John |
| Pull diluted EPS for 10 companies from EDGAR company facts. Check the earliest usable quarter, how fourth-quarter EPS can be derived, and whether first-filed and restated values can be told apart. | Whether Route B can start with 2015 events (needs EPS from about 2012) and whether LB-03 and LB-04 are workable. | John |
| Make one test call each to the Finnhub and FMP free tiers for earnings estimates, and to yfinance for a past quarter. | Whether any free source returns past estimates, and which fields it returns. | John |
| Check `kurry/sp500_earnings_transcripts` for 20 companies that left the S&P 500 during 2015 to 2024. | Survivorship in transcript coverage (TX-07). | John |
| Run the pre-announcement estimate test (VL-12), only if a vendor estimate source is considered. | Whether a low-cost vendor can build a consensus label. | John |
| Pull 20 events from 8-K Exhibit 99.1 and check the release dates. | Whether AE-01 can be met from primary documents. | John |

### Spike results

**Hugging Face transcript set, delisted companies (15 November 2026, partial).** The datasets-server filter API was unreliable: a first run of 25 tickers mostly timed out or returned 500 and 502 errors, so it showed nothing. A retry with backoff returned four tickers:

| Ticker | Rows | Year range | Note |
|---|---|---|---|
| AAPL (current member) | 79 | 2005 to 2025 | Full coverage |
| XLNX (acquired 2022) | 60 | 2006 to 2021 | Present, but nothing after 2021 |
| TWTR (acquired 2022) | 16 | 2018 to 2021 | Present, but starts 2018 |
| ATVI (acquired 2023) | 27 | 2015 to 2021 | Present, but nothing after 2021 |

What this shows: the set is not limited to current index members. What it does not show: whether coverage of removed companies is complete. Three of three removed companies tested end in 2021 or earlier, which suggests their last quarters or years may be missing. The meaning of the `year` field (fiscal or calendar) was not checked. Sixteen of the twenty removed companies planned for the test were not retried, so TX-07 still needs the full coverage table. The list of removed companies comes from general knowledge and has not been checked against index history.

**EDGAR SIC spike (19 November 2026).** Eighteen companies, one 10-K header each from 2015, 2019 and 2023 (AAPL, MSFT, PFE, KO, GE, IBM, INTC, T, VZ, DIS, F, NFLX, AMZN, META, GOOGL, TSLA, PYPL, MA; DIS and GOOGL had no 2015 filing in the sample; XOM and JPM returned no header and were not retried). The `ASSIGNED-SIC` value in every header equalled the current `sic` in the submissions data, for every company and year. That fits two readings: EDGAR stamps today's code on old filings, or no company in the sample changed. The sample cannot tell them apart, and it shows no evidence of a dated sector history. Result: inconclusive, leaning negative. Sector scoring is switched off for the December scope (decision C-29). A longer spike is worth running only if sector scoring is built later.

**EDGAR diluted EPS spike.** Partial, one company only (Apple), run before the decisions of 18 November 2026. The submissions data has a UTC acceptance time with seconds and an `items` field that lists Item 2.02. `sic` is a single current value, so it does not show history. Diluted EPS facts each have a `filed` date. There is no fourth-quarter EPS fact, so it must be derived (LB-03). The ten-company run is not done, so depth, restatement counts and early-period coverage are still unmeasured. The full script needs the SEC contact in the `SEC_USER_AGENT` environment variable, which the owner sets (decision C-10).

## 13. Open Decisions

Open decisions are in the [decision log](../decision-log.md). Those that concern this document: D-06 (thresholds), D-18 (transcript sources and demo design), D-19 (fundamentals source), D-21 (optional institutional access) and D-23 (label thresholds).

## 14. Sources Checked

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
| S&P Global, GICS sector changes: https://www.spglobal.com/spdji/en/education/article/talkingpoints-an-overview-of-sp-500-sector-indices-and-25-years-of-gics | Background on GICS revisions | Title seen. Not read. |
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

Library pages read 14 November 2026: faq/250332 (I/B/E/S, updated 28 October 2024), faq/188353 (WRDS access, 31 January 2023), faq/192199 (Capital IQ, 23 October 2023), faq/193007 (transcripts, 28 October 2024), faq/228851 (LSEG Workspace) and faq/228031 (Datastream). They are dated 2022 to 2025 and may be out of date. The live WRDS catalogue was not checked.

Points not verified: FMP plans and endpoints (pages blocked); Finnhub; the timing of every low-cost vendor's stored estimate (VL-12 settles it); the licence of Alpha Vantage data for a public demo; yfinance history depth; I/B/E/S Summary History timing and revision handling (rules in CE-06 are from general knowledge of the database, not read from WRDS documentation); whether Manchester holds Zacks or Capital IQ Estimates; the Zacks WRDS one-sheet (PDF text could not be read); Benzinga and Massive prices and licence; the origin of the Hugging Face transcript sets; Compustat GICS history; the claim that EDGAR holds only current SIC codes; the Refinitiv Workspace estimate history; the Datastream series codes; and all licence terms marked "unverified" in Section 4.
