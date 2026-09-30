"""PEEK reference for 05 — spend."""

from __future__ import annotations

from typing import Any

from agentstack.spend import BudgetExceeded
from agentstack.types import SpendEvent


class SpendMeter:
    def __init__(
        self,
        *,
        prices: dict[str, dict[str, float]] | None = None,
        run_cap_usd: float = 1.0,
        day_cap_usd: float = 10.0,
        warn_ratio: float = 0.8,
    ):
        self.prices = prices or {}
        self.run_cap_usd = run_cap_usd
        self.day_cap_usd = day_cap_usd
        self.warn_ratio = warn_ratio
        self._events: list[SpendEvent] = []

    def price_model(self, model: str, tokens_in: int, tokens_out: int) -> float:
        table = self.prices.get(model)
        if table is None:
            raise KeyError(f"unknown model: {model}")
        return float(table.get("input", 0.0)) * tokens_in + float(table.get("output", 0.0)) * tokens_out

    def record(self, event: SpendEvent) -> None:
        run_spent = self._run_spent(event.run_id) + event.usd
        day_spent = self._day_spent() + event.usd
        if run_spent >= self.run_cap_usd:
            raise BudgetExceeded(event.run_id, run_spent, self.run_cap_usd)
        if day_spent >= self.day_cap_usd:
            raise BudgetExceeded(event.run_id, day_spent, self.day_cap_usd)
        self._events.append(event)

    def allow(self, run_id: str, next_usd: float = 0.0) -> bool:
        if next_usd < 0:
            return False
        return (
            self._run_spent(run_id) + next_usd < self.run_cap_usd
            and self._day_spent() + next_usd < self.day_cap_usd
        )

    def receipt(self, run_id: str) -> dict[str, Any]:
        events = [event for event in self._events if event.run_id == run_id]
        spent = self._run_spent(run_id)
        waste = _waste(events)
        return {
            "run_id": run_id,
            "spent_usd": spent,
            "cap_usd": self.run_cap_usd,
            "day_spent_usd": self._day_spent(),
            "day_cap_usd": self.day_cap_usd,
            "warn": spent >= self.warn_ratio * self.run_cap_usd,
            "waste_usd": sum(item["usd"] for item in waste),
            "waste": waste,
            "events": [
                {
                    "kind": event.kind,
                    "run_id": event.run_id,
                    "usd": event.usd,
                    "tool": event.tool,
                    "note": event.note,
                    "model": event.model,
                    "tokens_in": event.tokens_in,
                    "tokens_out": event.tokens_out,
                }
                for event in events
            ],
        }

    def _run_spent(self, run_id: str) -> float:
        return sum(event.usd for event in self._events if event.run_id == run_id)

    def _day_spent(self) -> float:
        return sum(event.usd for event in self._events)


def _waste(events: list[SpendEvent]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    groups: dict[tuple[str, str], dict[str, Any]] = {}
    for event in events:
        if event.kind != "tool" or not event.tool:
            continue
        signature = (event.tool, event.note)
        if signature not in seen:
            seen.add(signature)
            continue
        bucket = groups.setdefault(
            signature,
            {"tool": event.tool, "note": event.note, "repeats": 0, "usd": 0.0},
        )
        bucket["repeats"] += 1
        bucket["usd"] += event.usd
    return list(groups.values())
