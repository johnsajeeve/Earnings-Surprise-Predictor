#!/usr/bin/env python3
"""Generate audits/requirements_traceability.md deterministically.

Run from anywhere:  python3 audits/generate_traceability.py

Inputs:
  - the twelve requirement documents in docs/requirements/ (read, never modified);
  - audits/assessments.py, which holds the audit findings made by inspecting the repository.
Outputs: requirements_traceability.md, acceptance_index.md and pending_values.md, the same every time for the same inputs. No timestamps are generated.

Every requirement found in the documents appears in the output. A requirement that has no entry in
ASSESSED is classified UNVERIFIED ("not assessed"), never PASS (rules: Deterministic_audit.md
Sections 7 and 8). ID discovery uses the same patterns as docs/tools/check_requirements.py, so the
counts should match it.
"""

import ast
import collections
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from assessments import ASSESSED  # noqa: E402  (the data file sits beside this script)

ROOT = os.path.normpath(os.path.join(HERE, ".."))
REQ = os.path.join(ROOT, "docs", "requirements")
OUT = os.path.join(HERE, "requirements_traceability.md")
OUT_AC = os.path.join(HERE, "acceptance_index.md")
OUT_PENDING = os.path.join(HERE, "pending_values.md")
TESTS = os.path.join(ROOT, "tests")
DECISIONS = os.path.join(ROOT, "docs", "decision-log.md")

DOCS = [
    ("market", "market-requirements.md", "Market"),
    ("product", "product-requirements.md", "Product"),
    ("data", "data-requirements.md", "Data"),
    ("project-wide", "project-wide-requirements.md", "Project-Wide"),
    ("feature", "feature-engineering-requirements.md", "Feature Engineering"),
    ("agent", "explanation-agent-requirements.md", "Explanation Agent"),
    ("database", "database-requirements.md", "Database"),
    ("frontend", "frontend-requirements.md", "Frontend"),
    ("ingestion", "ingestion-and-preparation-requirements.md", "Ingestion and Preparation"),
    ("modelling", "modelling-and-evaluation-requirements.md", "Modelling and Evaluation"),
    ("serving", "api-and-serving-requirements.md", "API and Serving"),
    ("deployment", "deployment-and-operations-requirements.md", "Deployment and Operations"),
]
PRIORITY = re.compile(r"^(Must if built|Must|Should|Could|Won't)\b")
NOT_ASSESSED = "Not assessed in this audit (scope: Docker skeleton). No evidence either way."


def read(path):
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def cells(line):
    parts = re.split(r"(?<!\\)\|", line.strip())
    return [c.strip() for c in parts[1:-1]]


def clean(text):
    return " ".join(text.split())


def parse(doc_key, text):
    found = {}
    for line in text.splitlines():
        m = re.match(r"^\| ([A-Z]{1,5}-?\d+) \|", line)
        if not m:
            continue
        c = cells(line)
        rid = c[0]
        if rid.startswith("ER-") and len(c) >= 4:
            priority, desc = "", f"{c[1]}. User sees {c[2]} System: {c[3]}"
        elif rid.startswith("EP-") and len(c) >= 4:
            priority, desc = "", f"{c[1]} {c[2]}: {c[3]}"
        elif rid.startswith("SCR-") and len(c) >= 5:
            priority, desc = c[4], f"{c[1]}: {c[2]}"
        elif (rid.startswith("SM-") or rid.startswith("TH-")) and len(c) >= 3:
            priority, desc = "", f"{c[1]}: {c[2]}"
        elif rid.startswith("GATE-"):
            priority, desc = "", c[1] if len(c) > 1 else ""
        elif rid.startswith("NFR-") and len(c) >= 4:
            priority, desc = c[1], c[2] + ": " + c[3]
        elif len(c) >= 3 and PRIORITY.match(c[1]):
            priority, desc = c[1], c[2]
        else:  # market needs and any table without a priority column
            priority, desc = "", c[1] if len(c) > 1 else ""
        found[rid] = (priority, clean(desc))
    # Requirements written as headings with Priority and Requirement lines (Product FR-xx).
    for m in re.finditer(
        r"^### ([A-Z]{2,4}-\d+):\s*(.*?)\n(.*?)(?=^#{2,3} |\Z)", text, re.M | re.S
    ):
        rid, title, body = m.group(1), m.group(2), m.group(3)
        pm = re.search(r"\*\*Priority\.\*\*\s*(Must if built|Must|Should|Could|Won't)", body)
        rm = re.search(r"\*\*Requirement\.\*\*\s*(.*?)(?=\n\s*\n|\n\*\*|\Z)", body, re.S)
        found[rid] = (pm.group(1) if pm else "", clean(rm.group(1)) if rm else clean(title))
    return found


def sort_key(rid):
    m = re.match(r"^([A-Z]+)-?(\d+)$", rid)
    return (m.group(1), int(m.group(2)))


def esc(text):
    return text.replace("|", "\\|")


SENTENCE_BREAK = re.compile(r"(?<=[.!?])\s+(?=[A-Z0-9(`\"'])")


def sentences(text):
    """Split an acceptance check into its separate checks, in order."""
    text = clean(text)
    if not text:
        return []
    return [p.strip() for p in SENTENCE_BREAK.split(text) if p.strip()]


def parse_acceptance(text):
    """id -> ordered list of acceptance checks. Derived, never hand-edited."""
    found = collections.OrderedDict()
    lines = text.splitlines()
    i = 0
    while i < len(lines):
        if (
            lines[i].startswith("|")
            and i + 1 < len(lines)
            and re.match(r"^\|[-| :]+\|$", lines[i + 1])
        ):
            header = [h.lower() for h in cells(lines[i])]
            col = next((k for k, h in enumerate(header) if h.startswith("acceptance")), None)
            if col is None and "threshold" in header and "area" in header:
                col = header.index("threshold")
            j = i + 2
            while j < len(lines) and lines[j].startswith("|"):
                c = cells(lines[j])
                rid = c[0] if c else ""
                if re.match(r"^[A-Z]{1,5}-\d+$", rid):
                    if rid.startswith("ER-") and len(c) >= 4:
                        found[rid] = [f"User sees {c[2]}", f"System: {c[3]}"]
                    elif rid.startswith("EP-") and len(c) >= 4:
                        found[rid] = [f"{c[1]} {c[2]}: {c[3]}"]
                    elif rid.startswith("SCR-") and len(c) >= 3:
                        found[rid] = [c[2]]
                    elif rid.startswith("SM-") and len(c) >= 4:
                        found[rid] = sentences(c[2]) + [f"Counter-metric: {c[3]}"]
                    elif rid.startswith("TH-") and len(c) >= 3:
                        found[rid] = [c[2]]
                    elif col is not None and col < len(c):
                        found[rid] = sentences(c[col])
                j += 1
            i = j
        else:
            i += 1
    for m in re.finditer(r"^### ([A-Z]{2,4}-\d+):.*?(?=^#{2,3} |\Z)", text, re.M | re.S):
        body = m.group(0)
        am = re.search(r"\*\*Acceptance criteria\.\*\*(.*?)(?=\n\*\*|\Z)", body, re.S)
        if am:
            bullets = [clean(b[2:]) for b in am.group(1).splitlines() if b.startswith("- ")]
            found[m.group(1)] = bullets or sentences(am.group(1))
    return found


def open_decisions():
    return set(re.findall(r"^\| (D-\d+) \|", read(DECISIONS), re.M))


def marked_tests():
    """requirement reference -> list of tests that carry pytest.mark.req(reference)."""
    found = collections.defaultdict(list)
    if not os.path.isdir(TESTS):
        return found
    for fname in sorted(os.listdir(TESTS)):
        if not fname.endswith(".py"):
            continue
        tree = ast.parse(read(os.path.join(TESTS, fname)))
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                for dec in node.decorator_list:
                    if (
                        isinstance(dec, ast.Call)
                        and isinstance(dec.func, ast.Attribute)
                        and dec.func.attr == "req"
                    ):
                        for arg in dec.args:
                            if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
                                found[arg.value].append(f"tests/{fname}::{node.name}")
    return found


def main():
    per_doc = collections.OrderedDict()
    for key, fname, _label in DOCS:
        per_doc[key] = parse(key, read(os.path.join(REQ, fname)))
    all_ids = {rid for d in per_doc.values() for rid in d}
    texts = {key: read(os.path.join(REQ, fname)) for key, fname, _label in DOCS}
    acceptance = collections.OrderedDict()
    for key, _fname, _label in DOCS:
        acceptance[key] = parse_acceptance(texts[key])
    valid_refs = {rid for d in acceptance.values() for rid in d}
    for d in acceptance.values():
        for rid, checks in d.items():
            valid_refs.update(f"{rid}-AC{n}" for n in range(1, len(checks) + 1))
    marks = marked_tests()
    bad = sorted(ref for ref in marks if ref not in valid_refs and ref not in all_ids)
    if bad:
        sys.exit(f"pytest.mark.req names references that no requirement document defines: {bad}")
    unknown = sorted(set(ASSESSED) - all_ids)
    if unknown:
        sys.exit(f"ASSESSED names IDs that no requirement document defines: {unknown}")

    counts = collections.Counter()
    sections = []
    for key, fname, label in DOCS:
        rows = [
            f"## {label} requirements ({fname})",
            "",
            "| ID | Priority | Original requirement | Implementation files | Test files | Status | Verification evidence |",
            "|---|---|---|---|---|---|---|",
        ]
        for rid in sorted(per_doc[key], key=sort_key):
            priority, desc = per_doc[key][rid]
            status, impl, tests, evidence = ASSESSED.get(
                rid, ("UNVERIFIED", "-", "-", NOT_ASSESSED)
            )
            marked = sorted(
                {
                    t
                    for ref, ts in marks.items()
                    if ref == rid or ref.startswith(rid + "-AC")
                    for t in ts
                }
            )
            if marked:
                tests = "; ".join(
                    ([] if tests in ("-", "none") or tests.startswith("none ") else [tests])
                    + [f"marked: {t}" for t in marked]
                )
            counts[status] += 1
            rows.append(
                f"| {rid} | {esc(priority) or '-'} | {esc(desc)} | {esc(impl)} | {esc(tests)} | {status} | {esc(evidence)} |"
            )
        sections.append("\n".join(rows))

    assessed_counts = collections.Counter(v[0] for v in ASSESSED.values())
    total = sum(len(d) for d in per_doc.values())
    head = [
        "# Requirements Traceability",
        "",
        "Generated by `audits/generate_traceability.py` from `docs/requirements/` and `audits/assessments.py`. Do not edit by hand: change the assessment data and run the script again.",
        "Evidence and commands: [initial audit](audit_2026-11-17.md) and [remediation and re-verification](remediation_2026-11-17.md).",
        "",
        "Classification (Deterministic_audit.md Section 8): PASS, PARTIAL, FAIL, BLOCKED, UNVERIFIED. A requirement is never COMPLETE without verification evidence.",
        "",
        "## Summary",
        "",
        f"- Requirements found in the twelve documents: {total} (market {len(per_doc['market'])}, product {len(per_doc['product'])}, data {len(per_doc['data'])}, project-wide {len(per_doc['project-wide'])}, feature engineering {len(per_doc['feature'])}, explanation agent {len(per_doc['agent'])}, database {len(per_doc['database'])}, frontend {len(per_doc['frontend'])}, ingestion and preparation {len(per_doc['ingestion'])}, modelling and evaluation {len(per_doc['modelling'])}, API and serving {len(per_doc['serving'])}, deployment and operations {len(per_doc['deployment'])}).",
        f"- Assessed in this audit: {len(ASSESSED)}. "
        + ", ".join(
            f"{k} {assessed_counts[k]}"
            for k in ("PASS", "PARTIAL", "FAIL", "BLOCKED", "UNVERIFIED")
        )
        + ".",
        f"- Not assessed (scope was the Docker skeleton), classified UNVERIFIED: {total - len(ASSESSED)}.",
        "- All rows: "
        + ", ".join(
            f"{k} {counts[k]}" for k in ("PASS", "PARTIAL", "FAIL", "BLOCKED", "UNVERIFIED")
        )
        + ".",
        "- **Overall project status: not PASS.** Mandatory requirements are FAIL, PARTIAL or UNVERIFIED (Section 8).",
        "",
    ]
    with open(OUT, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(head) + "\n" + "\n\n".join(sections) + "\n")

    # Acceptance index: the addressable checks that tests refer to (rid-ACn).
    ac_rows = [
        "# Acceptance Index",
        "",
        "Generated by `audits/generate_traceability.py` from `docs/requirements/`. Do not edit by hand.",
        'Every check of every requirement has a reference `ID-ACn`, numbered in the order it appears in the requirement document. A test names the check it exercises with `@pytest.mark.req("ID-ACn")`, or `@pytest.mark.req("ID")` for the whole requirement. A marker says what a test exercises. It does not say the requirement is satisfied. If a requirement\'s wording changes, this file changes, and CI fails until it is regenerated and the tests that name those references are reviewed.',
        "",
    ]
    n_checks = 0
    for key, fname, label in DOCS:
        ac_rows += [f"## {label} ({fname})", "", "| Reference | Check |", "|---|---|"]
        for rid in sorted(acceptance[key], key=sort_key):
            for n, check in enumerate(acceptance[key][rid], 1):
                ac_rows.append(f"| {rid}-AC{n} | {esc(check)} |")
                n_checks += 1
        ac_rows.append("")
    ac_rows += [
        "## Requirements with no check of their own",
        "",
        "These are goals, non-goals, stretch objectives, market needs, conflicts and gates. They are proved through the requirements that implement or resolve them, so a test does not name them directly. A test for one of them is a sign that a checkable requirement is missing.",
        "",
        "| Requirement |",
        "|---|",
    ]
    for key, _fname, _label in DOCS:
        for rid in sorted(set(per_doc[key]) - set(acceptance[key]), key=sort_key):
            ac_rows.append(f"| {rid} |")
    ac_rows.append("")
    with open(OUT_AC, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(ac_rows))

    # Pending values: requirements that depend on an open decision, so no build task treats them as final.
    open_ds = open_decisions()
    pend = collections.OrderedDict()
    for key, _fname, _label in DOCS:
        blocks = {}
        for line in texts[key].splitlines():
            m = re.match(r"^\| ([A-Z]{1,5}-\d+) \|", line)
            if m:
                blocks[m.group(1)] = line
        for m in re.finditer(r"^### ([A-Z]{2,4}-\d+):.*?(?=^#{2,3} |\Z)", texts[key], re.M | re.S):
            blocks[m.group(1)] = m.group(0)
        for rid, body in blocks.items():
            deps = sorted(
                {d for d in re.findall(r"\bD-\d+\b", body) if d in open_ds},
                key=lambda d: int(d[2:]),
            )
            if deps:
                pend[rid] = deps
    pv = [
        "# Pending Values",
        "",
        "Generated by `audits/generate_traceability.py` from `docs/requirements/` and the open decisions in `docs/decision-log.md`. Do not edit by hand.",
        "A requirement listed here cites a decision that is still open. Before a build task touches it, the task brief (Deterministic_audit.md, Drift controls) names the decision, and the work stops if the decision is needed to proceed and John has not answered.",
        "",
        "| Requirement | Open decisions it cites |",
        "|---|---|",
    ]
    for rid in sorted(pend, key=sort_key):
        pv.append(f"| {rid} | {', '.join(pend[rid])} |")
    with open(OUT_PENDING, "w", encoding="utf-8", newline="\n") as fh:
        fh.write("\n".join(pv) + "\n")
    print(
        f"wrote {os.path.relpath(OUT, ROOT)}: {total} requirements, {len(ASSESSED)} assessed; acceptance index {n_checks} checks; pending values {len(pend)} requirements"
    )


if __name__ == "__main__":
    main()
