# ADR 0001: Celery with Redis as the task queue

Status: **Accepted** by John on 18 November 2026 (decision C-22, which closes D-10). Drafted 17 November 2026. It records a choice the proposal already makes.

Requirement: Project-Wide SC-01.

## Context

- The proposal names the task queue directly: "Task Queue: Celery + Redis" (Section 4.2), and "data ingestion workers" (Section 4.1). Milestone 1 includes "Celery workers".
- SC-01 says the design follows the proposal, and that Kafka, Redis Streams or Cloud Tasks are used only if an ADR justifies them.
- Jobs this system must run: scheduled ingestion with retries (PL-01, PL-02), idempotent tasks (EQ-07), and the explanation agent as a background job (FR-19). The target corpus is about 4,000 to 5,000 earnings events (SSOT Section 4).
- The first deployment is a local Docker Compose build, then Cloud Run if time allows (decision C-07).

## Decision

Use Celery with Redis as the broker (Redis database 0) and as the result store (database 1). One queue design. No second queue technology.

## Alternatives named by SC-01, not chosen

- Kafka, Redis Streams, Cloud Tasks. The proposal does not call for them, and the corpus is small. In the requirement documents read for this ADR, none was found that needs their features. They would add a second moving part to a 15 to 20 hours a week project (SSOT Section 11). This is a judgement, not a measured comparison.

## Evidence so far

- The Docker Compose stack runs Redis and a Celery worker. A task sent from the API round-trips through Redis and the worker (audit of 17 November 2026, `audits/audit_2026-11-17.md` sections 3 and 4).

## Consequences and open points

- PL-02 asks for three retries with backoff and then a dead-letter queue. How the dead-letter step is built has not been designed.
- How the worker runs on Cloud Run (always-on, or a separate service) is not decided. It is settled at the deployment step.
- The result store is Redis, which this project does not treat as a durable record. Anything that must be kept (run logs under PL-01) is to be written to PostgreSQL. That is not built yet.
- If this decision changes, SC-01 and the deployment diagram in `docs/architecture/` change with it.
