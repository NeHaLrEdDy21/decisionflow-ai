"""CRM Agent -- normalises CRM data into a customer record."""
from __future__ import annotations

from agents.base import BaseAgent, State, register
from tools.crm_tool import parse_crm


@register
class CRMAgent(BaseAgent):
    key = "crm"
    label = "CRM"

    def run(self, state: State) -> State:
        raw = state.get("inputs", {}).get("crm")
        if not raw:
            return {"crm": {}}
        record = parse_crm(raw)
        self.log.info("CRM: %s | renewal in %sd | ARR $%s | health %s",
                      record["name"], record["renewal_days"],
                      record["arr"], record["health"])
        return {"crm": record}
