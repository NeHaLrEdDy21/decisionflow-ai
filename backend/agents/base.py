"""Reusable agent interface.

Every agent subclasses ``BaseAgent`` and implements ``run(state)`` returning a
patch dict that is merged into the shared workflow state. Agents register
themselves in ``REGISTRY`` by key, so adding a new agent later is a matter of
creating one file and registering it -- no orchestration code changes.
"""
from __future__ import annotations

import time
from abc import ABC, abstractmethod
from typing import Any, Dict

from logging_config import get_logger

State = Dict[str, Any]
REGISTRY: dict[str, "BaseAgent"] = {}


class BaseAgent(ABC):
    #: unique key used by the planner and registry
    key: str = "base"
    #: human friendly label shown in the UI timeline
    label: str = "Base Agent"

    def __init__(self) -> None:
        self.log = get_logger(f"agent.{self.key}")

    @abstractmethod
    def run(self, state: State) -> State:
        """Return a dict patch to merge into the shared state."""

    def execute(self, state: State) -> State:
        """Wrapper that logs timing and records execution trace in state."""
        start = time.perf_counter()
        self.log.info("START %s", self.label)
        try:
            patch = self.run(state) or {}
            status = "ok"
        except Exception as exc:  # pragma: no cover - defensive
            self.log.exception("Agent %s failed: %s", self.key, exc)
            patch = {"errors": {**state.get("errors", {}), self.key: str(exc)}}
            status = "error"
        elapsed = round((time.perf_counter() - start) * 1000)
        self.log.info("END   %s (%dms, %s)", self.label, elapsed, status)
        trace = state.get("trace", []) + [{
            "agent": self.key, "label": self.label,
            "status": status, "ms": elapsed,
        }]
        patch["trace"] = trace
        return patch


def register(agent_cls: type[BaseAgent]) -> type[BaseAgent]:
    """Class decorator that registers an agent instance under its key."""
    REGISTRY[agent_cls.key] = agent_cls()
    return agent_cls
