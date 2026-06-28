"""Thin wrapper around the SQLite memory store used by the Memory Agent."""
from __future__ import annotations

from typing import Any

from db import database


def recall(customer_id: str) -> list[dict[str, Any]]:
    """Return prior interactions for a customer (most recent first)."""
    return database.get_memory(customer_id)


def remember(entry: dict[str, Any]) -> str:
    return database.add_memory(entry)
