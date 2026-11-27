"""Licence rules over the two registers (Licensing LC-01 to LC-11; Data SR-01, SR-03;
Project-Wide ET-03).

`source_register.csv` lists every dataset and `third_party_register.csv` every library, container
image, model and word list. A class says what the licence or terms allow. This is a record of what
the pages said on the date given. It is not legal advice.
"""

import csv
import re
from datetime import date
from pathlib import Path

HERE = Path(__file__).parent
DATASETS = HERE / "source_register.csv"
THIRD_PARTY = HERE / "third_party_register.csv"

CLASSES = {
    "permissive": "reuse, change and redistribution allowed, with notices",
    "public-information": "government information the publisher says may be reused",
    "weak-copyleft": "a library used unchanged; changes to the library itself must be shared",
    "share-alike": "reuse allowed with attribution; adaptations carry the same licence",
    "non-commercial": "no commercial use",
    "source-available": "source can be read and used with limits; not an open-source licence",
    "restricted": "terms limit the use, for example personal or academic use only",
    "unclear": "the statements conflict, or the origin or licence is not established",
}
# What may be put in a deployed or published bundle (LC-02). Share-alike is not permissive.
DEPLOYABLE_DATA = frozenset({"permissive", "public-information"})
# What may be committed to the public repository: share-alike only with its attribution (LC-06).
REDISTRIBUTABLE_DATA = frozenset({"permissive", "public-information", "share-alike"})
# What a library or image may be for use in a deployed system (LC-11).
ALLOWED_SOFTWARE = frozenset({"permissive", "weak-copyleft"})
RECHECK_DAYS = 90


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as fh:
        return list(csv.DictReader(fh))


def datasets() -> list[dict[str, str]]:
    return _read(DATASETS)


def third_party() -> list[dict[str, str]]:
    return _read(THIRD_PARTY)


def not_deployable_datasets(rows: list[dict[str, str]] | None = None) -> dict[str, str]:
    """Datasets in use whose licence class does not allow a deployed or published copy."""
    return {
        r["dataset_id"]: r["licence_class"]
        for r in (datasets() if rows is None else rows)
        if r["licence_class"] not in DEPLOYABLE_DATA
    }


# every source name the code uses, and the register rows it covers (LC-07)
SOURCE_DATASETS = {
    "sec-edgar": ("eps_actuals", "announcement_times", "fundamentals", "company_identifiers"),
    "hf-transcripts": ("transcripts_hf",),
    "yfinance": ("consensus_yfinance",),
    "yfinance-prices": ("prices_yfinance",),
    "github-fja05680-sp500": ("index_membership",),
    "wikipedia-sp500-history": ("removal_names_reasons",),
}
# sources whose published terms bar automated access without written permission (LC-08)
AUTOMATION_BARRED = frozenset({"consensus_yfinance", "prices_yfinance"})
# the dataset each scheduled job collects from; a job that collects nothing outside has none
JOB_DATASETS = {
    "capture-consensus": ("consensus_yfinance",),
    "check-8k": ("announcement_times",),
    "check-transcripts": ("transcripts_hf",),
    "data-gates": (),
}


def jobs_on_barred_sources(jobs: list[str]) -> list[str]:
    """Scheduled jobs that collect from a source whose terms bar automated collection (LC-08)."""
    return [j for j in jobs if AUTOMATION_BARRED & set(JOB_DATASETS.get(j, ()))]


def bundle_violations(manifest: list[str], rows: list[dict[str, str]] | None = None) -> list[str]:
    """Why a deployment bundle holding these dataset ids is not allowed (LC-04, SR-03, DP-13). An
    id with no register row is a violation too: nothing unregistered is deployed."""
    known = {r["dataset_id"]: r["licence_class"] for r in (datasets() if rows is None else rows)}
    out = []
    for dataset in manifest:
        if dataset not in known:
            out.append(f"{dataset}: not in the source register")
        elif known[dataset] not in DEPLOYABLE_DATA:
            out.append(f"{dataset}: licence class '{known[dataset]}' may not be deployed")
    return out


def software_exceptions(rows: list[dict[str, str]] | None = None) -> dict[str, str]:
    """Libraries and images in use whose class is not allowed for a deployed system (LC-11)."""
    return {
        r["component"]: r["licence_class"]
        for r in (third_party() if rows is None else rows)
        if r["kind"] in ("python-package", "container-image")
        and r["licence_class"] not in ALLOWED_SOFTWARE
    }


def locked_packages(lock_text: str) -> dict[str, str]:
    """{package: version} from a pinned requirements lock."""
    found = re.findall(r"^([A-Za-z0-9_.-]+)(?:\[[^\]]*\])?==([^\s;\\]+)", lock_text, re.M)
    return dict(found)


def stale_rows(rows: list[dict[str, str]], today: date, column: str) -> list[str]:
    """Rows whose licence check is older than RECHECK_DAYS, or has no date (LC-10)."""
    out = []
    for r in rows:
        key = r.get("dataset_id") or r.get("component") or "?"
        try:
            checked = date.fromisoformat(r[column])
        except (KeyError, ValueError):
            out.append(key)
            continue
        if (today - checked).days > RECHECK_DAYS:
            out.append(key)
    return out


def notices() -> str:
    """The attribution notices, built from the registers (LC-05)."""
    lines = [
        "# Third-party notices",
        "",
        "Built from the registers by `python -m earnings.licensing notices`. Do not edit by hand.",
        "A licence class records what the source's pages said when checked. "
        "It is not legal advice.",
        "",
        "## Data",
    ]
    for r in datasets():
        lines.append(f"- **{r['dataset']}**: {r['source']}. Class: {r['licence_class']}. "
                     f"{r['licence']}")  # fmt: skip
    lines += ["", "## Software, models and word lists"]
    for r in third_party():
        lines.append(f"- {r['component']} {r['version']} ({r['kind']}): {r['licence']}")
    return "\n".join(lines) + "\n"


def main(argv: list[str]) -> int:
    if len(argv) > 2 and argv[1] == "notices":
        Path(argv[2]).write_text(notices(), "utf-8")
        return 0
    print("not deployable data:", not_deployable_datasets())
    print("software exceptions:", software_exceptions())
    if len(argv) > 2 and argv[1] == "bundle":
        found = bundle_violations(argv[2:])
        print("\n".join(found) or "bundle allowed")
        return 1 if found else 0
    return 0


if __name__ == "__main__":
    import sys

    raise SystemExit(main(sys.argv))
