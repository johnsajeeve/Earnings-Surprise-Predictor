# Data card: dataset version wave-1.8-2026-11-26

## Coverage
- Events: 3183 (2565 usable as labelled rows)
- Companies: 93
- Announcement dates: 2013-01-16 to 2024-12-19
- Label route: time-series; EPS basis: gaap-diluted

## Sources and licences
- Actual diluted EPS and EPS history: SEC EDGAR XBRL company facts API (data.sec.gov). Licence: Public SEC data. Anyone can download it free. Fair access: 10 requests per second, declared User-Agent required. (status checked)
- 8-K Item 2.02 acceptance times: SEC EDGAR submissions API (data.sec.gov). Licence: Public SEC data. Anyone can download it free. Fair access: 10 requests per second, declared User-Agent required. (status checked)
- Revenue, gross profit, operating income: SEC EDGAR XBRL company facts API (data.sec.gov). Licence: Public SEC data. Anyone can download it free. Fair access: 10 requests per second, declared User-Agent required. (status checked)
- Historical earnings call transcripts 2005 to 2025: Hugging Face dataset kurry/sp500_earnings_transcripts, revision f3ded372da8d18dc6ad98955c4558e34b5fe6d45. Licence: MIT in the card metadata. The card also says For research and educational use only. It names no origin for the text. (status checked)
- Forward consensus snapshots (current values only): yfinance 1.8.0, reading Yahoo Finance. Licence: yfinance is Apache-2.0. Its README says the data is intended for research and educational purposes and personal use only, and refers to Yahoo's terms of use, which were not read. (status checked)
- S&P 500 membership with dated additions and removals: GitHub fja05680/sp500, file sp500_ticker_start_end.csv, commit a2430f2af0c79ddf0748e91de11bdeb1616ab5a7. Licence: MIT License (GitHub licence API and the LICENSE file, Copyright 2019-2020 Farrell J. Aultman) (status checked)
- Daily prices, for momentum and outcome returns: yfinance 1.8.0, reading Yahoo Finance. Licence: yfinance is Apache-2.0. Its README says the data is intended for research and educational purposes and personal use only, and refers to Yahoo's terms of use, which were not read. (status checked)
- Past quarterly actual, estimate and surprise (last 4 quarters only): Finnhub free API key, endpoint /stock/earnings. Licence: Finnhub terms of service: all plans are for personal use only, and data or derived results may not be redistributed or shared with anyone without Finnhub's written approval. (status checked)
- Ticker to CIK map and company name to CIK lookup: SEC EDGAR files company_tickers.json and Archives/edgar/cik-lookup-data.txt. Licence: Public SEC data. Anyone can download it free. Fair access: 10 requests per second, declared User-Agent required. (status checked)
- Names and reasons for companies added to or removed from the S&P 500: Wikipedia page Historical components of the S&P 500 (MediaWiki API, action=parse). Licence: CC BY-SA 4.0 (Wikipedia text licence). Reuse needs attribution and share-alike. (status checked)

## Transformations
- Transcript text: cleaning rules version 1 (characters and spaces only); raw text kept apart.
- Sections: prepared remarks and Q&A split by the boundary rule of decision C-48.
- EPS: diluted EPS from XBRL; fourth quarter derived as the year minus nine months and flagged.
- Label: time-series SUE (Data LB-01) from first-filed history; sample standard deviation.
- Split basis: the price source's dated share-split ratios for companies with prices, otherwise the SEC split-ratio tag.
- Prices: raw closes rebuilt from the yfinance close and its split list; dated factors apart.

## Known gaps
- 143 events: no quarterly EPS stored for the company (DR-26)
- 249 events: the announced quarter is not in the stored EPS
- 174 events: fewer than 6 prior seasonal differences
- Transcript coverage 2015 to 2024: 86.9% against 90% (TX-04); results cover the covered events
- 17 of 100 companies have no price history (mostly removed companies); their price features are unavailable
- 24 labels built on a wrongly scaled EPS value are excluded from training (DR-27)
- Second-source check of closing prices not run: no second price source key yet (PX-01)

## Sign-off
- Not signed off: no reviewer who did not build the dataset has been named (Data GS-01, decision D-09).
