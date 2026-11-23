# Database Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns how PostgreSQL is used: access, keys, time handling, append-only rules, raw data, writes, performance and the schema additions the other documents need. The entity list is Product Section 11, which this document does not repeat. The central rule of the project is that every row carries the date it became knowable (pipeline.md Step 2), so most requirements here protect that rule.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a value the project leaves open says "pending D-38", and it is not final until John decides D-38 in the [decision log](../decision-log.md) (Project-Wide SS-02). Ideas that do not trace to the project are not requirements. They are listed in decision D-41.

| Already defined elsewhere | Where |
|---|---|
| Versioned migrations only, matched to the deployed schema | Product PL-05 |
| Raw transcript stored unchanged, cleaned text separate | Product PL-06 |
| Idempotent ingestion | Product FR-13 |
| Estimate snapshots never overwritten | Product FR-14 |
| First-reported actuals kept, corrections as versions | Data AE-04, LB-04, FD-03 |
| Membership, ticker and sector history | Data IM-01 to IM-03, SEC-01 |
| Schema match, quarantine, uniqueness, date order, re-run equality | Data DV-01 to DV-08 |
| Pinned image tags | Project-Wide EQ-04 |
| Secrets from the environment | Project-Wide SP-06 |
| Database restore in the runbook | Project-Wide DO-04 |
| Ingestion run records with row counts | Product PL-01 |

## 2. Engine and access

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-01 | Must | PostgreSQL is the only store for entities, features, predictions and explanations. Redis is the task broker and result backend only and holds no project data of record. The PostgreSQL version is the exact tag in `docker-compose.yml`. Every extension in use is created by a migration. | A search of the code finds no other database for entities. The extension list matches the migrations. | SSOT Section 8; Project-Wide SC-01, EQ-04 |
| DB-02 | Must | Separate database roles exist for: migrations, the workers (write), the API (read) and the explanation agent (read the evidence tables, write only the explanation tables, Explanation Agent AG-02). The API role is read, plus insert-only on the Explanation table so it can create a pending explanation job (API and Serving SV-06). No application role is a superuser. Passwords come from the environment. | Each role is tested for one allowed and one forbidden statement. | Explanation Agent AG-02; Project-Wide SP-02, SP-06; decision C-44 |
| DB-03 | Must | Pools are bounded so the API and the workers together stay below the server's connection limit, and a statement time-out is set. The values are in decision C-44. | A load fixture with more clients than the pool does not exhaust connections. A long query is cancelled. | Project-Wide SP-02 (unrestricted resource consumption); decision C-44 |

## 3. Keys and integrity

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-04 | Must | `company_id` is the SEC CIK (decision C-19), stored in one canonical form that is written down. No table uses the ticker as a key. | Join on `company_id` across ten known ticker changes gives one history (Data IM-03). | Decision C-19; Data IM-03 |
| DB-05 | Must | Uniqueness is enforced by the database, not only by code: event on company, fiscal period and announcement date (Data DV-03); one kept transcript per event (Data TX-05); one FeatureVector per event, feature-set version and prediction point; one Prediction per event, model version and prediction point; one Explanation per prediction, prompt version and model version. | Inserting a duplicate of each fails. | Data DV-03, TX-05; Product FR-13, FR-11, FR-01 |
| DB-06 | Must | The three date fields are NOT NULL, or the event row is marked incomplete. Class values, probabilities (each between 0 and 1) and statuses have CHECK constraints. | Insert of an out-of-range probability fails. | Product FR-02; Data DV-02 |

## 4. Time and history

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-07 | Must | Every point in time is stored as a timestamp with time zone in UTC. There is no timestamp without a time zone. | Schema query finds no timestamp-without-zone column. | Data DV-07 (UTC); Product Section 11 |
| DB-08 | Must | Tables that hold facts that can be corrected or replaced are append-only: EstimateSnapshot, ActualEps, EpsHistory, FundamentalsFiling and any other versioned fact. The worker role has no UPDATE or DELETE on them. A correction is a new row with a later knowledge time. | The worker role's UPDATE on each such table fails. | Product FR-14; Data AE-04, LB-04, FD-03 |
| DB-09 | Must | Reading history for a prediction goes through one documented as-of function or view that returns, for an entity and a date D, the latest version whose knowledge time is strictly before D. Feature code reads versioned tables only through it. | A planted version dated D or later is not returned. A test finds no direct read of a versioned table in the feature code. | Data GATE-2, FD-02, LB-04, VL-02; Product FR-22 |
| DB-10 | Must | Validity periods (index membership, ticker history, sector assignment) use half-open ranges, so the end date is not part of the period. The database refuses overlapping periods for the same company. Overlap protection needs the `btree_gist` extension, created by a migration (DB-01). | An overlapping membership insert fails. A date on a boundary resolves to exactly one period. | Data IM-01, SEC-01; Product SRS-01, Section 11 |

## 5. Raw data and lineage

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-11 | Must | Every payload from an outside source is kept as received, with its source, URL, retrieval time and hash, so a table can be rebuilt from raw data. Payloads are not edited. | Rebuild from stored payloads gives identical table hashes (Data DV-08). | Data SR-04, DV-08 |
| DB-12 | Must | Every derived row records what produced it: feature-set version, model version, prompt version and model identifier where they apply. A row without lineage is rejected. | Insert of a FeatureVector without a feature-set version fails. | Product FR-11; Project-Wide AI-01 |

## 6. Writes

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-13 | Must | The unit of work is one event. All rows for an event in one stage are written in one transaction, so a failure leaves no partial event. Writes are upserts on the keys in DB-05. On the append-only tables in DB-08 the write is insert-or-ignore. Rows that fail validation go to a quarantine table with the reason (Data DV-01). | Fault injected mid-event leaves no rows for that event. Re-running a stage leaves the row count unchanged. | Product FR-13; Data DV-01 |

## 7. Performance and size

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-14 | Must | Indexes exist for the queries the system runs: ticker as of a date; event by company and fiscal period; sentences by transcript and position; sentences by transcript ordered by a feature score (the agent's retrieval, Explanation Agent AG-06); features by event and feature-set version; predictions by event. A query plan check shows an index is used and the sentence table is not scanned in full. | `EXPLAIN` output for each named query is stored and shows an index scan on the loaded 100-company data. | Decision C-11; Product NFR-01 |
| DB-15 | Should | The database size is measured after the 100-company load and the disk needed for the full corpus is estimated from it, with the measured and estimated figures kept apart. | Size report exists. | Decision C-08, C-18; Product NFR-09 |

## 8. Test data

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-16 | Must | Tests run against a separate database, never the one holding project data. Synthetic and mock rows are never written to the project database, and test fixtures say they are synthetic. | The test configuration refuses to start against the project database name. | Project-Wide SC-04; Deterministic audit rules (real, synthetic and mock data kept apart) |

## 9. Schema additions the other new documents need

These are changes to Product Section 11 and need approval under change control before any migration is written (decision D-38). They are listed here so they are decided once.

| Addition | Needed by |
|---|---|
| `EstimateSnapshot` (approved, decision C-44): `company_id` required, `event_id` nullable until the event is built, `low_estimate`, `high_estimate`, `eps_basis`, `period_label`, `source_version` and the raw response as received | Data SR-10, CE-01, CE-03; Product FR-14 |
| `RawPayload` table: payload id, source, URL, retrieval time, hash, body or file path (approved, decision C-45: body as bytea) | DB-11 |
| `TranscriptSentence` columns: analytic flag, truncated flag, forward-guidance flag, speaker role, FinBERT model revision | Feature Engineering FE-02, FE-06, FE-14, FE-05 |
| `FeatureVector`: prediction point (T0 or T1) and a reason code per unavailable feature | Feature Engineering FE-23, FE-24 |
| `FeatureSetVersion` table: registry hash and each component version | Feature Engineering FE-28 |
| `Prediction`: prediction point (T0 or T1) | Decision C-17 |
| `Explanation` and `ClaimLabel`: evidence ids per claim, token counts, estimated cost | Explanation Agent AG-26 |
| `Explanation`: `failure_reason`, `completed_at`, the unique key on prediction, prompt version and model version, and the API role's insert grant. The job identifier is the explanation identifier | API and Serving SV-06; Product FR-19, NFR-02; DB-02, DB-05 |
| Quarantine table, and run records shared by ingestion, features and explanation jobs (run records approved as `ingestion_run`, decision C-45; the quarantine table is not yet approved) | DB-13, Product PL-01 |
| `EvaluationReport` table: model version, prediction point, metric, value, interval bounds, label route, created time | Modelling and Evaluation MD-21 |
| `TestReadLog` table, append-only: read time, job, model version, feature-set version, row count | Product ML-02; Feature Engineering FE-30 |
| `ThresholdFreeze` table, append-only: thresholds, clip limits, window, frozen time, code version | Data LB-06, VL-06; Ingestion and Preparation IG-19; Feature Engineering FE-25 |
| `Signoff` table, append-only: subject (model version or dataset version), reviewer, date, record reference | Product ML-06; Data GS-01 |
| `DeadLetter` table (approved, decision C-45): task name, argument hash, error class, time, attempt count | Ingestion and Preparation IG-02 |

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DB-17 | Must | The additions above, once approved, are made by migration, and Product Section 11 is updated in the same change. | Section 11 matches the migrated schema. | Product PL-05; decision D-38 |

## 10. Evidence read

No requirement above depends on an outside source. Articles on bitemporal data (valid time and transaction time, append-only corrections, PostgreSQL range types) were read as summaries. They informed the wording of DB-08 to DB-10. None covers backtesting directly, so the schema spike should check that the as-of function behaves as DB-09 says.

Searches were run on 18 November 2026.
