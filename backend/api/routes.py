"""REST API for DecisionFlow AI."""
from __future__ import annotations

import json
from typing import Any, Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

from db import database
from logging_config import get_logger
from workflow.graph import run_workflow

log = get_logger("api")
router = APIRouter()

# In-memory store of the most recent analysis (per session/demo).
_LAST: dict[str, Any] = {}


class UploadPayload(BaseModel):
    transcript: Optional[str] = None
    crm: Optional[Any] = None
    email: Optional[str] = None
    support_ticket: Optional[str] = None
    notes: Optional[str] = None


class DecisionPayload(BaseModel):
    recommendation_id: str
    modified_action: Optional[str] = None


def _normalise_inputs(p: UploadPayload) -> dict:
    inputs: dict[str, Any] = {}
    if p.transcript:
        inputs["transcript"] = p.transcript
    if p.crm:
        inputs["crm"] = p.crm if isinstance(p.crm, dict) else json.loads(p.crm)
    if p.email:
        inputs["email"] = p.email
    if p.support_ticket:
        inputs["support_ticket"] = p.support_ticket
    if p.notes:
        inputs["notes"] = p.notes
    return inputs


@router.post("/upload")
def upload(payload: UploadPayload) -> dict:
    """Stage customer inputs (no analysis yet)."""
    inputs = _normalise_inputs(payload)
    if not inputs:
        raise HTTPException(400, "No customer information provided.")
    _LAST["inputs"] = inputs
    crm = inputs.get("crm", {})
    if crm:
        database.upsert_customer(crm)
    return {"status": "uploaded", "inputs_received": list(inputs.keys())}


@router.post("/analyze")
def analyze(payload: Optional[UploadPayload] = None) -> dict:
    """Run the full agent workflow and persist recommendations."""
    inputs = _normalise_inputs(payload) if payload and any(
        _normalise_inputs(payload).values()) else _LAST.get("inputs")
    if not inputs:
        raise HTTPException(400, "Nothing to analyze. Upload customer data first.")

    state = run_workflow(inputs)
    crm = state.get("crm", {})
    customer_id = database.upsert_customer(crm) if crm else state.get("customer_id", "unknown")

    run_id = database.save_run(customer_id, state)
    saved = database.save_recommendations(run_id, customer_id, state.get("recommendations", []))

    _LAST.update({"state": state, "run_id": run_id, "customer_id": customer_id,
                  "recommendations": saved})

    return {
        "run_id": run_id,
        "customer_id": customer_id,
        "plan": state.get("plan", []),
        "trace": state.get("trace", []),
        "customer": crm,
        "conversation": state.get("conversation", {}),
        "knowledge": state.get("knowledge", []),
        "risk": state.get("risk", {}),
        "opportunity": state.get("opportunity", {}),
        "recommendations": saved,
        "memory_history": state.get("memory_history", []),
        "errors": state.get("errors", {}),
    }


@router.get("/recommendations")
def recommendations(customer_id: Optional[str] = None) -> dict:
    return {"recommendations": database.get_recommendations(customer_id)}


@router.post("/approve")
def approve(payload: DecisionPayload) -> dict:
    rec = database.decide_recommendation(payload.recommendation_id, "approved",
                                         payload.modified_action)
    if not rec:
        raise HTTPException(404, "Recommendation not found.")
    database.add_memory({
        "customer_id": rec["customer_id"],
        "customer_name": rec.get("customer_id"),
        "kind": "decision",
        "action": payload.modified_action or rec["action"],
        "result": "approved",
        "detail": {"reason": rec.get("reason"), "confidence": rec.get("confidence")},
    })
    return {"status": "approved", "recommendation": rec}


@router.post("/reject")
def reject(payload: DecisionPayload) -> dict:
    rec = database.decide_recommendation(payload.recommendation_id, "rejected")
    if not rec:
        raise HTTPException(404, "Recommendation not found.")
    database.add_memory({
        "customer_id": rec["customer_id"],
        "customer_name": rec.get("customer_id"),
        "kind": "decision",
        "action": rec["action"],
        "result": "rejected",
        "detail": {"reason": rec.get("reason")},
    })
    return {"status": "rejected", "recommendation": rec}


@router.post("/modify")
def modify(payload: DecisionPayload) -> dict:
    if not payload.modified_action:
        raise HTTPException(400, "modified_action required.")
    rec = database.decide_recommendation(payload.recommendation_id, "modified",
                                         payload.modified_action)
    if not rec:
        raise HTTPException(404, "Recommendation not found.")
    database.add_memory({
        "customer_id": rec["customer_id"], "customer_name": rec.get("customer_id"),
        "kind": "decision", "action": payload.modified_action, "result": "modified",
        "detail": {"original": rec["action"]},
    })
    return {"status": "modified", "recommendation": rec}


@router.get("/memory")
def memory(customer_id: Optional[str] = None) -> dict:
    return {"memory": database.get_memory(customer_id)}


@router.get("/customer")
def customer(customer_id: str) -> dict:
    cust = database.get_customer(customer_id)
    if not cust:
        raise HTTPException(404, "Customer not found.")
    return {"customer": cust, "memory": database.get_memory(customer_id)}
