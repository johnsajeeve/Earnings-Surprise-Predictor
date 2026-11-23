"""Company table: company_id is the SEC CIK as ten digits (Database DB-04, DB-05, decision C-19).

Revision ID: 0001
Revises:
"""

from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE company (
            company_id text PRIMARY KEY CONSTRAINT company_id_is_ten_digit_cik
                CHECK (company_id ~ '^[0-9]{10}$'),
            name text NOT NULL
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE company")
