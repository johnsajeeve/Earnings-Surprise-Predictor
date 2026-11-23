"""Store payloads as received (Database DB-11, Ingestion IG-10)."""

from sqlalchemy import Engine, text

from earnings.clients.edgar import RawResponse


def store_payload(engine: Engine, raw: RawResponse) -> bool:
    """Insert the payload. Returns False when the same content for the same URL is already stored,
    so fetching the same thing twice leaves one row (Project-Wide EQ-07).
    """
    with engine.begin() as conn:
        return bool(
            conn.execute(
                text(
                    "INSERT INTO raw_payload (source, url, retrieved_at, sha256, content_type, "
                    "byte_length, body) VALUES (:source, :url, :at, :sha, :ctype, :length, :body) "
                    "ON CONFLICT (source, url, sha256) DO NOTHING"
                ),
                {
                    "source": raw.source,
                    "url": raw.url,
                    "at": raw.retrieved_at,
                    "sha": raw.sha256,
                    "ctype": raw.content_type,
                    "length": len(raw.body),
                    "body": raw.body,
                },
            ).rowcount
        )


def latest_payload(engine: Engine, source: str, url: str) -> bytes | None:
    """The most recently retrieved body for a URL, read back from the database."""
    with engine.connect() as conn:
        row = conn.execute(
            text(
                "SELECT body FROM raw_payload WHERE source = :s AND url = :u "
                "ORDER BY retrieved_at DESC LIMIT 1"
            ),
            {"s": source, "u": url},
        ).first()
    return None if row is None else bytes(row[0])
