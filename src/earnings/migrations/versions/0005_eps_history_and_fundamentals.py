"""EpsHistory and FundamentalsFiling: XBRL facts as dated versions (Data LB-03, LB-04, AE-03,
AE-04, FD-01 to FD-03; Database DB-08, DB-09).

Both tables hold every version of a fact that a filing reported, never an update. The first-filed
value is the earliest version and a restatement is a later row with its own filing date. Reads for
a prediction go through the as-of functions below, which show only versions filed strictly before
the announcement date.

The columns extend the field lists in Product Section 11 (period dates, accession number, filing
date per version, derived flag, tag). They are reported to John as a schema detail to approve.

Revision ID: 0005
Revises: 0004
"""

from alembic import op

revision = "0005"
down_revision = "0004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE eps_history (
            eps_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            period_start date NOT NULL,
            period_end date NOT NULL,
            period_kind text NOT NULL CHECK (period_kind IN ('quarter', 'year')),
            fiscal_year integer,
            fiscal_period text,
            eps_diluted numeric NOT NULL,
            derived boolean NOT NULL DEFAULT false,
            basis text NOT NULL DEFAULT 'gaap',
            form text,
            accession text NOT NULL,
            filed_at date NOT NULL,
            payload_id bigint REFERENCES raw_payload (payload_id),
            CONSTRAINT eps_history_period CHECK (period_end > period_start),
            CONSTRAINT eps_history_one_version UNIQUE
                (company_id, period_start, period_end, derived, accession)
        )
        """
    )
    op.execute("CREATE INDEX eps_history_company_period ON eps_history (company_id, period_end)")
    op.execute(
        """
        CREATE TABLE fundamentals_filing (
            fundamentals_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            period_start date NOT NULL,
            period_end date NOT NULL,
            fiscal_year integer,
            fiscal_period text,
            revenue numeric,
            revenue_tag text,
            gross_profit numeric,
            operating_income numeric,
            derived boolean NOT NULL DEFAULT false,
            form text,
            accession text NOT NULL,
            filed_at date NOT NULL,
            payload_id bigint REFERENCES raw_payload (payload_id),
            CONSTRAINT fundamentals_period CHECK (period_end > period_start),
            CONSTRAINT fundamentals_one_version UNIQUE
                (company_id, period_start, period_end, derived, accession)
        )
        """
    )
    op.execute(
        "CREATE INDEX fundamentals_company_period ON fundamentals_filing (company_id, period_end)"
    )
    # Append only: the worker may insert and read, never update or delete (DB-08).
    op.execute("REVOKE UPDATE ON eps_history, fundamentals_filing FROM earnings_worker")
    for table, key in (("eps_history", "eps_id"), ("fundamentals_filing", "fundamentals_id")):
        fn = f"{table}_as_of"
        op.execute(
            f"""
            CREATE FUNCTION {fn}(p_company text, p_as_of date)
            RETURNS SETOF {table} LANGUAGE sql STABLE AS $$
                SELECT DISTINCT ON (period_start, period_end, derived) *
                FROM {table}
                WHERE company_id = p_company AND filed_at < p_as_of
                ORDER BY period_start, period_end, derived, filed_at DESC, {key} DESC
            $$
            """
        )
        first = f"{table}_first_filed"
        op.execute(
            f"""
            CREATE FUNCTION {first}(p_company text, p_as_of date)
            RETURNS SETOF {table} LANGUAGE sql STABLE AS $$
                SELECT DISTINCT ON (period_start, period_end, derived) *
                FROM {table}
                WHERE company_id = p_company AND filed_at < p_as_of
                ORDER BY period_start, period_end, derived, filed_at ASC, {key} ASC
            $$
            """
        )


def downgrade() -> None:
    for table in ("fundamentals_filing", "eps_history"):
        op.execute(f"DROP FUNCTION {table}_first_filed(text, date)")
        op.execute(f"DROP FUNCTION {table}_as_of(text, date)")
    op.execute("DROP TABLE fundamentals_filing")
    op.execute("DROP TABLE eps_history")
