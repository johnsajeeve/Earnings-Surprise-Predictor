"""Daily prices and corporate actions from yfinance (Data PX-01; source register: development and
research use only, never in the public demo). The answer is stored as received, then parsed from
the stored copy (Ingestion IG-10)."""

import json
from datetime import UTC, datetime
from typing import Any

from earnings.clients.edgar import RawResponse, SourceError

SOURCE = "yfinance-prices"
HISTORY_START = "2012-01-01"


class CollectionDisabled(RuntimeError):
    """Yahoo collection is off (decision C-61)."""


def require_yahoo_collection() -> None:
    from earnings.config import get_settings

    if not get_settings().yahoo_collection:
        raise CollectionDisabled(
            "collection from Yahoo is off: its terms bar automated access without written "
            "permission (decision C-61). See YAHOO_COLLECTION in .env.example"
        )


def url_for(ticker: str) -> str:
    return f"yfinance://history/{ticker}"


def fetch_payload(ticker: str, start: str = HISTORY_START, end: str | None = None) -> bytes:
    """One ticker's daily rows and its full split and dividend lists, as JSON. The close is the one
    yfinance returns with auto_adjust off: adjusted for splits, not for dividends."""
    require_yahoo_collection()
    import yfinance

    handle = yfinance.Ticker(ticker)
    frame = handle.history(start=start, end=end, auto_adjust=False)
    if frame is None or frame.empty:
        raise SourceError(f"yfinance returned no prices for {ticker}")
    rows: list[dict[str, Any]] = [
        {"date": str(day.date()), "close": float(r["Close"]), "volume": int(r["Volume"])}
        for day, r in frame.iterrows()
        if r["Close"] == r["Close"]  # NaN is the only value that differs from itself
    ]
    splits = {str(d.date()): float(v) for d, v in handle.splits.items()}
    dividends = {str(d.date()): float(v) for d, v in handle.dividends.items()}
    body = {
        "ticker": ticker,
        "version": yfinance.__version__,
        "start": start,
        "rows": rows,
        "splits": splits,
        "dividends": dividends,
    }
    return json.dumps(body, sort_keys=True).encode()


def response(ticker: str, body: bytes) -> RawResponse:
    return RawResponse(
        source=SOURCE,
        url=url_for(ticker),
        status=200,
        content_type="application/json",
        body=body,
        retrieved_at=datetime.now(UTC),
        source_version=json.loads(body)["version"],
    )
