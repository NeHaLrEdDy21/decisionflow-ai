"""LLM access layer.

Wraps Google Gemini and provides a deterministic MOCK fallback so the
platform is fully demoable without an API key. Every agent calls
``llm_json`` / ``llm_text`` rather than talking to a provider directly,
which keeps provider choice in one place.
"""
from __future__ import annotations

import json
import re
from typing import Any

from config import GEMINI_MODEL, GOOGLE_API_KEY, MOCK_MODE
from logging_config import get_logger

log = get_logger("llm")

_client = None


def _get_client():
    global _client
    if _client is not None:
        return _client
    from langchain_google_genai import ChatGoogleGenerativeAI

    kwargs = dict(model=GEMINI_MODEL, google_api_key=GOOGLE_API_KEY, temperature=0.2)
    # Gemini 2.5 models "think" by default which is slow; disable for snappy
    # demo latency. Ignored gracefully by models/versions that don't support it.
    try:
        _client = ChatGoogleGenerativeAI(thinking_budget=0, **kwargs)
    except Exception:
        _client = ChatGoogleGenerativeAI(**kwargs)
    return _client


def _extract_json(text: str) -> Any:
    """Best-effort parse of a JSON object/array out of an LLM response."""
    text = text.strip()
    fence = re.search(r"```(?:json)?\s*(.*?)```", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        match = re.search(r"(\{.*\}|\[.*\])", text, re.DOTALL)
        if match:
            return json.loads(match.group(1))
        raise


def llm_text(prompt: str, *, system: str = "") -> str:
    """Return a plain-text completion (or a mock note in offline mode)."""
    if MOCK_MODE:
        return "[mock] " + prompt[:120]
    messages = []
    if system:
        messages.append(("system", system))
    messages.append(("human", prompt))
    resp = _get_client().invoke(messages)
    return resp.content if isinstance(resp.content, str) else str(resp.content)


def llm_json(prompt: str, *, system: str = "", mock: Any | None = None) -> Any:
    """Return parsed JSON from the model.

    In MOCK_MODE (or on any provider error) the supplied ``mock`` value is
    returned so the workflow never breaks during a demo.
    """
    if MOCK_MODE:
        log.info("MOCK_MODE active -> returning canned response")
        return mock
    sys_prompt = (system + "\nRespond ONLY with valid JSON. No prose, no markdown fences.").strip()
    try:
        raw = llm_text(prompt, system=sys_prompt)
        return _extract_json(raw)
    except Exception as exc:  # pragma: no cover - defensive for live demo
        log.warning("LLM call failed (%s); falling back to mock", exc)
        return mock
