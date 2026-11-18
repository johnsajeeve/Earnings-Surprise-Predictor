"""Request logging (Product NFR-11, audit finding F-03).

Every request is logged with a request identifier, latency and status code. Per Project-Wide SP-05
the log carries only those fields plus the method and path (which holds the requested ticker). It
does not log the client address, headers or query string, so uvicorn's own access log is switched
off in the run command.
"""

import logging
import sys
import time
import uuid
from collections.abc import Awaitable, Callable

from fastapi import FastAPI, Request, Response

logger = logging.getLogger("earnings.request")
if not logger.handlers:
    _handler = logging.StreamHandler(sys.stdout)
    _handler.setFormatter(logging.Formatter("%(asctime)s %(message)s"))
    logger.addHandler(_handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False


def install(app: FastAPI) -> None:
    @app.middleware("http")
    async def log_requests(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # A new identifier per request. A client-supplied one is ignored (avoids log injection).
        request_id = uuid.uuid4().hex
        started = time.perf_counter()
        status = 500  # stays 500 if the handler raises, so failures are logged too
        try:
            response = await call_next(request)
            status = response.status_code
            response.headers["X-Request-ID"] = request_id
            return response
        finally:
            latency_ms = (time.perf_counter() - started) * 1000
            logger.info(
                "request_id=%s method=%s path=%s status=%d latency_ms=%.1f",
                request_id,
                request.method,
                request.url.path,
                status,
                latency_ms,
            )
