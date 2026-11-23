# Universe fixtures: origin

All files are REAL data, retrieved on 23 November 2026 by the project's own clients and trimmed to what the tests need. None is synthetic.

| File | Origin | Trimmed to |
|---|---|---|
| `sp500_ticker_start_end_full.csv` | `fja05680/sp500` file `sp500_ticker_start_end.csv` (MIT), commit a2430f2af0c79ddf0748e91de11bdeb1616ab5a7 | not trimmed (28 KB) |
| `membership_sample.csv` | the same file | rows of 24 tickers used by the rename tests |
| `sec_tickers_sample.json` | SEC `company_tickers.json` | 18 entries, including `BBT`, which the SEC lists for an unrelated company |
| `cik_lookup_sample.txt` | SEC `Archives/edgar/cik-lookup-data.txt` | the lines of the CIKs above |
| `wikipedia_history_sample.json` | Wikipedia, Historical components of the S&P 500 (CC BY-SA 4.0), MediaWiki API response | the header rows and the original HTML rows that mention those tickers; attribution: Wikipedia contributors |
