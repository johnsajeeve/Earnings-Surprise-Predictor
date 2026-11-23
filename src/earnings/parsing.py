"""Parsers that read stored payloads. They never touch the network (Ingestion IG-10)."""

import json
from typing import Any


def parse_diluted_eps(payload: bytes) -> list[dict[str, Any]]:
    """The diluted EPS facts of an EDGAR company-facts payload, one dict per fact.

    Each keeps the period, the value and the filing details, so later steps can choose the
    first-filed value (Data LB-03, LB-04). Nothing is derived or dropped here.
    """
    facts = json.loads(payload)["facts"]["us-gaap"].get("EarningsPerShareDiluted")
    if not facts:
        return []
    return [
        {
            "start": f.get("start"),
            "end": f["end"],
            "value": f["val"],
            "filed": f["filed"],
            "form": f.get("form"),
            "fiscal_period": f.get("fp"),
            "fiscal_year": f.get("fy"),
            "accession": f.get("accn"),
        }
        for f in facts["units"]["USD/shares"]
    ]
