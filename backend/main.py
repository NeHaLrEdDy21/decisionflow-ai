"""DecisionFlow AI -- FastAPI entrypoint.

Run: uvicorn main:app --reload --port 8000
"""
from __future__ import annotations

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Import agents so they self-register in the REGISTRY.
import agents.planner  # noqa: F401
import agents.conversation_agent  # noqa: F401
import agents.crm_agent  # noqa: F401
import agents.knowledge_agent  # noqa: F401
import agents.risk_agent  # noqa: F401
import agents.opportunity_agent  # noqa: F401
import agents.recommendation_agent  # noqa: F401
import agents.explanation_agent  # noqa: F401
import agents.memory_agent  # noqa: F401

from api.routes import router
from config import MOCK_MODE
from db.database import init_db
from logging_config import get_logger
from tools.vector_store import init_store

log = get_logger("main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    backend = init_store()
    log.info("Startup complete | knowledge backend=%s | MOCK_MODE=%s", backend, MOCK_MODE)
    yield


app = FastAPI(title="DecisionFlow AI", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/api")


@app.get("/")
def root() -> dict:
    return {"service": "DecisionFlow AI", "status": "ok", "mock_mode": MOCK_MODE,
            "docs": "/docs"}


@app.get("/api/health")
def health() -> dict:
    """Reports exactly why the system is or isn't using live Gemini."""
    from config import GEMINI_MODEL, GOOGLE_API_KEY
    info = {
        "status": "healthy",
        "mock_mode": MOCK_MODE,
        "api_key_detected": bool(GOOGLE_API_KEY),
        "model": GEMINI_MODEL,
        "provider_ready": False,
        "reason": "",
    }
    if MOCK_MODE:
        info["reason"] = "MOCK_MODE on (no API key detected or FORCE_MOCK=true)."
        return info
    try:
        from langchain_google_genai import ChatGoogleGenerativeAI  # noqa: F401
        info["provider_ready"] = True
        info["reason"] = "Live Gemini available."
    except Exception as exc:  # package missing -> calls fall back to mock
        info["reason"] = f"langchain-google-genai not installed: {exc}. Run: pip install langchain-google-genai"
    return info
