"""transcript and transcript_section (Product Section 11; Ingestion IG-11, IG-14, IG-17, IG-18;
Data TX-01, TX-02, TX-05, TX-06; Product PL-06).

A transcript row holds the raw text exactly as received (with its hash) and the cleaned text in a
separate column, the speaker turns with roles, the section boundary found by the written rule, and
the earnings release it is linked to. The same source row twice gives one row, and for one
earnings release only one transcript is `kept` (the earliest call; the rest are `duplicate`).

The columns extend the field lists of Product Section 11 (decision D-47). The rows can be rebuilt
from the raw payloads, so the worker may update them.

Revision ID: 0007
Revises: 0006
"""

from alembic import op

revision = "0007"
down_revision = "0006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE transcript (
            transcript_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            company_id text NOT NULL REFERENCES company (company_id),
            ticker text NOT NULL,
            fiscal_year integer,
            fiscal_quarter integer,
            call_date date NOT NULL,
            call_at timestamptz,
            source text NOT NULL,
            source_ref text NOT NULL,
            payload_id bigint REFERENCES raw_payload (payload_id),
            release_accession text NOT NULL,
            release_accepted_at timestamptz NOT NULL,
            raw_text text NOT NULL CHECK (raw_text <> ''),
            raw_hash text NOT NULL
                CONSTRAINT transcript_raw_hash CHECK (raw_hash ~ '^[0-9a-f]{64}$'),
            cleaned_text text NOT NULL,
            cleaning_rules_version text NOT NULL,
            turns jsonb NOT NULL,
            segmentation_status text NOT NULL
                CONSTRAINT transcript_segmentation CHECK (segmentation_status IN ('ok', 'failed')),
            boundary_turn integer,
            status text NOT NULL DEFAULT 'kept'
                CONSTRAINT transcript_status CHECK (status IN ('kept', 'duplicate')),
            CONSTRAINT transcript_boundary_when_ok
                CHECK ((segmentation_status = 'ok') = (boundary_turn IS NOT NULL)),
            CONSTRAINT transcript_one_source_row UNIQUE (company_id, source_ref)
        )
        """
    )
    op.execute(
        "CREATE UNIQUE INDEX transcript_one_kept_per_release ON transcript "
        "(company_id, release_accession) WHERE status = 'kept'"
    )
    op.execute("CREATE INDEX transcript_company_call ON transcript (company_id, call_date)")
    op.execute(
        """
        CREATE TABLE transcript_section (
            section_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            transcript_id bigint NOT NULL REFERENCES transcript (transcript_id),
            kind text NOT NULL
                CONSTRAINT transcript_section_kind CHECK (kind IN ('prepared', 'qa')),
            text text NOT NULL,
            CONSTRAINT transcript_section_one_kind UNIQUE (transcript_id, kind)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE transcript_section")
    op.execute("DROP TABLE transcript")
