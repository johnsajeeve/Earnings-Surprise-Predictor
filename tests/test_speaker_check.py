"""A call must be the company's own, and participant lists are not speech (Ingestion IG-14, IG-18;
Data TX-01; drift DR-23 and DR-37; decision C-62).

All names and text here are SYNTHETIC, shaped like the real cases: a source that files an acquired
company's calls under the buyer, and calls that begin with a list of participants.
"""

import pytest

from earnings import speaker
from earnings import transcripts as tr


def _turns(*pairs):
    return [{"speaker": s, "text": t} for s, t in pairs]


LISTED = _turns(
    ("Executives", "Ada Byrne - Head of IR Cal Dorn - CFO"),
    ("Analysts", "Eli Fox - Some Bank"),
    ("Operator", "Welcome. A question-and-answer session will follow the remarks."),
    ("Ada Byrne", "Good morning."),
    ("Cal Dorn", "Our results."),
    ("Operator", "[Operator Instructions] Our first question comes from Eli Fox."),
    ("Eli Fox", "My question?"),
    ("Cal Dorn", "An answer."),
)


@pytest.mark.req("IG-18", "FR-15", "TX-06")
@pytest.mark.code("src/earnings/transcripts.py")
def test_participant_lists_are_not_speaking_turns_when_the_boundary_is_found():
    # real: 1,007 calls had the boundary on the opening announcement because the two lists counted
    assert tr.find_boundary(LISTED) == 5
    labelled = tr.label_turns(LISTED, 5)
    assert [t["section"] for t in labelled] == ["prepared"] * 5 + ["qa"] * 3
    roles = {t["speaker"]: t["role"] for t in labelled}
    assert roles["Ada Byrne"] == roles["Cal Dorn"] == "management"
    assert roles["Eli Fox"] == "analyst"


@pytest.mark.req("IG-14", "TX-01")
@pytest.mark.code("src/earnings/speaker.py")
def test_a_call_is_the_companys_when_its_opening_names_it_not_when_another_does():
    pattern = speaker.name_pattern(["Northwind Widgets, Inc.", "Contoso Holdings", "NWW"])
    assert speaker.names_company(pattern, "Welcome to the Northwind Widgets earnings call.")
    assert speaker.names_company(pattern, "Welcome to Contoso's third quarter call.")  # former name
    assert speaker.names_company(pattern, "This is the NWW results call.")  # reviewed brand name
    assert not speaker.names_company(pattern, "Welcome to the Fabrikam earnings call.")
    assert not speaker.names_company(
        pattern, "Welcome to the call. " + "x " * 4000 + "Northwind Widgets"
    )
    assert not speaker.names_company(pattern, "Welcome to the Northwindows call.")  # whole words


@pytest.mark.req("IG-14", "TX-01")
@pytest.mark.code("src/earnings/speaker.py")
def test_a_call_that_never_says_the_name_needs_two_of_the_companys_own_managers():
    managers = speaker.executives(LISTED)
    assert managers == {"ada byrne", "cal dorn"}  # no operator, no list, no analyst
    known = {"ada byrne", "cal dorn", "gil hart"}
    assert speaker.accepted(False, {"ada byrne", "cal dorn"}, known, False)
    assert not speaker.accepted(
        False, {"ada byrne", "zed other"}, known, False
    )  # one is not enough
    assert not speaker.accepted(False, {"zed other", "yan more"}, known, False)
    assert speaker.accepted(True, set(), known, False)  # the name is enough by itself
    assert speaker.accepted(False, set(), known, True)  # a reviewed exception
    middle = _turns(("Operator", "Hi."), ("Cal J. Dorn - CFO", "a"), ("Ada Byrne", "b"),
                    ("Operator", "First question."), ("Q Person", "q"))  # fmt: skip
    assert speaker.executives(middle) == {"cal dorn", "ada byrne"}  # initials and titles dropped
