"""SEC EDGAR client (Ingestion IG-07, IG-08, IG-10; Project-Wide SP-06, decision C-10).

It fetches and returns the raw payload with its metadata. It does not interpret the data:
parsing is a separate step that reads stored payloads (IG-10).
"""

import hashlib
import logging
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any, Protocol
from urllib.parse import urlparse

from earnings.limits import RedisSlidingWindowLimiter, SlidingWindowLimiter

log = logging.getLogger(__name__)

SOURCE = "sec-edgar"
# The SEC allows 10 requests a second. The client keeps below it (decision C-45).
MAX_REQUESTS_PER_SECOND = 8
TIMEOUT_SECONDS = 30


class MissingContactError(RuntimeError):
    """SEC_USER_AGENT is not set. The SEC asks every automated client to identify itself."""


class SourceError(RuntimeError):
    """The source did not return the data. The message never holds the contact string."""


class Session(Protocol):
    def get(self, url: str, *, headers: dict[str, str], timeout: float) -> Any: ...


@dataclass(frozen=True)
class RawResponse:
    source: str
    url: str
    status: int
    content_type: str | None
    body: bytes
    retrieved_at: datetime
    source_version: str | None = None  # Data SR-04, where the source states one

    @property
    def sha256(self) -> str:
        return hashlib.sha256(self.body).hexdigest()


def _is_sec_host(url: str) -> bool:
    host = urlparse(url).hostname or ""
    return host == "sec.gov" or host.endswith(".sec.gov")


class EdgarClient:
    def __init__(
        self,
        user_agent: str,
        session: Session | None = None,
        limiter: SlidingWindowLimiter | RedisSlidingWindowLimiter | None = None,
    ) -> None:
        self._user_agent = user_agent
        if session is None:
            import requests

            session = requests.Session()
        self._session = session
        self._limiter = limiter or SlidingWindowLimiter(MAX_REQUESTS_PER_SECOND)

    def __repr__(self) -> str:
        return "EdgarClient(user_agent=<hidden>)"

    def get(self, url: str) -> RawResponse:
        if not self._user_agent.strip():
            raise MissingContactError("SEC_USER_AGENT is not set, so no request was sent")
        if not _is_sec_host(url):
            # The contact string identifies the owner. It goes to the SEC and nowhere else.
            raise ValueError("the EDGAR client only sends requests to sec.gov hosts")
        self._limiter.acquire()
        response = self._session.get(
            url, headers={"User-Agent": self._user_agent}, timeout=TIMEOUT_SECONDS
        )
        path = urlparse(url).path
        status = int(response.status_code)
        body = bytes(response.content)
        # One line per request: the path, the status and the size. Never the contact string.
        log.info("edgar GET %s -> %s, %s bytes", path, status, len(body))
        if status != 200:
            raise SourceError(f"EDGAR returned status {status} for {path}")
        return RawResponse(
            source=SOURCE,
            url=url,
            status=status,
            content_type=response.headers.get("Content-Type"),
            body=body,
            retrieved_at=datetime.now(UTC),
        )
