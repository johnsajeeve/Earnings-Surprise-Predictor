"""Unit tests for GET /health. Dependencies are stand-ins, so no running stack is needed.

Synthetic stand-ins are used only here, in automated tests (Project-Wide SC-04).
Traces to: Product API-02 (/health is unversioned), Product Section 13, Project-Wide SP-06.
"""

from types import SimpleNamespace

import pytest
from fastapi.testclient import TestClient

from earnings.api import main


@pytest.fixture(autouse=True)
def fresh_health_cache():
    """/health reuses its result for a few seconds (F-07). Each test starts with an empty cache."""
    main._reset_cache()
    yield
    main._reset_cache()


@pytest.fixture
def client():
    return TestClient(main.app)


def _stub(monkeypatch, postgres="ok", redis="ok", worker="ok"):
    monkeypatch.setattr(main, "_check_postgres", lambda: postgres)
    monkeypatch.setattr(main, "_check_redis", lambda: redis)
    monkeypatch.setattr(main, "_check_worker", lambda: worker)


@pytest.mark.req("NFR-04-AC1")
@pytest.mark.code("src/earnings/api/main.py")
def test_all_ok_returns_200(client, monkeypatch):
    _stub(monkeypatch)
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["checks"] == {"postgres": "ok", "redis": "ok", "worker": "ok"}


@pytest.mark.req("NFR-04-AC1")
@pytest.mark.code("src/earnings/api/main.py")
@pytest.mark.parametrize("failing", ["postgres", "redis", "worker"])
def test_any_failure_returns_503_and_names_the_component(client, monkeypatch, failing):
    _stub(monkeypatch, **{failing: "error: boom"})
    response = client.get("/health")
    assert response.status_code == 503
    body = response.json()
    assert body["status"] == "degraded"
    assert body["checks"][failing] == "error: boom"


@pytest.mark.req("SP-06")
@pytest.mark.code("src/earnings/api/main.py", "src/earnings/config.py")
def test_sec_user_agent_value_is_never_returned(client, monkeypatch):
    _stub(monkeypatch)
    monkeypatch.setattr(
        main,
        "get_settings",
        lambda: SimpleNamespace(sec_user_agent="PLANTED-CONTACT-VALUE", health_cache_seconds=0),
    )
    response = client.get("/health")
    assert "PLANTED-CONTACT-VALUE" not in response.text
    assert response.json()["sec_user_agent_set"] is True


@pytest.mark.req("SP-06")
@pytest.mark.code("src/earnings/api/main.py", "src/earnings/config.py")
def test_sec_user_agent_unset_is_reported_false(client, monkeypatch):
    _stub(monkeypatch)
    monkeypatch.setattr(
        main, "get_settings", lambda: SimpleNamespace(sec_user_agent="", health_cache_seconds=0)
    )
    assert client.get("/health").json()["sec_user_agent_set"] is False


@pytest.mark.req("NFR-04-AC1")
@pytest.mark.code("src/earnings/api/main.py", "src/earnings/db.py")
def test_database_exception_is_reported_not_raised(monkeypatch):
    def broken_engine():
        raise RuntimeError("database unreachable")

    monkeypatch.setattr(main, "get_engine", broken_engine)
    assert main._check_postgres() == "error: RuntimeError"
