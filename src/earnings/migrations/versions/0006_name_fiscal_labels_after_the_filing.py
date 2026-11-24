"""Name the fiscal labels after what they describe: the filing, not the period.

XBRL tags a fact with the fiscal year and period of the filing that reported it. The same period
therefore carries several labels across its versions (found by the Phase 1 independent audit), so
the columns are renamed to say so and are not used to match periods. Periods are matched by their
start and end dates. Mapping to calendar quarters is Data DV-06 and FD-04 (Wave 1.7).

Revision ID: 0006
Revises: 0005
"""

from alembic import op

revision = "0006"
down_revision = "0005"
branch_labels = None
depends_on = None

TABLES = ("eps_history", "fundamentals_filing")


def upgrade() -> None:
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} RENAME COLUMN fiscal_year TO filing_fiscal_year")
        op.execute(f"ALTER TABLE {table} RENAME COLUMN fiscal_period TO filing_fiscal_period")


def downgrade() -> None:
    for table in TABLES:
        op.execute(f"ALTER TABLE {table} RENAME COLUMN filing_fiscal_year TO fiscal_year")
        op.execute(f"ALTER TABLE {table} RENAME COLUMN filing_fiscal_period TO fiscal_period")
