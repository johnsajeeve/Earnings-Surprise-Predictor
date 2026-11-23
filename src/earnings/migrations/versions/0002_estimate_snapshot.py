"""EstimateSnapshot: forward consensus snapshots (Data SR-08, SR-10, CE-01; Product FR-14).

Shape approved in decision C-44: company_id is required and event_id is empty until the event is
built (Wave 1.6, which adds the link to the event table). Rows are appended only: the worker role
may insert and read but not update or delete. A snapshot cannot be stamped before the capture
start date (SR-08), and one company has one snapshot per source, period and UTC day.

Revision ID: 0002
Revises: 0001
"""

from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None

# The first capture day. Earlier timestamps are refused (SR-08). Matches consensus.CAPTURE_START.
CAPTURE_START = "2026-11-23 00:00:00+00"


def upgrade() -> None:
    op.execute(
        f"""
        CREATE TABLE estimate_snapshot (
            snapshot_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            event_id bigint,
            mean_estimate numeric NOT NULL,
            low_estimate numeric,
            high_estimate numeric,
            std_estimate numeric,
            estimate_count integer,
            eps_basis text,
            period_label text NOT NULL,
            source text NOT NULL,
            source_version text NOT NULL,
            captured_at timestamptz NOT NULL
                CONSTRAINT captured_at_not_before_start CHECK (captured_at >= '{CAPTURE_START}'),
            raw_payload jsonb NOT NULL
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX estimate_snapshot_one_per_day ON estimate_snapshot "
        "(company_id, source, period_label, ((captured_at AT TIME ZONE 'UTC')::date))"
    )
    # Append only. The default privileges grant UPDATE, so take it back for the worker.
    op.execute("REVOKE UPDATE ON estimate_snapshot FROM earnings_worker")


def downgrade() -> None:
    op.execute("DROP TABLE estimate_snapshot")
