"""Alembic environment. Migrations run on a connection that earnings.migrate passes in."""

from alembic import context

connection = context.config.attributes.get("connection")
if connection is None:
    raise RuntimeError("run migrations through earnings.migrate, not the alembic command line")

context.configure(connection=connection, target_metadata=None)
with context.begin_transaction():
    context.run_migrations()
