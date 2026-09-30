"""06 — Evals. Implement TraceEvaluator."""

from __future__ import annotations

from typing import Any

from agentstack.types import Report, TraceEvent


class TraceEvaluator:
    """Score a frozen trace against a spec. No model calls.

    Invariant: a committed golden trace is scored with zero API keys.
    Dimensions are separate: task, policy, spend, memory fidelity.
    """

    def score(self, trace: list[TraceEvent], spec: dict[str, Any]) -> Report:
        raise NotImplementedError("06-evals: implement TraceEvaluator.score")
