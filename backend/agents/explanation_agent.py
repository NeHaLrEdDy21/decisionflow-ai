"""Explanation Agent -- attaches transparent evidence to each recommendation."""
from __future__ import annotations

from agents.base import BaseAgent, State, register


@register
class ExplanationAgent(BaseAgent):
    key = "explanation"
    label = "Explanation"

    def run(self, state: State) -> State:
        recs = state.get("recommendations", [])
        conv = state.get("conversation", {})
        crm = state.get("crm", {})
        knowledge = state.get("knowledge", [])
        risk = state.get("risk", {})

        knowledge_titles = [k.get("title") for k in knowledge]
        explained = []
        for r in recs:
            evidence = {
                "transcript": conv.get("summary", ""),
                "crm": (
                    f"Renewal in {crm.get('renewal_days')} days, ARR ${crm.get('arr')}, "
                    f"health {crm.get('health')}" if crm else ""
                ),
                "knowledge": knowledge_titles,
                "business_rules": [
                    f"Risk level: {risk.get('risk_level', 'n/a')}",
                    "Renewal within 30 days triggers proactive outreach.",
                ],
            }
            r2 = dict(r)
            r2["evidence"] = evidence
            r2["explanation"] = {
                "evidence_sources": [k for k in ("Meeting transcript" if conv else None,
                                                 "CRM renewal data" if crm else None,
                                                 *(knowledge_titles or [])) if k],
                "reasoning": r.get("reason", ""),
                "confidence": r.get("confidence"),
            }
            explained.append(r2)
        self.log.info("Explained %d recommendations", len(explained))
        return {"recommendations": explained}
