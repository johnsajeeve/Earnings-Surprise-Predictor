"""Settings read from environment variables. Nothing secret is stored in code."""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import URL


class Settings(BaseSettings):
    model_config = SettingsConfigDict(extra="ignore")

    # Required. Docker Compose sets these. The app fails at start-up if one is missing.
    postgres_host: str
    postgres_db: str
    celery_broker_url: str
    celery_result_backend: str

    # Passwords of the three application roles (Database DB-02, decision C-44). The superuser above
    # is used only to create the roles and the database, never by the running application.
    db_migrator_password: str
    db_worker_password: str
    db_api_password: str

    # The superuser. Only the migration step and the test suite set these; the worker does not
    # have them, and the running application never uses them.
    postgres_user: str = ""
    postgres_password: str = ""

    # Where large downloaded source files live (the `data` volume in docker-compose.yml).
    data_dir: str = "/data"

    # Port inside the Docker network. The host port in .env is a different setting.
    postgres_internal_port: int = 5432

    # Capture the day's consensus when the worker starts and today has no snapshot (C-46).
    # Off by default, so a test or CI stack makes no outside calls. Set true on the machine
    # that runs the daily capture.
    capture_catch_up: bool = False

    # Collection through yfinance. Off: Yahoo's terms bar automated access without written
    # permission (read 26 November 2026; decision C-61). Turning it on is the owner's choice and
    # needs that permission or a recorded decision to accept the risk.
    yahoo_collection: bool = False

    # Contact string the SEC asks for in the User-Agent header (decision C-10).
    # Optional here, because the health check must work before it is set.
    sec_user_agent: str = ""

    # How long a /health result is reused, in seconds (audit finding F-07).
    health_cache_seconds: float = 5.0

    def role_password(self, role: str) -> str:
        return {
            "migrator": self.db_migrator_password,
            "worker": self.db_worker_password,
            "api": self.db_api_password,
        }[role]

    def database_url_for(self, role: str, database: str | None = None) -> URL:
        """Connection URL for one application role (Database DB-02). Never the superuser."""
        return URL.create(
            "postgresql+psycopg",
            username=ROLE_NAMES[role],
            password=self.role_password(role),
            host=self.postgres_host,
            port=self.postgres_internal_port,
            database=database or self.postgres_db,
        )


ROLE_NAMES = {
    "migrator": "earnings_migrator",
    "worker": "earnings_worker",
    "api": "earnings_api",
}


@lru_cache
def get_settings() -> Settings:
    # The required fields are filled from environment variables, which mypy cannot see.
    return Settings()  # type: ignore[call-arg]
