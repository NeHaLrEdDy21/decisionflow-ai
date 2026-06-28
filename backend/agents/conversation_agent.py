"""Conversation Agent -- analyses a meeting transcript."""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from llm import llm_json


@register
class ConversationAgent(BaseAgent):
    key = "conversation"
    label = "Conversation"

    def run(self, state: State) -> State:
        transcript = state.get("inputs", {}).get("transcript", "")
        if not transcript:
            return {"conversation": {}}

        prompt = (
            "You are a Customer Success analyst. Analyse this meeting transcript "
            "and extract structured insight.\n\nTRANSCRIPT:\n" + transcript +
            "\n\nReturn JSON with keys: summary, pain_points (list), goals (list), "
            "sentiment (Positive/Neutral/Negative), competitors (list), "
            "urgency (High/Medium/Low), missing_information (list)."
        )
        mock = {
            "summary": "Customer is satisfied with the platform but has active pricing concerns ahead of renewal and needs SSO.",
            "pain_points": ["Pricing concerns before renewal", "Needs SSO / enterprise security"],
            "goals": ["Renew with predictable pricing", "Roll out SSO to all users"],
            "sentiment": "Positive",
            "competitors": [],
            "urgency": "High",
            "missing_information": ["Decision maker / economic buyer not confirmed", "Budget ceiling unknown"],
        }
        result = llm_json(prompt, mock=mock)
        return {"conversation": result}
