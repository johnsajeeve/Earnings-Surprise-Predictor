"""price_daily and adjustment_factor, and the source version of a raw payload
(Data PX-01 to PX-03, SR-04; decisions C-49 and C-51; Database DB-08, DB-09).

Prices are the raw close only. Splits and dividends are dated factors in their own table, so an
adjusted series is computed when it is read and is never stored beside raw prices. Both tables are
append only: a corrected value is a new row. Reads for a prediction go through the functions below,
which show only dates on one side of a given day.

Revision ID: 0010
Revises: 0009
"""

from alembic import op

revision = "0010"
down_revision = "0009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE raw_payload ADD COLUMN source_version text")
    op.execute(
        """
        CREATE TABLE price_daily (
            price_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            ticker text NOT NULL,
            price_date date NOT NULL,
            close_raw numeric NOT NULL CHECK (close_raw > 0),
            volume bigint,
            source text NOT NULL,
            source_version text NOT NULL,
            captured_at timestamptz NOT NULL DEFAULT now(),
            payload_id bigint REFERENCES raw_payload (payload_id),
            CONSTRAINT price_daily_one_version UNIQUE (company_id, source, price_date, close_raw)
        )
        """
    )
    op.execute("CREATE INDEX price_daily_company_date ON price_daily (company_id, price_date)")
    op.execute(
        """
        CREATE TABLE adjustment_factor (
            factor_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            ex_date date NOT NULL,
            kind text NOT NULL CONSTRAINT factor_kind CHECK (kind IN ('split', 'dividend')),
            value numeric NOT NULL CHECK (value > 0),
            source text NOT NULL,
            source_version text NOT NULL,
            captured_at timestamptz NOT NULL DEFAULT now(),
            payload_id bigint REFERENCES raw_payload (payload_id),
            CONSTRAINT adjustment_factor_one_version
                UNIQUE (company_id, source, ex_date, kind, value)
        )
        """
    )
    op.execute("REVOKE UPDATE ON price_daily, adjustment_factor FROM earnings_worker")
    # Momentum may see only days before the announcement session; outcomes only from it (PX-02).
    for name, comparison in (("price_daily_before", "<"), ("price_daily_from", ">=")):
        op.execute(
            f"""
            CREATE FUNCTION {name}(p_company text, p_day date)
            RETURNS SETOF price_daily LANGUAGE sql STABLE AS $$
                SELECT DISTINCT ON (source, price_date) *
                FROM price_daily
                WHERE company_id = p_company AND price_date {comparison} p_day
                ORDER BY source, price_date, captured_at DESC, price_id DESC
            $$
            """
        )
    op.execute(
        """
        CREATE FUNCTION adjustment_factor_as_of(p_company text, p_day date)
        RETURNS SETOF adjustment_factor LANGUAGE sql STABLE AS $$
            SELECT DISTINCT ON (source, ex_date, kind) *
            FROM adjustment_factor
            WHERE company_id = p_company AND ex_date < p_day
            ORDER BY source, ex_date, kind, captured_at DESC, factor_id DESC
        $$
        """
    )


def downgrade() -> None:
    op.execute("DROP FUNCTION adjustment_factor_as_of(text, date)")
    op.execute("DROP FUNCTION price_daily_from(text, date)")
    op.execute("DROP FUNCTION price_daily_before(text, date)")
    op.execute("DROP TABLE adjustment_factor")
    op.execute("DROP TABLE price_daily")
    op.execute("ALTER TABLE raw_payload DROP COLUMN source_version")
