# Frontend Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns how the Streamlit dashboard is built and how it behaves: structure, calls to the API, job states, content rules, privacy and testing. What the screens contain is in Product Sections 3, 12 and 14 and the UI requirements (UI-01 to UI-05). The framework is Streamlit (decision C-16, ADR 0002). This document does not repeat them.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a value the project leaves open says "pending D-39", and it is not final until John decides D-39 in the [decision log](../decision-log.md) (Project-Wide SS-02). Ideas that do not trace to the project are not requirements. They are listed in decision D-41.

| Already defined elsewhere | Where |
|---|---|
| Journeys J1 to J4 and the screens | Product Sections 3 and 14 |
| Error messages | Product Section 12 |
| Ticker autocomplete, chart text alternative, citation status, sector view, keyboard use | Product UI-01 to UI-05 |
| Disclaimer, evidence base, as-of times, limitations notice | Product FR-08, FR-21, FR-22, FR-28 |
| Direction labelled "toward miss" or "toward beat" | Product FR-04 |
| Sector display states | Product SRS-11, SRS-12 |
| Colour contrast and accessibility check, narrow screens, time to first result | Product NFR-07, NFR-08, NFR-13 |
| Authentication on API calls | Product API-06 |
| Secrets from the environment | Project-Wide SP-06 |
| Plain-text rendering of explanation text | Explanation Agent AG-16 |
| Usability study and ethics approval | Project-Wide ET-01, ET-02; Product Section 15 |
| One frontend framework | Project-Wide SC-02 |

## 2. Structure and API use

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| UX-01 | Must | The dashboard is a client of the API only. It has no database connection and imports no model, feature or agent code. Everything it shows comes from an API response, so authentication and request logging (Product API-06, NFR-11) apply to it. | The dashboard's container has no database credentials. A search finds no database import. | Product API-06, NFR-11; pipeline.md Step 8; ADR 0002 |
| UX-02 | Must | All API calls go through one client module with a timeout, and it maps each failure to the matching Product Section 12 message. Raw exceptions and stack traces are never shown. Each error state in Section 12 (ER-01 to ER-13) has a test against a stubbed API. The timeout value is pending D-39. | One test per error state ER-01 to ER-13. | Product Section 12; pending D-39 |

## 3. Behaviour

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| UX-03 | Must | Explanation jobs (Product FR-19) show pending, complete and failed. The page checks status at a fixed interval until a limit, then tells the user to check again later. The user can leave and return, using the job id kept in the session. A failed job shows the stored reason. Interval and limit are pending D-39. | Stubbed job that completes after 6 seconds shows the three states. | Product FR-19, NFR-02; pending D-39 |

## 4. Content and honesty

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| UX-04 | Must | The explanation view shows, beside each claim: its label and reason (Product EX-02), the cited sentence copied from the database with the date of the call it came from (Explanation Agent AG-07), and the citation's verification status (Product UI-03). A partially verified explanation says so at the top. | UI test on complete and partially verified fixtures. | Product UI-03, EX-02, FR-05; Explanation Agent AG-07 |
| UX-05 | Must | Every entry in the API envelope's warnings array (Product API-04) is shown on the prediction card, for example "Limited history". Warnings are not collapsed or hidden. | Fixture with two warnings shows both. | Product API-04, FR-07 |
| UX-06 | Must | Predictions made before the release (T0) and after the call (T1) are labelled and never shown as one number. A T1 prediction says it uses the event's own transcript and is not a forecast. | Fixture with both shows two labelled cards. | Decision C-17; pipeline.md 2.3 |
| UX-07 | Must | The evaluation page shows the baseline table first, with every metric and its interval, and the full model's result has the same prominence whether it beats the baselines or not. A negative result is stated in plain words. | Fixture where the full model loses to the baseline shows the statement. | Product FR-06, TR-01; SSOT Section 2 (a negative result is valid) |

## 5. Privacy and licence

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| UX-08 | Should | Streamlit's usage statistics are switched off in configuration, and the dashboard loads no third-party scripts or trackers, so the statement that no end-user data is stored stays true. Whether the default is on in the installed version is to be checked, not assumed. | Configuration test. Page source lists no external script. | Market Section 6 (data protection); Project-Wide SP-05 |
| UX-09 | Must | The dashboard displays only the cited sentences, never a full transcript, until the licence question in decision D-18 is settled. Cited sentences stay within the quotation limit in the source register (Data SR-11). | A page test finds no transcript text beyond the cited sentences and none over the limit. | Data SR-03, SR-11; decision D-18 |

## 6. Testing and packaging

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| UX-10 | Should | The usability tasks for J1 and J2 are written before testing, with the success rule (completes without help) and the counter-metric (time to complete J2). No participant is recruited before ethics approval. | Task script is on file and dated before the first session. | Product Section 15; Project-Wide ET-01 |
| UX-11 | Should | The dashboard runs as its own Compose service with an exact package pin and a health check. Streamlit moves from the pending list to the runtime list at that point, under change control. | Service starts from the README command and its health check passes. | Project-Wide EQ-04, DO-01; decision D-28 |

## 7. Open items

Choices that need John are in decision D-39 (timeouts, polling interval and limit, and whether the public demo shows any transcript text beyond cited sentences).

## 8. Evidence read

No requirement above depends on an outside source. Streamlit's documentation on caching and session state was read as search-result summaries only. The installed version's behaviour was not tested. No accessibility or interface source was found, so accessibility rests on the existing Product requirements.

Searches were run on 18 November 2026.
