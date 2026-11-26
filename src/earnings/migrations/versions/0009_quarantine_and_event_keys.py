"""quarantine table and the event uniqueness rule (Data DV-01, DV-03). The ticker lookup index
of DB-14 already exists as the exclusion constraints of migration 0004.

Quarantine holds rows that fail a validation check. They are kept for a person to review and are not
dropped from their own table by the check. The unique index makes one event per company, fiscal
quarter and announcement date a database rule (DV-03).

Revision ID: 0009
Revises: 0008
"""

from alembic import op

revision = "0009"
down_revision = "0008"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE quarantine (
            quarantine_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source_table text NOT NULL,
            row_key text NOT NULL,
            reason text NOT NULL,
            detail jsonb,
            first_seen_at timestamptz NOT NULL DEFAULT now(),
            reviewer_note text,
            CONSTRAINT quarantine_one_per_reason UNIQUE (source_table, row_key, reason)
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX earnings_event_one_per_quarter ON earnings_event "
        "(company_id, period_end, announcement_date) WHERE period_end IS NOT NULL"
    )
    op.execute(
        "CREATE INDEX ticker_history_lookup ON ticker_history (ticker, valid_from, valid_to)"
    )


def downgrade() -> None:
    op.execute("DROP INDEX earnings_event_one_per_quarter")
    op.execute("DROP TABLE quarantine")
