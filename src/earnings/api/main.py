"""FastAPI application. Only the health check exists so far."""

import threading
import time

import redis
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import text

from earnings.api import middleware
from earnings.celery_app import celery_app
from earnings.config import get_settings
from earnings.db import get_engine

app = FastAPI(title="Earnings Surprise Predictor", version="0.0.1")
middleware.install(app)


def _check_postgres() -> str:
    try:
        with get_engine().connect() as conn:
            conn.execute(text("SELECT 1"))
        return "ok"
    except Exception as exc:  # noqa: BLE001  report the failure, never crash the health check
        return f"error: {type(exc).__name__}"


def _check_redis() -> str:
    try:
        client = redis.Redis.from_url(
            get_settings().celery_broker_url, socket_connect_timeout=2, socket_timeout=2
        )
        client.ping()
        return "ok"
    except Exception as exc:  # noqa: BLE001  report the failure, never crash the health check
        return f"error: {type(exc).__name__}"


def _check_worker() -> str:
    try:
        # limit=1 returns as soon as one worker replies. Without it, ping waits the full timeout.
        replies = celery_app.control.ping(timeout=2.0, limit=1)
        return "ok" if replies else "error: no worker replied"
    except Exception as exc:  # noqa: BLE001  report the failure, never crash the health check
        return f"error: {type(exc).__name__}"


# /health is public, and each uncached call costs a broker round trip of up to 2 seconds.
# The result is therefore reused for a few seconds (audit finding F-07, Project-Wide SP-02).
# A failure can show up to that many seconds late.
_cache_lock = threading.Lock()
_cached: tuple[float, dict[str, object], int] | None = None  # (time, body, status)


def _reset_cache() -> None:
    global _cached
    with _cache_lock:
        _cached = None


def _compute_health() -> tuple[dict[str, object], int]:
    checks = {
        "postgres": _check_postgres(),
        "redis": _check_redis(),
        "worker": _check_worker(),
    }
    healthy = all(value == "ok" for value in checks.values())
    body: dict[str, object] = {
        "status": "ok" if healthy else "degraded",
        "checks": checks,
        # Reports whether the SEC contact is set. It never returns the value.
        "sec_user_agent_set": bool(get_settings().sec_user_agent),
    }
    return body, 200 if healthy else 503


# A plain "def" runs in FastAPI's thread pool, so these blocking calls do not stall the server.
@app.get("/health")
def health() -> JSONResponse:
    global _cached
    ttl = get_settings().health_cache_seconds
    now = time.monotonic()
    with _cache_lock:
        if ttl > 0 and _cached is not None and now - _cached[0] < ttl:
            return JSONResponse(_cached[1], status_code=_cached[2])
    body, status = _compute_health()
    with _cache_lock:
        _cached = (now, body, status)
    return JSONResponse(body, status_code=status)
