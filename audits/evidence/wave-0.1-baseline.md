# Wave 0.1: regression baseline (Step 0.1.1)

Measured on 23 November 2026, branch `build/wave-0-1`, commit `1d0c46f` plus the uncommitted plan and audit files. Docker 29.9.3, server and client, Linux engine. This is the anchor for every later regression comparison (implementation_audit.md Section 2, check 3).

## Wave 0.1

Requirements touched: EQ-01, EQ-04 (re-verified), EQ-02 (lint, format, types), DO-03 and DO-05 (generated files and ID checks).

## Commands run

Stack (the existing `.env` was kept, not overwritten with `.env.example`):

`docker compose up --build -d --wait --wait-timeout 300`

Tests, CI style (the command of the `tests` job in `.github/workflows/ci.yml`, plus `-rs` and `--junitxml`; only `tests/` and `requirements-dev.txt` mounted):

`docker compose run --rm --no-deps -v "$PWD/tests:/app/tests:ro" -v "$PWD/requirements-dev.txt:/app/requirements-dev.txt:ro" -v "<out>:/out" api sh -c 'pip install --user -q -r requirements-dev.txt && python -m pytest -p no:cacheprovider tests -rs --junitxml=/out/baseline.xml'`

Tests, full repository (the repository mounted at `/repo`, so the checks that read `docs/`, `.github/` and `scripts/` can run):

`docker compose run --rm --no-deps -v "$PWD:/repo" -v "<out>:/out" -w /repo -e PYTHONPATH=/repo/src api sh -c 'pip install --user -q -r requirements-dev.txt && python -m pytest -p no:cacheprovider tests -rs --junitxml=/out/baseline_full.xml'`

Static and generated-file checks: `ruff check .`, `ruff format --check .`, `mypy` (inside the same image, repository mounted), then on the host `python3 docs/tools/check_requirements.py`, `audits/generate_traceability.py`, `scripts/test_matrix.py build` and `verify`, `scripts/check_requirement_refs.py`, `scripts/check_commit_refs.py`, `scripts/check_plan_coverage.py`, `scripts/check_pins.py`.

## Output

Full output is in `wave-0.1-scripts/baseline_ci_style_output.txt`, `baseline_full_repo_output.txt` and `host_checks_output.txt`.

| Run | Tests | Passed | Failed | Errors | Skipped | Expected failures |
|---|---|---|---|---|---|---|
| CI style | 624 | 25 | 0 | 0 | 599 | 0 |
| Full repository | 624 | 42 | 0 | 0 | 580 | 2 |

Skips by reason, CI-style run (599): NOT IMPLEMENTED 407, BLOCKED 56, NEEDS PERSON 35, NEEDS MEASUREMENT 81, NEEDS REPO 20.
Skips by reason, full-repository run (580): NOT IMPLEMENTED 407, BLOCKED 56, NEEDS PERSON 35, NEEDS MEASUREMENT 81, NEEDS REPO 1 (the one that needs `git`, which the image does not contain).
The 2 expected failures are `test_sc_06_ac1` and `test_sc_07_ac1` (no ADR exists yet for plain-SQL retrieval and for the label route).
Blocked decisions behind the 56 BLOCKED skips: D-36 12, D-42 8, D-43 3, D-38 4, D-37 4 plus 1 with D-06, D-34 4, D-45 4, D-35 2, D-39 2, D-28 2, D-32 2, D-22 2, D-18 2, D-15 2, D-27 1, D-40 and D-46 1.

Other checks, all exit 0: `ruff check .` (after moving my throwaway spike scripts out of lint scope), `ruff format --check .` (47 files), `mypy` (8 source files, no issues), the six consistency checks above, and `check_pins.py`. After regeneration `git diff` shows no change to any generated file. The test matrix reports 617 tests, 16 checks whose best test is a real check.

One warning in both runs: `StarletteDeprecationWarning: Using httpx with starlette.testclient is deprecated; install httpx2 instead` (library, not project code).

## Result per requirement

- EQ-01 (tests run): PASS for the mechanism, as run locally in the same container CI uses. Not run in GitHub Actions in this step.
- EQ-02 (lint, format, types): PASS locally. Same note.
- EQ-04 (builds from a clean checkout with one command, pinned dependencies): PARTIAL. The build succeeded and `check_pins.py` passed, but see "Not verified" for the clean-state limit.
- DO-05 and the generated files: PASS locally.

## Not verified

- **The stack was not rebuilt from a clean state.** The database and Redis containers were already running, and the named volume was not deleted, so this is `up --build` over an existing stack. A volume reset would erase the skeleton database, which holds nothing of value, but I did not delete anything without asking. EQ-04 stays PARTIAL until a clean-clone run is done (planned for the P0 gate).
- The result was not reproduced in GitHub Actions.
- 20 checks need the full repository, which the CI `tests` job does not mount, so the CI job itself does not run them. They run only in the full-repository run above. Whether that is the intended CI design is a question for John (it may deserve a separate CI job, which would be a change to the workflow).

## Drift found

DR-08: the CI `tests` job mounts only `tests/` and `requirements-dev.txt`, so 20 tests that check documents, the workflow and scripts are skipped there as NEEDS REPO. They are covered by other CI jobs for some checks, but not all. Not a disagreement with a requirement text. Reported for John.

## Assumptions

`.env` already existed (dated 17 November 2026). I did not read or print its contents, so I make no claim about what it holds. It is git-ignored.

## Measured values

- Test run time: 2.2 s (CI style), 3.4 s (full repository). Build and start of the stack: not timed.
- Hours spent on this step: about 0.5. Acceptance checks closed: 0 (this is a measurement step).
