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
                    "byte_length, body, source_version) VALUES "
                    "(:source, :url, :at, :sha, :ctype, :length, :body, :version) "
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
                    "version": raw.source_version,
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


def verify_hashes(engine: Engine) -> list[int]:
    """Ids of stored payloads whose body no longer matches the hash recorded at retrieval
    (Data SR-04). An empty list means every payload is intact.
    """
    with engine.connect() as conn:
        rows = conn.execute(
            text(
                "SELECT payload_id FROM raw_payload "
                "WHERE encode(sha256(body), 'hex') <> sha256 ORDER BY payload_id"
            )
        )
        return [int(r[0]) for r in rows]


if __name__ == "__main__":
    from earnings.db import get_engine

    engine = get_engine("api")
    with engine.connect() as conn:
        total = conn.execute(text("SELECT count(*) FROM raw_payload")).scalar_one()
    bad = verify_hashes(engine)
    print(f"raw payloads: {total}; hash mismatches: {len(bad)} {bad}")
    raise SystemExit(1 if bad else 0)
