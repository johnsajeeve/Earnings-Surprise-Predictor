# Wave 1.6 task brief: events and the time-series SUE (25 November 2026)

Written for John before any build work (drift control 2). Nothing in this wave is built yet.

## Requirements and acceptance checks served

- Data: LB-01-AC1 (hand-calculated SUE to four decimals), LB-02-AC1 (exclusion count per year, zero variance unavailable), LB-04-AC1 (planted later restatement, original value used), LB-05-AC1 (split inside the window gives the unsplit SUE), CE-05-AC1 (label_route stored, mixing fails).
- Product: FR-02-AC1 and AC2 (three date fields non-null or event incomplete; late transcript flagged and excluded), FR-14-AC1 and AC2 (snapshot linked to event; snapshots on or after the announcement excluded).
- Ingestion: IG-20-AC1 (date gate in the preparation stages), IG-22-AC1 (coverage report matches a hand count on 5 companies), IG-19 (the label stage refuses validation and test years without a freeze record, IG-19-AC2).
- Database: DB-06-AC1 (out-of-range probability fails), DB-15-AC1 (size report).
- Thresholds: TH-11, TH-15.
- Moved out by the plan: LB-03 (Wave 1.7), class labels and cut-offs (Wave 2.5, LB-06, VL-06).

## Files to change (proposed)

- New migration 0008: `earnings_event` table (columns of Product Section 11: event_id, company_id, fiscal_period, transcript_date, information_date, announcement_date, announcement_time_utc, eps_basis, label_route, sue, plus an incomplete flag and status).
- New `src/earnings/events.py` (build events from the linked transcript, release and EPS history; SUE; exclusions; coverage report) and `src/earnings/label.py` (the formula, split adjustment, first-filed rule, route check).
- Link of `estimate_snapshot.event_id` to events (FR-14), reading only snapshots captured before the announcement.
- Tests: `tests/test_events.py`, `tests/test_label.py`, fixture company with a hand-calculated SUE, planted restatement, planted split, zero-variance series.
- Evidence file `audits/evidence/wave-1.6.md`, ledger, logbook, drift register.

## Open decisions the requirements cite

None of the listed pending values (`audits/pending_values.md`) blocks this wave. Needs John (can build on my proposal, flagged D-47 style if not approved):
1. **Event table columns.** Section 11 lists the columns; I add `incomplete`, `status`, the release accession and `exclusion_reason`. Approve, or name different ones.
2. **What one event is.** Proposal: one event per kept transcript linked to an 8-K Item 2.02 release (3,183 now), fiscal period taken from the EPS filing that the release reports, `information_date` = filing date of the latest EPS used (FR-02, LB-04). Events with no transcript are not events in December scope (TX-04 is Wave 1.7).
3. **Split factors.** LB-05 needs dated split factors, which come from the price tables in Wave 1.8 (PX-01) that you have not yet approved. Proposal: build LB-05 with factors inferred from the EPS facts' own share-basis fields in the SEC data where present; otherwise LB-05 stays BLOCKED until the price tables are approved. I will not invent factors.

## Out of scope

Class labels and cut-offs (Wave 2.5), press-release comparison LB-03 and the data gates (Wave 1.7), prices (Wave 1.8), consensus-route events (the prospective set), sector scoring (OFF, C-29), any features.

## Test plan and risks

Hand calculation on fixtures, planted restatement and split, zero variance, a test that two routes in one set fail, a planted future record that fails the gate, mutation checks on the formula (window size 8, minimum 6, first-filed rule). Risk: share-basis handling (Apple 7-for-1 seen in Wave 1.4); 79 of 100 companies have the 10 quarters for early events, so exclusions will be reported per year, not hidden.

## Leftovers carried from Wave 1.5 (checked 25 November)

IG-19 stage order (the full check closes with this wave and 1.7), NFR-03 (waits for D-45), TX-05-AC2 (DV-03, Wave 1.7), IG-10/IG-12 Alpha Vantage client (deferred, C-45), TX-03/IG-18/TH-02 (John's 50 labels), independent audit of Wave 1.5 (not yet run).
