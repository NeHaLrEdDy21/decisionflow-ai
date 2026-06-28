"""Shared workflow state schema."""
from __future__ import annotations

from typing import Any, Dict, List, TypedDict


class FlowState(TypedDict, total=False):
    inputs: Dict[str, Any]
    customer_id: str
    plan: List[str]
    conversation: Dict[str, Any]
    crm: Dict[str, Any]
    knowledge: List[Dict[str, Any]]
    risk: Dict[str, Any]
    opportunity: Dict[str, Any]
    recommendations: List[Dict[str, Any]]
    memory_recall: List[Dict[str, Any]]
    memory_history: List[Dict[str, Any]]
    trace: List[Dict[str, Any]]
    errors: Dict[str, str]
