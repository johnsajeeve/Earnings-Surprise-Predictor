#!/usr/bin/env python3
"""Check that tests point at real requirements (drift control; Project-Wide DO-03).

Run from the repository root:  python3 scripts/check_requirement_refs.py

Rules:
 1. Every reference in @pytest.mark.req("ID") or ("ID-ACn") exists in audits/acceptance_index.md,
    which is generated from the requirement documents.
 2. Every test function carries a req marker, or is listed in tests/legacy_unmarked.txt.
    The legacy list only shrinks: an entry that no longer exists or is now marked is an error.
Standard library only, so it runs without installing anything.
"""

import ast
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
INDEX = os.path.join(ROOT, "audits", "acceptance_index.md")
TESTS = os.path.join(ROOT, "tests")
LEGACY = os.path.join(TESTS, "legacy_unmarked.txt")


def valid_references():
    refs = set()
    with open(INDEX, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\| ([A-Z]{1,5}-\d+)-AC\d+ \|", line)
            if m:
                refs.add(m.group(0).split()[1])
                refs.add(m.group(1))
            m = re.match(r"^\| ([A-Z]{1,5}-?\d+) \|$", line.strip())
            if m:
                refs.add(m.group(1))
    return refs


def marker_refs(node):
    out = []
    for dec in node.decorator_list:
        if (
            isinstance(dec, ast.Call)
            and isinstance(dec.func, ast.Attribute)
            and dec.func.attr == "req"
        ):
            out += [
                a.value
                for a in dec.args
                if isinstance(a, ast.Constant) and isinstance(a.value, str)
            ]
    return out


def main():
    valid = valid_references()
    legacy = set()
    if os.path.exists(LEGACY):
        with open(LEGACY, encoding="utf-8") as fh:
            legacy = {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}
    problems, seen = [], set()
    for fname in sorted(os.listdir(TESTS)):
        if not (fname.startswith("test_") and fname.endswith(".py")):
            continue
        with open(os.path.join(TESTS, fname), encoding="utf-8") as fh:
            tree = ast.parse(fh.read())
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name.startswith(
                "test_"
            ):
                key = f"{fname}::{node.name}"
                seen.add(key)
                refs = marker_refs(node)
                for ref in refs:
                    if ref not in valid:
                        problems.append(f"{key}: unknown requirement reference {ref}")
                if not refs and key not in legacy:
                    problems.append(
                        f"{key}: no @pytest.mark.req(...) and not in tests/legacy_unmarked.txt"
                    )
                if refs and key in legacy:
                    problems.append(f"{key}: now marked, remove it from tests/legacy_unmarked.txt")
    for key in sorted(legacy - seen):
        problems.append(
            f"legacy entry {key} does not exist, remove it from tests/legacy_unmarked.txt"
        )
    if problems:
        print("FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: {len(seen)} tests, {len(legacy)} legacy unmarked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
