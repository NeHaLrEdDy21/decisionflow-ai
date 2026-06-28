"""ChromaDB-backed vector store for enterprise knowledge.

Falls back to a lightweight keyword index when ChromaDB or an embedding
backend is unavailable, so the Knowledge Agent always returns something
useful during a demo.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from config import CHROMA_DIR, KNOWLEDGE_DIR
from logging_config import get_logger

log = get_logger("tool.vector_store")

_COLLECTION = "enterprise_knowledge"
_client = None
_collection = None
_keyword_docs: list[dict[str, Any]] = []


def _load_files() -> list[dict[str, str]]:
    docs = []
    for path in sorted(Path(KNOWLEDGE_DIR).glob("*")):
        if path.suffix.lower() in {".md", ".txt"}:
            docs.append({"id": path.stem, "title": path.stem.replace("_", " ").title(),
                         "text": path.read_text(encoding="utf-8", errors="ignore")})
    return docs


def _chunk(text: str, size: int = 600) -> list[str]:
    words = text.split()
    return [" ".join(words[i:i + size]) for i in range(0, len(words), size)] or [text]


def init_store() -> str:
    """Index knowledge docs. Returns the backend used: 'chroma' or 'keyword'."""
    global _client, _collection, _keyword_docs
    docs = _load_files()
    _keyword_docs = []
    for d in docs:
        for i, chunk in enumerate(_chunk(d["text"])):
            _keyword_docs.append({"id": f"{d['id']}-{i}", "title": d["title"], "text": chunk})
    try:
        import chromadb
        from chromadb.utils import embedding_functions

        _client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        ef = embedding_functions.DefaultEmbeddingFunction()
        try:
            _client.delete_collection(_COLLECTION)
        except Exception:
            pass
        _collection = _client.create_collection(_COLLECTION, embedding_function=ef)
        _collection.add(
            ids=[d["id"] for d in _keyword_docs],
            documents=[d["text"] for d in _keyword_docs],
            metadatas=[{"title": d["title"]} for d in _keyword_docs],
        )
        log.info("Indexed %d chunks into ChromaDB", len(_keyword_docs))
        return "chroma"
    except Exception as exc:
        log.warning("ChromaDB unavailable (%s); using keyword fallback", exc)
        _collection = None
        return "keyword"


def search(query: str, k: int = 4) -> list[dict[str, Any]]:
    query = query if isinstance(query, str) else str(query)
    if _collection is not None:
        try:
            res = _collection.query(query_texts=[query], n_results=k)
            hits = []
            for doc, meta in zip(res["documents"][0], res["metadatas"][0]):
                hits.append({"title": meta.get("title", "Document"), "snippet": doc[:300]})
            return hits
        except Exception as exc:
            log.warning("Chroma query failed (%s); keyword fallback", exc)
    # keyword fallback
    terms = {t.lower() for t in query.split() if len(t) > 3}
    scored = []
    for d in _keyword_docs:
        score = sum(d["text"].lower().count(t) for t in terms)
        if score:
            scored.append((score, d))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [{"title": d["title"], "snippet": d["text"][:300]} for _, d in scored[:k]]
