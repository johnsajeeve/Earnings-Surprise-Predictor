# Wave 0.1: spike results (Steps 0.1.3 to 0.1.6, partial)

Run on 23 November 2026. Rules were written first in [wave-0.1-spike-plan.md](wave-0.1-spike-plan.md). Throwaway scripts and raw result files are in `wave-0.1-scripts/` for audit only. They are not project code, so the scripts are stored with a `.txt` ending to keep them out of the lint run (ruff found style errors in them, which do not matter for a one-off script).

## Wave 0.1

Requirements touched: IG-16 (Spike A), LB-02, LB-03, IG-09 (Spike B), SR-10, CE-01 (Spike C, partial), SR-03, TX-07 (Spike D, partial).

## Commands run

- Environment: a Python 3.14.4 virtual environment in the session scratchpad, outside the project, with `pyarrow 26.0.1`, `requests 2.32.5`, `yfinance 1.8.0`. No project dependency file changed.
- Transcript set: `curl -L` of `kurry/sp500_earnings_transcripts` at revision `f3ded372da8d18dc6ad98955c4558e34b5fe6d45`, file `parquet_files/part-0.parquet`, 1,824,805,388 bytes, SHA-256 `9a305a1c4cbf6c4b0b9c8b98b242ea3de4dbe0ad43937dc54b56418629a17b31`. 33,362 rows.
- Spike A: `venv/bin/python spikeA2.py` (copy: `wave-0.1-scripts/spikeA2.py.txt`, results `spikeA_results.json`).
- Spike B: `venv/bin/python spikeB.py` (copy: `wave-0.1-scripts/spikeB.py.txt`, results `spikeB_results.json`) and two follow-up requests for Exxon (CIK 34088 company facts and submissions, and the ticker file entry for XOM).
- Spike C: `yfinance.Ticker(t).earnings_estimate` for AAPL, MSFT, JPM, KO, F.
- Spike D: reading the dataset card, and a count of symbols in the set against the current SEC ticker file.
- The SEC contact string was read from the environment, sent only to `sec.gov` hosts (the script asserts the host), and never printed or written. Request rate was at most 4 a second.

## Output and result per spike

### Spike A: call time against 8-K acceptance time (IG-16)

- The `date` field holds a time of day. 33,166 of 33,362 rows have a non-midnight time. 196 rows (0.6%) are `00:00:00`, which is a placeholder, not a real time (136 of the 20,194 rows in 2015 to 2024). No time zone is stated anywhere in the card or the data.
- Sample: 50 events, seed 2027, five a year from 2015 to 2024, from tickers that are in the current SEC ticker file. 47 of 50 matched an 8-K with Item 2.02 within 3 days. Unmatched: APA 2015-02-12, APA 2019-02-28, EVRG 2019-11-10. The pass line in the plan (at least 40 of 50 matched) is met.
- Gap = filing acceptance time minus call time, in minutes. Positive means the call came first.
  - If the call time is US Eastern: the call came first in 2 of 47. Median gap -180, quartiles -1008, -180, -59, range -2989 to +985. 44 of 47 are within 24 hours and 27 of 47 within 6 hours. The two call-first cases are FTV 2016-08-02 (a `00:00:00` placeholder) and DHI 2020-01-27 08:30 (filing 263 minutes later).
  - If the call time is UTC: the call came first in 26 of 47, median +87. That would mean most companies filed their 8-K after the call, which is implausible for 8:30 and 17:00 call times.
- Reading: the Eastern reading fits the data and the UTC reading does not look plausible, but the time zone is a hypothesis. It is not stated by the source. Under the Eastern reading the 8-K usually precedes the call, so the T0 cutoff (earlier of the two times, C-17) would usually be the 8-K time.
- Three of the 47 are more than 24 hours apart (ICE 2017-11-04, GOOG 2017-10-27, RTX 2018-04-26). Whether those are wrong matches or true date errors was not checked.

### Spike A2: which clock does the call time use (added the same day, rules in the spike plan)

Results, measured:

- Business-hours test over all 33,166 non-midnight rows: 96.1% of the stamped times fall between 08:00 and 17:30. If the stamps were UTC (or London winter time) and were read as US Eastern, only 31.5% would. The most common stamps are 17:00, 08:30, 10:00, 09:00, 11:00, 08:00, 16:30: the usual US call times.
- Summer against winter medians, 400-event sample (377 matched, seed 2028): H1 Eastern with daylight saving, difference 24 minutes; H2 Eastern standard time all year, 36; H3 London, 12; H4 UTC, 42. By the written rule H3 and H4 fail the business-hours condition, and H1 and H2 are within 20 minutes of each other, so this test alone was inconclusive.
- After-close anchor test (the follow-up written before it ran): 2,749 events whose 8-K was accepted 16:00 to 16:30 Eastern on the call date and whose call is stamped 16:30 or 17:00. Median gap (filing minus call) was -35 minutes in summer (1,674 events) and -35 in winter (698 events) when the stamp is read as Eastern with daylight saving: a difference of 0 minutes. When the stamp is read as Eastern standard time all year the summer median is -95 and the winter -35: a difference of 60 minutes, the daylight-saving shift. The written rule (smaller difference below 20 and the other above 40) selects H1.
- Reading: the call stamps are US Eastern local clock time with daylight saving. The after-close filing comes about 35 minutes before the call, which is consistent with `acceptanceDateTime` being UTC as assumed.
- Limits: the anchor test covers calls stamped 16:30 and 17:00 for 216 companies. Calls for companies in other time zones were not separately tested, and the 0.6% of rows stamped `00:00:00` have no usable time. The result describes the clock of the stamps. It does not prove what the data vendor intended for every row.
- Scripts and results: `wave-0.1-scripts/spikeA3.py.txt`, `spikeA4.py.txt`, `spikeA3_results.json`, `spikeA4_results.json`.

### Spike B: EPS depth and bulk files (LB-02, LB-03, IG-09)

- Quarters of diluted EPS ending on or before 2014-09-30 (contiguous run, including derived fourth quarters): AAPL 24, MSFT 29, JPM 23, KO 23, IBM 23, PFE 23, F 23, XLNX 22, ATVI 23, XOM 0. Plan rule (at least 10 quarters for at least 8 of 10 companies): met, 9 of 10.
- Earliest quarter end among the nine: 2007-09-30 (MSFT) to 2009-06-27 (XLNX).
- Fourth-quarter EPS: no direct fact exists, it is derived from the full year and three quarters (LB-03). Derived counts per company ranged from 1 to 17.
- First-filed against restated: each fact carries its `filed` date, so the first-filed value can be picked. Between 0 and 25 periods per company have a different value in a later filing (AAPL 25, MSFT 10, IBM 0). LB-04 (first-filed) is workable.
- **Finding for IM-03 and C-19 (the CIK is the company identifier):** the current SEC ticker file maps XOM to CIK 2115436, "ExxonMobil Holdings Corp", whose diluted EPS history starts 2025-06-30. The history from 2007 sits under CIK 34088, "Exxon Mobil Corporation", whose current ticker list is empty. So "match current tickers through the SEC file" (C-19) gives the wrong CIK for a company that moved to a new holding company. The cause was not investigated beyond these two entries.
- Bulk files (IG-09): both exist. `companyfacts.zip` is 1,428,910,853 bytes, last modified Sat 21 Nov 2026 05:08:08 GMT. `submissions.zip` is 1,577,451,757 bytes, last modified Sat 21 Nov 2026 05:15:30 GMT. Server date at the check was Mon 23 Nov 2026 14:00 GMT. This is one observation. Nightly refresh needs a second observation on another day, so IG-09's question stays open.

### Spike C: consensus source (SR-10), yfinance only

- yfinance returned, for all 5 tickers, for the current quarter: mean (`avg`), `low`, `high`, `numberOfAnalysts`, `yearAgoEps`, growth, currency and a `methodology` field. No standard deviation. Current values only.
- The `methodology` field differs by ticker: AAPL `gaap`, and MSFT, JPM, KO, F `normalized`. For the label this matters, because CE-03 requires the estimate and the actual to be on the same EPS basis.
- The plan's rule (mean and analyst count for at least 4 of 5 tickers): met, 5 of 5, for yfinance.
- Finnhub and FMP: not run. Both need a free key that John must create. BLOCKED.
- Yahoo's terms of use for this data were not read in this step. The data document records them as personal-use terms. That is not confirmed here.

### Spike D: transcript source (D-18), partial

- Card wording, quoted: front matter `license: mit`, and the section "License & Limitations" says "Licensed under MIT. For research and educational use only." The card names no transcript provider and no origin of the text. The field `company_id` is described as "Capital IQ Company identifier". These match the research note in D-18.
- The set has 685 symbols. 92 of them are not in the current SEC ticker file, and 76 of those have their last transcript before 2025 (examples: XLNX last 2020, TIF 2019, ETFC 2020, JWN 2021, PXD 2023). Symbols that are not in the current file include renamed tickers as well as removed companies, so this is not yet a count of removed companies. The set therefore does contain companies that are no longer listed.
- 1 row has empty text (also in 2015 to 2024).
- Removed-company check, done with the membership file `fja05680/sp500` as a candidate source (D-32 is still open; commit `a2430f2af0c79ddf0748e91de11bdeb1616ab5a7`, file SHA-256 `b2f4fe2f2e4dce8eaf0eb4fbd3946a32a20c1ddfe69687dfca3b6b59a0b71f9f`, MIT). The file holds 1,209 tickers. 230 of them have a last stint in the index that ended between 2015 and 2024. 20 of those were sampled with seed 2029 (`wave-0.1-scripts/spikeD2.py.txt`):
  - 12 have transcripts in the set: CMA, FL, HFC, HOG, HP, LM, LUMN, MUR, SE, SLG, UNM, XRAY.
  - 8 have no transcript at all: CA, CHK, ESV, LB, MON, SWN, TE, WFM.
  - Across all 230 removed tickers, 126 (55%) appear in the set. So coverage of removed companies is partial, a survivorship gap for TX-07 to report. A missing ticker can also be a ticker change, because the file is keyed by ticker.
  - The membership file has no company identifier. A reused or changed ticker cannot be told apart from the file alone (for example SE appears in the set from 2007 to 2018, which fits the old holder of that ticker, not the company that holds it now). This bears on IM-03.
  - The set holds a company's whole history, not only its index years (LUMN has 73 transcripts from 2006 but only 10 inside its 2020 to 2023 stint).
- Not done: Alpha Vantage, which needs a free key from John.

### Spike E: FinBERT scoring speed (FE-09), measured

- Checkpoint: `ProsusAI/finbert`, **as an example only. It is not the chosen checkpoint** (D-35 is open). Labels: positive, negative, neutral.
- Environment: a throwaway `python:3.12.16-slim` container, `torch 2.15.0+cpu`, `transformers 5.23.0` (the versions in `requirements-pending.txt`), no project file changed. Hardware as seen from Docker and WSL: 6 CPUs and about 10 GB of memory; `lscpu` names the processor as Intel Core Ultra 7 256V. The model loaded in 54.9 s including the download.
- Data: 1,000 real sentences (seed 2030) from 200 random transcripts of 2015 to 2024, split with a simple regular expression because spaCy is not installed here. Mean 19.2 words, longest 115. Truncation at 512 tokens.
- Result, one timed pass per setting after one warm-up pass: batch 16 in input order 17.4 sentences a second; batch 32 in input order 14.7; batch 32 sorted by length 28.3.
- Size of the corpus: 100 randomly sampled transcripts averaged 469 sentences (median 461, range 162 to 823) by the same simple split.
- Projection, for about 4,000 transcripts (100 companies, 40 quarters, C-35), 1.88 million sentences: 18.4 hours at 28.3 a second, 29.9 hours at 17.4, 35.4 hours at 14.7. For all 20,194 transcripts of 2015 to 2024 in the set (9.5 million sentences): about 93 to 151 hours. The plan's report line (48 hours for 100 companies) is not exceeded.
- Limits: one pass per setting, so run-to-run variation is unknown. The sentence count comes from a regular expression, not spaCy, and the project excludes operator and safe-harbour text (FE-02), so the real count differs. Docker saw 6 of the machine's cores. A different checkpoint can change the speed.
- Scripts: `wave-0.1-scripts/finbert_prep.py.txt`, `finbert_speed.py.txt`.

## Not verified

- Step 0.1.1 baseline (see wave-0.1-baseline.md): BLOCKED.
- Spike A: the call-time time zone, and the three events more than 24 hours apart.
- Spike B: whether the bulk files are refreshed nightly (needs a second day); the cause of the XOM change.
- Spike C: Finnhub, FMP, and Yahoo's terms.
- Spike D: Alpha Vantage, and whether the 8 companies with no transcript are ticker changes or true gaps.
- Spike E: the chosen checkpoint (D-35), run-to-run variation, and speed with spaCy sentence counts.
- Step 0.1.10 (decision session): not started. Steps 0.1.8 and 0.1.9 are in wave-0.1-register-and-adr.md.

## Drift found

- DR-06 (new): C-19 says tickers are matched to the CIK through the SEC ticker file. For XOM the file gives a CIK with no earlier history. Not a code disagreement, but the closed decision C-19 does not cover successor entities. Needs John.
- Spike A found that the `date` field has no stated time zone, while Product FR-22 and IG-15 need call times stored in UTC. Spike A2 measured the clock (US Eastern with daylight saving), and John asked that the best-fitting zone be used. Recorded as C-42.

## Assumptions

- Eastern time for the call time in the first Spike A reading was a hypothesis. Spike A2 tested it.
- A "quarter" in Spike B is a period of 80 to 100 days in the XBRL facts, and a full year is 350 to 380 days.
- The 50-event sample uses tickers in the current SEC file, so it excludes companies that no longer trade. It does not represent removed companies.

## Measured values

- Spikes: about one working session. No acceptance check changed from NOT TESTED because of spikes alone.
- Download: 1,824,805,388 bytes in about 2 minutes.
