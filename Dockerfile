# One image for the API and the Celery worker. Compose chooses the command.
# Base image pinned to an exact version (Project-Wide EQ-04).
FROM python:3.12.16-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app

# Run as a normal user, not root.
RUN useradd --create-home --uid 1000 app

# Layer 1: the build fails here if any requirement line is not pinned with == (EQ-04).
COPY scripts/check_pins.py ./scripts/check_pins.py
COPY requirements.txt requirements.lock ./
RUN python scripts/check_pins.py requirements.txt requirements.lock

# Layer 2: install. The lock file pins every transitive package too.
# Copied before the code, so code edits do not reinstall packages.
RUN pip install -r requirements.txt -c requirements.lock

# Layer 3: application code.
COPY src/ ./src/
ENV PYTHONPATH=/app/src

USER app

EXPOSE 8000

# Default command is the API. The worker service overrides it in docker-compose.yml.
# The access log is off because earnings.api.middleware writes the request log (NFR-11, SP-05).
CMD ["uvicorn", "earnings.api.main:app", "--host", "0.0.0.0", "--port", "8000", "--no-access-log"]
