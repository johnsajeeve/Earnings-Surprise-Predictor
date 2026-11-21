# ADR 0002: Streamlit for the frontend

Status: **Accepted** by John on 18 November 2026 (decision C-22, which closes D-10). Drafted 17 November 2026. It records decision C-16 (John, 16 November 2026).

Requirement: Project-Wide SC-02.

## Context

- The proposal says "Streamlit (or React)" (Section 4.2) and asks for a lightweight dashboard: ticker input, a beat or miss prediction with a confidence score, and key explanatory factors (Section 2).
- SC-02 requires one framework to be chosen by ADR, with only that framework in the repository.
- Capacity is 15 to 20 hours a week, and the pipeline, models, API, explanation agent and evaluation are due by the end of December (decisions C-06, SSOT Section 11). The decision log recorded Streamlit as the recommended choice for capacity (D-10).

## Decision

Use Streamlit. No React code or dependencies are added to the repository.

## Alternative, not chosen

- React. It gives more control over the interface, at a higher build cost than the capacity allows.

## Consequences and open points

- Streamlit is not installed yet. It is listed in `requirements-pending.txt` and moves to `requirements.txt` when the frontend step starts.
- Whether Streamlit can deliver every Must screen in Product Section 14, and the accessibility requirement NFR-07, has not been checked. It is checked when the dashboard is built.
- If this decision changes, SC-02 and the technology table in the SSOT are affected. The SSOT is edited only by the owner.
