"""The call type of a transcript and the filing of an event's EPS (Data TX-01, AE-01; decision
C-58). The independent audit of 26 November 2026 found that neither was stored.

Every transcript of the one source is an earnings call, so the column has that default. The EPS
accession and filing date are those of the first filing of the quarter the label announces.

Revision ID: 0011
Revises: 0010
"""

from alembic import op

revision = "0011"
down_revision = "0010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute("ALTER TABLE transcript ADD COLUMN call_type text NOT NULL DEFAULT 'earnings call'")
    op.execute("ALTER TABLE earnings_event ADD COLUMN eps_accession text")
    op.execute("ALTER TABLE earnings_event ADD COLUMN eps_filed_at date")


def downgrade() -> None:
    op.execute("ALTER TABLE earnings_event DROP COLUMN eps_filed_at")
    op.execute("ALTER TABLE earnings_event DROP COLUMN eps_accession")
    op.execute("ALTER TABLE transcript DROP COLUMN call_type")
