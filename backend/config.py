"""Central configuration for DecisionFlow AI.

All tunables live here so business logic is not hardcoded across agents.
"""
from __future__ import annotations

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge"
SAMPLE_DATA_DIR = BASE_DIR / "sample_data"
DB_DIR = BASE_DIR / "db"
CHROMA_DIR = BASE_DIR / "db" / "chroma"
SQLITE_PATH = BASE_DIR / "db" / "decisionflow.sqlite"
LOG_DIR = BASE_DIR / "logs"

for _d in (DB_DIR, CHROMA_DIR, LOG_DIR):
    _d.mkdir(parents=True, exist_ok=True)

# --- LLM ---
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "gemini").lower()
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "").strip()
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
FORCE_MOCK = os.getenv("FORCE_MOCK", "false").lower() == "true"

# True when we cannot (or are told not to) call a real model.
MOCK_MODE = FORCE_MOCK or not GOOGLE_API_KEY

# --- Workflow: ordered list of agents the planner may schedule. ---
# Adding a new agent later = add its key here and register it in the registry.
DEFAULT_PIPELINE = [
    "conversation",
    "crm",
    "knowledge",
    "risk",
    "opportunity",
    "recommendation",
    "explanation",
    "memory",
]

MAX_RECOMMENDATIONS = 5
