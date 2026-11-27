"""Is a transcript the company's own call? (Ingestion IG-14, Data TX-01; drift DR-37; decision
C-62.)

The transcript source files an acquired company's calls under the buyer's ticker and name, and a
release filed within three days does not rule them out, because both companies report in the same
weeks. So the call itself is checked: its opening must name the company (its names in the SEC data,
former ones included, and a short reviewed list of brand names), or at least two of its managers
must also be managers on calls of the company that do name it. Analysts do not count: they follow
many companies. A call that passes neither is rejected and listed.
"""

import csv
import re
from collections.abc import Iterable
from pathlib import Path

from earnings import transcripts as tr

HERE = Path(__file__).parent
OPENING_CHARS = 5000
SHARED_MANAGERS = 2
_SUFFIXES = re.compile(
    r"\b(inc|incorporated|corp|corporation|co|company|companies|ltd|limited|plc|holdings?|group|"
    r"the|de|md|nv|sa|ag|llc|lp|trust|new)\b"
)


def normalise(value: str) -> str:
    value = value.lower().replace("&", " and ")
    value = re.sub(r"/[a-z]+/?$", " ", value)  # SEC state suffixes such as /DE/
    value = re.sub(r"[^a-z0-9 ]+", " ", value.replace("'", "").replace("’", ""))
    return " ".join(_SUFFIXES.sub(" ", value).split())


def name_pattern(names: Iterable[str]) -> re.Pattern[str]:
    """One pattern for every name of a company, matched as whole words."""
    forms = sorted({n for n in map(normalise, names) if len(n.replace(" ", "")) >= 3},
                   key=len, reverse=True)  # fmt: skip
    if not forms:
        return re.compile(r"(?!x)x")  # matches nothing
    return re.compile(rf"(?<![a-z0-9])(?:{'|'.join(map(re.escape, forms))})s?(?![a-z0-9])")


def names_company(pattern: re.Pattern[str], text: str) -> bool:
    return bool(pattern.search(normalise(text[:OPENING_CHARS])))


def aliases() -> dict[str, list[str]]:
    """Brand names a company calls itself that its SEC names do not hold, each with a reason."""
    out: dict[str, list[str]] = {}
    with (HERE / "company_aliases.csv").open(encoding="utf-8", newline="") as fh:
        for row in csv.DictReader(fh):
            out.setdefault(row["company_id"], []).append(row["alias"])
    return out


def exceptions() -> list[str]:
    with (HERE / "speaker_exceptions.csv").open(encoding="utf-8", newline="") as fh:
        return [row["source_ref_suffix"] for row in csv.DictReader(fh)]


def executives(turns: list[dict[str, str]]) -> set[str]:
    """First and last name of each person who speaks before the questions start."""
    spoken = [t for t in turns if not tr.is_participant_list(t["speaker"])]
    boundary = tr.find_boundary(spoken)
    out = set()
    for turn in spoken[:boundary] if boundary is not None else []:
        if tr.is_operator(turn["speaker"]):
            continue
        parts = normalise(re.split(r" [-–] ", turn["speaker"])[0]).split()
        if len(parts) >= 2:
            out.add(f"{parts[0]} {parts[-1]}")
    return out


def accepted(named: bool, managers: set[str], known: set[str], excepted: bool) -> bool:
    return named or excepted or len(managers & known) >= SHARED_MANAGERS
