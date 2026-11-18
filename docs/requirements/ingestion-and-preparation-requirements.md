# Ingestion and Preparation Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns how data gets into the system and becomes events ready for features: the Celery job design, schedules, source clients, rate limits, the universe, event building, announcement time, cleaning, segmentation and the order of the preparation stages. The data requirements say which sources are acceptable and what the data must satisfy (Data document). The pipeline document describes the steps (pipeline.md Steps 1 and 3). This document says how the jobs must behave.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a value the project leaves open says "pending D-45", and it is not final until John decides D-45 in the [decision log](../decision-log.md) (Project-Wide SS-02). Research on the internet informed the wording and is listed in Section 8. It is not a requirement by itself.

| Already defined elsewhere | Where |
|---|---|
| Sources, licences, free primary route | Data Section 4A, SR-01 to SR-11 |
| Transcript, EPS, consensus, membership, price and fundamentals checks | Data Section 7 |
| Label construction | Data LB-01 to LB-08 |
| Verification and validation tests | Data DV-01 to DV-08, VL-01 to VL-12 |
| Run records, retries and dead letter, idempotency, raw text | Product PL-01 to PL-06, FR-13, FR-14 |
| Segmentation and cleaned text | Product FR-15; Data TX-03 |
| Storage rules | Database DB-01 to DB-17 |
| Feature computation | Feature Engineering FE-01 to FE-31 |

## 2. Job framework

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| IG-01 | Must | Ingestion and preparation run as Celery tasks, one task per source and unit of work (a company, or an event). Every task is safe to run twice with the same input and leaves the same rows (writes follow Database DB-13). This is what allows a task to be acknowledged only after it finishes, so a crashed worker does not lose it. | Running the same task twice gives an identical table hash. Killing a worker mid-task and restarting gives the row count of a clean run. | Product FR-13, PL-02; Project-Wide SC-01, EQ-06; ADR 0001 |
| IG-02 | Must | A failed task retries up to three times with exponential backoff and random jitter, then is written to a dead-letter table with the task name, a hash of its arguments, the error class, the time and the attempt count. The table is the dead-letter queue, because Redis does not provide one. | An injected failure produces three retries and one dead-letter row. | Product PL-02; ADR 0001 (open point on the dead-letter queue) |
| IG-03 | Must | Every task writes a run record: job name, source, start, end, status and row counts (Product PL-01). A run that processed zero rows because of an error is not recorded as successful. | Each run produces a queryable row. A forced error gives status failed. | Product PL-01 |
| IG-04 | Should | The Redis redelivery timeout is set longer than the longest task, or long tasks are split into smaller ones, so a running task is not delivered a second time. | The longest task in the 100-company run finishes inside the timeout, and the setting is recorded. | Project-Wide EQ-06; Product FR-13 |

## 3. Schedules and source limits

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| IG-05 | Must | All scheduled jobs are defined in one configuration file. The initial jobs are: the daily consensus snapshot capture (Data SR-10), a daily check for new transcripts, a daily check for new 8-K Item 2.02 filings, and a daily run of the data gates. Backfill is started by hand, not on a schedule. Run times are pending D-45. | The schedule file lists each job with its time. A job missing from the file does not run. | Data SR-10; Product NFR-03, PL-01; pipeline.md Step 1 |
| IG-06 | Must | A scheduled job that did not run, or ran more than 3 consecutive days late, is reported, and events affected by a gap in the consensus capture are flagged. | Simulated 4-day gap is reported and the affected events carry the flag. | Data SR-10 |
| IG-07 | Must | Source limits are enforced in code, not by hope. The EDGAR client never exceeds 10 requests a second. The Alpha Vantage client never exceeds the free 25 requests a day and keeps a persistent counter that survives a restart. A task that would exceed a limit waits or is deferred to the next window, and is not counted as failed. | Test with a mocked clock shows no more than 10 EDGAR requests in any second and no more than 25 Alpha Vantage requests in a day. | Data Section 4A.1; Data SR-07; decision C-03 |
| IG-08 | Must | The EDGAR client refuses to send any request when `SEC_USER_AGENT` is unset or empty, and sends it as the request's user agent when set. The value is never logged or returned (decision C-10; Project-Wide SP-06). | With the variable unset, the client raises an error and sends nothing. | Decision C-10; Project-Wide SP-06 |
| IG-09 | Should | Backfill uses the SEC bulk files where they exist (`companyfacts` and `submissions`) instead of one request per company, to stay far below the request limit and finish faster. Whether the files are refreshed nightly, as pipeline.md states, is confirmed in the first spike. | Backfill of the 100-company subset uses the bulk files, and the request count is recorded. | pipeline.md Step 1; Product NFR-09; decision C-18 |

## 4. Source clients and raw data

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| IG-10 | Must | There is one client per source (EDGAR, Hugging Face, Alpha Vantage, yfinance). A client fetches and returns the raw payload with its metadata and stores it through Database DB-11. A client does not interpret the data. Parsing is a separate step that reads stored payloads, so a parsing fix never needs a new download. | Parsing runs from stored payloads with the network disabled. | pipeline.md Step 1; Data SR-04; Database DB-11 |
| IG-11 | Must | The Hugging Face transcript set is loaded as a dated snapshot with its revision recorded. Rows with empty text are rejected, counted and listed. | Load report shows the revision and the number of empty rows rejected. | Data Section 4A.1 (some records are empty); Data SR-04, TX-01 |
| IG-12 | Should | Every client has a recorded-response test, using short fixtures labelled as real or synthetic, so the parsers are tested without calling the source. | Tests pass with the network disabled. Fixtures state their origin. | Project-Wide SC-04; Explanation Agent AG-19 |

## 5. Universe, events and announcement time

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| IG-13 | Must | The universe is built from the membership source chosen under D-32, with a start and end date per membership spell and the SEC CIK as the identifier. Tickers are matched to CIKs through the SEC ticker file. A company whose ticker changed or was removed is matched by name, and each such match is written to a review list. | Ten known renames give one continuous history. Every name match appears in the review list. | Decision C-19; Data IM-01 to IM-03 |
| IG-14 | Must | Each transcript is linked to a company, fiscal quarter and announcement, giving one event on the key in Database DB-05. A transcript that cannot be linked is rejected with a reason. Duplicates follow Data TX-05. | Unlinked fixture is rejected with a reason. Duplicate fixture follows TX-05. | Data TX-01, TX-05, DV-03, DV-06; Product FR-02 |
| IG-15 | Must | For each event the announcement time is the acceptance time of the 8-K Item 2.02 filing, stored in UTC, with the call time stored beside it. The T0 cutoff is the earlier of the two times (decision C-17). Mapping to the trading day follows Data DV-07. | Fixture with a call before the filing and one after both give the earlier time as the cutoff. | Data AE-01, DV-07; decision C-17; pipeline.md Section 2.3 |
| IG-16 | Must | Before this step is built, the spike in pipeline.md Section 2.3 is run: for 50 events, compare the call time in the Hugging Face set with the 8-K acceptance time and report how often, and by how much, the call comes first. The result is written into Data Section 12. | Spike result is in Data Section 12. | pipeline.md Section 2.3; decision C-12 |

## 6. Cleaning, segmentation and stage order

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| IG-17 | Must | Cleaning only removes non-speech artefacts and normalises whitespace and quote characters. The list of cleaning rules is versioned, and the raw text is never changed. | Hash of raw text is identical before and after cleaning. Rule list has a version. | Product PL-06; Feature Engineering FE-03 |
| IG-18 | Must | The boundary between prepared remarks and Q&A is found by a written rule that uses speaker turns where the source provides them (the Hugging Face set has speaker turns but no section split). A call where no boundary is found is flagged "Segmentation failed" and its Q&A features are unavailable. The rule is pending D-45. | On 50 hand-labelled calls at least 95% of boundaries are correct. A call with no marker is flagged. | Product FR-15; Data TX-03, TX-06; pending D-45 |
| IG-19 | Must | The preparation stages run in this order, and each reads only the outputs of earlier stages: universe, events, EPS history, transcripts cleaned and segmented, sentences, label, gates. Each stage can be re-run alone and gives identical tables (Data DV-08). The label stage refuses to run for validation and test years until the threshold freeze record exists (Data LB-06, VL-06). | Re-running any stage leaves table hashes unchanged. The label stage run without a freeze record fails. | pipeline.md Step 3; Data DV-08, LB-06, GATE-4 |
| IG-20 | Must | The date gates (Data GATE-1 to GATE-5) and the planted-future tests (Data VL-01, VL-02) run as automated tests that fail the build. | A planted record dated after its cutoff makes the test fail. | pipeline.md Step 3; Product FR-22; Data VL-01, VL-02 |

## 7. Scope and reporting

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| IG-21 | Should | Ingestion takes its company list as a parameter. The December run uses the 100-company subset, about 20 of them removed from the index, and widening needs no code change. | The same job runs for 5 and for 100 companies from a list file. | Decision C-18; D-28 |
| IG-22 | Must | After each load a coverage report is produced: the share of universe events with a transcript by year, by sector and separately for companies that left the index, with every missing company and quarter listed. | Report exists after a run and matches a hand count on 5 companies. | Data TX-04, TX-07 |

## 8. Evidence read

No requirement above depends on an outside source. Read as background, mostly as summaries:
- SEC "Accessing EDGAR Data" page: current maximum 10 requests a second, and a declared user agent is asked for. Whether the bulk files are refreshed nightly was not confirmed by this search.
- Celery practitioner articles: tasks should be idempotent before late acknowledgement is used, and retries should use backoff and jitter with a limit. Official Celery documentation was not retrieved, and the scheduler and redelivery-timeout details are to be checked against it when the jobs are built.

Searches were run on 18 November 2026.
