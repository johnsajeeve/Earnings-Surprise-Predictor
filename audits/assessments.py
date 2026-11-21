"""Audit findings per requirement, read by generate_traceability.py.

id -> (status, implementation files, test files, evidence)

Status values: PASS, PARTIAL, FAIL, BLOCKED, UNVERIFIED (Deterministic_audit.md Section 8).
Evidence points to two reports:
  - "audit N"        = audits/audit_2026-11-17.md (initial audit), section N.
  - "remediation N"  = audits/remediation_2026-11-17.md (re-verification after fixes), section N.
A requirement with no entry here is reported UNVERIFIED (not assessed). Only requirements the Docker
skeleton touches are assessed. Last updated: 17 Nov 2026, after the F-01 to F-08 fixes.
"""

ASSESSED = {
    "SC-01": (
        "PARTIAL",
        "docker-compose.yml; src/earnings/celery_app.py; src/earnings/tasks.py; docs/adr/0001-celery-redis-task-queue.md",
        "tests/test_stack_integration.py::test_celery_task_round_trip_through_redis_and_worker",
        "Celery with Redis runs and a task round-trips (19 tests pass, remediation 5). ADR 0001 is Accepted (John, 18 Nov 2026, decision C-22). The acceptance check also requires the deployment diagram to match the ADR, and that has not been checked.",
    ),
    "SC-02": (
        "PASS",
        "requirements-pending.txt (streamlit only; no React); docs/adr/0002-streamlit-frontend.md",
        "none (verified by command)",
        "ADR 0002 is Accepted (John, 18 Nov 2026, decision C-22). A search of code and configuration files outside docs/ found no React reference, and Streamlit is the only frontend package listed, in requirements-pending.txt. Limit: Streamlit is not installed yet.",
    ),
    "EQ-01": (
        "PARTIAL",
        ".github/workflows/ci.yml; tests/",
        "tests/test_config.py; tests/test_health_unit.py; tests/test_stack_integration.py",
        "19 tests pass locally (remediation 5). A CI workflow runs them, and each of its commands was run locally, but the workflow has never run on GitHub. Merging into main requires the five CI checks (branch protection, 18 Nov 2026), but they have never run, and an administrator can bypass.",
    ),
    "EQ-02": (
        "PARTIAL",
        "pyproject.toml; .github/workflows/ci.yml",
        "none",
        "ruff check, ruff format --check and mypy are configured and pass locally (18 files formatted, 8 source files typed, exit 0; remediation 5). They are in the CI workflow, which has not run on GitHub. A planted style error failing the CI job was not demonstrated. Scope choices are in remediation 6.",
    ),
    "EQ-03": (
        "PARTIAL",
        "GitHub repository settings (not a repository file)",
        "none (verified by GitHub API read-back)",
        "Branch protection was enabled on main on 18 Nov 2026 (decision C-23). Read back: pull request with 1 approving review required, the five CI checks required, force pushes and deletion blocked. Administrators can bypass (enforce_admins false), so a direct push by the owner is not blocked, and as a solo project there is no second reviewer. Before this, main was 'Branch not protected' (HTTP 404, 17 Nov 2026).",
    ),
    "EQ-04": (
        "PASS",
        "requirements.txt; requirements.lock; requirements-pending.txt; requirements-dev.txt; scripts/check_pins.py; Dockerfile; docker-compose.yml; README.md",
        "none (verified by command, not by a test file)",
        "Every line in the four requirements files is pinned with ==, and the Python, Postgres and Redis images use exact tags. The Dockerfile runs scripts/check_pins.py first: a planted 'requests>=2.0' failed the build (exit 1). A no-cache build from a fresh checkout using the README command succeeded and matched requirements.lock (39 of 39 packages), image 326 MB (remediation 3.1). Limits: tags rather than digests; the documented line chains two commands.",
    ),
    "EQ-06": (
        "PARTIAL",
        "docker-compose.yml; src/earnings/api/main.py",
        "none",
        "Stopping the worker, Redis and the database was observed by hand: /health returned 503 naming the failing parts and the stack recovered after restart (audit 3.2). No scripted tests exist and there are no jobs or rows, so duplicate or missing rows could not be checked.",
    ),
    "EQ-07": (
        "UNVERIFIED",
        "src/earnings/tasks.py",
        "none",
        "The only task is a ping with no state. No ingestion task exists to test.",
    ),
    "EQ-08": (
        "PARTIAL",
        ".github/workflows/ci.yml; requirements-dev.txt",
        "none",
        "pip-audit 2.10.1 on requirements.lock reported 'No known vulnerabilities found' (remediation 3.5). The job is in the CI workflow, which has not run on GitHub.",
    ),
    "SP-05": (
        "PARTIAL",
        "src/earnings/api/middleware.py; docker-compose.yml; Dockerfile",
        "none",
        "Log lines carry timestamp, request id, method, path, status and latency only. The client address and the query string are not logged (remediation 3.3). No retention job exists and there is no log schema test.",
    ),
    "SP-06": (
        "PARTIAL",
        ".gitignore; .env.example; docker-compose.yml; src/earnings/config.py; .github/workflows/ci.yml",
        "tests/test_health_unit.py::test_sec_user_agent_value_is_never_returned",
        "No secrets in source: gitleaks 8.30.1 found no leaks in the git history (9 commits) or the working files, and a planted fake token in a scratch folder failed the scan (remediation 3.5). The SEC contact is passed from the shell and never returned by /health. The scan is in the CI workflow, which has not run on GitHub.",
    ),
    "NFR-11": (
        "PASS",
        "src/earnings/api/middleware.py; src/earnings/api/main.py; docker-compose.yml",
        "none (verified by command; automated tests deferred by John's instruction)",
        "Verified by hand on three request kinds: a 200, a 404, and an unhandled exception logged as 500. Each log line has a request id, latency and status, and responses carry an X-Request-ID header (remediation 3.3). Limit: three request kinds were checked, not every one.",
    ),
    "API-01": (
        "PARTIAL",
        "src/earnings/api/main.py",
        "tests/test_stack_integration.py::test_openapi_specification_is_served_and_lists_health",
        "OpenAPI is served and lists /health (passes). Only one of the Section 13 endpoints exists, so it cannot match them all.",
    ),
    "API-02": (
        "PARTIAL",
        "src/earnings/api/main.py",
        "tests/test_stack_integration.py::test_unknown_unversioned_path_returns_404",
        "An unknown unversioned path returns 404 (passes). Satisfied only vacuously: /health is the only endpoint and there is no /v1 endpoint or /metrics yet.",
    ),
    "API-06": (
        "UNVERIFIED",
        "none",
        "none",
        "No JWT is implemented. /health is exempt by the requirement, and no other endpoint exists, so the 401 check cannot be run.",
    ),
    "PL-03": (
        "FAIL",
        "src/earnings/api/main.py",
        "none",
        "Not implemented: /health reports service status only, not the latest transcript date. No transcripts exist yet.",
    ),
    "PL-05": (
        "UNVERIFIED",
        "requirements-pending.txt (alembic listed, not installed)",
        "none",
        "Alembic is not installed (moved to requirements-pending.txt) and no migration or schema exists, so the migration check cannot be run.",
    ),
}
