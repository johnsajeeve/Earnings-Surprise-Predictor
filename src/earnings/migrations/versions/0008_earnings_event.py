"""earnings_event: one row per kept transcript linked to an earnings release (Product FR-02 and
Section 11; Data LB-01, LB-02, CE-05; Database DB-06).

Holds the three dates, the label route and the continuous time-series SUE. Class labels are not
stored here: their cut-offs are set during EDA and frozen later (Data LB-06, Wave 2.5). The rows can
be rebuilt from the stored facts, so the worker may update them.

The columns extend Product Section 11 (decision D-47, item l): period_end, the release accession,
`incomplete`, `status`, `exclusion_reason`, and the SUE bookkeeping columns.

Revision ID: 0008
Revises: 0007
"""

from alembic import op

revision = "0008"
down_revision = "0007"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE earnings_event (
            event_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            transcript_id bigint NOT NULL UNIQUE REFERENCES transcript (transcript_id),
            period_end date,
            fiscal_period text,
            transcript_date date,
            information_date date,
            announcement_date date,
            announcement_time_utc timestamptz,
            release_accession text NOT NULL,
            eps_basis text NOT NULL,
            label_route text NOT NULL
                CONSTRAINT event_label_route CHECK (label_route IN ('time-series', 'consensus')),
            sue numeric,
            sue_reason text,
            differences_used integer,
            splits_applied integer NOT NULL DEFAULT 0,
            incomplete boolean NOT NULL DEFAULT false,
            status text NOT NULL DEFAULT 'included'
                CONSTRAINT event_status CHECK (status IN ('included', 'excluded')),
            exclusion_reason text,
            CONSTRAINT event_three_dates CHECK (
                incomplete OR (transcript_date IS NOT NULL AND information_date IS NOT NULL
                               AND announcement_date IS NOT NULL)),
            CONSTRAINT event_sue_or_reason CHECK ((sue IS NULL) = (sue_reason IS NOT NULL)),
            CONSTRAINT event_exclusion_reason
                CHECK ((status = 'excluded') = (exclusion_reason IS NOT NULL))
        )
        """
    )
    op.execute(
        "CREATE INDEX earnings_event_company ON earnings_event (company_id, announcement_date)"
    )


def downgrade() -> None:
    op.execute("DROP TABLE earnings_event")
