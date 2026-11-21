# API and Serving Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns how the FastAPI service is built and behaves: its layers, what each endpoint does, job handling, authentication, limits, metrics and health. Product Section 6 (API-01 to API-07), Section 12 (error states) and Section 13 (endpoint list) say what the API offers. This document says how it must work. It does not repeat them.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a value the project leaves open says "pending D-43", and it is not final until John decides D-43 in the [decision log](../decision-log.md) (Project-Wide SS-02). Research on the internet informed the choices and is listed in Section 6. It is not a requirement by itself.

| Already defined elsewhere | Where |
|---|---|
| OpenAPI, /v1 prefix, error shape, envelope, pagination, JWT, rate limit | Product API-01 to API-07 |
| The endpoint list | Product Section 13 |
| Error messages | Product Section 12 |
| Prediction lookup, edge cases, history, asynchronous explanation, ticker validation | Product FR-01, FR-07, FR-09, FR-19, FR-20 |
| Latency, freshness, request logging, metrics | Product NFR-01 to NFR-03, NFR-11, NFR-12 |
| Request logs contain only the allowed fields | Project-Wide SP-05 |
| Security review of the API | Project-Wide SP-02 |
| Stored predictions are read, not computed live | Decision C-15 |

## 2. Structure and behaviour

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SV-01 | Must | The API reads stored predictions, features, evaluation reports and explanations. It never runs FinBERT, spaCy, XGBoost scoring or training inside a request. The API image therefore needs none of the heavy machine learning packages. | A search of the API code finds no import of the model packages. A request makes no model call. | Decision C-15; Product FR-01; Modelling and Evaluation MD-22 |
| SV-02 | Must | The code is in three layers: routes (request and response shapes), services (the rules in this document) and repositories (the only code that touches the database). Routes contain no query. | A static check finds no database call in a route. | Product API-01; Database DB-02 |
| SV-03 | Must | "Latest prediction" for a ticker means the stored T0 prediction of the most recent event whose cutoff has passed. A T1 prediction, where it exists, is returned as a separate item and labelled (decision C-17). The ticker is resolved to a company as of today, using ticker history. | Fixture company with a renamed ticker resolves to one company. T0 and T1 are returned as two labelled items. | Decision C-17; Product FR-01, FR-20; Data IM-03 |
| SV-04 | Must | Every prediction and explanation response uses the envelope from Product API-04. Warnings such as "Limited history" and the as-of times of the inputs (Product FR-22) are in the envelope, so the dashboard can show them. | Contract test checks the envelope and the as-of times on each prediction endpoint. | Product API-04, FR-07, FR-22; Frontend UX-05 |
| SV-05 | Must | Inputs are validated before any lookup: ticker (Product FR-20), date range (the start not after the end, and a maximum span set under D-43) and page size (Product API-05). Invalid input gets the error shape in Product API-03. | Fixture with each invalid input returns the expected status and message. | Product FR-20, API-03, API-05; Project-Wide SP-02 |
| SV-06 | Must | The explanation job endpoint creates the job as a pending Explanation row (the job identifier is the explanation identifier) and queues the task, then returns the identifier within 500 ms (Product FR-19). If queuing fails, the row is marked failed with the reason "queue unavailable" and the response is 503 (Product ER-14). Asking again for the same prediction, prompt version and model version returns the existing job or stored explanation, not a second job. A job moves from pending to running to complete or failed, and never back. An unknown job identifier returns 404 in the Product API-03 error shape. | Two identical requests give one job. Status never moves backwards. A queue failure leaves a failed row. An unknown identifier returns 404. | Product FR-19, NFR-02; Explanation Agent AG-21 |
| SV-07 | Must | The history endpoint joins each prediction with its realised outcome and shows "Pending" while the outcome is not known. The evaluation endpoint reads the stored report (Modelling and Evaluation MD-21), checks the model name against the allowed list, and states "unavailable" with a reason for the consensus baseline when it does not exist. | Fixture with an unreleased event shows Pending. Unknown model name returns 422. | Product FR-09, FR-06, Section 13 |
| SV-08 | Must | At start-up, and in /health, the API checks the artefact checksum of the model behind the stored predictions. On a mismatch the prediction endpoints answer with the Section 12 message and the health status reports it. The failed check is also written as an error-level log line naming the artefact. | Altered artefact makes the prediction endpoint return 503 with the Section 12 message. The error log line exists. | Product ML-03, Section 12; Modelling and Evaluation MD-23 |

## 3. Cost, limits and metrics

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SV-09 | Must | The cached-prediction latency target in Product NFR-01 is measured with a load test (Project-Wide EQ-05), not assumed. Stored predictions never change for a given event, model version and prediction point, so they can be served from the database with an index on the lookup key (Database DB-14). An extra cache is added only if the measured figure misses the target. | Load test report states the 95th percentile against 500 ms. | Product NFR-01; Project-Wide EQ-05; Database DB-14 |
| SV-10 | Should | Each client is rate limited with the counter held in Redis, which is already in the stack. A limited request returns 429 with a Retry-After header (Product API-07). /health and /metrics are not limited. If Redis is unavailable the limiter lets requests through and logs a warning, so the demo stays up. That behaviour is pending D-43. | Load fixture over the limit gets 429 with the header. Redis stopped: requests pass and a warning is logged. | Product API-07; Project-Wide SP-02; pending D-43 |
| SV-11 | Should | /metrics exposes request counts, a latency histogram and error counts, labelled by route template and not by the raw path, so tickers never become metric labels. | Scrape output contains route templates and no ticker values. | Product NFR-12; Project-Wide SP-05 |
| SV-12 | Must | /health reports the status of the database, Redis and the worker (done), the latest transcript date per ticker (Product PL-03), the ingestion status (Section 13) and the artefact check (SV-08). The ingestion status is part of the body and never changes the HTTP status. A failed database, Redis, worker or artefact check does. It never returns a secret or the value of a configuration variable. | Health response lists the date for a test ticker and the artefact status. Secret scan of the response passes. | Product PL-03, NFR-03, Section 13; Project-Wide SP-06 |
| SV-13 | Must | Request size, query time and page size are bounded, and the browser cross-origin setting is not a wildcard. The dashboard calls the API from the server side (Frontend UX-01), so no cross-origin access is needed by default. | Oversized body is refused. A cross-origin test request from an arbitrary origin is refused. | Project-Wide SP-02 (resource consumption, security misconfiguration); Frontend UX-01 |
| SV-14 | Must | An error from PostgreSQL or from the queue is reported with the ER-14 message and the name of the failed part, with no partial result and no stack trace. Every 5xx is logged with its request identifier. A data source error is never raised inside a request, because requests read stored data (SV-01). | Injected failure fixtures return the message and are logged. | Product FR-07, API-03, NFR-11 |

## 4. Authentication (deferred)

John said authentication is a later problem. It is therefore not part of the December scope (decision D-28). Until it is built, the stack binds its ports to 127.0.0.1 only (already true in `docker-compose.yml`), so nothing is reachable from outside the machine. The requirements below are written now so the design is settled, and they must be met before the API is exposed beyond the machine and before the backend milestone is signed off (Product Section 16).

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| SV-15 | Must (before any exposure) | Every endpoint except /health requires a JWT (Product API-06). The design is a single-owner demo token: there is no user table and no login endpoint, because public accounts are a non-goal. The token is signed with a secret read from the environment, has an expiry, and is issued by a command-line script run by the owner. The signing algorithm is fixed on the server, and a token with the algorithm "none" or a different algorithm is rejected. The signing library is PyJWT, which the FastAPI documentation uses, and it is added to the dependencies under change control when this is built. | Request without a token returns 401. Expired, tampered and "none" tokens return 401. | Product API-06, NG4; Project-Wide SP-02, SP-06, EQ-04 |
| SV-16 | Must (before any exposure) | The dashboard and any other client read the token from the environment (Frontend UX-01) and never from source. The token and secret are never logged. | Secret scan passes. Logs contain no token. | Project-Wide SP-06; Frontend UX-01 |

## 5. Pending items

Choices that need John are in decision D-43: the maximum date span (SV-05), the rate limit values and the behaviour when Redis is down (SV-10), and the timing of authentication (SV-15).

## 6. Evidence read

No requirement above depends on an outside source. Read as background, mostly as summaries:
- FastAPI security documentation (as mirrored in search results): token handling with PyJWT and password hashing with pwdlib. A third-party guide that uses passlib reflects older advice. The live English page was not retrieved. This project has no passwords, so only the token part applies.
- Rate limiting articles: a Redis-backed limiter with a Retry-After header on 429 is the common pattern. Failing open or closed when Redis is down is a design choice, and the one here is a proposal. Whether the metrics route is affected by the limiter was not covered, so it is exempted explicitly.
- No official slowapi or instrumentator documentation was retrieved. Their exact APIs are checked when they are added.

Searches were run on 18 November 2026.
