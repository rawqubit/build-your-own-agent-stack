"""05 — Spend meter. Implement SpendMeter."""

from __future__ import annotations

from typing import Any

from agentstack.types import SpendEvent


class BudgetExceeded(Exception):
    def __init__(self, run_id: str, spent: float, cap: float):
        super().__init__(f"run {run_id} spent ${spent:.4f} >= cap ${cap:.4f}")
        self.run_id = run_id
        self.spent = spent
        self.cap = cap


class SpendMeter:
    """Ledger + cap + waste detector.

    Invariant: the next paid call is blocked once a cap is crossed.
    Identical tool loops are marked waste, not just summed.
    """

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
        raise NotImplementedError("05-spend: implement SpendMeter.__init__")

    def price_model(self, model: str, tokens_in: int, tokens_out: int) -> float:
        raise NotImplementedError("05-spend: implement SpendMeter.price_model")

    def record(self, event: SpendEvent) -> None:
        raise NotImplementedError("05-spend: implement SpendMeter.record")

    def allow(self, run_id: str, next_usd: float = 0.0) -> bool:
        raise NotImplementedError("05-spend: implement SpendMeter.allow")

    def receipt(self, run_id: str) -> dict[str, Any]:
        raise NotImplementedError("05-spend: implement SpendMeter.receipt")
