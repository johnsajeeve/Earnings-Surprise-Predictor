# Wave 1.7 task brief: dataset validation and sign-off (25 November 2026)

Written for John before any build work (drift control 2). Nothing in this wave is built yet.

## Requirements and acceptance checks served

- Validation of tables and events: DV-01 (quarantine count per run), DV-02 and TH-15 (zero nulls in the three dates), DV-03 (event unique on company, quarter, announcement date), DV-04 (extreme values flagged for a reviewer note), DV-05 (date order), DV-06 and FD-04 (fiscal period to calendar quarter, five non-calendar companies), DV-07 (UTC and trading day, after-close release to the next session), DV-08 (rerun gives identical table hashes), DB-14 (indexes and a query plan check).
- Sources agree: AE-02 and TH-03 (press release EPS against XBRL on 200 events, 98% within 0.5%, yfinance as a cross-check), LB-03 and TH-12 (derived fourth quarter against press release on 20 companies), AE-03, CE-03, VL-07 (EPS basis, 50 events), CE-01 to CE-03, VL-01 (planted future estimate excluded).
- Bias and coverage: TX-04 and TH-01 (90% of target events have a transcript), TX-07 (coverage by year, survivor status), VL-05 and TH-06 (survivorship), SRS-14 (sector scoring off, record it).
- Sign-off: VL-08 (canary of 20 releases), VL-09 and TH-08 (hand audit of 100 events, 2% at most), GS-01 (sign-off by a reviewer who did not build it), GS-02 (data card), GATE-1, GATE-2, GATE-3, GATE-5.
- Carried from Waves 1.5 and 1.6: TX-05-AC2 (DV-03), TX-03 and IG-18 (your 50 labels), AE-01, TH-15, IG-19 (stage order).

## Files to change (proposed)

- New `src/earnings/validation.py` (checks DV-01 to DV-08 over the stored tables, quarantine table, table hashes), `src/earnings/pressrelease.py` (find the EX-99 press release of an 8-K Item 2.02, parse diluted EPS; only the sec.gov host gets the contact string), `src/earnings/canary.py` if the canary list is committed as data.
- Migration 0009: `quarantine` table and indexes of DB-14; `dataset_version` and `signoff` tables if John approves (GS-01, GS-02, CE-05 route record).
- Data card and gate report as generated files under `audits/evidence/wave-1.7/`; tests in `tests/test_validation.py`, `tests/test_pressrelease.py`.
- Evidence `audits/evidence/wave-1.7.md`, ledger, logbook, drift register.

## Open decisions and pending values the requirements cite

1. **D-26 sample sizes.** VL-09 asks for 100 hand-audited events and AE-02 for 200. These are person work for VL-09. Halve them, or keep? Without an answer I build for the full sizes and mark the person part NEEDS PERSON.
2. **D-09 the independent reviewer** for GS-01. A named person is needed. Until then GS-01 is BLOCKED and the dataset is not signed off.
3. **Trading calendar (DV-07).** There is no NYSE holiday data in the project. Options: (a) a committed holiday list from the NYSE published schedule, 2012 to 2026, with its source named; (b) a new dependency (`exchange_calendars`), which needs your approval; (c) take trading days from the price table in Wave 1.8. My recommendation is (a).
4. **Wave order for VL-05 and TH-06.** The survivorship check needs prices and an independent index return, which come with Wave 1.8 and your price-table approval. Proposal: do VL-05, TH-06 and DV-05's price-window part after Wave 1.8, and mark them BLOCKED here, stated, not skipped. TH-06 is set from the first comparison run and recorded before the validation set is read (VL-05 text).
5. **Canary list (VL-08).** 20 widely reported releases with public EPS values. I can propose 20 company-quarters, but the "public record" check against press releases is only as good as the source; I would use the 8-K press releases themselves, so this overlaps with AE-02. You approve the list or give one.
6. **DV-04 extreme values.** The reviewer notes are person work, flagged rows listed for you.
7. **The five non-calendar companies (DV-06).** I propose them from the 100-company list by fiscal year end (for example Apple, Microsoft, Nike, FedEx, Oracle) and check them against their filings.

## Out of scope

Prices (Wave 1.8), class cut-offs (Wave 2.5), features, models, the sector features (off, C-29), any threshold change (C-37: a miss is stated, thresholds are not moved).

## Test plan and risks

Every gate gets a measured number in the evidence file, including a miss. Tests use real rows from the loaded data where possible and planted synthetic defects (label each). Known risk: EPS depth gaps (DR-26, 143 events have no EPS at all) will lower AE-02 and LB-03 samples; I report the covered sample, I do not substitute. The press-release parse may not yield EPS for every release (formats differ); unparsed ones are counted and listed. Mutation checks on the validators.

## Leftovers carried (checked 25 November)

TX-03, IG-18, TH-02: your 50 labels. D-45 run times (NFR-03, IG-05). D-47 (a) to (l). DR-23, DR-25, DR-26. Independent audit of Waves 1.5 and 1.6 not yet run.
