# Independent audit of commit c5a9801 (Waves 0.1 to 1.8), 26 November 2026

A fresh agent that had not built the project audited a separate clone, in its own Docker project, with read-only access to the real database. Its overall verdict was **FAIL**: "do not use `earnings_event.sue` for training yet". The summary below is its findings; the last two columns are what was done afterwards by Claude. **The fixes have not been audited by a fresh agent.**

| # | Severity | Finding | Checked by Claude | State |
|---|---|---|---|---|
| 1 | Critical | A later direct fact erased the value derivable earlier, and the announced quarter could come from a filing long after D (LB-04) | Confirmed (CSX Q4 2020) | Fixed: both versions kept; the announced quarter must be first filed within 100 days after D |
| 2 | Critical | Derived quarters subtracted pre-split from post-split figures (Copart stored -0.56 for 0.36) | Confirmed | Fixed |
| 3 | Critical | The parser read only the first XBRL unit: 11 companies (PepsiCo, FedEx, Danaher and others) had every event unlabelled. DR-19 and DR-26 wrongly blamed the SEC data | Confirmed, same 11 companies | Fixed; a missing unit now raises |
| 4 | High | Calls filed under a company's current ticker before a rename were dropped silently | Confirmed by the reload (+246 transcripts) | Fixed |
| 5 | High | A shifted period end replaced the first-filed value | Confirmed by its test case | Fixed |
| 6 | High | The T0 cutoff was never applied | Confirmed in code | Fixed for snapshots and the price-window session; no feature uses it yet |
| 7 | High | A reverse split mixed with a spin-off was ignored (Hilton) | Confirmed in code | Labels whose window holds such a ratio now have no label (11 events). No factor was invented |
| 8 | High | Several checks could not fail; mutations survived | Accepted | Planted-fault tests added; the price-window check now compares reads with the stored prices. The mutations were not rerun |
| 9 | High | Tests claimed checks they did not exercise; stale placeholders | Accepted | 18 markers lowered from a check to the requirement; 64 stale placeholders removed |
| 10 | Medium | No call type, no EPS filing on events, no last trading date | Confirmed | Call type and EPS filing added (migration 0011). Last trading date still missing (IM-02 stays failed) |
| 11 | Medium | Unapproved values; the D-47 text had been deleted | Confirmed | Text restored (C-59). Values listed as open decision D-48 |
| 12 | Medium | A reused ticker joins two companies to old membership spells (Ameriprise 1996-99, Hilton 1996-2007) | Not checked | Open (DR-36). No event from 2013 on is affected |
| 13 | Medium | Traceability file stale; no reviewer notes; old payloads without a version; capture list missing companies | Accepted | 7 companies added to the capture list (16 without a price series left out). The rest is open |
| 14 | Low | Unused guards; early market closes ignored; database start-up race | Accepted | Health check now waits for TCP; survivorship reads the latest factors. Early closes open |

## Real data before and after the fixes

| | At the audit (c5a9801) | After |
|---|---|---|
| Transcripts kept | 3,183 | 3,431 |
| Events with a label | 2,617 | 3,196 |
| Usable labelled events (included) | 2,565 | 3,130 |
| of which 2015 to 2021 | 1,518 | 1,836 |
| Transcript coverage 2015 to 2024 (target 90%) | 86.9% | 89.0%, still not met |
| Press release sample of 200: agree | 82 | 94 (88 unread) |
| Fourth-quarter sample of 20: agree | 8 | 9 |

Two builds give the same events hash.

## Outside check of the labels

The auditor's own recomputation (written without the project's label functions) was rerun on the new data. It agrees with 3,132 labels and differs on 13. All 13 were traced: 10 (Copart, Fastenal) are the split fault the auditor said its own script shares, and the new values equal the ones it gave as corrected; 2 (ICE) are the same fault in its script; 1 (State Street) arises because its script has no value for the fourth quarter of 2012. It produces no label for 51 events the project labels (48 PepsiCo, whose 16 and 17 week quarters it cannot handle, and 3 State Street), so **those 51 have no outside check**. The project withholds 26 labels the script gives, by its two new rules.

## Defects found while fixing

PepsiCo needed two more fixes: a 16-week fourth quarter (111 days) was not treated as a quarter, and a 119-day gap in a 53-week year broke the run of quarters.

## Auditor's own limits

It did not check the tests-only CI variant, gitleaks, pip-audit, outside source documents, the hand samples, a second price source, a full split audit, or much of the early-wave code. Its count of wrong labels was a lower bound.

## Verification of the fixes

- Full repository pytest: 255 passed, 471 skipped, 3 expected failures, 0 failed. CI-style: 233 passed, 0 failed. ruff, format and mypy pass.
- Planted faults in the new fixes: 14 of 14 caught (one survived first, a call with no recorded time; a test was added).
- Acceptance checks of the built waves without a real test: 36. This is higher than the 26 reported earlier the same day, because 18 markers that overclaimed were lowered to the requirement. All 597 checks have a test of some kind, every test names a requirement, and every source file is declared by a test. 48 IDs have no acceptance check (needs, goals, non-goals, stretch items, gates, conflicts).
