# Earnings-Surprise-Predictor

LLM-Powered Earnings Surprise Predictor. A BSc Computer Science third year project (University of Manchester, 2026-27). The scope, requirements and decisions are in [docs/](docs/SSOT.md). Working rules are in [Deterministic_audit.md](Deterministic_audit.md).

## Run it

Needs Docker with Compose. One command from a clean checkout:

```
cp .env.example .env && docker compose up --build -d
```

Then check it:

```
curl http://localhost:8000/health
```

A healthy stack answers `200` with `"status": "ok"` for Postgres, Redis and the worker. Stop it with `docker compose down`. Add `-v` to also delete the database.

`SEC_USER_AGENT` (your contact for the SEC) is read from your shell environment and is never written to a file. Set it in `~/.bashrc` before running anything that calls SEC EDGAR.

## Checks

The commands CI runs, for use locally. Tools are pinned in `requirements-dev.txt` and run in a throwaway container, so nothing is installed on your machine:

```
python3 scripts/check_pins.py requirements.txt requirements.lock requirements-pending.txt requirements-dev.txt
docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD:/work" -w /work python:3.12.16-slim sh -c \
  'pip install -q --root-user-action=ignore -r requirements.txt -c requirements.lock -r requirements-dev.txt \
   && ruff check --no-cache . && ruff format --check --no-cache . && mypy --cache-dir=/tmp/mypycache'
docker compose run --rm --no-deps -v "$PWD/tests:/app/tests:ro" -v "$PWD/requirements-dev.txt:/app/requirements-dev.txt:ro" api sh -c \
  'pip install --user -q -r requirements-dev.txt && python -m pytest -p no:cacheprovider tests'
```

The tests that call the live services need the stack running (`docker compose up -d --wait`).

## Dependencies

Every dependency is pinned to an exact version (Project-Wide EQ-04), and the image build fails if one is not.

- `requirements.txt`: what the code uses now.
- `requirements.lock`: every package including transitive ones, used as a constraints file by the Dockerfile.
- `requirements-pending.txt`: pinned packages for later steps. Not installed.
- `requirements-dev.txt`: test, lint, type and security tools. Not in the image.

## Audit

See [audits/](audits/): the audit report and the generated requirements traceability file.
