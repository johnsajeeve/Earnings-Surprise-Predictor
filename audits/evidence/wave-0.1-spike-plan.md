# Wave 0.1: spike plan, written before any spike was run

Written 23 November 2026, before Spikes A to E ran (Step 0.1.2, Deterministic_audit.md Section 5). Each spike has a question, the data, the method, and the rule that turns the result into a decision. The rules are Claude's proposals, not requirement values. John may change them. A change after a spike has run is recorded as a change, with the date, and the earlier rule stays visible.

Rules that apply to every spike:
- The SEC contact string (`SEC_USER_AGENT`, C-10) is sent only to `sec.gov` hosts, by a script that reads it from the environment. It is never printed, logged, committed or sent to another host. Other hosts get the generic client name `earnings-project-check`.
- EDGAR requests stay at or below 5 a second (the limit is 10, IG-07).
- Spike scripts are throwaway. They live in the session scratchpad and are not committed to `src/`. Downloaded data stays in its own directory in the scratchpad and is not committed.
- Results are reported as measured. A result that is poor is reported as poor. No spike result changes a requirement, and a change to Data Section 12 is shown to John first (C-12, drift control 4).
- Real data only. No synthetic or mock rows appear in any result (SC-04).

## Spike A: call time against 8-K acceptance time (IG-16, C-17)

- Question: for events in the Hugging Face set, how often does the call precede the 8-K Item 2.02 filing, and by how much?
- First check, before sampling: does the `date` field of `kurry/sp500_earnings_transcripts` (documented as `YYYY-MM-DD HH:MM:SS`) hold a real time of day, or is it always midnight? If it is always midnight, the comparison cannot be made at the minute level, and that is the result.
- Data: the set at revision `f3ded372da8d18dc6ad98955c4558e34b5fe6d45`; EDGAR submissions for the sampled companies.
- Method: sample 50 events with a fixed random seed (2027), drawn evenly across 2015 to 2024 from companies that EDGAR can resolve by ticker. For each, find the 8-K whose items include 2.02 and whose filing date is within 3 calendar days of the call date, and take its acceptance time in UTC. Convert the call time using the time zone the set states, or report that none is stated.
- Report: events matched, events unmatched with the reason, share where the call is first, median and range of the gap in minutes, and the 25th and 75th percentiles.
- Decision rule: none to pass or fail. The result decides only whether the C-17 cutoff rule (earlier of the two times) needs the call time to be reliable. If fewer than 40 of 50 events can be matched, or the call time has no time of day, report that the T0 cutoff cannot be verified from this set and ask John.

## Spike B: EPS depth and bulk files (LB-02, LB-03, IG-09)

- Question: does EDGAR XBRL company facts give at least 10 quarters of diluted EPS before a company's first 2015 event, can fourth-quarter EPS be derived, and can first-filed values be told from restated ones?
- Data: company facts for 10 companies, fixed in advance: AAPL, MSFT, JPM, XOM, KO, IBM, PFE, F, XLNX (acquired 2022), ATVI (acquired 2023). Two removed companies are included on purpose, because the universe must include removals (IM-02).
- Method: count distinct quarterly diluted EPS values by fiscal period from 2012 to 2024; mark whether a fourth-quarter value exists directly or has to be derived (full year minus three quarters); compare the `filed` dates of repeated facts for the same period to see whether the original filing is distinguishable. Also check by one request whether the SEC bulk files (`companyfacts.zip`, `submissions.zip`) exist and read their last-modified header, then repeat on a second day.
- Report: per company, earliest quarter, quarters available before 2015, whether Q4 is derived, whether restated values are visible.
- Decision rule: Route B is workable for 2015 events if at least 8 of the 10 companies have at least 10 quarters before their first 2015 event. A lower count is reported with the companies and the cause, and John decides what follows. It is not worked around.
- Bulk file refresh (IG-09) needs two observations on different days. After one day the result is recorded as "one observation".

## Spike C: consensus source (SR-10, CE-01, VL-12)

- Question: which free source returns an estimate mean, a standard deviation and an analyst count for an upcoming quarter, and under what terms?
- Data: 5 tickers, fixed: AAPL, MSFT, JPM, KO, F. Sources: yfinance; the Finnhub and FMP free tiers.
- Method: one call per source per ticker. Record fields returned, whether they are current values only, and the terms stated by the source.
- Blockers known in advance: Finnhub and FMP need a free key that John must create. Their result is BLOCKED until he does. yfinance is not installed in the project image, so it runs from a throwaway virtual environment in the scratchpad.
- Decision rule: a source is a candidate for Wave 0.3 only if it returns a mean and an analyst count for the upcoming quarter for at least 4 of 5 tickers on a documented route. The standard deviation is reported but does not decide, because the free route has none (Data 4A.1).

## Spike D: transcript source (D-18, SR-03, TX-07)

- Question: what do the licence and card of the Hugging Face set say, are removed companies present, and does the set cover 2015 to 2024 for them?
- Data: README and licence of the set at the revision above; the parquet file.
- Method: read the card and licence; list the companies with transcripts for each year; take 20 companies that left the S&P 500 during 2015 to 2024 (names fixed from the membership source chosen later, or from a list John approves) and report their first and last transcript dates.
- Report: licence wording quoted exactly, origin statement or its absence, empty-text rows, coverage of the removed companies by year.
- Decision rule: none to pass or fail. The result goes to John for D-18. A removed company with no transcript is reported as a coverage gap (TX-07), not filled.
- Alpha Vantage needs a free key from John. Until he supplies it that part is BLOCKED.

## Spike E: FinBERT scoring speed (FE-09)

- Question: how many sentences a second does FinBERT score on this CPU, and how many hours does the 100-company corpus need?
- Method: score 1,000 real sentences taken from the transcript set, in batches, in a throwaway environment outside the project image, so that no dependency file changes. Record hardware, library versions, batch size and sentences per second. Project the hours from the sentence count of a sample of 100 transcripts.
- Checkpoint: D-35 (which FinBERT checkpoint) is still open. The speed is measured with the checkpoint John names. Until then it is reported for `ProsusAI/finbert` as an example only, labelled "not the chosen checkpoint".
- Blockers: Docker is not running (see the baseline record). Torch for Python 3.14 may not be available. If neither works, Spike E is BLOCKED and says why.
- Decision rule: none to pass or fail. If the projected scoring time for 100 companies exceeds 48 hours, report it to John with the options in plan Section 9.

## Spike A2: which clock does the call time use? (added 23 November 2026, before it ran)

Added after John asked whether UK time or another zone fits. This tests the zone question on a larger sample. Written before the run.

- Question: which of four readings of the Hugging Face `date` field makes the 8-K and call times consistent: H1 US Eastern with daylight saving, H2 US Eastern standard time all year (fixed UTC-5), H3 Europe/London (UK time with daylight saving), H4 UTC.
- Sample: 400 events, seed 2028, 40 a year for 2015 to 2024, from tickers in the current SEC ticker file. The 8-K matched is the Item 2.02 filing whose filing date is nearest the call date (within 3 days, ties to the earliest), chosen without using any time zone.
- Test 1, clustering of call times of day over the whole set (33,362 rows): what share fall in US business hours 08:00 to 17:30, and which times are the most common.
- Test 2, daylight saving: for events with |gap| at most 24 hours, compute the median gap (filing minus call) in summer (April to October) and in winter (December to February), leaving out March and November because the clocks change then. Under the right reading the two medians agree. Under a reading that ignores daylight saving the summer median moves by about 60 minutes.
- Decision rule: the reading with the smallest absolute difference between the summer and winter medians, together with a business-hours share above 85% under that reading, is preferred. If two readings are within 20 minutes of each other on Test 2, report both and ask John. The rule does not prove the source's intent. It reports which reading the data supports.

### Spike A2 follow-up: after-close anchor test (added 23 November 2026, before it ran)

Spike A2 ran first. Its result: the business-hours test rules out H3 (London) and H4 (UTC), because read as US Eastern their calls fall in business hours only 31.5% of the time against 96.1% for H1 and H2. Test 2 (summer against winter medians) gave absolute differences of 24 minutes for H1 and 36 for H2. These are within the 20-minute band of each other, so by the rule written above the result is inconclusive between H1 and H2, and the median gap is too noisy (inter-quartile range near 900 minutes) to separate them. This follow-up tries a sharper test and is written before it runs.

- Anchor: companies that release after the close file the 8-K at about 16:00 to 16:30 Eastern and hold the call at 16:30 or 17:00. The filing time comes from EDGAR (UTC) and is converted to Eastern with daylight saving, which is correct whatever the call stamp means.
- Sample: every row in 2015 to 2024 whose stamp is 16:30 or 17:00, with a matched 8-K Item 2.02 (nearest filing date, within 3 days, ties to the earliest) whose acceptance time is between 16:00 and 16:30 Eastern.
- Test: for H1 and H2, the median gap (filing minus call) in summer (April to October) and in winter (December to February), with the number of events in each. The right reading gives the same median in both seasons. A reading that ignores daylight saving shifts the summer median by about 60 minutes.
- Decision rule: the reading with the smaller summer-winter difference is preferred if it is below 20 minutes and the other is above 40 minutes. Otherwise the result is inconclusive and John is told so.

## Spike C2: Finnhub free key (added 23 November 2026, before it ran)

John supplied a free Finnhub key, so the part of Spike C that was blocked can run.

- Question: on a free key, does Finnhub return (a) a quarterly estimate mean, high, low and analyst count for the upcoming quarter, and (b) past actual and estimate pairs per quarter (which would bear on VL-12)?
- Data: the same 5 tickers as Spike C (AAPL, MSFT, JPM, KO, F). Endpoints tried: `/stock/eps-estimate` (quarterly) and `/stock/earnings`. One call each per ticker, key in the `X-Finnhub-Token` header, sent only to `finnhub.io`.
- Report: HTTP status, fields returned, number of periods, whether a standard deviation is present, and the response when the plan does not cover the endpoint. The key is never printed or stored in any file in the repository.
- Decision rule: Finnhub is a candidate second source for Wave 0.3 if the estimate endpoint returns a mean and an analyst count for at least 4 of 5 tickers on the free key. If it answers 403 or similar, it is reported as not available on the free plan and the register says so. `/stock/earnings` results are reported for VL-12 but do not by themselves adopt Finnhub as a label source, because nothing shows when each stored estimate was taken.
