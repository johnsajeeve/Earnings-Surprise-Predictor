"""Database engine. Tables and migrations come in the next step."""

from functools import lru_cache

from sqlalchemy import Engine, create_engine

from earnings.config import get_settings


@lru_cache
def get_engine() -> Engine:
    # pool_pre_ping drops dead connections instead of raising on the next request.
    return create_engine(get_settings().database_url, pool_pre_ping=True)
