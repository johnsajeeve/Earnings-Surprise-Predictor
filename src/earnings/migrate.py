"""Create the roles and the database, and apply the migrations (Database DB-02, DB-03, DB-16,
Product PL-05, decision C-44).

Run:  python -m earnings.migrate

The superuser from the environment is used here and nowhere else. It creates the three roles
(migrator, worker, api), gives the migrator the database, and sets each role's time-outs. The
migrations then run as the migrator. Every step can be run again with the same result.
"""

from pathlib import Path

import psycopg
from alembic import command
from alembic.config import Config
from alembic.script import ScriptDirectory
from psycopg import sql
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from sqlalchemy.pool import NullPool

from earnings.config import ROLE_NAMES, get_settings

# Statement time-outs per role in seconds (decision C-44). Lock and idle-in-transaction time-outs
# are the same for every role.
STATEMENT_TIMEOUT_SECONDS = {"migrator": 300, "worker": 120, "api": 10}
LOCK_TIMEOUT_SECONDS = 5
IDLE_IN_TRANSACTION_TIMEOUT_SECONDS = 60

_MIGRATIONS = Path(__file__).parent / "migrations"


def _admin(database: str) -> psycopg.Connection:
    s = get_settings()
    return psycopg.connect(
        host=s.postgres_host,
        port=s.postgres_internal_port,
        user=s.postgres_user,
        password=s.postgres_password,
        dbname=database,
        autocommit=True,
    )


def _ident(name: str) -> sql.Identifier:
    return sql.Identifier(name)


def bootstrap(database: str) -> None:
    """Create or update the roles and the database. Safe to repeat."""
    s = get_settings()
    migrator, worker, api = (ROLE_NAMES[r] for r in ("migrator", "worker", "api"))
    with _admin("postgres") as conn:
        for role in ("migrator", "worker", "api"):
            name = ROLE_NAMES[role]
            exists = conn.execute("SELECT 1 FROM pg_roles WHERE rolname = %s", (name,)).fetchone()
            verb = "ALTER" if exists else "CREATE"
            conn.execute(
                sql.SQL(
                    verb + " ROLE {} LOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION "
                    "PASSWORD {}"
                ).format(_ident(name), sql.Literal(s.role_password(role)))
            )
            for key, value in (
                ("statement_timeout", f"{STATEMENT_TIMEOUT_SECONDS[role]}s"),
                ("lock_timeout", f"{LOCK_TIMEOUT_SECONDS}s"),
                (
                    "idle_in_transaction_session_timeout",
                    f"{IDLE_IN_TRANSACTION_TIMEOUT_SECONDS}s",
                ),
            ):
                conn.execute(
                    sql.SQL("ALTER ROLE {} SET {} = {}").format(
                        _ident(name), _ident(key), sql.Literal(value)
                    )
                )
        found = conn.execute("SELECT 1 FROM pg_database WHERE datname = %s", (database,))
        if found.fetchone():
            conn.execute(
                sql.SQL("ALTER DATABASE {} OWNER TO {}").format(_ident(database), _ident(migrator))
            )
        else:
            conn.execute(
                sql.SQL("CREATE DATABASE {} OWNER {}").format(_ident(database), _ident(migrator))
            )
        conn.execute(sql.SQL("REVOKE ALL ON DATABASE {} FROM PUBLIC").format(_ident(database)))
        for name in (worker, api):
            conn.execute(
                sql.SQL("GRANT CONNECT ON DATABASE {} TO {}").format(_ident(database), _ident(name))
            )
    with _admin(database) as conn:
        conn.execute("REVOKE ALL ON SCHEMA public FROM PUBLIC")
        conn.execute(sql.SQL("GRANT ALL ON SCHEMA public TO {}").format(_ident(migrator)))
        conn.execute(
            sql.SQL("GRANT USAGE ON SCHEMA public TO {}, {}").format(_ident(worker), _ident(api))
        )
        # Tables the migrator creates later: the worker reads and writes but never deletes, the
        # API only reads. Append-only tables are tightened by the migrations that create them.
        for target, privileges in ((worker, "SELECT, INSERT, UPDATE"), (api, "SELECT")):
            conn.execute(
                sql.SQL(
                    "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
                    "GRANT " + privileges + " ON TABLES TO {}"
                ).format(_ident(migrator), _ident(target))
            )
        conn.execute(
            sql.SQL(
                "ALTER DEFAULT PRIVILEGES FOR ROLE {} IN SCHEMA public "
                "GRANT USAGE, SELECT ON SEQUENCES TO {}"
            ).format(_ident(migrator), _ident(worker))
        )


def migrator_url(database: str) -> URL:
    return get_settings().database_url_for("migrator", database)


def _config() -> Config:
    config = Config()
    config.set_main_option("script_location", str(_MIGRATIONS))
    return config


def head_revision() -> str | None:
    return ScriptDirectory.from_config(_config()).get_current_head()


def upgrade(database: str, revision: str = "head") -> None:
    _run(database, lambda config: command.upgrade(config, revision))


def downgrade(database: str, revision: str) -> None:
    _run(database, lambda config: command.downgrade(config, revision))


def _run(database: str, action) -> None:  # type: ignore[no-untyped-def]
    engine = create_engine(migrator_url(database), poolclass=NullPool)
    try:
        with engine.begin() as connection:
            config = _config()
            config.attributes["connection"] = connection
            action(config)
    finally:
        engine.dispose()


def _require_test_database(database: str, action: str) -> None:
    """Only a database whose name ends in _test may be dropped or emptied (Database DB-16)."""
    if not database.endswith("_test"):
        raise RuntimeError(f"refusing to {action} {database!r}: it is not a test database")


def drop_database(database: str) -> None:
    """Drop a test database."""
    _require_test_database(database, "drop")
    with _admin("postgres") as conn:
        conn.execute(sql.SQL("DROP DATABASE IF EXISTS {} WITH (FORCE)").format(_ident(database)))


def truncate_all(database: str) -> None:
    """Empty every table except the migration history. Test databases only."""
    _require_test_database(database, "empty")
    with _admin(database) as conn:
        tables = [
            row[0]
            for row in conn.execute(
                "SELECT tablename FROM pg_tables "
                "WHERE schemaname = 'public' AND tablename <> 'alembic_version'"
            )
        ]
        for table in tables:
            conn.execute(sql.SQL("TRUNCATE {} CASCADE").format(_ident(table)))


def main() -> None:
    database = get_settings().postgres_db
    if database.endswith("_test"):
        raise RuntimeError("the project database name must not end in _test (Database DB-16)")
    bootstrap(database)
    upgrade(database)
    print(f"database {database}: roles ready, migrations at {head_revision()}", flush=True)


if __name__ == "__main__":
    main()
