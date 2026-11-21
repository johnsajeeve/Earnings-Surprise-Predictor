#!/usr/bin/env python3
"""Requirement, test and code relationship (drift control; Project-Wide DO-03).

Run from the repository root:
  python3 scripts/requirement_tests.py check      coverage rules, exit 1 on a problem
  python3 scripts/requirement_tests.py map        the relationship as a markdown table
  python3 scripts/requirement_tests.py scaffold   write a placeholder test for each acceptance
                                                  check that has none

The three sides:
  requirement  an ID or an acceptance check (ID-ACn) from audits/acceptance_index.md
  test         a function in tests/test_*.py, with @pytest.mark.req("ID-ACn")
  code         the project files the test exercises, @pytest.mark.code("src/...")

Rules checked:
 1. Every acceptance check has at least one test that names it as ID-ACn.
 2. Every test names at least one requirement (scripts/check_requirement_refs.py checks that the
    references exist).
 3. Every path in a code marker exists.
A placeholder test calls not_tested() and is skipped. It is reported as NOT TESTED, never as
passed. IDs with no acceptance check (needs N, goals PG, non-goals NG, stretch ST, conflicts C,
gates GATE) are listed, not required to have a test.
Standard library only, so it runs without installing anything.
"""

import ast
import os
import re
import sys
import textwrap

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INDEX = os.path.join(ROOT, "audits", "acceptance_index.md")
PENDING = os.path.join(ROOT, "audits", "pending_values.md")
KINDS_FILE = os.path.join(ROOT, "scripts", "requirement_test_kinds.txt")
REQ_DIR = os.path.join(ROOT, "docs", "requirements")
TESTS = os.path.join(ROOT, "tests")
SECTION = "# Placeholders written by scripts/requirement_tests.py scaffold. Replace the call to"
SECTION_2 = "# not_tested() with a real check when the code this test exercises is built."


def load_index():
    """Return ({id: [(ref, text)]}, {id: requirement document file name}), in index order."""
    checks, files = {}, {}
    current = None
    with open(INDEX, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^## .*\((.+-requirements\.md)\)", line)
            if m:
                current = m.group(1)
                continue
            m = re.match(r"^\| (([A-Z]{1,5}-?\d+)-AC\d+) \| (.*) \|$", line.rstrip("\n"))
            if m and current:
                checks.setdefault(m.group(2), []).append((m.group(1), m.group(3)))
                files[m.group(2)] = current
    return checks, files


def load_unchecked_ids():
    """IDs defined in the requirement documents that have no acceptance check."""
    ids = set()
    for name in os.listdir(REQ_DIR):
        if not name.endswith("-requirements.md"):
            continue
        with open(os.path.join(REQ_DIR, name), encoding="utf-8") as fh:
            for line in fh:
                m = re.match(r"^\| ([A-Z]{1,5}-?\d+) \|", line)
                if m:
                    ids.add(m.group(1))
                m = re.match(r"^### ([A-Z]{2,4}-\d+):", line)
                if m:
                    ids.add(m.group(1))
    return ids


def load_pending():
    out = {}
    with open(PENDING, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\| ([A-Z]{1,5}-\d+) \| (D-[\d, D-]+) \|$", line.strip())
            if m:
                out[m.group(1)] = m.group(2)
    return out


def load_kinds():
    out = {}
    with open(KINDS_FILE, encoding="utf-8") as fh:
        for line in fh:
            if line.strip() and not line.startswith("#"):
                rid, kind = line.strip().split(" ", 1)
                out[rid] = kind
    return out


def markers(node):
    """req references, code paths, xfail flag and placeholder kind of one test function."""
    reqs, code, xfail, kind = [], [], False, None
    for dec in node.decorator_list:
        if isinstance(dec, ast.Call) and isinstance(dec.func, ast.Attribute):
            args = [a.value for a in dec.args if isinstance(a, ast.Constant)]
            if dec.func.attr == "req":
                reqs += args
            elif dec.func.attr == "code":
                code += args
            elif dec.func.attr == "xfail":
                xfail = True
    for sub in ast.walk(node):
        if (
            isinstance(sub, ast.Call)
            and isinstance(sub.func, ast.Name)
            and sub.func.id == "not_tested"
            and sub.args
            and isinstance(sub.args[0], ast.Constant)
            and sub.args[0].value != "NEEDS REPO"  # a conditional skip, the test still checks
        ):
            kind = sub.args[0].value
    return reqs, code, xfail, kind


def load_tests():
    found = []
    for fname in sorted(os.listdir(TESTS)):
        if not (fname.startswith("test_") and fname.endswith(".py")):
            continue
        with open(os.path.join(TESTS, fname), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                reqs, code, xfail, kind = markers(node)
                if kind:
                    status = f"not tested ({kind})"
                elif xfail:
                    status = "expected failure (requirement not met yet)"
                else:
                    status = "real check"
                found.append(
                    {
                        "key": f"{fname}::{node.name}",
                        "file": fname,
                        "name": node.name,
                        "reqs": reqs,
                        "code": code,
                        "status": status,
                    }
                )
    return found


def covering(tests, ref):
    """Tests that name this exact acceptance check."""
    return [t for t in tests if ref in t["reqs"]]


def rank(status):
    """Order of strength: a real check beats an expected failure, which beats not tested."""
    return {"real check": 0, "expected failure (requirement not met yet)": 1}.get(status, 2)


def check():
    checks, _ = load_index()
    tests = load_tests()
    problems = []
    acs = [ref for items in checks.values() for ref, _ in items]
    status_count = {}
    for ref in acs:
        hits = covering(tests, ref)
        if not hits:
            problems.append(f"{ref}: no test names this acceptance check")
            continue
        best = min((t["status"] for t in hits), key=rank)
        status_count[best] = status_count.get(best, 0) + 1
    for t in tests:
        if not t["reqs"]:
            problems.append(f"{t['key']}: names no requirement")
        for path in t["code"]:
            if not os.path.exists(os.path.join(ROOT, path)):
                problems.append(f"{t['key']}: code marker path does not exist: {path}")
    unchecked = sorted(load_unchecked_ids() - set(checks))
    print(f"requirements with acceptance checks: {len(checks)}")
    print(f"acceptance checks: {len(acs)}")
    print(f"tests: {len(tests)}")
    for status, number in sorted(status_count.items()):
        print(f"  checks whose best test is {status}: {number}")
    print(f"IDs with no acceptance check (no test required): {len(unchecked)}")
    if problems:
        print("FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print("OK")
    return 0


def table():
    checks, _ = load_index()
    tests = load_tests()
    rows = ["| Requirement check | Test | Code | Status |", "|---|---|---|---|"]
    for items in checks.values():
        for ref, _ in items:
            hits = covering(tests, ref) or [None]
            for t in hits:
                if t is None:
                    rows.append(f"| {ref} | none | none | NO TEST |")
                else:
                    code = ", ".join(t["code"]) or "none yet"
                    rows.append(f"| {ref} | {t['key']} | {code} | {t['status']} |")
    print("\n".join(rows))
    return 0


def slug(text):
    words = re.sub(r"[^a-z0-9]+", " ", text.lower()).split()[:7]
    return "_".join(words)[:60].strip("_")


def stub(ref, text, kind, why, taken):
    rid = ref.split("-AC")[0]
    base = f"test_{rid.lower().replace('-', '_')}_ac{ref.split('-AC')[1]}_{slug(text)}"
    name, n = base, 2
    while name in taken:
        name, n = f"{base}_{n}", n + 1
    taken.add(name)
    clean = text.replace("\\", "")
    # ruff format adds a space when the text ends with a quote mark.
    one_line = f'    """{ref}: {clean}{" " if clean.endswith(chr(34)) else ""}"""'
    if len(one_line) <= 100:
        doc = one_line
    else:
        # Closing quotes on their own line: the layout the rest of the repository uses.
        doc = textwrap.fill(
            f"{ref}: {clean}", width=92, initial_indent='    """', subsequent_indent="    "
        )
        doc += '\n    """'
    call = f'    not_tested("{kind}", "{why}")'
    if len(call) > 100:
        call = f'    not_tested(\n        "{kind}", "{why}"\n    )'
    return f'@pytest.mark.req("{ref}")\ndef {name}():\n{doc}\n{call}\n'


def header(doc_file):
    title = doc_file.replace("-requirements.md", "").replace("-", " ")
    return (
        f'"""Tests for the {title} requirements ({doc_file}).\n\n'
        "Each test exercises one acceptance check, named in @pytest.mark.req(...). A test that\n"
        "calls not_tested() is a placeholder for code that does not exist yet. It is skipped and\n"
        "reported as NOT TESTED, never as passed. Replace the call with a real check when the\n"
        'code is built (Deterministic_audit.md, Phase D).\n"""\n\n'
        "import pytest\n\n"
        "from requirement_support import not_tested\n"
    )


def scaffold():
    checks, files = load_index()
    tests = load_tests()
    pending, kinds = load_pending(), load_kinds()
    existing = {t["name"] for t in tests}
    new_by_file = {}
    for rid, items in checks.items():
        for ref, text in items:
            if covering(tests, ref):
                continue
            if rid in pending:
                kind, why = "BLOCKED", f"waits for open decision {pending[rid]}"
            elif kinds.get(rid) == "NEEDS PERSON":
                kind, why = "NEEDS PERSON", "needs a sign-off, review or approval by a person"
            elif kinds.get(rid) == "NEEDS MEASUREMENT":
                kind, why = "NEEDS MEASUREMENT", "needs a measured run on real data or hardware"
            else:
                kind, why = "NOT IMPLEMENTED", "the code this check exercises is not built yet"
            fname = "test_req_" + files[rid].replace("-requirements.md", "").replace("-", "_")
            new_by_file.setdefault(fname + ".py", []).append(
                (files[rid], stub(ref, text, kind, why, existing))
            )
    for fname, items in new_by_file.items():
        path = os.path.join(TESTS, fname)
        blocks = [b for _, b in items]
        if os.path.exists(path):
            with open(path, encoding="utf-8") as fh:
                current = fh.read()
            if "not_tested" not in current or "import pytest" not in current:
                print(f"cannot append to {fname}: it must import pytest and not_tested")
                return 1
            out = current.rstrip("\n") + "\n"
            if SECTION not in out:
                out += f"\n\n{SECTION}\n{SECTION_2}\n"
                out += "\n\n".join(blocks)
            else:
                out += "\n\n" + "\n\n".join(blocks)
        else:
            out = header(items[0][0]) + f"\n\n{SECTION}\n{SECTION_2}\n" + "\n\n".join(blocks)
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(out)
        print(f"{fname}: {len(blocks)} placeholder tests written")
    if not new_by_file:
        print("nothing to write: every acceptance check has a test")
    return 0


def main(argv):
    commands = {"check": check, "map": table, "scaffold": scaffold}
    if len(argv) != 2 or argv[1] not in commands:
        print(__doc__)
        return 2
    return commands[argv[1]]()


if __name__ == "__main__":
    sys.exit(main(sys.argv))
