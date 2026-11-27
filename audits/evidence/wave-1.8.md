# Wave 1.8: prices (PARTIAL, 26 November 2026)

Brief: `wave-1.8-task-brief.md`. Approvals: decisions C-49 (tables and Section 11), C-50 (missing prices), C-51 (data-quality recommendations), C-52 (DV-05 wording).

## Commands and results

| Check | Result |
|---|---|
| ruff format, ruff check, mypy | PASS (125 files, 49 source files) |
| Full repository pytest | PASS: 227 passed before the last test, 534 skipped, 3 expected failures, 0 failed; the last test passes with `tests/test_prices.py` (12 passed) |
| CI-style pytest (image rebuilt) | PASS: 206 passed, 0 failed, before the last test |
| Mutation checks on `prices.py` (10) | 10 of 10 caught. One survived first (the reused-ticker refusal at loading); a test was added |
| Migration 0010 on the project database | applied |

## Real data

- Load (`wave-1.8/price_load_report.json`): 83 of 100 companies, 302,718 daily raw closes, 8,411 factors. 17 unavailable: 15 the source has nothing for, and ANSS and WBD refused because the returned series covers none of their events (the ticker now returns a few 2026 rows). 2,947 of 3,183 events belong to a company with prices.
- Raw price rebuild: Apple 6 June 2014 rebuilt as 645.57 from the source's 23.056; Danaher 1 and 5 July 2016 rebuilt as 102.32 and 80.40. I know these as the traded prices; they are **not** a recorded second-source check.
- Against the source's own adjusted close, 964 of 970 company-years of total return agree within 0.2 points. The one large difference is Danaher 2016: the source lists the Fortive spin-off twice, as a price ratio and as a dividend, and its adjusted close counts both (73% for the year; counted once it is 11.3%). Fixed in the total-return calculation and recorded (DR-34).
- Price windows (DV-05): 2,947 events checked, 0 violations.
- Labels: the price source's dated share splits now drive LB-05 for priced companies. 69 more labels changed value (33 by more than 0.5, 8 changed sign). 2,617 labelled. 56 events excluded (the 24 scale-error labels are new here, C-51). Usable and included: 2,565, of which 1,518 in 2015 to 2021. Two builds give the same hash.
- Database: 761 MB.

## Survivorship (VL-05, first run; `wave-1.8/price_report.json`)

Equal-weighted yearly total return of the index members among the priced companies (50 to 78 a year), 2013 to 2024.

| Compared with | Mean yearly gap, universe minus index | Mean size of the gap | Years above the index | Range |
|---|---|---|---|---|
| `^SP500TR` (value weighted) | +0.7 points | 4.5 | 7 of 12 | -7.8 to +8.5 |
| `RSP` (equal weighted) | +3.3 points | 4.7 | 8 of 12 | -4.4 to +8.9 |

Of the companies later removed from the index that were members in a given year, only a minority have prices (for example 4 of 14 in 2013, 6 of 15 in 2016, 3 of 8 in 2021).

**Reading:** against the closer benchmark, the priced universe did better by about 3 points a year, with the sign changing in 4 of 12 years. That is the direction survivorship bias would give, and most removed companies are missing, so it is the likely cause, but this run cannot separate it from the effect of a 100-company sample (50 to 78 names a year). VL-05 asks for a persistent gap above TH-06 to be investigated. TH-06 is **not set**: John sets it from this run before the validation set is read.

## Result per requirement

| ID | Status | Basis |
|---|---|---|
| PX-01 | PARTIAL | Factors stored apart with dates (AC1 first half). The 20-close second-source check is BLOCKED: no second source key (C-50) |
| PX-02 | PASS locally | Planted future price excluded; windows checked on 2,947 events |
| PX-03 | PASS locally | Mixed series fails; only raw closes are stored |
| LB-05 | PARTIAL | Dated factors from the price source for 83 companies; the SEC tag for the other 17, which does not list every split |
| VL-05 | PARTIAL | First run done and recorded; removed companies mostly lack prices; investigation and TH-06 open |
| TH-06 | NEEDS PERSON | John |
| DV-05 | PASS locally | Reworded (C-52): 0 information-date violations, 8 calls before the filing listed, 0 price-window violations |
| DV-04 | PARTIAL | Value set (above 10), 34 flagged. Reviewer notes are still to be written |
| SR-04, DR-14 | PARTIAL | `source_version` stored for new price payloads; older payloads have none |
| GATE-4 | not passed | PX-01 second source open |

Data licence: yfinance data is for development and research only (source register). No price is committed except a nine-day Apple excerpt used by the tests, and it must not go into the demo bundle.

Not an independent audit.

## Correction, 26 November 2026, after the independent audit

The independent audit failed this wave as committed. Several results above are wrong or came from faulty parsing; see `independent-audit-2026-11-26.md` (DR-35) for the findings, the fixes and the corrected numbers. Where this file explains a gap by the SEC data, that explanation is withdrawn.
