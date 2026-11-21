"""Settings read from environment variables. Nothing secret is stored in code."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Required. Docker Compose sets these. The app fails at start-up if one is missing.
    postgres_host: str
    postgres_user: str
    postgres_password: str
    postgres_db: str
    celery_broker_url: str
    celery_result_backend: str

    # Port inside the Docker network. The host port in .env is a different setting.
    postgres_internal_port: int = 5432

    # Contact string the SEC asks for in the User-Agent header (decision C-10).
    # Optional here, because the health check must work before it is set.
    sec_user_agent: str = ""

    # How long a /health result is reused, in seconds (audit finding F-07).
    health_cache_seconds: float = 5.0

    @property
    def database_url(self) -> URL:
        # Built from parts, not a string, so a password containing @ : / # ? is escaped
        # correctly (audit finding F-04).
        return URL.create(
            "postgresql+psycopg",
            username=self.postgres_user,
            password=self.postgres_password,
            host=self.postgres_host,
            port=self.postgres_internal_port,
            database=self.postgres_db,
        )


@lru_cache
def get_settings() -> Settings:
    # The required fields are filled from environment variables, which mypy cannot see.
    return Settings()  # type: ignore[call-arg]
