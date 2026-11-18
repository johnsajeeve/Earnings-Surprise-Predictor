#!/usr/bin/env python3
"""Fail if any dependency line is not pinned to an exact version (Project-Wide EQ-04).

Usage:  python3 scripts/check_pins.py requirements.txt requirements.lock ...
Exit code 0 if every requirement line is pinned with ==, 1 otherwise. The Dockerfile runs this
before installing anything, so an unpinned dependency fails the image build.
"""

import re
import sys

# name, optional [extras], then == and a concrete version. No ranges, no wildcards, no URLs.
PINNED = re.compile(
    r"^[A-Za-z0-9][A-Za-z0-9._-]*(\[[A-Za-z0-9._,-]+\])?==[A-Za-z0-9][A-Za-z0-9.+!_-]*$"
)


def check(path: str) -> list[str]:
    problems = []
    with open(path, encoding="utf-8") as handle:
        for number, raw in enumerate(handle, start=1):
            line = raw.split("#", 1)[0].strip()  # drop comments
            if line and not PINNED.match(line):
                problems.append(f"{path}:{number}: not pinned with ==: {line}")
    return problems


def main(paths: list[str]) -> int:
    if not paths:
        print("usage: check_pins.py FILE [FILE ...]", file=sys.stderr)
        return 2
    problems = [p for path in paths for p in check(path)]
    for problem in problems:
        print(problem, file=sys.stderr)
    if problems:
        print(f"FAIL: {len(problems)} unpinned requirement line(s)", file=sys.stderr)
        return 1
    print(f"OK: every requirement line in {', '.join(paths)} is pinned")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
