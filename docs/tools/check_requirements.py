#!/usr/bin/env python3
"""Structural checks for the requirement documents (market, product, data, project-wide and the four component documents).

Run from anywhere:  python3 docs/tools/check_requirements.py

Checks:
 1. No requirement ID is defined twice.
 2. Every ID prefix is defined in the document that owns it (see requirements/README.md).
 3. Every cited ID is defined, or is listed as withdrawn.
 4. No withdrawn ID is cited in the requirement documents (except as history).
 5. "Product X", "Data X", "Project-Wide X", "Market X" citations point at the right document.
 6. Relative markdown links resolve.
It does not check meaning. Contradictions between documents still need a human read.
"""
import collections, os, re, sys

DOCS = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
REQ = os.path.join(DOCS, "requirements")
FILES = {"market": "market-requirements.md", "product": "product-requirements.md",
         "data": "data-requirements.md", "project-wide": "project-wide-requirements.md",
         "feature": "feature-engineering-requirements.md", "agent": "explanation-agent-requirements.md",
         "database": "database-requirements.md", "frontend": "frontend-requirements.md"}
OWNER = {
    "market": {"N"},
    "product": {"PG", "NG", "ST", "FR", "SRS", "EX", "NFR", "API", "PL", "ML", "TR", "MR", "UI"},
    "data": {"GATE", "SR", "TX", "AE", "CE", "LB", "IM", "SEC", "PX", "FD", "DV", "VL", "GS"},
    "project-wide": {"C", "ASM", "PD", "SS", "SC", "EQ", "SP", "ET", "OR", "AI", "DO"},
    "feature": {"FE"},
    "agent": {"AG"},
    "database": {"DB"},
    "frontend": {"UX"},
}
WITHDRAWN = ({f"MFR-{i:02d}" for i in range(1, 20)} | {f"MNFR-{i:02d}" for i in range(1, 8)} |
              {f"DR-{i:02d}" for i in range(1, 11)} |
              {"TR-03", "MR-03", "MR-07", "CP-01", "CP-02", "AD-01", "AD-02", "OP-01", "OP-02", "OP-03",
               "NFR-05", "NFR-06", "NFR-10"})
CITE = {"Product": "product", "Data": "data", "Project-Wide": "project-wide", "Market": "market",
        "Feature Engineering": "feature", "Explanation Agent": "agent", "Database": "database",
        "Frontend": "frontend"}


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def main():
    text = {k: read(os.path.join(REQ, f)) for k, f in FILES.items()}
    defs = collections.defaultdict(list)
    for k, t in text.items():
        for m in re.finditer(r"^\| ([A-Z]{1,5}-?\d+) \|", t, re.M):
            defs[m.group(1)].append(k)
        for m in re.finditer(r"^### ([A-Z]{2,4}-\d+):", t, re.M):
            defs[m.group(1)].append(k)
    problems = []

    dups = {k: v for k, v in defs.items() if len(v) > 1}
    if dups:
        problems.append(f"1 duplicate definitions: {dups}")

    misplaced = [(i, v[0]) for i, v in defs.items() if re.sub(r"-?\d+$", "", i) not in OWNER[v[0]]]
    if misplaced:
        problems.append(f"2 IDs in the wrong document: {misplaced}")

    alltext = "".join(text.values())
    cited = {r for r in re.findall(r"\b([A-Z]{1,5}-?\d+)\b", alltext) if re.match(r"^(N\d+|[A-Z]{2,5}-\d+)$", r)}
    undefined = sorted(r for r in cited if r not in defs and r not in WITHDRAWN
                       and r != "SHA-256" and not re.match(r"^(C|D)-\d", r))
    if undefined:
        problems.append(f"3 undefined IDs: {undefined}")

    stale = {}
    for k, t in text.items():
        for w in WITHDRAWN:
            n = len(re.findall(r"\b" + re.escape(w) + r"\b", t))
            if n:
                stale[(k, w)] = n
    # Historical mentions are allowed in the header line that explains the move.
    stale = {key: n for key, n in stale.items() if key not in {("data", "DR-01"), ("data", "DR-10")}}
    if stale:
        problems.append(f"4 withdrawn IDs still cited: {stale}")

    wrong = []
    for k, t in text.items():
        for m in re.finditer(r"\b(Product|Data|Project-Wide|Market|Feature Engineering|Explanation Agent|Database|Frontend) ([A-Z]{1,5}-?\d+)\b", t):
            i = m.group(2)
            if i in defs and CITE[m.group(1)] not in defs[i]:
                wrong.append((k, m.group(1), i, defs[i]))
    if wrong:
        problems.append(f"5 citations naming the wrong document: {wrong}")

    broken = []
    for root, _, files in os.walk(DOCS):
        for f in files:
            if f.endswith(".md"):
                p = os.path.join(root, f)
                for m in re.finditer(r"\]\(([^)#\s]+\.md)\)", read(p)):
                    if not os.path.exists(os.path.normpath(os.path.join(root, m.group(1)))):
                        broken.append((os.path.relpath(p, DOCS), m.group(1)))
    if broken:
        problems.append(f"6 broken links: {broken}")

    counts = {k: sum(1 for v in defs.values() if v[0] == k) for k in FILES}
    print("IDs defined:", counts)
    if problems:
        print("FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print("OK: checks 1 to 6 pass")
    return 0


if __name__ == "__main__":
    sys.exit(main())
