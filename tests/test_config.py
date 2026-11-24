"""Settings must fail loudly when required configuration is missing (explicit error handling).

Traces to: Project-Wide SP-06 (configuration comes from the environment), EQ-04 (container).
"""

import pytest
from pydantic import ValidationError

from earnings.config import Settings

REQUIRED = (
    "POSTGRES_HOST",
    "POSTGRES_DB",
    "DB_MIGRATOR_PASSWORD",
    "DB_WORKER_PASSWORD",
    "DB_API_PASSWORD",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
)


@pytest.mark.req("SP-06")
@pytest.mark.code("src/earnings/config.py")
@pytest.mark.parametrize("missing", REQUIRED)
def test_missing_required_setting_raises(monkeypatch, missing):
    for name in REQUIRED:
        monkeypatch.setenv(name, "x://placeholder")
    monkeypatch.delenv(missing)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


@pytest.mark.req("SP-06")
@pytest.mark.code("src/earnings/config.py")
def test_sec_user_agent_is_optional(monkeypatch):
    for name in REQUIRED:
        monkeypatch.setenv(name, "x://placeholder")
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    assert Settings(_env_file=None).sec_user_agent == ""


@pytest.mark.req("DB-02")
@pytest.mark.code("src/earnings/config.py")
def test_the_superuser_settings_are_optional_so_a_service_can_run_without_them(monkeypatch):
    for name in REQUIRED:
        monkeypatch.setenv(name, "x://placeholder")
    monkeypatch.delenv("POSTGRES_USER", raising=False)
    monkeypatch.delenv("POSTGRES_PASSWORD", raising=False)
    settings = Settings(_env_file=None)
    assert (settings.postgres_user, settings.postgres_password) == ("", "")
    assert not hasattr(settings, "database_url")  # no URL for the superuser exists in the code
