"""Sentences of a transcript, and which of them count for text features
(Feature Engineering FE-01 to FE-04).

A sentence is a slice of one speaker turn of the cleaned transcript, so it can be found again in the
cleaned text by exact match. Operator turns and the safe-harbour passage are marked non-analytic.
They are stored and scored, and left out of every text feature.
"""

import re
from collections.abc import Callable, Iterable
from dataclasses import dataclass, replace
from functools import lru_cache
from importlib.metadata import version
from typing import Any

SPACY_MODEL = "en_core_web_sm"
SAFE_HARBOUR_RULE_VERSION = "1"  # the rule John approved on 27 November 2026 (decision C-67)
_HARBOUR_START = re.compile(r"forward-looking statement|safe harbor|safe harbour", re.IGNORECASE)
_HARBOUR_END = re.compile(
    r"forward-looking|safe harbor|actual results|risk factors|SEC filings|"
    r"securities and exchange commission|no obligation to update",
    re.IGNORECASE,
)

# text of one turn -> its sentences, in order, each a slice of that text
Splitter = Callable[[list[str]], Iterable[list[str]]]


@dataclass(frozen=True)
class Sentence:
    position: int  # 0-based, over the whole call
    turn: int
    section: str  # prepared or qa
    speaker: str
    role: str  # management, analyst, operator or unknown (FE-04, TX-06)
    text: str
    analytic: bool


@lru_cache(maxsize=1)
def _pipeline() -> Any:
    import spacy

    # the dependency parser sets the sentence boundaries; the other parts are not needed here
    return spacy.load(SPACY_MODEL, disable=["tagger", "attribute_ruler", "lemmatizer", "ner"])


def spacy_split(texts: list[str]) -> Iterable[list[str]]:
    for doc in _pipeline().pipe(texts, batch_size=64):
        yield [s for s in (span.text.strip() for span in doc.sents) if s]


def splitter_version() -> str:
    """The spaCy package and model versions, recorded with every run (FE-01)."""
    return f"spacy {version('spacy')}; {SPACY_MODEL} {version(SPACY_MODEL)}"


def safe_harbour_span(texts: list[str]) -> range:
    """Rule version 1, applied to the sentences of one prepared-remarks turn: from the first that
    names forward-looking statements or a safe harbour, through the last in the same turn that uses
    one of the closing phrases. Empty when the turn has no opening phrase."""
    start = next((i for i, t in enumerate(texts) if _HARBOUR_START.search(t)), None)
    if start is None:
        return range(0)
    ends = [i for i in range(start, len(texts)) if _HARBOUR_END.search(texts[i])]
    return range(start, (ends[-1] if ends else start) + 1)


def sentences(turns: list[dict[str, Any]], split: Splitter = spacy_split) -> list[Sentence]:
    """The sentences of a stored transcript, from its turns (speaker, role, section, text)."""
    out: list[Sentence] = []
    for index, (turn, texts) in enumerate(zip(turns, split([t["text"] for t in turns]),
                                              strict=True)):  # fmt: skip
        found = [
            Sentence(len(out) + i, index, turn["section"], turn["speaker"], turn["role"], text,
                     turn["role"] != "operator")
            for i, text in enumerate(texts)
        ]  # fmt: skip
        if turn["section"] == "prepared" and turn["role"] != "operator":
            for i in safe_harbour_span(texts):
                found[i] = replace(found[i], analytic=False)
        out.extend(found)
    return out
