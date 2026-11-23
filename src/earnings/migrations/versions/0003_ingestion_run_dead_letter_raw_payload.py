"""ingestion_run, dead_letter and raw_payload (decision C-45).

ingestion_run is the run record of Product PL-01 and Ingestion IG-03. dead_letter is the table
that stands in for a dead-letter queue (IG-02). raw_payload keeps every payload as received
(Database DB-11, Ingestion IG-10). The last two are insert only for the worker role.

Revision ID: 0003
Revises: 0002
"""

from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE ingestion_run (
            run_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            job_name text NOT NULL,
            source text NOT NULL,
            started_at timestamptz NOT NULL DEFAULT now(),
            ended_at timestamptz,
            status text NOT NULL CONSTRAINT ingestion_run_status
                CHECK (status IN ('running', 'succeeded', 'failed')),
            rows_read integer NOT NULL DEFAULT 0 CHECK (rows_read >= 0),
            rows_written integer NOT NULL DEFAULT 0 CHECK (rows_written >= 0),
            error_class text,
            task_id text,
            CONSTRAINT ingestion_run_ended_when_finished
                CHECK ((status = 'running') = (ended_at IS NULL))
        )
        """
    )
    op.execute("CREATE INDEX ingestion_run_job_started ON ingestion_run (job_name, started_at)")
    op.execute("CREATE INDEX ingestion_run_task ON ingestion_run (task_id)")
    op.execute(
        """
        CREATE TABLE dead_letter (
            dead_letter_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            task_name text NOT NULL,
            args_hash text NOT NULL
                CONSTRAINT dead_letter_hash CHECK (args_hash ~ '^[0-9a-f]{64}$'),
            error_class text NOT NULL,
            failed_at timestamptz NOT NULL DEFAULT now(),
            attempt_count integer NOT NULL CHECK (attempt_count >= 1),
            run_id bigint REFERENCES ingestion_run (run_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE raw_payload (
            payload_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            source text NOT NULL,
            url text NOT NULL,
            retrieved_at timestamptz NOT NULL,
            sha256 text NOT NULL CONSTRAINT raw_payload_hash CHECK (sha256 ~ '^[0-9a-f]{64}$'),
            content_type text,
            byte_length integer NOT NULL,
            body bytea NOT NULL,
            CONSTRAINT raw_payload_length CHECK (byte_length = octet_length(body)),
            CONSTRAINT raw_payload_one_per_content UNIQUE (source, url, sha256)
        )
        """
    )
    # Insert only for the worker. The default privileges grant UPDATE, so take it back.
    op.execute("REVOKE UPDATE ON dead_letter, raw_payload FROM earnings_worker")


def downgrade() -> None:
    op.execute("DROP TABLE raw_payload")
    op.execute("DROP TABLE dead_letter")
    op.execute("DROP TABLE ingestion_run")
