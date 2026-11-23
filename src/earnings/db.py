"""Database engines, one per application role (Database DB-02, DB-03, decision C-44)."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from earnings.config import get_settings

# Per process: 5 connections plus 5 overflow, wait at most 10 seconds for one (decision C-44).
POOL_SIZE = 5
MAX_OVERFLOW = 5
POOL_TIMEOUT_SECONDS = 10


@lru_cache
def get_engine(role: str = "api") -> Engine:
    """The pooled engine for a role: 'api' (read only) or 'worker' (read and write, no delete)."""
    return create_engine(
        get_settings().database_url_for(role),
        pool_size=POOL_SIZE,
        max_overflow=MAX_OVERFLOW,
        pool_timeout=POOL_TIMEOUT_SECONDS,
        # pool_pre_ping drops dead connections instead of raising on the next request.
        pool_pre_ping=True,
    )
