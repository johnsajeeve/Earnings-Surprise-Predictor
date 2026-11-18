#!/usr/bin/env python3
"""Check that commits that change code name the requirement they serve (drift control).

Run from the repository root:  python3 scripts/check_commit_refs.py

Looks at commits after the one in .github/commit-refs-baseline. A commit that changes anything
under src/, tests/ or scripts/ must mention a requirement ID (for example FR-01 or FE-12-AC1) in
its message, or say "Requirement: none" with a reason. Documents-only commits are exempt. Merge
commits are skipped. Standard library only.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASELINE = os.path.join(ROOT, ".github", "commit-refs-baseline")
CODE = ("src/", "tests/", "scripts/")
PREFIXES = (
    "PG NG ST FR SRS EX NFR API PL ML TR MR UI ER EP SCR SM "
    "GATE SR TX AE CE LB IM SEC PX FD DV VL GS TH "
    "ASM PD SS SC EQ SP ET OR AI DO FE AG DB UX IG MD SV DP"
).split()
ID = re.compile(r"\b(?:" + "|".join(PREFIXES) + r")-\d+(?:-AC\d+)?\b|\bN[1-7]\b")


def git(*args):
    return subprocess.run(
        ["git", *args], cwd=ROOT, capture_output=True, text=True, check=True
    ).stdout


def main():
    with open(BASELINE, encoding="utf-8") as fh:
        base = fh.read().strip()
    commits = git("rev-list", "--no-merges", "--reverse", f"{base}..HEAD").split()
    problems = []
    for sha in commits:
        files = git("show", "--name-only", "--pretty=format:", sha).split()
        if not any(f.startswith(CODE) for f in files):
            continue
        message = git("show", "-s", "--format=%B", sha)
        if not ID.search(message) and "Requirement: none" not in message:
            problems.append(f"{sha[:7]}: changes code but names no requirement ID")
    if problems:
        print("FAIL")
        for p in problems:
            print(" -", p)
        return 1
    print(f"OK: {len(commits)} commits after the baseline checked")
    return 0


if __name__ == "__main__":
    sys.exit(main())
