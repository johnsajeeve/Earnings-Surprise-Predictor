# Wave 2.1 task brief: sentences and FinBERT (27 November 2026)

For John, before any build work (drift control 2). Nothing in this wave is built.

## Entry gate: not fully met, stated plainly

The plan's Phase 2 gate asks for the Phase 1 gate to be passed. **It is not**: transcript coverage is 88.2% against 90% (TX-04), the press-release comparison cannot show AE-02, the 50 boundary labels (TX-03) and the 100-event hand audit (VL-09) are not done, and no reviewer has signed off the data (GS-01). The data faults two audits found in labels and transcripts are fixed but the latest fixes have not been audited by a fresh agent. Starting Wave 2.1 is reasonable because it works one transcript at a time and its output can be rebuilt; **no model may be trained on it until the Phase 1 gate is settled.**

## Requirements and acceptance checks served

FE-01-AC1, FE-01-AC2 (spaCy sentences, versions recorded, same rows on a rerun); FE-02-AC1 (operator turns and the safe-harbour paragraph marked non-analytic); FE-03-AC1 (every sentence an exact substring of the cleaned text); FE-04-AC1 (no speaker roles: stored as unavailable); FE-05-AC1, AC2 (checkpoint and revision on every score, register entry); FE-06-AC1, AC2 (long sentences cut explicitly, flagged, share reported); FE-07-AC1 (call means, four decimals); FE-09-AC1 (speed with the hardware). FE-29 (idempotent writes) for these tables.

## Files to change

Migration for `transcript_sentence` (Product Section 11, with `speaker`, `role`, `analytic`, `truncated`, `model_revision` added, a schema change), `src/earnings/sentences.py`, `src/earnings/finbert.py`, a scoring Celery task, tests with synthetic transcripts, evidence `wave-2.1.md`.

## New dependencies (change control: needs your yes)

Versions read from PyPI on 27 November 2026.

| Package | Version | Licence as stated | Note |
|---|---|---|---|
| spaCy | 3.8.18 | MIT | |
| en_core_web_sm model | 3.8.0 | MIT | Trained on OntoNotes 5 (LDC), a licensed corpus, plus WordNet and ClearNLP data. The parser is needed for the negation rule later |
| torch, CPU wheel from the PyTorch index | 2.15.0+cpu | Apache-2.0 and BSD-family | The default PyPI wheel pulls CUDA packages and is not used |
| transformers | 5.24.1 | Apache-2.0 | Very new (24 November). I would pin it after a load test of FinBERT, or an earlier release if it fails |
| ProsusAI/finbert weights, revision 0bc2ac10 | decided, C-54 | CC BY-NC-SA 4.0 | Non-commercial; downloaded into the data volume, never committed |

They go in the worker image only (DP-03), so the API image stays small. That is a Dockerfile change.

## Needed from you: the safe-harbour rule (FE-02)

FE-02 says the detection rule is pending D-36, and D-36 as approved says only that safe-harbour text is excluded, not how it is found. **My proposal:** in the prepared remarks, mark non-analytic every sentence of a turn from the first sentence that contains "forward-looking statement" or "safe harbor" (or "safe harbour"), through the last sentence in that same turn that contains one of: "forward-looking", "safe harbor", "actual results", "risk factors", "SEC filings", "securities and exchange commission", "no obligation to update". I will report how many calls it matches and show you 20 examples before it is relied on.

## Cost and risk

Scoring about 3,394 calls: the 23 November spike measured 14.7 to 28.3 sentences a second on 6 CPUs and about 469 sentences a call, so roughly 16 to 30 hours (an estimate from that spike, to be re-measured, FE-09). It runs in the background. The machine has 9 GB of memory available to WSL, so memory is watched (DP-02).

## Out of scope

Linguistic features (Wave 2.2, which also needs the D-34 phrase lists shown to you first), tabular features, any model.
