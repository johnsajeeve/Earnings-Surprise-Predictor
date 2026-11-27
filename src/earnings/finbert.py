"""FinBERT scores for every sentence, stored with the model revision
(Product FR-16; Feature Engineering FE-05, FE-06, FE-07, FE-09, FE-29).

The weights are ProsusAI/finbert at one pinned revision (decision C-54). Their licence is
CC BY-NC-SA 4.0, non-commercial: they are downloaded to the data volume and never committed.
A transcript already scored with this revision is not scored again unless its sentences changed.
"""

import hashlib
import json
import logging
import os
import platform
import sys
import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Protocol

from sqlalchemy import Engine, text

from earnings import sentences as sn

log = logging.getLogger(__name__)

MODEL_ID = "ProsusAI/finbert"
REVISION = "0bc2ac10dda6929bcb1f77ccc43c7ec5c424f031"
# of the files at that revision, as first downloaded on 27 November 2026
SHA256 = {
    "config.json": "f6449ddda85eb726207a40be59c0cd3bd4b142ccb27298d5e45f9ae3396b1abe",
    "model.safetensors": "e5897858ff819aad7629b96ce521ae5477952d03634ef5dd30ed2d76357a9f00",
    "special_tokens_map.json": "303df45a03609e4ead04bc3dc1536d0ab19b5358db685b6f3da123d05ec200e3",
    "tokenizer_config.json": "ffc7913f6084b138dad68de5a0c2f0ee25ac983709260901e01f53be5796b9d9",
    "vocab.txt": "07eced375cec144d27c900241f3e339478dec958f92fddbc551f295c992038a3",
}
FILES = list(SHA256)
MAX_TOKENS = 512
BATCH = 32
LABELS = ("positive", "negative", "neutral")


class FewerSentences(RuntimeError):
    """A changed transcript has fewer sentences than are stored for this revision."""


@dataclass(frozen=True)
class Score:
    positive: float
    negative: float
    neutral: float
    truncated: bool  # the sentence was longer than the model accepts and was cut (FE-06)


class Scorer(Protocol):
    revision: str

    def score(self, texts: Sequence[str]) -> list[Score]: ...


def model_dir() -> Path:
    from earnings.config import get_settings

    return Path(get_settings().data_dir) / "models" / "finbert"


def download(cache: Path) -> dict[str, Any]:
    """Fetch the pinned revision into the data volume. Safetensors weights only, so loading runs
    no code from the download."""
    from huggingface_hub import snapshot_download

    path = Path(snapshot_download(MODEL_ID, revision=REVISION, allow_patterns=FILES,
                                  cache_dir=cache))  # fmt: skip
    digests = {name: hashlib.sha256((path / name).read_bytes()).hexdigest() for name in FILES}
    changed = sorted(name for name in FILES if digests[name] != SHA256[name])
    if changed:
        raise RuntimeError(f"downloaded files differ from the pinned ones: {', '.join(changed)}")
    return {"model": MODEL_ID, "revision": REVISION, "path": str(path), "sha256": digests}


class FinBert:
    """The model in inference mode, loaded from the local copy only. Not fine-tuned (FE-05)."""

    revision = REVISION

    def __init__(self, cache: Path) -> None:
        import torch
        from huggingface_hub import snapshot_download
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        path = snapshot_download(MODEL_ID, revision=REVISION, allow_patterns=FILES,
                                 cache_dir=cache, local_files_only=True)  # fmt: skip
        self._torch = torch
        self._tokenizer = AutoTokenizer.from_pretrained(path)
        self._model = AutoModelForSequenceClassification.from_pretrained(
            path, use_safetensors=True
        ).eval()
        # the order of the three outputs is read from the model, never assumed
        names = {int(i): str(name).lower() for i, name in self._model.config.id2label.items()}
        self._order = [next(i for i, name in names.items() if name == label) for label in LABELS]

    def score(self, texts: Sequence[str]) -> list[Score]:
        if not texts:
            return []
        lengths = [len(ids) for ids in self._tokenizer(list(texts), truncation=False,
                                                       verbose=False)["input_ids"]]  # fmt: skip
        out: list[Score | None] = [None] * len(texts)
        by_length = sorted(range(len(texts)), key=lengths.__getitem__)  # less padding per batch
        for first in range(0, len(texts), BATCH):
            chosen = by_length[first : first + BATCH]
            encoded = self._tokenizer([texts[i] for i in chosen], padding=True, truncation=True,
                                      max_length=MAX_TOKENS, return_tensors="pt")  # fmt: skip
            with self._torch.inference_mode():
                probabilities = self._model(**encoded).logits.softmax(-1).tolist()
            for i, row in zip(chosen, probabilities, strict=True):
                positive, negative, neutral = (row[k] for k in self._order)
                out[i] = Score(positive, negative, neutral, lengths[i] > MAX_TOKENS)
        return [s for s in out if s is not None]


def score_transcript(
    engine: Engine, transcript_id: int, scorer: Scorer, split: sn.Splitter = sn.spacy_split
) -> dict[str, int]:
    """Split one transcript and store its scored sentences, all in one transaction.

    Run again, it writes nothing (FR-16, FE-29). If only the marks changed (analytic, role,
    section), they are updated and nothing is rescored. If the sentences themselves changed, the
    rows of this revision are replaced. Rows of other revisions are never touched."""
    with engine.connect() as conn:
        turns = conn.execute(
            text("SELECT turns FROM transcript WHERE transcript_id = :t"), {"t": transcript_id}
        ).scalar_one()
        sections = {
            r.kind: r.section_id
            for r in conn.execute(
                text("SELECT kind, section_id FROM transcript_section WHERE transcript_id = :t"),
                {"t": transcript_id},
            )
        }
        stored = conn.execute(
            text("SELECT position, text, speaker, role, analytic, section_id "
                 "FROM transcript_sentence WHERE transcript_id = :t AND model_revision = :r "
                 "ORDER BY position"),
            {"t": transcript_id, "r": scorer.revision},
        ).all()  # fmt: skip
    found = sn.sentences(turns, split)
    rows = [
        {"t": transcript_id, "s": sections[s.section], "p": s.position, "x": s.text,
         "sp": s.speaker, "ro": s.role, "a": s.analytic, "r": scorer.revision}
        for s in found
    ]  # fmt: skip
    if [(r.position, r.text) for r in stored] == [(row["p"], row["x"]) for row in rows]:
        changed = [
            row for row, old in zip(rows, stored, strict=True)
            if (row["sp"], row["ro"], row["a"], row["s"])
            != (old.speaker, old.role, old.analytic, old.section_id)
        ]  # fmt: skip
        if changed:
            with engine.begin() as conn:
                conn.execute(
                    text("UPDATE transcript_sentence SET speaker = :sp, role = :ro, "
                         "analytic = :a, section_id = :s WHERE transcript_id = :t "
                         "AND model_revision = :r AND position = :p"),
                    changed,
                )  # fmt: skip
        return {"scored": 0, "marks_updated": len(changed), "sentences": len(rows)}
    if len(stored) > len(rows):
        # replacing these would need rows deleted, which the worker role may not do (Database DB-02)
        raise FewerSentences(
            f"transcript {transcript_id} now has {len(rows)} sentences and {len(stored)} are "
            "stored; the stored rows were left as they are"
        )
    scores = scorer.score([s.text for s in found])
    for row, score in zip(rows, scores, strict=True):
        row.update(pos=score.positive, neg=score.negative, neu=score.neutral, tr=score.truncated)
    if rows:
        with engine.begin() as conn:
            conn.execute(
                text("INSERT INTO transcript_sentence (transcript_id, section_id, position, text, "
                     "speaker, role, analytic, truncated, finbert_positive, finbert_negative, "
                     "finbert_neutral, model_revision) VALUES (:t, :s, :p, :x, :sp, :ro, :a, :tr, "
                     ":pos, :neg, :neu, :r) "
                     "ON CONFLICT ON CONSTRAINT sentence_one_place DO UPDATE SET "
                     "section_id = excluded.section_id, text = excluded.text, "
                     "speaker = excluded.speaker, role = excluded.role, "
                     "analytic = excluded.analytic, truncated = excluded.truncated, "
                     "finbert_positive = excluded.finbert_positive, "
                     "finbert_negative = excluded.finbert_negative, "
                     "finbert_neutral = excluded.finbert_neutral"),
                rows,
            )  # fmt: skip
    return {"scored": len(rows), "marks_updated": 0, "sentences": len(rows)}


def call_means(engine: Engine, transcript_id: int, revision: str = REVISION) -> dict | None:
    """The unweighted mean of each class over the call's analytic sentences, to four decimals
    (FE-07). None when the call has no scored analytic sentence: unavailable, not zero."""
    with engine.connect() as conn:
        row = conn.execute(
            text("SELECT count(*), avg(finbert_positive), avg(finbert_negative), "
                 "avg(finbert_neutral) FROM transcript_sentence WHERE transcript_id = :t "
                 "AND model_revision = :r AND analytic"),
            {"t": transcript_id, "r": revision},
        ).one()  # fmt: skip
    if not row[0]:
        return None
    means = {k: round(float(v), 4) for k, v in zip(LABELS, row[1:], strict=True)}
    return {"sentences": row[0], **means}


def pending(engine: Engine, revision: str = REVISION) -> list[int]:
    """Kept transcripts with no sentence scored by this revision, oldest call first."""
    with engine.connect() as conn:
        return list(
            conn.execute(
                text("SELECT transcript_id FROM transcript t WHERE status = 'kept' AND NOT EXISTS "
                     "(SELECT 1 FROM transcript_sentence s WHERE s.transcript_id = "
                     "t.transcript_id AND s.model_revision = :r) "
                     "ORDER BY call_date, transcript_id"),
                {"r": revision},
            ).scalars()
        )  # fmt: skip


class NoScoring:
    """A scorer that refuses, so that updating marks can never score a sentence."""

    def __init__(self, revision: str) -> None:
        self.revision = revision

    def score(self, texts: Sequence[str]) -> list[Score]:
        raise RuntimeError("the sentences changed: score them with the score command")


def remark(
    engine: Engine, revision: str = REVISION, split: sn.Splitter = sn.spacy_split
) -> dict[str, Any]:
    """Apply the current marking rules to the calls already scored, without scoring anything."""
    with engine.connect() as conn:
        ids = list(
            conn.execute(
                text("SELECT DISTINCT transcript_id FROM transcript_sentence "
                     "WHERE model_revision = :r ORDER BY transcript_id"),
                {"r": revision},
            ).scalars()
        )  # fmt: skip
    updated, failed = 0, []
    for transcript_id in ids:
        try:
            result = score_transcript(engine, transcript_id, NoScoring(revision), split)
            updated += result["marks_updated"]
        except Exception as exc:  # noqa: BLE001  one failing transcript must not stop the others
            log.error("marking failed for transcript %s: %s", transcript_id, exc)
            failed.append(transcript_id)
    return {"transcripts": len(ids), "marks_updated": updated, "failed": failed,
            "safe_harbour_rule": sn.SAFE_HARBOUR_RULE_VERSION}  # fmt: skip


def hardware() -> dict[str, Any]:
    cpu = ""
    info = Path("/proc/cpuinfo")
    if info.exists():
        cpu = next((line.split(":", 1)[1].strip() for line in info.read_text().splitlines()
                    if line.startswith("model name")), "")  # fmt: skip
    memory = os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
    return {"cpu": cpu or platform.processor(), "logical_cpus": os.cpu_count(),
            "memory_gb": round(memory / 2**30, 1)}  # fmt: skip


def score_many(
    engine: Engine, ids: list[int], scorer: Scorer, split: sn.Splitter = sn.spacy_split,
    every: int = 25,
) -> dict[str, Any]:  # fmt: skip
    """Score transcripts one by one. A failure is logged and listed, and the others go on. Each
    transcript is committed on its own, so a stopped run continues where it left off."""
    started, scored, failed = time.monotonic(), 0, []
    for number, transcript_id in enumerate(ids, 1):
        try:
            scored += score_transcript(engine, transcript_id, scorer, split)["scored"]
        except Exception as exc:  # noqa: BLE001  one failing transcript must not stop the others
            log.error("scoring failed for transcript %s: %s: %s", transcript_id,
                      type(exc).__name__, exc)  # fmt: skip
            failed.append(transcript_id)
        if number % every == 0 or number == len(ids):
            spent = time.monotonic() - started
            log.info("%d of %d transcripts, %d sentences, %.1f sentences a second", number,
                     len(ids), scored, scored / spent if spent else 0)  # fmt: skip
    seconds = time.monotonic() - started
    return {"transcripts": len(ids), "failed": failed, "sentences_scored": scored,
            "seconds": round(seconds, 1),
            "sentences_per_second": round(scored / seconds, 1) if seconds else None}  # fmt: skip


def main(argv: list[str]) -> int:
    from earnings.db import get_engine
    from earnings.runlog import run_record

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    command = argv[1] if len(argv) > 1 else ""
    if command == "download":
        print(json.dumps(download(model_dir()), indent=1))
        return 0
    if command == "score":
        engine = get_engine("worker")
        ids = pending(engine)
        if len(argv) > 2:
            ids = ids[: int(argv[2])]
        scorer = FinBert(model_dir())
        with run_record(engine, "score-sentences", MODEL_ID) as run:
            result = score_many(engine, ids, scorer)
            run.rows_read, run.rows_written = len(ids), result["sentences_scored"]
        result |= {"revision": REVISION, "splitter": sn.splitter_version(),
                   "safe_harbour_rule": sn.SAFE_HARBOUR_RULE_VERSION,
                   "hardware": hardware()}  # fmt: skip
        print(json.dumps(result, indent=1))
        return 1 if result["failed"] else 0
    if command == "remark":
        result = remark(get_engine("worker"))
        print(json.dumps(result, indent=1))
        return 1 if result["failed"] else 0
    print("python -m earnings.finbert download | score [HOW_MANY] | remark")
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
