"""LangGraph orchestration of the agent pipeline.

The Planner runs first and decides which downstream agents execute. We build
a LangGraph ``StateGraph`` where each agent is a node; the planner's output
gates execution (an agent that is not in the plan becomes a no-op). This keeps
the workflow configurable and lets new agents slot in via the registry.
"""
from __future__ import annotations

from typing import Any, Dict

from agents.base import REGISTRY
from config import DEFAULT_PIPELINE
from logging_config import get_logger
from tools.memory_tool import recall
from workflow.state import FlowState

log = get_logger("workflow")


def _make_node(agent_key: str):
    agent = REGISTRY[agent_key]

    def node(state: Dict[str, Any]) -> Dict[str, Any]:
        if agent_key in state.get("plan", DEFAULT_PIPELINE):
            return agent.execute(state)
        return {}

    return node


def build_graph():
    """Compile and return the LangGraph app (or None if langgraph missing)."""
    try:
        from langgraph.graph import END, START, StateGraph
    except Exception as exc:  # pragma: no cover
        log.warning("langgraph unavailable (%s); will run sequentially", exc)
        return None

    try:
        return _compile(StateGraph, START, END)
    except Exception as exc:
        log.warning("graph build failed (%s); will run sequentially", exc)
        return None


def _compile(StateGraph, START, END):
    g = StateGraph(FlowState)
    # Node names must NOT collide with state keys (LangGraph 0.2.x enforces this),
    # so every node is prefixed. The node still writes the real state keys.
    node = lambda k: f"agent_{k}"
    g.add_node(node("planner"), REGISTRY["planner"].execute)
    for key in DEFAULT_PIPELINE:
        g.add_node(node(key), _make_node(key))

    g.add_edge(START, node("planner"))
    prev = node("planner")
    for key in DEFAULT_PIPELINE:
        g.add_edge(prev, node(key))
        prev = node(key)
    g.add_edge(prev, END)
    return g.compile()


_APP = None


def _seed_recall(inputs: Dict[str, Any]) -> list:
    """Pre-load memory for the customer so risk/recommendation can use it."""
    crm = inputs.get("crm")
    if not crm:
        return []
    import json
    name = (crm if isinstance(crm, dict) else json.loads(crm)).get("name", "")
    cid = name.lower().replace(" ", "-")
    return recall(cid)


def run_workflow(inputs: Dict[str, Any]) -> FlowState:
    """Execute the full pipeline and return the final state."""
    global _APP
    state: FlowState = {"inputs": inputs, "trace": [], "errors": {},
                        "memory_recall": _seed_recall(inputs)}

    if _APP is None:
        _APP = build_graph()

    if _APP is not None:
        log.info("Running workflow via LangGraph")
        return _APP.invoke(state)

    # Sequential fallback (still planner-gated).
    log.info("Running workflow sequentially (fallback)")
    state.update(REGISTRY["planner"].execute(state))
    for key in DEFAULT_PIPELINE:
        if key in state.get("plan", []):
            state.update(REGISTRY[key].execute(state))
    return state
