# Deployment and Operations Requirements

Status: DRAFT, written 18 November 2026 for the owner's approval. Nothing here is approved until John says so. Authority: the [SSOT](../SSOT.md). If this document disagrees with the SSOT, this document is corrected.

## 1. Purpose and scope

This document owns where and how the system runs: the local Docker build, resource limits, secrets, continuous integration, logs and metrics, backups, release tagging and the optional Cloud Run deployment. Project-Wide EQ, SP, OR and DO and decision C-07 set the rules (local Docker first, then Cloud Run if time allows). This document turns them into build requirements.

Every requirement has a "Traces to" entry naming where in the project it comes from. A requirement that fixes a value the project leaves open says "pending D-44", and it is not final until John decides D-44 in the [decision log](../decision-log.md) (Project-Wide SS-02). Research on the internet informed the options in Section 2 and is listed in Section 6. It is not a requirement by itself.

| Already defined elsewhere | Where |
|---|---|
| Locally runnable Docker build first, then Cloud Run if time allows | Decision C-07 |
| Build on the owner's PC, CPU first | Decision C-08 |
| Exact pins, one-command run, image tags | Project-Wide EQ-04, DO-01 |
| Continuous integration, branch protection, lint, types, vulnerability scan | Project-Wide EQ-01 to EQ-03, EQ-08 |
| Load test, runbook, rollback in 10 minutes | Project-Wide EQ-05, DO-04 |
| Secrets, secret scan, request logs and retention | Project-Wide SP-05, SP-06 |
| Cost ceiling, zero data spend | Project-Wide OR-02; decision D-15 |
| ADR for each major technology choice, including deployment target | Project-Wide DO-02 |
| Uptime, metrics | Product NFR-04, NFR-12 |
| Data licences for any public demo | Data SR-03; decision D-18 |

## 2. Hosting options, and the recommendation

The key fact for cost: the API only reads stored predictions (decision C-15), and explanations can be generated ahead of time on the owner's machine. A cloud demo therefore does not need a Celery worker.

| Option | What runs in the cloud | Fit with the project |
|---|---|---|
| A. Local only | Nothing. The demo is the Compose stack plus a recorded demo | Zero cost. Meets C-07 and OR-02. Does not show the proposal's Cloud Run item. |
| B. Cloud Run, read only (recommended if D-15 allows any spend) | The API and the dashboard as Cloud Run services that scale to zero, plus a managed PostgreSQL holding only redistributable data. Predictions and explanations are generated locally and loaded | Shows Cloud Run and the proposal's stack. No always-on worker and no managed Redis. The database is the main continuing cost. |
| C. Cloud Run, full | Option B plus a worker running continuously and managed Redis | Highest cost. Billed continuously whether idle or busy. Needed only to show on-demand explanation jobs in the cloud. |

Costs of the managed database, managed Redis and workers were not verified here. The cost of an always-on instance is the point to remember: a minimum instance or a worker pool is billed all the time. The pricing pages and the calculator are checked before anything is created (DP-14).

## 3. Local build

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DP-01 | Must | The deliverable that always works is the Docker Compose build, started from the README with one command, with every setting from environment variables and the same images in every environment. Cloud is optional and never a dependency. | A clean checkout runs the README command and `/health` answers 200. Timed run is recorded. | Decision C-07; Project-Wide EQ-04, DO-01 |
| DP-02 | Must | Each service has a memory limit set so the whole stack, including FinBERT scoring, fits the owner's machine (9 GB available to WSL) without being killed. The peak memory of each service is measured during the 100-company run and recorded. | The 100-company pipeline finishes with no out-of-memory kill. Peak memory table exists. | Decision C-08, C-18; Feature Engineering FE-09 |
| DP-03 | Should | The heavy machine learning packages (torch, transformers, spaCy, XGBoost, SHAP) are installed only in the image used by the worker. The API image stays small. Splitting the image is a change to the Dockerfile and goes through change control. | API image has none of the model packages and is under the size recorded at the last build. | API and Serving SV-01; Project-Wide EQ-04, DO-01; Deterministic audit Section 6 |
| DP-04 | Must | Persistent data lives in named volumes: the database, the model artefacts and the model download cache. A command writes a database dump to a git-ignored folder, and a restore into a scratch database is tested once, with row counts compared. | Restore record shows matching counts. | Project-Wide DO-04; `.gitignore` |
| DP-05 | Must | The runbook is a file in the repository covering start, stop, reset, rebuild the database from stored raw data (Data DV-08), restore, and re-run one day's ingestion. Each step is run once and dated. | Each step has a dated run record. | Project-Wide DO-04, DO-01; Data DV-08 |

## 4. Pipeline, secrets, logs and releases

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DP-06 | Must | Secrets come from environment variables: a local `.env` file that is git-ignored, repository secrets for continuous integration, and the cloud secret manager if Option B or C is used. No secret is in an image layer, a log or a response. | Secret scan passes (Project-Wide SP-06). Image history contains no secret value. | Project-Wide SP-06 |
| DP-07 | Must | Continuous integration runs `docs/tools/check_requirements.py`, regenerates the traceability, acceptance-index and pending-values files and fails if they differ from what is committed, checks that every test marker names a real requirement reference (`scripts/check_requirement_refs.py`), and checks that commits that change code name a requirement (`scripts/check_commit_refs.py`). The job is named "Requirements consistency (DO-03, DO-05)". Making it a required check is a repository setting and needs John's approval. | A planted duplicate ID, a stale generated file, a test with an unknown reference and a code commit with no requirement ID each fail the job. | Project-Wide DO-03, DO-05; Deterministic audit (Drift controls) |
| DP-08 | Should | Images are tagged with the git commit, and each ModelVersion record stores the commit it was built from, so a result can be traced to code. Each milestone is a git tag. | ModelVersion has a commit field. Tags exist for finished milestones. | Product FR-11, ML-01; Project-Wide PD-03 |
| DP-09 | Must | Logs go to standard output as one line per event with a request identifier, and worker logs carry the task identifier. They hold only the fields in Product NFR-11 and the ticker, and are kept for the period in Project-Wide SP-05. Uptime is checked from `/health`. No paid monitoring service is used. | Log schema test (Project-Wide SP-05). | Product NFR-11, NFR-12; Project-Wide SP-05, OR-02 |
| DP-10 | Must | Nothing that must stay private is in the public repository: `.env`, data, model artefacts, and the proposal and planning notes. A repository scan before each push checks this. | Scan finds none of them. | Decision C-21; Project-Wide SP-06 |

## 5. Optional cloud deployment

| ID | Priority | Requirement | Acceptance check | Traces to |
|---|---|---|---|---|
| DP-11 | Should | A deployment-target ADR is written before any cloud resource is created, naming the option chosen from Section 2 and its cost. | ADR 0003 exists and is accepted. | Project-Wide DO-02; Decision D-15 |
| DP-12 | Must (if cloud is used) | A spend ceiling and a budget alert at 80% of it are set before the first resource exists, and the ceiling is decision D-15. | Budget alert exists before any resource is listed. | Project-Wide OR-02; decision D-15 |
| DP-13 | Must (if cloud is used) | The cloud database and any cloud storage hold only data that may be redistributed, or the demo is a bring-your-own-key design. Licensed transcripts and personal-use sources such as yfinance are never loaded. | The demo bundle manifest lists each source and its licence with no personal-use source. | Data SR-03, SR-11; decision D-18 |
| DP-14 | Should (if cloud is used) | Services are stateless, read their port and settings from the environment, use `/health` as the readiness check, scale to zero when idle, and run from an image tag so a rollback is a redeploy of the previous tag within 10 minutes (timed once). Pricing for each managed component is checked on the provider's pricing page before creation. | Rollback is timed once. Service scales to zero in a test. | Project-Wide DO-04, OR-02; Product NFR-04 |
| DP-15 | Should (if Option C) | A Celery worker cannot run as a request-driven Cloud Run service, because it takes no web requests. Option C needs a worker pool or a virtual machine, and the choice is recorded in ADR 0003. | ADR 0003 names how the worker runs. | ADR 0001 (open point on Cloud Run workers) |

## 6. Evidence read

No requirement above depends on an outside source. Read as background, mostly as summaries:
- Google Cloud documentation on Cloud Run worker pools and always-on CPU: worker pools are for background workloads that take no web requests, and they and any minimum instances are billed for the time they run, whether idle or busy. A news item claiming a price difference between worker pools and services came from an aggregator and is not relied on.
- Nothing retrieved covered Celery on Cloud Run, or the price of a managed PostgreSQL or managed Redis. Those figures are unverified.

Searches were run on 18 November 2026.

## 7. Pending items

Decision D-44: the hosting option (Section 2), whether ADR 0003 is written now or in January, and the image split in DP-03. The cost ceiling is D-15.
