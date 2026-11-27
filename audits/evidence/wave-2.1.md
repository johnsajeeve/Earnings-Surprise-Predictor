# Wave 2.1: sentences and FinBERT (27 November 2026)

Status: **PARTIAL**. Built and tested; scoring of the full set is a long run that had not finished when this was written. Started although the Phase 1 gate is not met (C-67); no model may be trained on this output until it is settled. Not audited by a fresh agent.

## What was built

`src/earnings/sentences.py`, `src/earnings/finbert.py`, migration 0012 (`transcript_sentence`), the task `earnings.score_transcript`, and a separate worker image (DP-03). The API image stayed at 857 MB; the worker image is 2.62 GB.

## Packages and model (C-67)

spaCy 3.8.18, en_core_web_sm 3.8.0 (installed from the release file, hash checked), torch 2.15.0+cpu from the PyTorch CPU index, transformers 5.24.1. A load test on a clean Python 3.12.16 image passed before they were pinned. Adding them changed no version in `requirements.lock`. `pip-audit` on the worker lock (torch checked as 2.15.0): no known vulnerabilities. ProsusAI/finbert revision `0bc2ac10dda6929bcb1f77ccc43c7ec5c424f031`, safetensors weights only, file hashes pinned in the code, kept in the data volume.

## Splitting all stored calls (no scoring), 3,394 kept transcripts

| Measure | Value |
|---|---|
| Sentences / counted for text features | 1,675,517 / 1,565,269 |
| Sentences not found in the cleaned text by exact match (FE-03) | 0 |
| Median sentences a call | 494 |
| Operator sentences left out | 100,430 |
| Safe-harbour sentences left out | 9,818 |
| Calls the rule matched / did not match | 2,957 / 437 |
| Unmatched calls that say "forward looking" without a hyphen | 30 |
| Calls matched in more than one turn | 28 |
| Sentences left out per matched call: 10th, 50th, 90th, 99th percentile, maximum | 1, 3, 5, 8, 141 |
| Participant-list sentences ("Executives", "Analysts" entries) still counted | 5,441 |

**Over-removal.** Four calls lose 141, 91, 76 and 52 sentences (AEP 2013-02-15, CAT 2015-04-23, CAT 2015-07-23, AEP 2016-11-01). One speaker gives the notice and then talks on in the same turn, and a later ordinary use of "forward-looking" or "actual results" stretches the passage. No other call loses more than 15. The approved rule was not changed (D-51).

The 20 examples John asked to see are in `audits/evidence/wave-2.1/safe_harbour_examples.md` (kept on this machine: transcript text). No verdicts yet.

## First scored calls (real data)

10 calls, 4,246 sentences, 116.0 s: **36.6 sentences a second**, splitting included (FE-09). Hardware: Intel Core Ultra 7 256V, 6 logical CPUs, 9.7 GB for WSL. Projection for the 1,675,517 sentences: about 12.7 hours. A corpus of all index members would be about five times this set (a scaling, not a measurement). The 10 are the oldest calls, so the rate over the whole run may differ.

A rerun of the same 10 calls with a scorer that raises if called: nothing scored, nothing updated, table hash unchanged (FE-29). Truncated sentences: 0 of 4,246. Rows not found in cleaned text: 0. Largest distance of the three scores from summing to 1: 1.3e-07.

## Checks

| Check | Status |
|---|---|
| FE-01-AC1, AC2; FE-03-AC1 | PASS on synthetic text with the real spaCy model; FE-03 also holds on all real calls above |
| FE-02 | PARTIAL: rule built as approved and tested. FE-02-AC1 compares hedge counts, which arrive in Wave 2.2. Over-removal above; examples not yet reviewed |
| FE-04 | PARTIAL: unknown roles are stored and means still computed. FE-04-AC1 also needs the Q&A delta (Wave 2.2) |
| FE-05-AC1, AC2 | PASS |
| FE-06-AC1 | PASS with the real tokenizer (local run; skipped in CI, which has no weights) |
| FE-06-AC2 | NOT TESTED: the feature report is FE-31, a later wave. The share is stored per row |
| FE-07-AC1; FE-29-AC1; FR-16-AC1, AC2 | PASS on synthetic data |
| FE-09-AC1 | PASS: the record above |

## Limits and differences from the brief

- The worker role may not delete rows (DB-02), and I did not widen that. Changed sentences are scored again and overwritten. If a changed transcript has fewer sentences, scoring stops with an error and the old rows stay.
- The spaCy and rule versions are recorded in the run output and here, not per row. FE-01 places them in the feature-set version (FE-28, a later wave).
- The columns added to Product Section 11's TranscriptSentence were listed in the task brief, but my chat summary asked only about packages and the rule. Section 11 is not edited; John is asked to confirm the columns (D-51).

## After John's four approvals (C-68, 27 November 2026)

- Safe-harbour rule version 2 (a closing phrase counts within 12 sentences of the opening one). Lists of who is on the call no longer count. The table of splitting figures above was measured with version 1; the version 2 figures are in the audit section below.
- Calls already scored with version 1 were re-marked with `python -m earnings.finbert remark`: 92 calls, 358 marks updated, nothing rescored. Full scoring was restarted with version 2.
- The secret scan ignores the two false positives. Product Section 11 lists the confirmed columns.
- The 20 example calls were drawn with version 1. Of the rule's matches, version 2 changes only calls that lost more than 13 sentences.
