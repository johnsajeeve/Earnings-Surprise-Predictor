"""Facts about the schema that the code and the tests both rely on (Database DB-08, DB-09)."""

# Tables that hold facts which can be corrected by a later row. The worker role has no UPDATE or
# DELETE on them (DB-08). A migration that creates a table of this kind adds it here, and a test
# compares this list with the database.
APPEND_ONLY_TABLES: tuple[str, ...] = (
    "estimate_snapshot",
    "raw_payload",
    "dead_letter",
    "eps_history",
    "fundamentals_filing",
)

# Versioned fact tables and the one function that reads them as of a date (DB-09). Feature code
# reads these tables only through the function. See docs/architecture/as-of-reads.md.
AS_OF_FUNCTIONS: dict[str, str] = {
    "estimate_snapshot": "estimate_snapshot_as_of",
    "eps_history": "eps_history_as_of",
    "fundamentals_filing": "fundamentals_filing_as_of",
}
