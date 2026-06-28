"""Knowledge Agent -- retrieves relevant enterprise documentation via RAG."""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from tools.rag import retrieve


@register
class KnowledgeAgent(BaseAgent):
    key = "knowledge"
    label = "Knowledge"

    def run(self, state: State) -> State:
        conv = state.get("conversation", {})
        queries: list[str] = []
        queries += [str(x) for x in conv.get("pain_points", [])]
        queries += [str(x) for x in conv.get("goals", [])]
        for inp in ("email", "support_ticket", "notes"):
            text = state.get("inputs", {}).get(inp)
            if text:
                queries.append(text[:200])
        if not queries:
            queries = ["renewal checklist", "pricing", "onboarding"]

        hits = retrieve(queries, k=2)
        self.log.info("Retrieved %d knowledge snippets", len(hits))
        return {"knowledge": hits}
