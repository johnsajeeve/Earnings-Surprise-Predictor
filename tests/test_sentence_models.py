"""The real spaCy model and the real FinBERT weights (Feature Engineering FE-01, FE-03, FE-06).

The text is SYNTHETIC. These run in the worker image only. The FinBERT tests also need the weights
in the data volume, so they run on the owner's machine and are skipped in continuous integration.
"""

import pytest

from earnings import finbert as fb
from earnings import sentences as sn
from earnings.transcripts import clean_text
from requirement_support import not_tested


def need_spacy():
    try:
        sn.splitter_version()
        import spacy  # noqa: F401
    except ImportError:  # PackageNotFoundError is a kind of ImportError
        not_tested("NOT IMPLEMENTED", "spaCy is installed in the worker image only")


# SYNTHETIC: six sentences, with the decimal points, abbreviations and quotes that trip splitters
RAW = [
    "Good  morning, and welcome to the call.   Revenue was $4.2 billion, up 3.5% in the U.S. "
    "market.",
    "Our CFO, Dr. Poe, said “margins held”.\nWe expect growth next year.",
    "What drove the change in inventory? Thank you.",
]


def turns():
    return [
        {"speaker": "Max Poe", "role": "management", "section": "prepared",
         "text": clean_text(t)}
        for t in RAW
    ]  # fmt: skip


@pytest.mark.req("FE-01-AC1", "FE-01-AC2")
@pytest.mark.code("src/earnings/sentences.py")
def test_a_known_text_gives_the_known_number_of_sentences_every_time():
    need_spacy()
    first = sn.sentences(turns())
    assert len(first) == 6, [s.text for s in first]
    assert sn.sentences(turns()) == first
    assert sn.splitter_version() == "spacy 3.8.18; en_core_web_sm 3.8.0"


@pytest.mark.req("FE-03-AC1")
@pytest.mark.code("src/earnings/sentences.py", "src/earnings/transcripts.py")
def test_every_sentence_is_found_in_the_cleaned_text_by_exact_match():
    need_spacy()
    cleaned = clean_text("\n\n".join(f"Max Poe: {t}" for t in RAW))
    assert all(s.text in cleaned for s in sn.sentences(turns()))


def need_weights():
    try:
        from earnings.config import get_settings

        get_settings()
        return fb.FinBert(fb.model_dir())
    except ImportError:
        not_tested("NOT IMPLEMENTED", "PyTorch and Transformers are in the worker image only")
    except OSError:
        not_tested("NEEDS MEASUREMENT", "the FinBERT weights are not in this environment")


@pytest.mark.req("FE-06-AC1", "FE-05")
@pytest.mark.code("src/earnings/finbert.py")
def test_a_sentence_longer_than_the_model_accepts_is_cut_and_flagged():
    scorer = need_weights()
    long_sentence = "revenue " * 600 + "grew."
    short, long_ = scorer.score(["Revenue grew.", long_sentence])
    assert not short.truncated and long_.truncated


@pytest.mark.req("FR-16", "FE-05")
@pytest.mark.code("src/earnings/finbert.py")
def test_the_three_scores_come_out_under_the_right_names_and_in_the_order_asked():
    scorer = need_weights()
    good, bad, flat = scorer.score(
        ["Profit rose sharply and beat expectations.", "Losses widened and sales collapsed.",
         "The meeting is on Tuesday."]
    )  # fmt: skip
    assert good.positive > 0.5 and bad.negative > 0.5 and flat.neutral > 0.5
    for s in (good, bad, flat):
        assert abs(s.positive + s.negative + s.neutral - 1) < 1e-5
