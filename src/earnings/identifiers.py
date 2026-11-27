"""Company identifiers (Database DB-04, decision C-19).

`company_id` is the SEC CIK, written as exactly ten digits with leading zeros, for example
"0000320193". It is text, so the zeros are never lost. No table uses the ticker as a key.
"""


def canonical_cik(value: str | int) -> str:
    """The canonical company_id for a CIK given as a number or digit string."""
    text = str(value).strip()
    if not text.isascii() or not text.isdigit() or len(text) > 10:
        raise ValueError(f"not a CIK: {value!r}")
    return text.zfill(10)
