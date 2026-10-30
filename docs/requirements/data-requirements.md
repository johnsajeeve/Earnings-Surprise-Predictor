# Data Requirements: Verification and Validation

Derived from the Market Requirements and Product Requirements (26 October 2026), the architecture deck (slides 3 and 4), and source research carried out 30 October 2026.

## 1. Purpose and Scope

This page sets out the data the predictor depends on, which source can supply each dataset, and the checks that prove the data passes the five gates in the architecture deck.

It covers six datasets: earnings call transcripts, actual EPS, pre-announcement consensus, index membership, sector classification and share prices.

For each dataset it sets:
- which sources are acceptable, and whether each one passes the gates;
- verification requirements: is the data correct, complete and consistently formatted?
- validation requirements: does the data hold up under the lookahead gates?

A dataset may build the label or the features only when its source passes every gate that depends on it (SR-02). A source that fails a gate can still support development or cross-checks, if its licence allows.

## 2. Gates Used on This Page

| Gate | Rule | Origin |
|---|---|---|
| G1 | Three dates stored separately for every event: transcript, estimate publication and announcement. | Deck slide 4, gate 1; Product FR-02 |
| G2 | Consensus estimates used are those captured before the announcement. | Deck slide 4, gate 2; Product FR-14 |
| G3 | The peer set and the universe are as they stood on the event date. | Deck slide 4, gate 3; Product FR-12 |
| G4 | The split is enforced in code and the test set is read once. | Deck slide 4, gate 4; Product FR-03 |
| G5 | Data is signed off and its provenance recorded before release. | Deck slide 4, gate 5, adapted from model sign-off to data sign-off |

## 3. Bottom Line

1. **No free or low-cost source gives historical point-in-time consensus.** yfinance and Alpha Vantage return current values. Financial Modeling Prep (FMP) states that it keeps no revision history and that users must store their own snapshots. Snapshots collected from now on cannot backfill 2015 to 2024.
2. **I/B/E/S via WRDS is the only route found to historical point-in-time consensus, and it is restricted at Manchester.** The library FAQ says IBES via WRDS is available "for AMBS Accounting and Finance researchers only". This blocks Gate 2 for the label. It needs a decision now, not in week 1 of the build.
3. **For transcripts, S&P Capital IQ Transcripts via WRDS is the strongest source found.** The library FAQ names no eligibility limit for it. That is not the same as confirming access for a Computer Science student.
4. **For membership and prices, CRSP via WRDS is the preferred source.** The library FAQ confirms it holds the full history of S&P 500 constituents. Eligibility is unverified.
5. **Yahoo-derived data cannot go into a public demo.** yfinance's README states that Yahoo's API is "intended for personal use only". The GitHub index file checked also takes its data from Yahoo Finance. Tiingo is limited to internal and personal use unless it is licensed.
6. **The public demo cannot rely on most licensed data.** It needs one of two designs: a historical demo slice built from redistributable data, or a bring-your-own-key design where the user supplies their own licensed credentials.
7. **The proposal's plan to take transcripts from SEC EDGAR is not sound.** Some issuers file transcripts as 8-K exhibits, but coverage is not systematic. This corrects Market DR-03.

## 4. Source Assessment

| Source | Dataset | Historical point-in-time? | Access for this project | Licence for public demo | Verdict |
|---|---|---|---|---|---|
| I/B/E/S via WRDS | Historical consensus and actuals | Yes. Standard research dataset with dated estimates. Revision handling to be confirmed from WRDS documentation (not read). | Restricted at Manchester to AMBS Accounting and Finance researchers. | Academic use only. | Preferred for consensus if access is granted. |
| LSEG Refinitiv Workspace | Consensus, transcripts, some historical estimate data | Unverified | Manchester has Workspace access per the library FAQ. | Unverified | Check whether dated historical estimates can be exported in bulk. |
| S&P Capital IQ Transcripts via WRDS | Earnings call transcripts | Transcripts carry event dates. First-publication timestamps unverified. | WRDS. Library FAQ states no eligibility limit. Coverage given as about 10,600 companies (FAQ) and about 8,000 (WRDS page). | Academic use only. | Preferred transcript source, subject to access and a segmentation test. |
| Refinitiv Advanced Events Search | Transcripts | Yes, by event | Manchester library access. Export is by PDF, Word or text; batch export needs a Windows tool. | Unverified | Fallback for small manual samples only. Not suitable for the pipeline. |
| FMP transcripts | Transcripts | Event-dated. Coverage of about 8,200 companies and 200,000 or more transcripts, from 10+ years by quarter. | Paid. Transcripts are included only in the Ultimate plan: $139 per month, or $99 per month billed annually. | Unverified | Commercial fallback if WRDS access fails. Check licence before paying. |
| FMP estimates | Consensus | No. Returns the current consensus only and states it has no revision history. | Paid plan | Unverified | Fails Gate 2 for backtesting. Usable forward-only from a start date. |
| yfinance | Consensus (current), recent EPS history, prices | No for estimates. `earnings_estimate` reads Yahoo's current estimates. `get_earnings_dates` scrapes Yahoo's calendar web page (default 12 rows, maximum 100). Depth of `earnings_history` is set by Yahoo. | Free, no key. Unofficial. | Fails: "intended for personal use only" under Yahoo's API terms. | Development and cross-checks only. |
| Alpha Vantage EARNINGS | Quarterly EPS with estimate and surprise | Unverified. Likely a current snapshot at fetch time. | Free key. Free-tier limit unverified. The official documentation could not be read from this environment. | Unverified | Cross-check for actual EPS only, until tested. |
| SEC EDGAR | Filing dates, 8-K press releases with EPS, some 8-K transcript exhibits | Yes, by filing date | Free and public | Public record | Use for announcement dates and actual-EPS cross-checks. Not a systematic transcript source. |
| CRSP via WRDS | Index membership, prices | Yes for membership (full history of S&P 500 constituents per the IESE FAQ). | WRDS. A tutorial states CRSP requires a subscription. Eligibility at Manchester unverified. | Academic use only. | Preferred for membership and prices, subject to access. |
| Compustat via WRDS | Index lists by date range, GICS fields | Lists can be built for a date range (IESE FAQ). Whether GICS history is stored by date is unverified. | WRDS. Eligibility unverified. | Academic use only. | Candidate for sector history. Verify the field history first. |
| Datastream | Monthly index membership | Yes, monthly series | Manchester has Datastream per the library FAQ. | Unverified | Fallback for membership. |
| Tiingo | Daily prices | Yes | Free tier available. Basic and Power accounts are for internal and personal use only. | Redistribution prohibited without a licence. Email Tiingo for a licence. | Internal development only. |
| GitHub `fja05680/dow-sp500-100-years` | Described as S&P 500 membership history | No. The file checked is a daily index-level series from 1927, sourced from Yahoo Finance. Membership is not confirmed. | Free, MIT licence on the repository. | Inherits Yahoo's personal-use restriction through its data source. | Do not use for membership unless the constituent data is verified. |

## 5. Gate Pass Matrix

| Dataset | Gates | Preferred source | Status | Blocker |
|---|---|---|---|---|
| Transcripts | G1, G4 | Capital IQ Transcripts via WRDS | Conditional | WRDS eligibility. Segmentation untested. |
| Transcripts (fallback) | G1, G4 | FMP Ultimate | Conditional | Cost and licence |
| Actual EPS | G1 | 8-K Exhibit 99.1 from SEC EDGAR, cross-checked against Capital IQ or IBES | Conditional | Primary-document parsing not built |
| Pre-announcement consensus | G2 | I/B/E/S via WRDS | Conditional | Manchester eligibility |
| Consensus (fallback) | G2 | yfinance, Alpha Vantage or FMP snapshots | Fails for backtest. Usable only forward from the capture start date. | No historical data |
| Index membership | G3 | CRSP via WRDS | Conditional | WRDS eligibility |
| Index membership (fallback) | G3 | Datastream monthly series | Conditional | Series codes not yet checked |
| Sector history | G3 | Compustat via WRDS | Unverified | GICS field history not checked |
| Sector (fallback) | G3 | SIC codes from EDGAR | Fails unless historical SIC is verified | EDGAR company records are believed to hold only the current code. To verify. |
| Prices | G4 (momentum feature) | CRSP via WRDS | Conditional | WRDS eligibility |
| Prices (fallback) | G4 | Tiingo | Internal development only | Licence |

## 6. Source Requirements

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| SR-01 | Must | Every dataset has a named source, licence, access route and access date recorded in a source register before ingestion starts. | Register has one row per dataset, each with a licence and a dated access check. | G5 | Market DR-05 |
| SR-02 | Must | A dataset builds the label or any feature only if its source passes every gate that depends on it. | Every feature column carries a source tag. An untagged column fails the build. | G1 to G4 | Product FR-02 |
| SR-03 | Must | Data in the public demo must be redistributable under its licence, or supplied by the user's own credentials. | Demo bundle manifest lists each source and its licence. Any personal-use source fails the check. | G5 | Market DR-05, CP-02 |
| SR-04 | Must | Raw responses are stored unchanged with retrieval time, source name and source version. | Hash of each stored raw file matches the hash recorded at retrieval. | G5 | Product PL-06 |
| SR-05 | Must | Eligibility for every WRDS dataset is confirmed in writing before week 3. | Written confirmation from the library or supervisor is on file. | G5 | Market DR-01, DR-03 |
| SR-06 | Must | Every Must dataset has a documented fallback source, and the fallback passes the same tests or the project scope is narrowed. | Register lists a fallback per dataset and records the test result for it. | G5 | Market DR-01 |
| SR-07 | Should | Scraped sources are used only in development, with request logs kept and rate limits respected. | Request log exists. No scraped source appears in the demo bundle. | G5 | Section 4 |
| SR-08 | Must | Snapshot-only sources are stored only as timestamped captures from the start date. They are never backfilled into historical rows. | Test rejects any row for a snapshot source whose capture time is missing or earlier than the start date. | G2 | Product FR-14 |

## 7. Dataset Requirements

### 7.1 Earnings Call Transcripts

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| TX-01 | Must | Each transcript has a company identifier linked to a permanent identifier, the event date and the call type. | 100% of rows have all three fields. Rows missing one are rejected and logged. | G1 | Product FR-02 |
| TX-02 | Must | A transcript is dated on or after its announcement, within a window of one trading day. | Violations are zero, or each violation is listed with a reason. | G1 | Product FR-02 |
| TX-03 | Must | The split between prepared remarks and Q&A is accurate. | On a hand-labelled sample of 50 transcripts, at least 95% of boundaries are correct. | G1 | Product FR-15 |
| TX-04 | Must | At least 90% of target events, S&P 500 2015 to 2024, have a transcript. | Coverage report lists every missing company and quarter. | G3 | Market DR-03 |
| TX-05 | Must | One transcript per event. Duplicates are resolved by the earliest first-publication time. | Unique-key test on company and event passes. | G1 | Product FR-13 |
| TX-06 | Should | Speaker and role labels are kept, so analyst questions and management answers can be separated. | Sample of 20 transcripts has labels on every turn. | G1 | Product FR-15 |

### 7.2 Actual EPS

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| AE-01 | Must | Each actual EPS value is linked to a primary document (8-K Exhibit 99.1 or a licensed vendor record) and its release date. | Every event has a document identifier and a release date. | G1 | Market DR-04 |
| AE-02 | Must | Actual EPS from two independent sources agrees within 0.5%, or the difference is explained. | At least 98% agreement on a sample of 200 events. | G1 | Market DR-04 |
| AE-03 | Must | The EPS basis (GAAP or adjusted) is recorded and used consistently for both the actual and the consensus. | Basis field is populated and has one value per dataset. Test in VL-07. | G2 | Product FR-01 |
| AE-04 | Must | The first reported actual is kept. Later corrections are stored as new versions. | After a simulated correction, the first-reported value is unchanged. | G5 | Market DR-07 |

### 7.3 Pre-Announcement Consensus

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| CE-01 | Must | Consensus mean and standard deviation are stored with the time they were captured. Every capture time is before the announcement. | Zero rows where capture time is on or after announcement. | G2 | Market DR-01, DR-10 |
| CE-02 | Must | No historical consensus is inferred from a current value. Where only current values exist, the project starts capturing on a dated schedule from the start date. | Test VL-01 passes. SR-08 test passes. | G2 | Product FR-14 |
| CE-03 | Must | Consensus is on the same basis as the actual EPS it is compared with. | Basis test VL-07 passes. | G2 | Product FR-01 |
| CE-04 | Must | Events with fewer than three estimates are excluded from the label and the exclusion count is reported. The standard deviation is undefined below that count. | Exclusion count is reported per year. | G2 | Proposal 5.1 (SUE) |

### 7.4 Index Membership

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| IM-01 | Must | Membership is stored with start and end dates for every company. The universe on each date matches the index membership on that date. | At sampled year-ends, company count matches the published count within 5, and differences are explained. | G3 | Market DR-02 |
| IM-02 | Must | Companies that were removed, delisted or acquired during 2015 to 2024 are included, each with its last trading date and removal reason. | Each year in the period has at least one such company. Each record has a removal date and reason. | G3 | Market DR-08 |
| IM-03 | Must | Ticker changes and identifier changes are linked through a permanent identifier, so a company's history is continuous. | Join on the permanent identifier produces one continuous history for ten known renames. | G3 | Market DR-02 |

### 7.5 Sector Classification

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| SC-01 | Must | Sector is assigned as it stood on the event date, from a dated history. The current classification is never used for past events. | Test VL-11: a company reclassified in 2023 shows its old sector before the change date. | G3 | Market DR-06 |
| SC-02 | Must | The peer set for the sector-relative score includes only companies that are in the universe on date D and have a known sector on D. | Unit test on a fixed date with a known peer set passes. | G3 | Product FR-12 |

### 7.6 Share Prices

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| PX-01 | Must | Split and dividend adjustments are stored separately from the raw price, with dated adjustment factors. | 20 sampled announcement-day closes match a second source. | G4 | Market DR-04 |
| PX-02 | Must | Momentum features use only prices dated before the announcement. Outcome returns use only prices from the announcement onwards. | Test with a planted future price shows it is excluded. | G4 | Product FR-03 |
| PX-03 | Must | Adjusted and unadjusted prices are never mixed in one series. yfinance returns dividend-adjusted prices by default. | Series-type check fails any series containing both. | G4 | Section 4 |

## 8. Verification Requirements

Verification asks whether the data is correct, complete and consistently formatted.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| DV-01 | Must | Every table matches its versioned schema. Rows that fail are quarantined, not dropped. | Quarantine count is reported per run. | G5 | Product PL-05 |
| DV-02 | Must | Null rates are measured for each field, and each field has a maximum. | The three date fields have zero nulls. Other fields are within the thresholds in Section 11. | G1 | Product FR-02 |
| DV-03 | Must | Each event is unique on company, fiscal quarter and announcement date. | Uniqueness check passes on every load. | G1 | Product FR-13 |
| DV-04 | Must | Extreme values are flagged for a person to review, not removed automatically. | Flagged rows have a reviewer note before the dataset is signed off. | G5 | Market DR-07 |
| DV-05 | Must | Date order holds: capture before announcement, announcement before or on transcript, and release before the price window. | Date-order test on every load reports zero violations. | G1, G2 | Product FR-02 |
| DV-06 | Must | Fiscal periods are mapped to calendar quarters, including companies with non-calendar fiscal years. | Mapping test passes on five known non-calendar companies. | G1 | Product FR-02 |
| DV-07 | Must | Announcement times are converted to UTC and mapped to the correct trading day. Releases after the close are dated to the next session. | Test covers a pre-open and an after-close release, both mapped correctly. | G1, G4 | Product FR-03 |
| DV-08 | Must | Re-running ingestion on the same raw snapshot produces identical tables. | Table hashes match between two runs. | G5 | Product NFR-05 |

## 9. Validation Requirements

Validation asks whether the data holds up under the gates. Each test is written so that it can fail.

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| VL-01 | Must | Planted-future estimate: a synthetic estimate captured one day after an announcement is inserted. | The pipeline excludes it. Any leaked row fails the build. | G2 | Market TR-03 |
| VL-02 | Must | Feature replay: for 30 events, rebuild each feature vector using only data dated before the announcement. | Rebuilt vectors match stored vectors. Any mismatch is a leak and fails the build. | G1, G2, G3 | Product FR-03 |
| VL-03 | Must | Peer-set replay: for 30 predictions, recompute the sector benchmark using only peers announced on or before D. | Recomputed values match stored values. | G3 | Product FR-12 |
| VL-04 | Must | Split and seal: row counts and date ranges match the split definitions. The test set is read only in the final evaluation job. | Access log shows test rows read once. | G4 | Product FR-03, ML-02 |
| VL-05 | Must | Survivorship check: the universe contains delisted names in every year, and the universe's average return is compared with an independent index return for the same period. | A persistent gap above a threshold set in Section 11 is investigated and recorded. | G3 | Market DR-08 |
| VL-06 | Must | Label balance and threshold freeze: class shares are reported per year. The SUE cut-offs are set during EDA and frozen before the test set is read. | No class is below 10% in any year (proposed threshold). Any change after the freeze is logged. | G4 | Proposal 5.1 |
| VL-07 | Must | Basis check: 50 sampled events are checked for the same EPS basis in actual and consensus. | Zero mismatches, or every mismatch is corrected and logged. | G2 | AE-03, CE-03 |
| VL-08 | Must | Known-event canary: 20 widely reported earnings surprises from public records are in the dataset with the expected class. | 20 of 20 correct, or each miss is investigated. | G5 | Product FR-01 |
| VL-09 | Must | Hand audit: 100 randomly sampled events are checked against their primary documents. | Error rate at or below 2%. | G5 | Market TR-01 |
| VL-10 | Must | Snapshot trial: for 20 tickers, the chosen snapshot source is captured daily for four weeks. Past-dated values are checked for change. | Results are recorded. Any change to a past-dated value rules out that source for backfill. This test is the only way to establish the behaviour of yfinance, Alpha Vantage and FMP, as their documentation could not be read. | G2 | SR-08 |
| VL-11 | Must | Sector history check: companies reclassified in 2023 are checked against the published list of changes. | Every sampled company shows the sector that applied on its event date. | G3 | SC-01 |

## 10. Data Governance

| ID | Priority | Requirement | Acceptance check | Gate | Traces to |
|---|---|---|---|---|---|
| GS-01 | Must | Each dataset version has a sign-off record. The reviewer did not build the dataset. Checks passed and known gaps are listed. | Sign-off exists before the dataset is used in training. | G5 | Market MR-03 |
| GS-02 | Must | Each dataset has a data card: source, licence, coverage, date range, transformations and known gaps. | Data card exists for every dataset version. | G5 | Market MR-02 |

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
| Null rate on the three date fields | 0% | DV-02 |

## 12. Week-One Experiments

Some source documents could not be read from this environment, so these tests should run before any build work relies on them.

| Experiment | What it settles | Owner |
|---|---|---|
| Ask the library, and if needed the supervisor, whether a Computer Science student can get IBES via WRDS. | Whether the label can use point-in-time consensus. | John, with Professor Goodacre |
| Confirm WRDS access for Capital IQ Transcripts, CRSP and Compustat. | Whether the transcript, membership and sector routes are open. | John, with the library |
| Start the snapshot trial (VL-10) on 20 tickers. | Whether yfinance, Alpha Vantage or FMP keep past values unchanged. | John |
| Pull Alpha Vantage EARNINGS for 10 tickers with a free key. | Field names, history depth and free-tier limit. Documentation could not be read. | John |
| Run `get_earnings_dates` for 10 tickers over 2019 to 2024. | Depth of past-event coverage and whether reported EPS matches the 8-K. | John |
| Pull 20 events from 8-K Exhibit 99.1 and check the release dates. | Whether AE-01 can be met from primary documents. | John |

## 13. Changes Needed in Earlier Documents

| Document | Item | Change |
|---|---|---|
| Market requirements | DR-01 (consensus) | Status confirmed as high risk. FMP has no history and yfinance is current-only. The only route is IBES, which is restricted. |
| Market requirements | DR-03 (transcripts) | Change the source from SEC EDGAR to Capital IQ via WRDS, or FMP as fallback. The SEC route is partial. |
| Market requirements | DR-05 (licence) | Add yfinance (personal use only), Tiingo (internal use only) and the GitHub index file (inherits Yahoo terms). |
| Market requirements | DR-06 (sector) | Add Compustat as the candidate source. Field history still to verify. |
| Product requirements | FR-14 (snapshots) | Add the rule that snapshot sources start from a capture date and cannot backfill (SR-08). Start capture early if IBES access is refused. |
| Proposal | Section 5.1 (data sources) | Replace the EDGAR transcript route, and name the consensus source once access is decided. |
| Architecture deck | Slide 6 (decisions) | Add the IBES access decision and the transcript source as decisions before week 1. |

I have not edited the Market or Product documents. These changes are listed for you to approve.

## 14. Open Decisions

1. Can a Computer Science student get IBES via WRDS at Manchester? If not, is there an approved route through the supervisor?
2. If IBES is refused, is the project scope changed to a forward-only label, which means no backtest over 2015 to 2024?
3. Is FMP's Ultimate plan worth paying for as the transcript fallback? It costs $99 to $139 per month and the licence is unverified.
4. Does the public demo use a historical slice or a bring-your-own-key design (SR-03)?
5. Which thresholds in Section 11 does Professor Goodacre accept?

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

Points not verified: Alpha Vantage limits and fields; yfinance history depth; I/B/E/S revision handling; Compustat GICS history; the claim that EDGAR holds only current SIC codes; the Refinitiv Workspace estimate history; the Datastream series codes; and all licence terms marked "unverified" in Section 4.
