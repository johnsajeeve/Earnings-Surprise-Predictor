# Universe fixtures: origin

All files are REAL data, retrieved on 23 November 2026 by the project's own clients and trimmed to what the tests need. None is synthetic.

| File | Origin | Trimmed to |
|---|---|---|
| `sp500_ticker_start_end_full.csv` | `fja05680/sp500` file `sp500_ticker_start_end.csv` (MIT), commit a2430f2af0c79ddf0748e91de11bdeb1616ab5a7 | not trimmed (28 KB) |
| `membership_sample.csv` | the same file | rows of 24 tickers used by the rename tests |
| `sec_tickers_sample.json` | SEC `company_tickers.json` | 18 entries, including `BBT`, which the SEC lists for an unrelated company |
| `cik_lookup_sample.txt` | SEC `Archives/edgar/cik-lookup-data.txt` | the lines of the CIKs above |
| `wikipedia_history_sample.json` | Wikipedia, Historical components of the S&P 500 (CC BY-SA 4.0), MediaWiki API response | the header rows and the original HTML rows that mention those tickers; attribution: Wikipedia contributors |

## Financial fixtures (Wave 1.4)

| File | Origin | Trimmed to |
|---|---|---|
| `aapl_companyfacts_2012_2015.json` | SEC company facts for Apple Inc. (CIK 0000320193), retrieved 23 November 2026 by the project's client | six tags (diluted EPS, three revenue tags, gross profit, operating income) and periods ending 2012-09-01 to 2015-12-31 |
| `aapl_submissions_8k_sample.json` | SEC submissions for Apple Inc., same day | 8 earnings-release 8-Ks (Item 2.02) since 2020 |
| `hf_transcript_excerpts.json` | Hugging Face `kurry/sp500_earnings_transcripts`, revision `f3ded372da8d18dc6ad98955c4558e34b5fe6d45`; REAL rows (Apple 2025-01-30 and 2025-05-01, Abbott 2020-07-15, Conagra 2024-12-19, DayForce 2022-02-10) | Texts cut to 400 characters, turns after the boundary cut; operator turns whole; the empty-text row is real |
| `aapl_8k_index.json` | SEC filing index of Apple 8-K 0000320193-25-000007, retrieved 25 November 2026 by the project's client | nothing |
| `aapl_press_release_table.html` | The same filing's exhibit 99.1, retrieved 25 November 2026 | the one table that holds the diluted EPS row |
| `aapl_split_ratio_tag.json` | SEC company facts for Apple Inc., stored payload of the project database, retrieved by the project client in November 2026 | only the tag StockholdersEquityNoteStockSplitConversionRatio1 |
