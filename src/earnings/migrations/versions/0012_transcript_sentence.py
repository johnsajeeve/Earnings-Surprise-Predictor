"""transcript_sentence (Product Section 11, TranscriptSentence; Product FR-16; Feature Engineering
FE-01 to FE-06, FE-29).

One row per sentence and FinBERT revision, so a new revision adds rows and the old scores stay.
Beside the fields of Product Section 11 it holds the speaker and role, whether the sentence counts
for text features, whether it was cut for the model, and the model revision (as listed in the
Wave 2.1 task brief). The
counts of hedge, negation and ordinary words arrive with the step that computes them.

The rows can be rebuilt from the transcript, so the worker may update them. As with other tables,
it may not delete them (DB-02).

Revision ID: 0012
Revises: 0011
"""

from alembic import op

revision = "0012"
down_revision = "0011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE transcript_sentence (
            sentence_id bigint GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
            transcript_id bigint NOT NULL REFERENCES transcript (transcript_id),
            section_id bigint NOT NULL REFERENCES transcript_section (section_id),
            position integer NOT NULL CHECK (position >= 0),
            text text NOT NULL CHECK (text <> ''),
            speaker text NOT NULL,
            role text NOT NULL
                CONSTRAINT sentence_role CHECK (role IN
                    ('management', 'analyst', 'operator', 'unknown')),
            analytic boolean NOT NULL,
            truncated boolean NOT NULL,
            finbert_positive double precision NOT NULL
                CHECK (finbert_positive BETWEEN 0 AND 1),
            finbert_negative double precision NOT NULL
                CHECK (finbert_negative BETWEEN 0 AND 1),
            finbert_neutral double precision NOT NULL
                CHECK (finbert_neutral BETWEEN 0 AND 1),
            model_revision text NOT NULL CHECK (model_revision <> ''),
            CONSTRAINT sentence_one_place UNIQUE (transcript_id, model_revision, position)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE transcript_sentence")
