"""Half-open validity periods and the as-of read (Database DB-08, DB-09, DB-10).

- btree_gist, so the database can refuse overlapping periods (DB-10, created here per DB-01).
- ticker_history and index_membership, two entities of Product Section 11. A period includes its
  start date and excludes its end date. An empty end date means it has not ended.
- estimate_snapshot_as_of: the one way to read snapshots for a prediction (DB-09). It returns,
  for a company and a time D, the latest snapshot per source and period captured strictly before D.

Revision ID: 0004
Revises: 0003
"""

from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS btree_gist")
    # The migration history is the migrator's alone: the default privileges would let the worker
    # and the API change it.
    op.execute("REVOKE ALL ON alembic_version FROM earnings_worker, earnings_api")
    op.execute(
        """
        CREATE TABLE ticker_history (
            ticker_history_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            ticker text NOT NULL CHECK (ticker <> ''),
            valid_from date NOT NULL,
            valid_to date,
            CONSTRAINT ticker_history_period CHECK (valid_to IS NULL OR valid_to > valid_from),
            -- one company may hold two tickers at once (two share classes), but not the same twice
            CONSTRAINT ticker_history_no_overlap_per_company EXCLUDE USING gist (
                company_id WITH =, ticker WITH =, daterange(valid_from, valid_to, '[)') WITH &&
            ),
            -- a ticker belongs to one company at a time
            CONSTRAINT ticker_history_one_company_per_ticker EXCLUDE USING gist (
                ticker WITH =, daterange(valid_from, valid_to, '[)') WITH &&
            )
        )
        """
    )
    op.execute(
        """
        CREATE TABLE index_membership (
            index_membership_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            valid_from date NOT NULL,
            valid_to date,
            removal_reason text,
            CONSTRAINT index_membership_period CHECK (valid_to IS NULL OR valid_to > valid_from),
            CONSTRAINT index_membership_no_overlap EXCLUDE USING gist (
                company_id WITH =, daterange(valid_from, valid_to, '[)') WITH &&
            )
        )
        """
    )
    op.execute(
        """
        CREATE FUNCTION company_for_ticker(p_ticker text, p_on date) RETURNS text
        LANGUAGE sql STABLE AS $$
            SELECT company_id FROM ticker_history
            WHERE ticker = p_ticker AND valid_from <= p_on AND (valid_to IS NULL OR p_on < valid_to)
        $$
        """
    )
    op.execute(
        """
        CREATE FUNCTION estimate_snapshot_as_of(p_company text, p_as_of timestamptz)
        RETURNS SETOF estimate_snapshot LANGUAGE sql STABLE AS $$
            SELECT DISTINCT ON (source, period_label) *
            FROM estimate_snapshot
            WHERE company_id = p_company AND captured_at < p_as_of
            ORDER BY source, period_label, captured_at DESC
        $$
        """
    )
    op.execute(
        "COMMENT ON FUNCTION estimate_snapshot_as_of(text, timestamptz) IS "
        "'The only way feature code reads estimate snapshots: the latest per source and period "
        "captured strictly before the given time (Database DB-09).'"
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION estimate_snapshot_as_of(text, timestamptz)")
    op.execute("DROP FUNCTION company_for_ticker(text, date)")
    op.execute("DROP TABLE index_membership")
    op.execute("DROP TABLE ticker_history")
    op.execute("DROP EXTENSION btree_gist")
