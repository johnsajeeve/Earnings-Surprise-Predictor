# Two images from one file. `app` is the API and the migration step. `worker` adds the model
# packages, which only the worker needs (Deployment DP-03).
# Base image pinned to an exact version (Project-Wide EQ-04).
FROM python:3.12.16-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Run as a normal user, not root.
RUN useradd --create-home --uid 1000 app
# A volume mounted here (docker-compose.yml, `data`) starts with this owner.
RUN mkdir /data && chown app /data

# Layer 1: the build fails here if any requirement line is not pinned with == (EQ-04).
COPY scripts/check_pins.py ./scripts/check_pins.py
COPY requirements.txt requirements.lock ./
RUN python scripts/check_pins.py requirements.txt requirements.lock

# Layer 2: install. The lock file pins every transitive package too.
# Copied before the code, so code edits do not reinstall packages.
RUN pip install -r requirements.txt -c requirements.lock


# ---- the worker: the same base, plus spaCy, PyTorch (CPU only) and Transformers ----------------
FROM base AS worker
COPY requirements-worker.txt requirements-worker.lock ./
RUN python scripts/check_pins.py requirements-worker.txt requirements-worker.lock
# PyTorch comes from its CPU index: the default package on PyPI brings the GPU libraries.
RUN pip install --no-deps torch==2.15.0+cpu --index-url https://download.pytorch.org/whl/cpu
RUN pip install -r requirements-worker.txt -r requirements-worker.lock -c requirements.lock
# The spaCy English model is not on PyPI. pip refuses the file if its hash differs.
RUN pip install --no-deps "en_core_web_sm @ https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-3.8.0/en_core_web_sm-3.8.0-py3-none-any.whl#sha256=1932429db727d4bff3deed6b34cfc05df17794f4a52eeb26cf8928f7c1a0fb85" && pip check

COPY src/ ./src/
ENV PYTHONPATH=/app/src
USER app
CMD ["celery", "-A", "earnings.celery_app", "worker", "--loglevel=info"]

# ---- the API and the migration step. Last, so a plain `docker build .` gives this one. --------
FROM base AS app
# Layer 3: application code.
COPY src/ ./src/
ENV PYTHONPATH=/app/src

USER app

EXPOSE 8000

# Default command is the API. The worker service overrides it in docker-compose.yml.
# The access log is off because earnings.api.middleware writes the request log (NFR-11, SP-05).
CMD ["uvicorn", "earnings.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
