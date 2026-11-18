# Consistency Review of the Requirement Documents

Date: 18 November 2026. Requested by John: no contradictions or duplicates across the requirement documents, everything aligned with the project and nothing taken from outside it, and no errors in earlier files. This review inspected the files as they are now. It does not rely on earlier reports.

## 1. What was checked and how

| Check | Method | Result |
|---|---|---|
| Duplicate and misplaced IDs, undefined citations, withdrawn IDs, wrong-document citations, broken links | `docs/tools/check_requirements.py` (extended to the four new documents) | PASS, after fixes |
| Broken markdown tables | Script comparing column counts of every table row in every `.md` file outside `docs/source` | PASS, no mismatches |
| Em dashes and en dashes in documents | Script over every `.md` file | PASS, none |
| Decision references | Script: every C-nn and D-nn cited exists in the decision log | PASS. D-10, D-30 and D-31 are closed decisions, cited only as history |
| Near-duplicate requirement text, new against existing | Text similarity of every new requirement against every existing one (threshold 0.45) | Two true duplicates found and removed (section 2); the rest were similar wording only |
| Every new requirement traces to the project | Manual: each row names the proposal, SSOT, an existing ID, a decision, pipeline.md or an ADR | Rows that did not were removed (decision D-41) |
| Priority counts quoted in documents | Script using the traceability parser | Existing counts correct; new counts added |
| Code and build | `docker compose up --build -d`, `/health`, `ruff check`, `ruff format --check`, `mypy`, `pytest`, `check_pins.py` | PASS: stack healthy, HTTP 200, 19 tests passed |
| Traceability | `audits/generate_traceability.py` run twice | Same hash both times; 348 requirements |

Not checked: meaning beyond what a person reads. The checker does not find contradictions in sense. The requirement text itself was read, not machine-verified, for the cross-document points below. The CI workflow has still never run on GitHub.

## 2. Errors and contradictions found, and what was done

| # | Finding | Fix |
|---|---|---|
| 1 | Decision D-33 proposed "a new Product requirement FR-28", but FR-28 already exists (limitations notice). | D-33 now says FR-29. |
| 2 | My first draft of the agent document allowed a template explanation when the model failed. Product Section 12 says the user sees "Explanation could not be generated." | Removed. The failure paths now end in that message (AG-15, AG-20). Template idea listed in D-41. |
| 3 | Agent draft AG-09 duplicated Product ST-05 (8-K corroboration) and AG-27 duplicated Product ST-03 (critic and revise). | Removed. Both are cited as existing requirements. |
| 4 | Agent draft listed counter-metrics that Product Section 15 does not contain. | AG-25 now lists the actual ones (explanation length, features discussed, human agreement). |
| 5 | Database draft said PostgreSQL is the only store, which contradicted Redis as broker. | DB-01 says Redis is the broker and result backend only. |
| 6 | Database draft DB-05 repeated PL-05 (versioned migrations), and DB-25 repeated the restore drill in DO-04. | Removed. |
| 7 | Many draft rows traced only to "design proposal" or outside research. | Removed or reworded to trace to the project. Removed ideas are in D-41. |
| 8 | Product SC-06 and DO-02 required a vector store ADR, but decision C-11 chose plain SQL and cites SC-06. | SC-06 now records the plain-SQL choice by ADR. DO-02 lists the retrieval method. |
| 9 | Several documents said "three" or "four" requirement documents. | Project-Wide Section 1, C11, ASM-04, SS-03, DO-05, the checker and the generator now cover all documents. |
| 10 | Data 4A.1 and the gate matrix named Wikipedia or `index-constitution` for membership. pipeline.md names `fja05680/sp500` and decision D-32 is open. | Both Data places now list the candidates and point to D-32. |
| 11 | Data Section 12 said the EDGAR spike script was not run. A one-company probe was run on 17 November. | Section 12 now states the partial result and its limit. |
| 12 | Drift review said Streamlit or React is "still to be chosen". C-16 chose Streamlit and C-22 accepted the ADR. | Corrected. |
| 13 | Drift review counts and the decision range D-01 to D-26 were out of date, and it had no row for the four new documents. | Updated. Capacity effect stated: 85 more requirements, 79 of them Must. |
| 14 | Project-Wide's list of related decisions named D-10, which is closed. | Now D-11 to D-17. |
| 15 | pipeline.md line on D-31 did not say it is closed. | Now says closed as C-17. |
| 16 | The logbook commit register had no row for a720023. | Added. |
| 17 | The traceability generator read only four documents, so new requirements would have no row. | Generator reads eight. 348 requirements, 17 assessed, the rest UNVERIFIED. |
| 18 | D-26 (re-tag Must requirements) did not mention the new documents. | Sentence added. |

## 3. Edits to existing requirement text (for John to reverse if wanted)

| File | Change | Why |
|---|---|---|
| Product FR-24, mean FinBERT row | "across all sentences" became "across all analytic sentences (Feature Engineering FE-02, FE-07)" | So FR-24 agrees with FE-07. Confirm under D-36. |
| Project-Wide SC-06 | Reworded to record plain-SQL retrieval (C-11) | Removes the conflict with C-11 |
| Project-Wide DO-02 | "vector store" became "sentence retrieval method (decision C-11)" | Same |
| Project-Wide DO-05 | Prefixes FE, AG, DB, UX added; "four documents" became "documents" | New documents |
| Project-Wide SS-03 | Sign-off covers the four component documents once approved (D-40) | New documents |
| Project-Wide ASM-04, C11, Section 1 | "three" and "four" wording | Count was out of date |
| Data 4A.1 and Section 5 (membership rows) | Candidates and D-32 named | Agree with pipeline.md |
| Data Section 12 (EDGAR spike) | Partial one-company result recorded | Was untrue |
| Drift review Sections 1, 2, 4 and 6 | Counts, rows, wording | Out of date |
| Decision log D-26, D-33, header, slide 6 row | See table above | Collision and range |

No change was made to the SSOT. The SSOT document map still lacks rows for the four new documents. Proposed wording is in decision D-40.

## 4. Open items from this review

- The SSOT Section 8 stack table still says "Streamlit or React (one to be chosen)", while decision C-16 chose Streamlit. The SSOT is owner-only and was not edited. John may want to update it.
- The proposal text (Section 4.3) says "multi-step tool-using" and the SSOT says "single-pass". The SSOT wins, and the agent document follows it. The proposal is not edited by Claude.
- Priority load: the new documents add 79 Must requirements. Whether that fits capacity is the existing D-03 and D-26 question.
- Unverified inputs remain: Bernard and Thomas eight-quarter window, whether "believe" is on the Loughran and McDonald list, and the Hugging Face transcript licence.

## 5. Update: four further component documents

Added later on 18 November 2026: ingestion and preparation (IG), modelling and evaluation (MD), API and serving (SV), deployment and operations (DP). The same checks were run again over all twelve requirement documents: checker passes (checks 1 to 6), no broken tables, no dashes, no undefined decision references, no email address in any file, traceability generator gives identical output twice (424 requirements).

| # | Finding | Fix |
|---|---|---|
| 19 | Decision D-01 (supervisor agreement on the label) was still cited as open in Data, Product, Project-Wide, the drift review and pipeline.md after John decided the label route himself. | Recorded as C-25, which closes D-01. Stale wording corrected. The SSOT still says "pending supervisor approval" and is owner-only, so the wording change is proposed in D-46. |
| 20 | Project-Wide SC-07 and SS-04 ask for the supervisor's agreement in writing, and John reports only that Professor Goodacre does not mind. | Not edited. D-46 asks John to note the no-objection in the next meeting action list. |
| 21 | Product Section 12 says the service refuses to serve when a model artefact fails its checksum, but decision C-15 says the API reads stored predictions and does not load a model. | Resolved in API and Serving SV-08: the API checks the artefact's checksum without loading it for scoring. |
| 22 | Two draft ingestion rows repeated Data TX-05 and DV-07. | Reduced to citations. |
| 23 | Product FR-01 requires three class probabilities summing to 1, which rules out a binary-only model. | Modelling and Evaluation Section 2 recommends one three-class model with the beat-against-miss AUC derived from it (D-42). |
| 24 | Drift review counts and coverage rows were out of date again. | Updated: 376 requirements outside the market document, 304 of them Must. |

Not checked: the pinned library versions that the new documents mention (PyJWT, a rate limiter, a metrics library) were not looked up. They are added to the dependency lists under change control when built. Prices for any managed cloud component were not verified.
