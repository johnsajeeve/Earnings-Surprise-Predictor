"""Sentences, the safe-harbour rule and stored FinBERT scores (Feature Engineering FE-01 to FE-07,
FE-29; Product FR-16).

Every transcript here is SYNTHETIC. The splitter and the scorer are stand-ins, so these tests run
without the model packages; tests/test_sentence_models.py uses the real ones.
"""

import json
import re

import pytest
from sqlalchemy import text

from earnings import finbert as fb
from earnings import licensing as lic
from earnings import sentences as sn

CID = "0000000001"


def split_on_stops(texts):  # stand-in splitter: a sentence ends at . ? or !
    return [[s.strip() for s in re.findall(r"[^.?!]+[.?!]?", t) if s.strip()] for t in texts]


class FakeScorer:
    """SYNTHETIC scores: fixed by the words of the sentence. Records what it was asked."""

    def __init__(self, revision="r1"):
        self.revision, self.asked = revision, []

    def score(self, texts):
        self.asked.extend(texts)
        out = []
        for t in texts:
            if "grew" in t:
                p = (0.9, 0.05, 0.05)
            elif "fell" in t:
                p = (0.1, 0.7, 0.2)
            else:
                p = (0.2, 0.1, 0.7)
            out.append(fb.Score(*p, truncated=len(t) > 80))
        return out


def turn(speaker, role, section, body):
    return {"speaker": speaker, "role": role, "section": section, "text": body}


HARBOUR = (
    "Today's call includes forward-looking statements. Results may differ. "
    "Actual results could vary for many reasons."
)
TURNS = [
    turn("Operator", "operator", "prepared", "Good day. Please stand by."),
    turn("Ida Row", "management", "prepared", f"Welcome all. {HARBOUR} Now to our chief."),
    turn("Max Poe", "management", "prepared", "Revenue grew. Margin fell."),
    turn("Operator", "operator", "qa", "First question."),
    turn("Ann Lee", "analyst", "qa", "Did actual results include a safe harbor sale?"),
    turn("Max Poe", "management", "qa", "Sales grew."),
]


def store(engine, turns, ref="synthetic-1"):
    """A SYNTHETIC stored transcript with its sections. Returns its id."""
    sections = {
        k: "\n\n".join(f"{t['speaker']}: {t['text']}" for t in turns if t["section"] == k)
        for k in ("prepared", "qa")
    }
    cleaned = "\n\n".join(v for v in sections.values() if v)
    with engine.begin() as conn:
        conn.execute(
            text("INSERT INTO company VALUES (:c, 'Northwind Widgets') ON CONFLICT DO NOTHING"),
            {"c": CID},
        )
        tid = conn.execute(
            text("INSERT INTO transcript (company_id, ticker, call_date, source, source_ref, "
                 "release_accession, release_accepted_at, raw_text, raw_hash, cleaned_text, "
                 "cleaning_rules_version, turns, segmentation_status, boundary_turn) VALUES "
                 "(:c, 'SYNW', '2020-01-01', 's', :r, :r, now(), :x, :h, :x, '1', "
                 "CAST(:t AS jsonb), 'failed', NULL) RETURNING transcript_id"),
            {"c": CID, "r": ref, "x": cleaned, "h": "a" * 64, "t": json.dumps(turns)},
        ).scalar_one()  # fmt: skip
        for kind, body in sections.items():
            if body:
                conn.execute(
                    text("INSERT INTO transcript_section (transcript_id, kind, text) "
                         "VALUES (:t, :k, :x)"), {"t": tid, "k": kind, "x": body},
                )  # fmt: skip
    return tid


def rows(engine, columns="*", order="model_revision, position"):
    with engine.connect() as conn:
        return conn.execute(
            text(f"SELECT {columns} FROM transcript_sentence ORDER BY {order}")
        ).all()


@pytest.fixture
def worker(test_db):
    from earnings.db import get_engine

    return get_engine("worker")


@pytest.mark.req("FE-02")
@pytest.mark.code("src/earnings/sentences.py")
def test_the_safe_harbour_span_starts_and_ends_on_the_approved_phrases():
    texts = ["Hello.", "This has FORWARD-LOOKING STATEMENTS.", "Things may change.",
             "See our SEC filings.", "Now the numbers."]  # fmt: skip
    assert sn.safe_harbour_span(texts) == range(1, 4)  # the sentence in between is inside
    assert sn.safe_harbour_span(["Under the safe harbour rules.", "Numbers."]) == range(0, 1)
    assert sn.safe_harbour_span(["Safe harbor applies.", "No obligation to update."]) == range(0, 2)
    # a closing phrase alone starts nothing
    assert sn.safe_harbour_span(["Actual results beat the plan.", "Risk factors fell."]) == range(0)
    assert sn.SAFE_HARBOUR_RULE_VERSION == "2"
    filler = [f"Point {i}." for i in range(20)]
    for distance, last in ((12, 12), (13, 0)):  # the closing phrase counts up to 12 sentences on
        texts = ["Safe harbor applies.", *filler]
        texts[distance] = "Actual results may differ."
        assert sn.safe_harbour_span(texts) == range(0, last + 1)


@pytest.mark.req("FE-02")
@pytest.mark.code("src/earnings/sentences.py")
def test_operator_turns_and_the_safe_harbour_passage_do_not_count_for_text_features():
    found = sn.sentences(TURNS, split_on_stops)
    assert [s.text for s in found if not s.analytic] == [
        "Good day.", "Please stand by.",
        "Today's call includes forward-looking statements.", "Results may differ.",
        "Actual results could vary for many reasons.", "First question.",
    ]  # fmt: skip
    # the rule is for prepared remarks: the analyst's question with the same words counts
    assert next(s for s in found if s.speaker == "Ann Lee").analytic
    # the text that counts is the same with and without the safe-harbour passage
    without = [dict(t, text=t["text"].replace(HARBOUR + " ", "")) for t in TURNS]
    counted = [s.text for s in sn.sentences(without, split_on_stops) if s.analytic]
    assert counted == [s.text for s in found if s.analytic]
    assert [s.position for s in found] == list(range(len(found)))


@pytest.mark.req("FE-02")
@pytest.mark.code("src/earnings/sentences.py")
def test_lists_of_who_is_on_the_call_do_not_count_for_text_features():
    turns = [
        turn("Executives", "management", "prepared", "Max Poe - Chief. Ida Row - Investors."),
        turn("Analysts", "analyst", "prepared", "Ann Lee - Some Bank."),
        turn("Max Poe", "management", "prepared", "Revenue grew."),
    ]
    found = sn.sentences(turns, split_on_stops)
    assert [s.text for s in found if s.analytic] == ["Revenue grew."]


@pytest.mark.req("FE-02", "FR-16")
@pytest.mark.code("src/earnings/finbert.py")
def test_new_marking_rules_reach_stored_calls_without_scoring_anything(worker):
    tid = store(worker, TURNS)
    fb.score_transcript(worker, tid, FakeScorer(), split_on_stops)
    right = rows(worker)
    with worker.begin() as conn:  # as if an older rule had counted everything
        conn.execute(text("UPDATE transcript_sentence SET analytic = true"))
    result = fb.remark(worker, "r1", split_on_stops)
    assert result["marks_updated"] == sum(not r.analytic for r in right) and not result["failed"]
    assert rows(worker) == right
    with worker.begin() as conn:  # changed text is not scored here
        conn.execute(text("UPDATE transcript SET turns = jsonb_set(turns, '{2,text}', "
                          "'\"Revenue fell.\"')"))  # fmt: skip
    assert fb.remark(worker, "r1", split_on_stops)["failed"] == [tid]
    assert rows(worker) == right


@pytest.mark.req("FE-29-AC1", "FR-16-AC1", "FE-05-AC1")
@pytest.mark.code("src/earnings/finbert.py", "src/earnings/migrations/versions")
def test_scoring_twice_writes_nothing_and_scores_no_sentence_again(worker):
    tid = store(worker, TURNS)
    scorer = FakeScorer()
    first = fb.score_transcript(worker, tid, scorer, split_on_stops)
    before = rows(worker)
    assert first["scored"] == len(before) == len(sn.sentences(TURNS, split_on_stops))
    asked = len(scorer.asked)
    assert fb.score_transcript(worker, tid, scorer, split_on_stops)["scored"] == 0
    assert rows(worker) == before and len(scorer.asked) == asked
    assert all(r.model_revision == "r1" for r in before)
    assert fb.pending(worker, "r1") == []


@pytest.mark.req("FE-05-AC1")
@pytest.mark.code("src/earnings/migrations/versions")
def test_the_database_refuses_a_score_without_a_model_revision(worker):
    from sqlalchemy.exc import IntegrityError

    tid = store(worker, TURNS)
    for revision in (None, ""):
        with pytest.raises(IntegrityError):
            fb.score_transcript(worker, tid, FakeScorer(revision), split_on_stops)
    assert rows(worker) == []


@pytest.mark.req("FR-16-AC2")
@pytest.mark.code("src/earnings/finbert.py")
def test_a_new_model_revision_rescores_and_keeps_the_old_scores(worker):
    tid = store(worker, TURNS)
    fb.score_transcript(worker, tid, FakeScorer("r1"), split_on_stops)
    old = rows(worker)
    assert fb.pending(worker, "r2") == [tid]
    new = FakeScorer("r2")
    assert fb.score_transcript(worker, tid, new, split_on_stops)["scored"] == len(old)
    both = rows(worker)
    assert [r for r in both if r.model_revision == "r1"] == old
    assert len([r for r in both if r.model_revision == "r2"]) == len(old)


@pytest.mark.req("FR-16", "FE-29")
@pytest.mark.code("src/earnings/finbert.py")
def test_changed_marks_are_updated_without_rescoring_and_changed_text_is_rescored(worker):
    tid = store(worker, TURNS)
    scorer = FakeScorer()
    fb.score_transcript(worker, tid, scorer, split_on_stops)
    asked = len(scorer.asked)

    def update_turns(turns):
        with worker.begin() as conn:
            conn.execute(
                text("UPDATE transcript SET turns = CAST(:j AS jsonb) WHERE transcript_id = :t"),
                {"j": json.dumps(turns), "t": tid},
            )

    changed = [dict(t) for t in TURNS]
    changed[4]["role"] = "unknown"
    update_turns(changed)
    result = fb.score_transcript(worker, tid, scorer, split_on_stops)
    assert result["marks_updated"] == 1 and result["scored"] == 0 and len(scorer.asked) == asked
    assert [r.role for r in rows(worker) if r.speaker == "Ann Lee"] == ["unknown"]
    changed[5]["text"] = "Sales fell."
    update_turns(changed)
    assert fb.score_transcript(worker, tid, scorer, split_on_stops)["scored"] > 0
    stored = rows(worker)
    assert [r.text for r in stored][-1] == "Sales fell." and stored[-1].finbert_negative == 0.7
    assert "Sales grew." not in [r.text for r in stored]
    update_turns(changed[:-1])  # now one sentence fewer: nothing is deleted or half replaced
    with pytest.raises(fb.FewerSentences):
        fb.score_transcript(worker, tid, scorer, split_on_stops)
    assert rows(worker) == stored


@pytest.mark.req("FE-29", "EQ-07")
@pytest.mark.code("src/earnings/finbert.py")
def test_a_failing_transcript_stores_nothing_and_the_others_are_still_scored(worker, caplog):
    bad, good = store(worker, TURNS, "synthetic-bad"), store(worker, TURNS[2:3], "synthetic-good")

    class Failing(FakeScorer):
        def score(self, texts):
            if len(texts) > 2:
                raise RuntimeError("injected scoring failure")
            return super().score(texts)

    result = fb.score_many(worker, [bad, good], Failing(), split_on_stops)
    assert result["failed"] == [bad] and result["sentences_scored"] == 2
    assert {r.transcript_id for r in rows(worker)} == {good}
    assert "injected scoring failure" in caplog.text
    assert fb.pending(worker, "r1") == [bad]  # a later run takes it up again


@pytest.mark.req("FE-07-AC1")
@pytest.mark.code("src/earnings/finbert.py")
def test_call_scores_are_the_plain_mean_of_the_sentences_that_count(worker):
    turns = [
        turn("Operator", "operator", "prepared", "Profit fell."),  # does not count
        turn("Max Poe", "management", "prepared", "Revenue grew. Margin fell. We met."),
    ]
    tid = store(worker, turns)
    fb.score_transcript(worker, tid, FakeScorer(), split_on_stops)
    # by hand: positive (0.9 + 0.1 + 0.2) / 3, negative (0.05 + 0.7 + 0.1) / 3, neutral the rest
    assert fb.call_means(worker, tid, "r1") == {
        "sentences": 3, "positive": 0.4, "negative": 0.2833, "neutral": 0.3167,
    }  # fmt: skip
    assert fb.call_means(worker, tid, "other-revision") is None  # unavailable, not zero


@pytest.mark.req("FE-04", "TX-06")
@pytest.mark.code("src/earnings/finbert.py", "src/earnings/sentences.py")
def test_a_call_without_speaker_roles_still_gets_scores_and_says_the_roles_are_unknown(worker):
    turns = [turn("Voice A", "unknown", "prepared", "Revenue grew. Margin fell.")]
    tid = store(worker, turns)
    fb.score_transcript(worker, tid, FakeScorer(), split_on_stops)
    assert {r.role for r in rows(worker)} == {"unknown"}
    assert fb.call_means(worker, tid, "r1")["sentences"] == 2


@pytest.mark.req("FE-06")
@pytest.mark.code("src/earnings/finbert.py")
def test_the_cut_flag_of_a_sentence_is_stored(worker):
    long_sentence = "Revenue grew " + "and grew " * 12 + "again."
    tid = store(worker, [turn("Max Poe", "management", "prepared", f"{long_sentence} We met.")])
    fb.score_transcript(worker, tid, FakeScorer(), split_on_stops)
    assert [r.truncated for r in rows(worker)] == [True, False]


@pytest.mark.req("FE-29-AC1")
@pytest.mark.code("src/earnings/tasks.py")
def test_the_scoring_task_run_twice_leaves_the_same_rows(worker, monkeypatch):
    from earnings import tasks

    tid = store(worker, TURNS)
    monkeypatch.setattr(tasks, "_scorer", lambda: FakeScorer(fb.REVISION))
    original = fb.score_transcript
    monkeypatch.setattr(
        tasks.finbert, "score_transcript", lambda e, t, s: original(e, t, s, split_on_stops)
    )
    assert tasks.score_transcript.apply(args=[tid]).get()["scored"] > 0
    before = rows(worker)
    assert tasks.score_transcript.apply(args=[tid]).get()["scored"] == 0
    assert rows(worker) == before


@pytest.mark.req("FE-05-AC2", "ET-03")
@pytest.mark.code("src/earnings/finbert.py", "src/earnings/third_party_register.csv")
def test_the_checkpoint_in_the_code_is_the_one_in_the_register_with_its_licence():
    row = next(r for r in lic.third_party() if r["component"] == fb.MODEL_ID)
    assert row["version"] == fb.REVISION and len(fb.REVISION) == 40
    assert row["licence"] == "CC BY-NC-SA 4.0" and row["training_data_licence"]
