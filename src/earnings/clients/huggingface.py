"""Hugging Face transcript file (Ingestion IG-10, IG-11).

The transcript set is one parquet file of 1.8 GB. It is too large to keep in one database row, so
it is downloaded to a volume once, checked against the checksum measured on 23 November 2026, and
read in batches. Each transcript that is used is then stored as received in `raw_payload`.
"""

import hashlib
import json
import logging
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from earnings.clients.edgar import RawResponse, SourceError

log = logging.getLogger(__name__)

SOURCE = "hf-transcripts"
DATASET = "kurry/sp500_earnings_transcripts"
REVISION = "f3ded372da8d18dc6ad98955c4558e34b5fe6d45"
FILE = "parquet_files/part-0.parquet"
URL = f"https://huggingface.co/datasets/{DATASET}/resolve/{REVISION}/{FILE}"
# Measured on 23 November 2026 from the file at this revision (Wave 0.1, Spike A).
EXPECTED_SHA256 = "9a305a1c4cbf6c4b0b9c8b98b242ea3de4dbe0ad43937dc54b56418629a17b31"
EXPECTED_BYTES = 1_824_805_388
USER_AGENT = "earnings-project (university research project)"
CHUNK = 4 * 1024 * 1024


def sha256_of(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        while chunk := fh.read(CHUNK):
            digest.update(chunk)
    return digest.hexdigest()


def download(dest: Path, session: Any = None) -> dict[str, Any]:
    """Fetch the pinned file to `dest` and return its manifest. Does nothing if it is already there
    and matches. A file that does not match the recorded checksum is refused and removed."""
    dest.parent.mkdir(parents=True, exist_ok=True)
    if (
        dest.exists()
        and dest.stat().st_size == EXPECTED_BYTES
        and sha256_of(dest) == EXPECTED_SHA256
    ):
        return manifest(dest, downloaded=False)
    if session is None:
        import requests

        session = requests.Session()
    temp = dest.with_suffix(".part")
    digest = hashlib.sha256()
    size = 0
    with session.get(URL, headers={"User-Agent": USER_AGENT}, stream=True, timeout=120) as response:
        if int(response.status_code) != 200:
            raise SourceError(f"{SOURCE} returned status {response.status_code}")
        with temp.open("wb") as fh:
            for chunk in response.iter_content(CHUNK):
                fh.write(chunk)
                digest.update(chunk)
                size += len(chunk)
    if size != EXPECTED_BYTES or digest.hexdigest() != EXPECTED_SHA256:
        temp.unlink(missing_ok=True)
        raise SourceError(f"{SOURCE}: the file does not match the recorded size and checksum")
    temp.replace(dest)
    return manifest(dest, downloaded=True)


def manifest(path: Path, downloaded: bool) -> dict[str, Any]:
    return {
        "source": SOURCE, "dataset": DATASET, "revision": REVISION, "file": FILE, "url": URL,
        "bytes": path.stat().st_size, "sha256": EXPECTED_SHA256, "downloaded_now": downloaded,
    }  # fmt: skip


def manifest_payload(info: dict[str, Any]) -> RawResponse:
    """The manifest as a stored payload: the revision and checksum of the snapshot on record."""
    body = json.dumps({k: v for k, v in info.items() if k != "downloaded_now"}, sort_keys=True)
    return RawResponse(SOURCE, URL, 200, "application/json", body.encode(), datetime.now(UTC))
