"""Settings must fail loudly when required configuration is missing (explicit error handling).

Traces to: Project-Wide SP-06 (configuration comes from the environment), EQ-04 (container).
"""

import pytest
from pydantic import ValidationError

from earnings.config import Settings

REQUIRED = (
    "POSTGRES_HOST",
    "POSTGRES_USER",
    "POSTGRES_PASSWORD",
    "POSTGRES_DB",
    "CELERY_BROKER_URL",
    "CELERY_RESULT_BACKEND",
)


@pytest.mark.parametrize("missing", REQUIRED)
def test_missing_required_setting_raises(monkeypatch, missing):
    for name in REQUIRED:
        monkeypatch.setenv(name, "x://placeholder")
    monkeypatch.delenv(missing)
    with pytest.raises(ValidationError):
        Settings(_env_file=None)


def test_sec_user_agent_is_optional(monkeypatch):
    for name in REQUIRED:
        monkeypatch.setenv(name, "x://placeholder")
    monkeypatch.delenv("SEC_USER_AGENT", raising=False)
    assert Settings(_env_file=None).sec_user_agent == ""
