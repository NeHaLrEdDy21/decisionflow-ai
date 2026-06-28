"""Risk Agent -- identifies renewal and account risks from all signals."""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from llm import llm_json


@register
class RiskAgent(BaseAgent):
    key = "risk"
    label = "Risk"

    def run(self, state: State) -> State:
        context = {
            "conversation": state.get("conversation", {}),
            "crm": state.get("crm", {}),
            "email": state.get("inputs", {}).get("email", ""),
            "support_ticket": state.get("inputs", {}).get("support_ticket", ""),
            "memory": state.get("memory_recall", []),
        }
        prompt = (
            "You are a Customer Success risk analyst. Given the context, identify "
            "account risks (renewal risk, negative sentiment, support issues, "
            "competitor mentions, budget concerns, missing stakeholders).\n\n"
            f"CONTEXT:\n{context}\n\n"
            "Return JSON with keys: risk_level (High/Medium/Low), "
            "risks (list of {type, reason, severity}), confidence (0-100), summary."
        )
        crm = context["crm"]
        renewal = crm.get("renewal_days", 99)
        mock = {
            "risk_level": "High" if renewal <= 30 else "Medium",
            "risks": [
                {"type": "Budget concern", "reason": "Customer is re-evaluating pricing before renewal.", "severity": "High"},
                {"type": "Missing stakeholder", "reason": "Economic buyer not confirmed in last meeting.", "severity": "Medium"},
                {"type": "Open support need", "reason": "SSO implementation requested but not yet delivered.", "severity": "Medium"},
            ],
            "confidence": 88,
            "summary": f"Renewal in {renewal} days with unresolved pricing and SSO concerns makes this an at-risk account.",
        }
        result = llm_json(prompt, mock=mock)
        if not isinstance(result, dict):
            result = {"risk_level": "Medium", "risks": result if isinstance(result, list) else [],
                      "confidence": 70, "summary": ""}
        return {"risk": result}
