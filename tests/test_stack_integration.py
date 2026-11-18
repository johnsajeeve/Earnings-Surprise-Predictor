"""Integration tests against the running Docker Compose stack (real Postgres, Redis, worker, API).

Start the stack first:  docker compose up -d --wait
These tests fail, not skip, if the stack is down. A skipped test would hide a BLOCKED state.

Traces to: Project-Wide SC-01 (Celery with Redis), Product API-01 and API-02, Product Section 13.
"""

import json
import os
import urllib.error
import urllib.request

API_URL = os.environ.get("TEST_API_URL", "http://api:8000")


def _get(path):
    try:
        with urllib.request.urlopen(API_URL + path, timeout=10) as response:
            return response.status, response.read().decode()
    except urllib.error.HTTPError as err:
        return err.code, err.read().decode()


def test_health_reports_all_services_ok():
    status, text = _get("/health")
    body = json.loads(text)
    assert status == 200, text
    assert body["checks"] == {"postgres": "ok", "redis": "ok", "worker": "ok"}


def test_celery_task_round_trip_through_redis_and_worker():
    from earnings.tasks import ping

    assert ping.delay().get(timeout=20) == "pong"


def test_postgres_accepts_a_query_with_the_app_credentials():
    from sqlalchemy import text

    from earnings.db import get_engine

    with get_engine().connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar() == 1


def test_openapi_specification_is_served_and_lists_health():
    status, text = _get("/openapi.json")
    assert status == 200
    assert "/health" in json.loads(text)["paths"]


def test_unknown_unversioned_path_returns_404():
    status, _ = _get("/not-a-real-path")
    assert status == 404
