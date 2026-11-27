# Bug review of the implementation so far, 26 November 2026

Asked by John. Done by Claude, so it is not an independent audit. Method: invariant queries on the real database, comparison of one result with an outside source (yfinance's dated split list), and a read of the label, event, financials, consensus, task, limiter, raw store, schedule and release-parsing modules. Not re-read line by line in this review: membership, universe, company matching (they had an independent audit on 24 November), the API skeleton, the database bootstrap, and the transcript loader beyond the parts named below.

## Defects found and fixed

| # | Defect | Effect on real data | Fix |
|---|---|---|---|
| 1 | Share splits were inferred from ratios between filings. The approved Wave 1.6 brief said factors come from the SEC data's own share-basis fields, or LB-05 stays blocked. Measured against yfinance's split list: 12 found, 22 missed (many of those are spin-off price adjustments, not share splits), 11 false: the same split applied twice (Copart, Fastenal, CSX), a scale error read as a million-to-one split, restatements read as splits | Part of the 144 changed labels | Factors now come from the SEC tag StockholdersEquityNoteStockSplitConversionRatio1, dated, known before D, applied once |
| 2 | When the announced quarter was missing from the data, the previous quarter was used, so an event got an older quarter's surprise as its label | 7 quarters had two events; some labels were for the wrong quarter | The announced quarter must not be more than 10 days old in filings, and must have ended at most 100 days before D (longest real case: 77) |
| 3 | The announcement date was the SEC filing date. A filing accepted after 17:30 is dated the next business day | 159 events had the wrong date, and history filed on the day itself was read as earlier | The New York day of the acceptance time |
| 4 | A consensus snapshot captured on the announcement day before the release was usable. FR-14 says nothing captured on or after the date. My test expected the wrong behaviour | None yet (snapshots start in November 2026) | Cut at the start of the announcement day; test corrected |
| 5 | The coverage gate counted 2013 and 2014. TX-04 defines 2015 to 2024. "Left the index" included companies that left before 2015 | Reported 85.3%; the correct figure is 86.9% (still below 90%) | Window and group corrected |
| 6 | "One trading day" counted exchange holidays | Late-call count | The NYSE calendar is used |
| 7 | A later filing with a shifted start date could replace a first-filed cumulative figure used to derive a quarter (same family as DR-30) | Not separately measured; included in the changed labels | The first filing is kept |
| 8 | The scale error reaches more labels than the two giant ones I reported: 24 labels use an inflated value | DR-27 understated | All 24 are quarantined and not changed |
| 9 | While fixing 8, my line edit duplicated a loop (24 flags counted 576 times). The test had one flagged event and could not see it | Wrong count for one run | Fixed; the test now uses two events |

Also found and recorded, not a code fault: 5 events have the quarter's EPS filed a few days before the earnings release. They are now excluded from training with that reason.

Tests were written first for defects 1 to 7: 11 new tests failed before the fixes and pass after. The earlier tests passed because their data was clean synthetic series.

## Effect on the stored events (same transcripts, rebuilt)

| | Before | After |
|---|---|---|
| Labelled events | 2,619 | 2,617 |
| Labels whose value changed | | 144, of which 62 by more than 0.5 and 19 changed sign (measured after the first round of fixes, before the 100-day window) |
| Excluded for review | 24 | 32 (27 late calls, 5 EPS before release) |
| Two events on one quarter | 7 | 0 |
| Quarantine | 26 | 32 flagged, 24 scale error, 1 above one million |
| Usable and not quarantined | not measured | 2,565 (1,518 in 2015 to 2021) |
| Coverage 2015 to 2024 | reported 85.3% | 86.9% (still in the index 90.6%, left 58.6%) |
| Press release sample of 200 | 83 agree, 22 differ or other column, 95 unread | 90 agree, 19 differ or other column, 91 unread |

Two builds give the same events hash (DV-08). Full tests 214 passed, CI-style 193 passed, 0 failed; ruff, format and mypy clean.

## What is still wrong or unproven

- **LB-05 is not met for every company.** The SEC tag covers 17 of the 18 plain share splits that yfinance lists for companies with prices (Henry Schein 2017 is missing). Reverse splits are not read. A company without the tag is not adjusted, so its labels for about three years after a split can be false. The dated factors from the price source (Wave 1.8) are needed (DR-32).
- Some tag dates are rough (Brown & Brown reports 31 December 2017 for a March 2018 split).
- The 100-day window and 10-day rule are my values (D-47 p).
- The 243 events with no quarter in the window and 143 with no EPS at all are not explained company by company.
- No fresh-agent audit of Waves 1.5 to 1.7 has been run.
