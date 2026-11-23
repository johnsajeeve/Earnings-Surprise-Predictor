#!/usr/bin/env python3
"""Check that the implementation plan covers every requirement and that the audit ledger is honest.

Run from the repository root:  python3 scripts/check_plan_coverage.py

Rules (Deterministic_audit.md Sections 3, 4, 7; docs/implementation-plan.md):
 1. Every requirement ID in audits/requirements_traceability.md is mapped exactly once in
    audits/plan_coverage.txt. No ID is left out, mapped twice, or invented.
 2. Every wave target in the map is a wave heading in docs/implementation-plan.md, or GOV, OFF, OPT.
 3. Every wave heading in the plan has one row in the ledger of audits/implementation_audit.md.
 4. A ledger row with status PASS names an evidence file under audits/evidence/ that exists and
    contains the wave number. A row with any other status names no evidence or an existing file.
 5. Status words are those of Deterministic_audit.md Section 8, plus NOT STARTED and IN PROGRESS.
Standard library only. It reads IDs, files and statuses. It does not read meaning.
"""

import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
TRACE = os.path.join(ROOT, "audits", "requirements_traceability.md")
MAP = os.path.join(ROOT, "audits", "plan_coverage.txt")
PLAN = os.path.join(ROOT, "docs", "implementation-plan.md")
LEDGER = os.path.join(ROOT, "audits", "implementation_audit.md")
EVIDENCE = os.path.join(ROOT, "audits", "evidence")
SPECIAL = {"GOV", "OFF", "OPT"}
STATUSES = {"NOT STARTED", "IN PROGRESS", "PASS", "PARTIAL", "FAIL", "BLOCKED", "UNVERIFIED"}
ID_RE = re.compile(r"^([A-Z]{1,5}?)(-?)(\d+)$")


def requirement_ids():
    ids = []
    with open(TRACE, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\| ([A-Z]{1,5}-?\d+) \|", line)
            if m:
                ids.append(m.group(1))
    return ids


def expand(token):
    """'FE-01..FE-07' -> list of IDs. A single ID returns itself."""
    if ".." not in token:
        return [token]
    lo, hi = token.split("..")
    a, b = ID_RE.match(lo), ID_RE.match(hi)
    if not a or not b or a.group(1) != b.group(1):
        raise ValueError(f"bad range {token!r}")
    width = len(a.group(3))
    first, last = int(a.group(3)), int(b.group(3))
    if last < first:
        raise ValueError(f"descending range {token!r}")
    return [f"{a.group(1)}{a.group(2)}{n:0{width}d}" for n in range(first, last + 1)]


def plan_waves():
    with open(PLAN, encoding="utf-8") as fh:
        text = fh.read()
    return re.findall(r"^\*\*Wave (\d+\.\d+)\. ", text, flags=re.M)


def main():
    errors = []
    known = requirement_ids()
    known_set = set(known)
    waves = plan_waves()
    if len(waves) != len(set(waves)):
        errors.append("plan has a repeated wave number")

    seen = {}
    with open(MAP, encoding="utf-8") as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            parts = line.split()
            if len(parts) != 2:
                errors.append(f"{MAP}:{n}: expected 'ID target', got {line!r}")
                continue
            token, target = parts
            if target not in SPECIAL and target not in waves:
                errors.append(f"{MAP}:{n}: target {target!r} is not a wave in the plan")
            try:
                ids = expand(token)
            except ValueError as exc:
                errors.append(f"{MAP}:{n}: {exc}")
                continue
            for i in ids:
                if i not in known_set:
                    errors.append(f"{MAP}:{n}: {i} is not a requirement in the traceability file")
                elif i in seen:
                    errors.append(f"{MAP}:{n}: {i} is mapped twice (also line {seen[i]})")
                else:
                    seen[i] = n
    for i in known:
        if i not in seen:
            errors.append(f"{i} is not mapped in audits/plan_coverage.txt")

    rows = {}
    with open(LEDGER, encoding="utf-8") as fh:
        for line in fh:
            m = re.match(r"^\| W(\d+\.\d+) \| ([^|]*) \| ([^|]*) \| ([^|]*) \|", line)
            if m:
                rows[m.group(1)] = (m.group(3).strip(), m.group(4).strip())
    for w in waves:
        if w not in rows:
            errors.append(f"wave {w} has no row in the ledger")
    for w in rows:
        if w not in waves:
            errors.append(f"ledger row W{w} is not a wave in the plan")
    for w, (status, evidence) in rows.items():
        if status not in STATUSES:
            errors.append(f"ledger W{w}: unknown status {status!r}")
            continue
        path = os.path.join(ROOT, evidence) if evidence not in ("", "-") else None
        if status == "PASS":
            if path is None or not os.path.isfile(path) or not path.startswith(EVIDENCE):
                errors.append(f"ledger W{w}: PASS needs an existing file under audits/evidence/")
            else:
                with open(path, encoding="utf-8") as fh:
                    if f"Wave {w}" not in fh.read():
                        errors.append(f"ledger W{w}: evidence file does not mention 'Wave {w}'")
        elif path is not None and not os.path.isfile(path):
            errors.append(f"ledger W{w}: evidence file {evidence} does not exist")

    mapped = len(seen)
    print(
        f"requirements: {len(known)}, mapped: {mapped}, "
        f"waves in plan: {len(waves)}, ledger rows: {len(rows)}"
    )
    if errors:
        for e in errors:
            print("ERROR:", e)
        print(f"FAIL: {len(errors)} problem(s)")
        return 1
    print("OK: every requirement mapped once, every wave has a ledger row, every PASS has evidence")
    return 0


if __name__ == "__main__":
    sys.exit(main())
