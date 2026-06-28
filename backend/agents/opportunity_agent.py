"""Opportunity Agent -- surfaces upsell / expansion opportunities."""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from llm import llm_json


@register
class OpportunityAgent(BaseAgent):
    key = "opportunity"
    label = "Opportunity"

    def run(self, state: State) -> State:
        context = {
            "conversation": state.get("conversation", {}),
            "crm": state.get("crm", {}),
            "knowledge": state.get("knowledge", []),
        }
        prompt = (
            "You are a Customer Success growth strategist. Identify expansion "
            "opportunities (upsell, cross-sell, feature adoption, training, "
            "enterprise onboarding, premium features).\n\n"
            f"CONTEXT:\n{context}\n\n"
            "Return JSON: opportunities (list of {opportunity, type, priority "
            "(High/Medium/Low), confidence (0-100), rationale})."
        )
        mock = {
            "opportunities": [
                {"opportunity": "Upsell Enterprise SSO/Security tier", "type": "Upsell",
                 "priority": "High", "confidence": 90,
                 "rationale": "Customer explicitly requested SSO; aligns with Enterprise tier."},
                {"opportunity": "Premium support add-on", "type": "Cross-sell",
                 "priority": "Medium", "confidence": 72,
                 "rationale": "Active support ticket signals appetite for faster SLAs."},
                {"opportunity": "Admin training & adoption workshop", "type": "Training",
                 "priority": "Medium", "confidence": 68,
                 "rationale": "Drives feature adoption and strengthens renewal."},
            ]
        }
        result = llm_json(prompt, mock=mock)
        if isinstance(result, list):
            result = {"opportunities": result}
        elif not isinstance(result, dict):
            result = {"opportunities": []}
        return {"opportunity": result}
