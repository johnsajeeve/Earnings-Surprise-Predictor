# Remediation and Re-verification: Findings F-01 to F-08

Date: 17 November 2026. Follows `audit_2026-11-17.md`. John approved F-01 to F-08 and asked that no new per-requirement tests be written yet. None were. The existing 16 test functions were only updated to match the changed code.

Every result below was produced again after the changes. The earlier audit was not reused as evidence.

## 1. Result

| Finding | Status | Evidence in section |
|---|---|---|
| F-01 Exact pins, one documented command | **Done, verified** | 3.1 |
| F-02 Trim unused dependencies | **Done, verified** (Option B, see 6) | 3.2 |
| F-03 Request logging | **Done, verified by hand** | 3.3 |
| F-04 Password with special characters | **Done, verified** | 3.4 |
| F-05 CI, lint, types, secret scan | **Done and each command verified locally. CI never run on GitHub (BLOCKED)** | 3.5 |
| F-06 ADRs | **Done**, status Proposed | 3.6 |
| F-07 Health check cost | **Done, verified** | 3.7 |
| F-08 Rules file loading | **Done, NOT TESTED in a new session** | 3.8 |

Traceability after re-verification (17 requirements assessed): PASS 2 (EQ-04, NFR-11), PARTIAL 10, FAIL 2 (EQ-03, PL-03), UNVERIFIED 3. The other 246 are UNVERIFIED because they were not assessed. **Overall: not PASS.**

## 2. What changed

Created: `scripts/check_pins.py`, `requirements-pending.txt`, `pyproject.toml`, `.github/workflows/ci.yml`, `src/earnings/api/middleware.py`, `docs/adr/0001-celery-redis-task-queue.md`, `docs/adr/0002-streamlit-frontend.md`, `CLAUDE.md`, `audits/assessments.py`, this report.

Modified: `Dockerfile`, `docker-compose.yml`, `.env.example`, `requirements.txt`, `requirements.lock`, `requirements-dev.txt`, `README.md`, `src/earnings/config.py`, `src/earnings/api/main.py`, `tests/test_config.py` and `tests/test_health_unit.py` (to match the new settings and the health cache), `audits/generate_traceability.py`, `audits/requirements_traceability.md` (regenerated), `docs/decision-log.md`, `docs/logbook.md`.

Not changed: the SSOT, the requirement documents, repository settings on GitHub.

## 3. Evidence by finding

**3.1 F-01 (EQ-04).**
- All four requirements files pass `scripts/check_pins.py`. Python, Postgres and Redis images use exact tags (`python:3.12.16-slim`, `postgres:16.16`, `redis:7.4.12-alpine`), checked to exist with `docker manifest inspect`.
- The Dockerfile runs the pin check before installing, and installs with `-c requirements.lock`, so transitive packages are pinned too.
- Planted fault: adding `requests>=2.0` to `requirements.txt` failed the build: `requirements.txt:24: not pinned with ==: requests>=2.0`, `docker build exit: 1`.
- Fresh checkout (29 files, no `.env`, no cache): `docker compose build --no-cache` exit 0 after `cp .env.example .env`. Stack healthy, `/health` HTTP 200. `pip freeze` matched `requirements.lock` exactly (39 of 39). Image 326 MB.
- README now holds the one command: `cp .env.example .env && docker compose up --build -d`.

**3.2 F-02.** Image 3.64 GB to 326 MB. Locked packages 129 to 39. Runtime now installs only what the code uses. The other packages, pinned, are in `requirements-pending.txt` with the step that will add each. `httpx` moved to `requirements-dev.txt`. Redundant `pydantic`, `numpy` and `pyarrow` lines removed. `alembic` moved to pending.

**3.3 F-03 (NFR-11, SP-05).** Sample lines:
```
request_id=4ee63493... method=GET path=/not-a-real-path status=404 latency_ms=0.2
request_id=b4d66a1c... method=GET path=/boom status=500 latency_ms=1.2
```
A request to `/boom?secret=abc` logged only the path, so the query string is not logged. Responses carry `X-Request-ID`. uvicorn's access log, which printed client addresses, is switched off. Three request kinds checked (200, 404, 500). No automated test, by instruction.

**3.4 F-04.** A throwaway Postgres with password `p@ss:/#?x&%` accepted a connection through the app's own settings code: `SELECT 1 -> 1`. The URL is now built from separate parts.

**3.5 F-05.**

| CI step | Run locally | Result |
|---|---|---|
| Pin check | `check_pins.py` on 4 files | OK |
| Lint | `ruff check .` | All checks passed |
| Format | `ruff format --check .` | 19 files formatted |
| Types | `mypy` | no issues in 8 source files |
| Tests | pytest in the stack | 19 passed, 1 warning (see 7) |
| Secret scan | `gitleaks git` (9 commits) and `gitleaks dir` | no leaks |
| Planted secret | fake token in a scratch folder | scan failed, exit 1 |
| Vulnerabilities | `pip-audit -r requirements.lock` | No known vulnerabilities found |
| Workflow syntax | `actionlint` | exit 0 |

Action tags `actions/checkout v7.0.1` and `actions/setup-python v7.1.0` exist, and Python 3.12.16 is in GitHub's runner manifest. **The workflow has not run on GitHub**, so job behaviour there is unverified. EQ-03: GitHub reports `main` as "Branch not protected" (HTTP 404). The repository is public.

**3.6 F-06.** ADR 0001 (Celery with Redis) and ADR 0002 (Streamlit) are written with status Proposed. Open points are stated, such as how a dead-letter queue and Cloud Run workers will work.

**3.7 F-07.** Uncached `_compute_health` takes 109 ms, then 6 ms, when healthy (about 2100 ms before the fix below). With the worker stopped it takes 2152 ms, bounded by the timeout. A repeated request inside 5 seconds answered in 6 ms from the cache. A failure can appear up to 5 seconds late.

**3.8 F-08.** `CLAUDE.md` contains one line, `@Deterministic_audit.md`. Not tested, because it only takes effect when a new session starts.

## 4. Defects found while fixing

1. **Undeclared dependency.** After trimming, the worker crash-looped: `ModuleNotFoundError: No module named 'packaging'`. kombu 5.7.0 requires only `amqp` and `vine` but its Redis transport imports `packaging`. The old image supplied it by accident. Fixed with `packaging==26.3`, commented in `requirements.txt`.
2. **Slow health check.** `celery.control.ping(timeout=2.0)` waited the full 2 seconds even when the worker answered at once, so an uncached `/health` always took about 2.1 s. Fixed with `limit=1`.
3. **mypy errors.** mypy could not see that `Settings()` reads the environment. Fixed with one targeted `# type: ignore[call-arg]` and a comment.
4. **Lint findings** from the first ruff run: long lines, an f-string without placeholders, formatting. Fixed.
5. **Environment fault, not code.** Twice, `python3 scripts/check_pins.py` failed with `FileNotFoundError` straight after a `docker run` on the Windows disk mount, and passed on retry with an absolute path. Cause not investigated.
6. **My own mistake.** A first no-cache build showed exit 1 because I ran it before copying `.env`, and the compose guard correctly refused. Rerun in the right order: exit 0.

## 5. Final re-run (after the last code change)

Pin check OK. `ruff check`, `ruff format --check` and `mypy`: exit 0. pytest: `19 passed, 1 warning in 0.84s`. Stack: api, db, redis, worker all healthy. `/health`: HTTP 200, all three checks ok. Traceability generator: same hash on repeated runs (`0905c607...`). `docs/tools/check_requirements.py`: OK.

## 6. Decisions I took that you may want to change

- **F-02:** you approved "all", and F-02 listed two options. I chose Option B (install only what is used). It is reversible by moving lines from `requirements-pending.txt`.
- **Lint scope:** `docs/` is excluded (it holds an older tool outside this work). Line length is enforced in `src`, `tests` and `scripts`, and not in `audits/`. The three deliberate `except Exception` blocks stay, each marked with a reason.
- **Request ids** are generated by the server and a client-supplied one is ignored.
- **Health cache** is 5 seconds.
- **ADRs** are Proposed, not Accepted, because the text is mine and not yet yours.
- **Image tags** are exact versions, not digests.

## 7. Not verified, and limits

- The CI workflow has never run on GitHub. A planted style error failing the CI job was not demonstrated.
- Branch protection is off (EQ-03). Nothing blocks a merge.
- F-08 not tested in a new session.
- pytest reports a deprecation warning: Starlette's test client now prefers `httpx2` over `httpx`. `httpx==0.28.1` works today. `httpx2` was not evaluated.
- The pinned versions in `requirements-pending.txt` were verified together in the earlier larger image, but not installed together again after the trim.
- Request logging was checked on three request kinds, not exhaustively.
- Fault behaviour (EQ-06) is still observed by hand only.

## 8. Needs your decision

1. **Branch protection on `main` (EQ-03).** I can enable it with `gh` once you say so. It would require pull requests and passing checks before merging.
2. **The repository is public.** `docs/source/` (the proposal PDF) is untracked but not ignored, so `git add .` would publish it. Decision D-30 is open. Do you want it ignored now?
3. **SSOT document map:** a row for `docs/adr/`. Only you edit the SSOT.
4. **Confirm ADRs 0001 and 0002**, which closes D-10.
5. **Nothing is committed.** Pushing would trigger the first CI run.

## 9. Update, 18 November 2026

John answered the section 8 questions and approved the rest. Changes since the section 5 re-run:

- **Branch protection enabled on `main`** (decision C-23). Read back from the GitHub API: pull request with 1 approving review, the five CI checks required, force pushes and deletion blocked, administrators can bypass. Because an administrator can bypass and there is no second reviewer, EQ-03 is PARTIAL, not PASS.
- **ADRs 0001 and 0002 accepted** (C-22). SC-02 is now PASS (one frontend framework, no React found in code or configuration). SC-01 stays PARTIAL because the deployment diagram was not compared with the ADR.
- **`docs/source/` is git-ignored** (C-21). The proposal PDF stays local because the repository is public.
- **SSOT map** gained the `adr/` row (C-24). The Status line of the SSOT was also edited by John, not by Claude.
- **Product data model** gained a `TranscriptSentence` entity (C-20).
- Traceability regenerated: PASS 3 (EQ-04, NFR-11, SC-02), PARTIAL 10, FAIL 1 (PL-03), UNVERIFIED 3. Overall: not PASS.

Not re-run at first on 18 November: lint, format, types and tests, because Docker Desktop was stopped (BLOCKED). Docker Desktop was started later the same day and the checks were re-run (see the paragraph that follows). Files under `src/`, `tests/`, `scripts/` and the build configuration have not changed since the section 5 run, which is the basis for carrying its results forward. The CI run on GitHub will be the first independent confirmation.

Re-run, 18 November 2026, after the component requirement documents and the consistency fixes (no `src/`, `tests/`, `scripts/` or build file changed in that work): `docker compose up --build -d` built and started all four services healthy. `GET /health` returned HTTP 200 with postgres, redis and worker ok. `ruff check` exit 0, `ruff format --check` 20 files already formatted, `mypy` no issues in 8 source files, `pytest` 19 passed with the same one Starlette deprecation warning. `python3 scripts/check_pins.py` OK on all four requirements files. PASS for these commands. The CI workflow has still never run on GitHub. This re-run supports EQ-01, EQ-02 and EQ-04 as before and does not change their status.
