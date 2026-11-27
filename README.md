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
python3 scripts/check_pins.py requirements.txt requirements.lock requirements-worker.txt requirements-worker.lock requirements-pending.txt requirements-dev.txt
docker run --rm -e PYTHONDONTWRITEBYTECODE=1 -v "$PWD:/work" -w /work python:3.12.16-slim sh -c \
  'pip install -q --root-user-action=ignore -r requirements.txt -c requirements.lock -r requirements-dev.txt \
   && ruff check --no-cache . && ruff format --check --no-cache . && mypy --cache-dir=/tmp/mypycache'
docker compose run --rm --no-deps -v "$PWD/tests:/app/tests:ro" -v "$PWD/requirements-dev.txt:/app/requirements-dev.txt:ro" api sh -c \
  'pip install --user -q -r requirements-dev.txt && python -m pytest -p no:cacheprovider tests'
```

The worker has its own image with spaCy, PyTorch (CPU) and Transformers (`requirements-worker.txt`). To score the stored transcripts with FinBERT (non-commercial licence, downloaded once to the data volume; scoring all calls takes many hours and continues where it left off if stopped):

```bash
docker compose exec worker python -m earnings.finbert download
docker compose run -d --name earnings-scoring worker python -m earnings.finbert score
docker logs --tail 3 earnings-scoring
```

The tests that call the live services need the stack running (`docker compose up -d --wait`).

### Requirement, test and code matrix

Every test names the requirement check it exercises with `@pytest.mark.req("FR-01-AC1")`, and the project files it exercises with `@pytest.mark.code("src/...")`. `scripts/test_matrix.py` turns those markers into one matrix that can be followed in any direction. It needs only Python.

```
python3 scripts/test_matrix.py build     # writes audits/test_matrix.json and .md (generated, committed)
python3 scripts/test_matrix.py verify    # every check has a test, and no check changed since its tests were reviewed
python3 scripts/test_matrix.py trace FR-01-AC1        # from a check to its tests and code
python3 scripts/test_matrix.py trace src/earnings/api/middleware.py   # from code to tests and checks
python3 scripts/test_matrix.py accept FR-01           # after reviewing the tests for FR-01
```

`tests/requirement_checks.lock` holds the wording of each check the tests were reviewed against. If a requirement is reworded, or checks are inserted or reordered, `verify` fails until the tests are reviewed and `accept` is run. To add measured results, which are not committed:

```
python -m coverage run -m pytest -p no:cacheprovider tests --junitxml=test-results/junit.xml
python -m coverage json --show-contexts -o test-results/coverage.json
python3 scripts/test_matrix.py results --junit test-results/junit.xml --coverage test-results/coverage.json
```

The report gives PASS, FAIL, BLOCKED or NOT TESTED for each check, and the files each test really executed beside the files its markers declare. A PASS means a test passed, not that the requirement is satisfied.

## Dependencies

Every dependency is pinned to an exact version (Project-Wide EQ-04), and the image build fails if one is not.

- `requirements.txt`: what the code uses now.
- `requirements.lock`: every package including transitive ones, used as a constraints file by the Dockerfile.
- `requirements-pending.txt`: pinned packages for later steps. Not installed.
- `requirements-dev.txt`: test, lint, type and security tools. Not in the image.

## Audit

See [audits/](audits/): the audit report and the generated requirements traceability file.
