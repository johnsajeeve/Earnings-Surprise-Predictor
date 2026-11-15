# Requirements

Authority: the [SSOT](../SSOT.md) is the single source of truth. Only the owner edits it. These documents must agree with it. If one does not, the document is corrected, not the SSOT. Open and pending items are in the [decision log](../decision-log.md).

Status: draft, restructured 15 November 2026.

## Documents

Each requirement is defined in exactly one document. Other documents cite its ID.

| Document | Owns | Requirements |
|---|---|---|
| [market-requirements.md](market-requirements.md) | Users, competitors, market needs and constraints | 7 needs (N1 to N7) |
| [product-requirements.md](product-requirements.md) | What the system does: functional, sector scoring, explanation, non-functional, API, pipeline, ML, evaluation and trust, model governance, UI | 91 requirements, plus 6 goals, 5 non-goals and 5 stretch objectives |
| [data-requirements.md](data-requirements.md) | Data sources, licences, label construction, verification and validation | 70 requirements, plus the five data gates |
| [project-wide-requirements.md](project-wide-requirements.md) | Delivery, assessment, supervision, engineering, security, ethics, operations, LLM operations, documentation | 54 requirements, plus 20 conflicts to resolve (C1 to C20) |
| [proposal-drift-review.md](proposal-drift-review.md) | Comparison of all documents with the SSOT | Not a requirements document |
| [library-enquiry-draft.md](library-enquiry-draft.md) | Draft email to the library for optional institutional data | Not a requirements document |
| assessment-requirements.md | Empty. Decision D-25 | None |

Architecture deck: [earnings-predictor-architecture.pptx](../architecture/earnings-predictor-architecture.pptx) (6 slides: title, system architecture, end-to-end workflow, five gates, explanation agent, deployment and open decisions).

## ID registry

An ID prefix belongs to one document.

| Document | Prefixes |
|---|---|
| Market | N |
| Product | PG (goals), NG (non-goals), ST (stretch), FR, SRS (sector scoring), EX (explanation), NFR, API, PL (pipeline), ML, TR (evaluation and trust), MR (model governance), UI |
| Data | GATE, SR (sources), TX, AE, CE, LB (label), IM, SEC, PX, FD, DV, VL, GS |
| Project-wide | C (conflicts), ASM, PD, SS, SC, EQ, SP, ET, OR, AI, DO |
| Decision log | C-nn (closed), D-nn (open) |

Rules:
1. An ID is never reused. A withdrawn ID stays in the table below.
2. A requirement is defined once. A second document may cite it, and may not restate it.
3. A new requirement goes in the document that owns its type (see the Documents table).

## Withdrawn IDs

Withdrawn on 15 November 2026 when requirements were moved to the document that owns them, or merged into a duplicate.

| Withdrawn ID | Now |
|---|---|
| Market MFR-01 to MFR-11 | Product FR-01 to FR-11 (same numbers) |
| MFR-12, MFR-13, MFR-14 | Product ST-01, ST-02, ST-03 |
| MFR-15, MFR-17, MFR-18 | Product FR-21, FR-22, FR-23 |
| MFR-16 | Product FR-12 and SRS-01 to SRS-14 |
| MFR-19 | Product FR-06 (conditional consensus-revision baseline) |
| MNFR-01, MNFR-02, MNFR-03, MNFR-05, MNFR-07 | Product NFR-01, NFR-03, NFR-04, NFR-02, NFR-07 |
| MNFR-04 | Product ML-01 |
| MNFR-06 | Project-Wide SP-06; JWT is Product API-06 |
| DR-01 | Data CE-05, LB-01 to LB-08 and Section 4A |
| DR-02, DR-08 | Data IM-01, IM-02 |
| DR-03 | Data TX-04 and Section 4A |
| DR-04 | Data AE-01 to AE-03 |
| DR-05 | Data SR-03 and SR-11 |
| DR-06 | Data SEC-01 |
| DR-07 | Data AE-04 |
| DR-09 | Data SR-04 |
| DR-10 | Data SR-10 and CE-01 |
| TR-03 | Product ML-02 |
| MR-03, MR-07 | Product ML-06 |
| CP-01 | Project-Wide ASM-02 |
| CP-02 | Data SR-11 |
| AD-01 | Product NFR-13 |
| AD-02 | Product FR-28 |
| Product NFR-05 | Product ML-01 |
| Product NFR-06, OP-01 | Project-Wide SP-06 |
| Product NFR-10 | Project-Wide EQ-09 |
| Product OP-02 | Project-Wide EQ-04 |
| Product OP-03 | Project-Wide DO-04 |
| Product G1 to G6 (goals) | Product PG-1 to PG-6 |
| Data G1 to G5 (gates) | Data GATE-1 to GATE-5 |
| Data SC-01, SC-02 (sector) | Data SEC-01, SEC-02 |
| Market and product open-decision lists, Data Sections 13 and 14, Project-Wide Sections 5 and 6 | [Decision log](../decision-log.md) |

Moved with the same ID: TR-01, TR-02, TR-04, TR-05, TR-06, MR-01, MR-02, MR-04, MR-05, MR-06 and EX-01 to EX-05 (market to product).
