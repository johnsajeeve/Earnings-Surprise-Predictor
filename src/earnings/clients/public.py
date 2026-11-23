"""Client for public sources that need no contact string (Ingestion IG-10).

It fetches and returns the raw payload with its metadata, like the EDGAR client. Each client is
tied to a source name and to a short list of allowed hosts, so it cannot be pointed elsewhere.
"""

import logging
from datetime import UTC, datetime
from urllib.parse import urlparse

from earnings.clients.edgar import RawResponse, Session, SourceError
from earnings.limits import SlidingWindowLimiter

log = logging.getLogger(__name__)

# A generic name, never a personal contact, for sources that do not ask for one.
USER_AGENT = "earnings-project (university research project)"
TIMEOUT_SECONDS = 60


class PublicClient:
    def __init__(
        self,
        source: str,
        allowed_hosts: tuple[str, ...],
        session: Session | None = None,
        limiter: SlidingWindowLimiter | None = None,
    ) -> None:
        self.source, self._hosts = source, allowed_hosts
        if session is None:
            import requests

            session = requests.Session()
        self._session = session
        self._limiter = limiter or SlidingWindowLimiter(1, 1.0)  # one request a second

    def get(self, url: str) -> RawResponse:
        parsed = urlparse(url)
        if parsed.scheme != "https" or parsed.hostname not in self._hosts:
            raise ValueError(f"{self.source} client may only fetch from {self._hosts}")
        self._limiter.acquire()
        response = self._session.get(
            url, headers={"User-Agent": USER_AGENT}, timeout=TIMEOUT_SECONDS
        )
        status, body = int(response.status_code), bytes(response.content)
        log.info("%s GET %s -> %s, %s bytes", self.source, parsed.path, status, len(body))
        if status != 200:
            raise SourceError(f"{self.source} returned status {status} for {parsed.path}")
        return RawResponse(
            source=self.source,
            url=url,
            status=status,
            content_type=response.headers.get("Content-Type"),
            body=body,
            retrieved_at=datetime.now(UTC),
        )
