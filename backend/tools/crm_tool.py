"""Parse raw CRM payloads into a normalised customer record."""
from __future__ import annotations

import json
from typing import Any


def parse_crm(raw: str | dict[str, Any]) -> dict[str, Any]:
    data = raw if isinstance(raw, dict) else json.loads(raw)
    return {
        "name": data.get("name", "Unknown Customer"),
        "health": int(data.get("health", 0) or 0),
        "renewal_days": int(data.get("renewal_days", 0) or 0),
        "arr": float(data.get("arr", 0) or 0),
        "open_opportunities": data.get("open_opportunities", []),
        "previous_meetings": data.get("previous_meetings", []),
        "owner": data.get("owner", "Customer Success Manager"),
        "raw": data,
    }
