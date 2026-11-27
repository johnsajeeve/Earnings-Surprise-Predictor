# Wave 1.8 task brief: prices (26 November 2026)

John approved the price tables and the data approach (decisions C-49, C-50) and said to start Wave 1.8 after the approvals research and the bug review.

## Requirements and acceptance checks served

- PX-01-AC1 (adjustments stored apart from the raw price with dated factors; 20 announcement-day closes against a second source: **BLOCKED** until the Tiingo key, C-50), PX-02-AC1 (momentum window only before the announcement session, outcome window only from it; a planted future price is excluded), PX-03-AC1 (a series holding both adjusted and unadjusted prices fails).
- VL-05 (survivorship: removed names in every year, universe return against `^SP500TR` and `RSP`); TH-06 is proposed from this first run and set by John before the validation set is read.
- DV-05 price-window part; LB-05 with the price source's dated split factors; DB-09 (as-of reads); DR-14 (`source_version` on `raw_payload`, C-51).

## Files

Migration 0010 (`price_daily`, `adjustment_factor`, `raw_payload.source_version`), `clients/yahoo.py`, `prices.py` (load, raw reconstruction, series with a type, as-of reads, survivorship comparison), `events.py` (split factors), tests, evidence.

## Open decisions and pending values

TH-06 (set after the first run). The second price source (Tiingo key). Nothing else blocks.

## Out of scope

Momentum and other features (Wave 2.3), returns used by a model, buying data, any second price source without a key.

## Test plan and risks

A real Apple excerpt around the June 2014 7-for-1 split checks that the rebuilt raw close is about 645; planted future prices; a mixed series; rerun adds nothing. Risks: a ticker reused by another company (a loaded series must cover the company's events or it is rejected); yfinance also adjusts its close for spin-off ratios, so every ratio in its split list is needed to rebuild the raw price, while only share splits apply to EPS.
