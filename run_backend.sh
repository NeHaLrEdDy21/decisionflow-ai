#!/usr/bin/env bash
cd "$(dirname "$0")/backend"
python -m venv .venv 2>/dev/null || true
source .venv/bin/activate 2>/dev/null || true
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
