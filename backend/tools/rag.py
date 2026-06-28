"""Retrieval-Augmented Generation helper over the knowledge vector store."""
from __future__ import annotations

from typing import Any

from tools import vector_store


def retrieve(queries: list[str], k: int = 3) -> list[dict[str, Any]]:
    """Retrieve and de-duplicate knowledge snippets for several queries."""
    seen: set[str] = set()
    results: list[dict[str, Any]] = []
    for q in queries:
        for hit in vector_store.search(q, k=k):
            key = hit["title"] + hit["snippet"][:40]
            if key not in seen:
                seen.add(key)
                results.append(hit)
    return results
