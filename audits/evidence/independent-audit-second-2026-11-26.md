# Second independent audit, commit 1479e7a, 26 November 2026

A second fresh agent, in its own clone with read-only database access, audited the fixes of the first audit with its own checking code. **Verdict: FAIL. "Do not use the event dataset for feature building or training yet."** The label arithmetic mostly holds and the stored tables are what the current code produces.

The table is the auditor's findings. "Checked by Claude" says what was verified independently of its report; **findings not marked as checked are the auditor's claims.**

| # | Severity | Finding | Checked by Claude | State |
|---|---|---|---|---|
| 1 | Critical, new | **Other companies' calls are attached to events.** The source files an acquired company's calls under the acquirer's ticker, and nothing checks who is speaking: Xilinx under AMD, Meritor under Cummins, Hill-Rom under Baxter, VEREIT under Realty Income, U.S. Concrete under Vulcan. At least 37 transcripts, 26 usable labelled events (20 in 2015 to 2021). My fallback match added 7 of the Xilinx calls; D-48 (h) was approved on my false statement that a wrong match could not link. Coverage would be about 88.1% | Yes: the opening lines of sampled calls name those other companies | **OPEN**. D-48 (h) goes back to John |
| 2 | High | The tag `EarningsPerShareBasicAndDiluted` is not read: 56 more events would have a label (48 in 2015 to 2021), and 4 stored labels use values that were not first filed | No | OPEN |
| 3 | High, new | The daily 8-K check stored newer filing lists and only the newest copy was read, so releases that rolled off would be lost at the next rebuild | Yes, by reading the code; the job had not run | **FIXED** (commit e0ad085), with a test |
| 4 | Medium | A later derivation can still hide an earlier one when start dates differ: 4 quarters, 13 events without a label | No | OPEN |
| 5 | Medium | 8 of 42 planted faults survive the whole suite | No | OPEN |
| 6 | Medium | Approval records go too far: C-53 closed D-11 and D-12, which had no recommendation; the D-34 phrase lists were approved under delegation although I had promised them to John first | No | OPEN, for John |
| 7 | Medium | Traceability: 17 of 480 requirements assessed | Known | OPEN |
| 8 | Low to medium | The SQL first-filed and as-of functions still group by exact dates (254 company-quarters). No feature code uses them yet | No | OPEN |
| 9 to 11 | Low | Checks that claim more than they show (VL-05-AC1, CE-01, AE-01 and the events hash); direct 16-week quarters dropped; one stub transcript | No | OPEN |

**Label recomputation by the auditor** (its own code, all 3,431 events, diluted tag only): 3,190 agree, 6 differ (all PepsiCo, a different but valid derivation), 13 labels it gives that the project does not (finding 4). This covers the 51 labels the first outside check could not. With the second EPS tag, 3,186 of 3,196 stored labels agree. It reused the project's date windows, so agreement does not test those values.

**Its own run of the suite:** 255 passed, 471 skipped, 3 expected failures. Secret scan (gitleaks): no leaks.

**Not checked by it:** outside source documents, the hand samples, a second price source, the raw transcript file, much of the early waves, and whether the scheduled jobs fire.

Disclosure by the auditor: its test containers first inherited the SEC contact string from the shell; it noticed within about a minute, before any job was due, and recreated them without it.
