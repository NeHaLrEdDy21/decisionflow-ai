"""Recommendation Agent -- produces the Top-N Next Best Actions."""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from config import MAX_RECOMMENDATIONS
from llm import llm_json


@register
class RecommendationAgent(BaseAgent):
    key = "recommendation"
    label = "Recommendation"

    def run(self, state: State) -> State:
        context = {
            "conversation": state.get("conversation", {}),
            "crm": state.get("crm", {}),
            "risk": state.get("risk", {}),
            "opportunity": state.get("opportunity", {}),
            "knowledge": state.get("knowledge", []),
            "memory": state.get("memory_recall", []),
        }
        prompt = (
            f"You are a Customer Success strategist. Based on the full context, "
            f"produce the top {MAX_RECOMMENDATIONS} Next Best Actions before renewal.\n\n"
            f"CONTEXT:\n{context}\n\n"
            "Return JSON: recommendations (list of {action, priority "
            "(High/Medium/Low), confidence (0-100), business_impact, reason, "
            "expected_outcome}). Order by priority then confidence."
        )
        mock = {
            "recommendations": [
                {"action": "Schedule a pricing & renewal alignment meeting",
                 "priority": "High", "confidence": 95,
                 "business_impact": "Protects $42,000 ARR renewal",
                 "reason": "Customer raised budget concerns before renewal (transcript + email).",
                 "expected_outcome": "Agreed pricing path and reduced churn risk."},
                {"action": "Deliver SSO implementation plan and timeline",
                 "priority": "High", "confidence": 92,
                 "business_impact": "Unblocks renewal and enables Enterprise upsell",
                 "reason": "SSO requested in meeting and in an open support ticket.",
                 "expected_outcome": "SSO scoped; customer confidence increased."},
                {"action": "Confirm economic buyer / decision maker",
                 "priority": "High", "confidence": 84,
                 "business_impact": "De-risks the renewal decision",
                 "reason": "Stakeholder map incomplete; buyer not confirmed.",
                 "expected_outcome": "Right approver engaged before renewal date."},
                {"action": "Share Enterprise tier proposal with ROI summary",
                 "priority": "Medium", "confidence": 78,
                 "business_impact": "Potential expansion revenue",
                 "reason": "SSO + security needs map to Enterprise tier.",
                 "expected_outcome": "Expansion opportunity formally on the table."},
                {"action": "Book an admin adoption / training workshop",
                 "priority": "Medium", "confidence": 70,
                 "business_impact": "Improves health score and stickiness",
                 "reason": "Drives feature adoption ahead of renewal.",
                 "expected_outcome": "Higher product usage and engagement."},
            ]
        }
        result = llm_json(prompt, mock=mock)
        # Gemini may return either {"recommendations": [...]} or a bare [...].
        if isinstance(result, list):
            recs = result
        else:
            recs = result.get("recommendations", []) if isinstance(result, dict) else []
        return {"recommendations": recs[:MAX_RECOMMENDATIONS]}
