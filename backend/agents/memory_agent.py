"""Memory Agent -- recalls prior interactions and persists run summaries.

It runs at the START of the pipeline (recall) and again after a human
decision (store). The ``run`` here handles recall + storing the run summary;
human decisions are persisted via the API/approve flow.
"""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from tools.memory_tool import recall, remember


@register
class MemoryAgent(BaseAgent):
    key = "memory"
    label = "Memory"

    def run(self, state: State) -> State:
        crm = state.get("crm", {})
        customer_id = state.get("customer_id") or (
            (crm.get("name") or "unknown").lower().replace(" ", "-")
        )
        # Persist a summary of this analysis so future runs can recall it.
        conv = state.get("conversation", {})
        remember({
            "customer_id": customer_id,
            "customer_name": crm.get("name", "Unknown Customer"),
            "kind": "analysis",
            "action": "Generated next best actions",
            "result": state.get("risk", {}).get("risk_level", "n/a") + " risk",
            "detail": {
                "summary": conv.get("summary", ""),
                "num_recommendations": len(state.get("recommendations", [])),
            },
        })
        history = recall(customer_id)
        self.log.info("Memory: stored run, %d prior entries for %s", len(history), customer_id)
        return {"customer_id": customer_id, "memory_history": history}
