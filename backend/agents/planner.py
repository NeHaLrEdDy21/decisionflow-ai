"""Planner Agent.

Pure orchestration: decides WHICH agents run based on which inputs were
supplied. It performs NO business reasoning.
"""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from config import DEFAULT_PIPELINE


@register
class PlannerAgent(BaseAgent):
    key = "planner"
    label = "Planner"

    def run(self, state: State) -> State:
        inputs = state.get("inputs", {})
        plan: list[str] = []

        if inputs.get("transcript"):
            plan.append("conversation")
        if inputs.get("crm"):
            plan.append("crm")
        # knowledge/risk/opportunity/recommendation/explanation/memory always
        # run when there is any input to reason over.
        if inputs:
            plan += ["knowledge", "risk", "opportunity",
                     "recommendation", "explanation", "memory"]

        # Preserve canonical ordering and drop anything unknown.
        ordered = [a for a in DEFAULT_PIPELINE if a in plan]
        self.log.info("Execution plan: %s", ordered)
        return {"plan": ordered}
