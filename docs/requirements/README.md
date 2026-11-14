# Requirements

Four requirement documents and a drift review for the Earnings Surprise Predictor, plus the architecture deck in `docs/architecture/`.

| Document | Scope | Requirements |
|---|---|---|
| [product-requirements.md](product-requirements.md) | What the system does: goals, non-goals, functional and non-functional requirements, API, data model, screens, milestones | 26 functional (FR-01 to FR-26), 14 sector-scoring (SRS-01 to SRS-14), 12 non-functional, 5 stretch (ST-01 to ST-05) |
| [market-requirements.md](market-requirements.md) | Who needs it, competitors, user needs, trust and model risk requirements | 58 (IDs MFR, MNFR, DR, TR, MR, EX, CP, AD) |
| [data-requirements.md](data-requirements.md) | Data sources, licences, point-in-time checks, verification and validation against the five gates | 57 (GATE-1 to GATE-5; includes FD-01 to FD-04, CE-05, VL-12) |
| [project-wide-requirements.md](project-wide-requirements.md) | Delivery, assessment, supervision, engineering, security, ethics, operations, LLM operations, documentation | 50 |

Architecture deck: [earnings-predictor-architecture.pptx](../architecture/earnings-predictor-architecture.pptx) (6 slides: title, system architecture, end-to-end workflow, five gates, explanation agent, deployment and open decisions).

Also: [proposal-drift-review.md](proposal-drift-review.md), the comparison against the proposal (the scope baseline).

Status: draft, revised 14 November 2026 to remove drift from the proposal. Open decisions are listed in each document. Changes to the planning notes and the proposal are listed in the project-wide document, Section 6, and have not been applied.
