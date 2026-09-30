"""05 — ledger, cap, and repeated-tool waste."""

from __future__ import annotations

import pytest

from agentstack.spend import BudgetExceeded, SpendMeter
from agentstack.types import SpendEvent


PRICES = {"fake-small": {"input": 0.01, "output": 0.02}}


def _meter(**kwargs) -> SpendMeter:
    fields = {"prices": PRICES, "run_cap_usd": 1.0, "day_cap_usd": 10.0, "warn_ratio": 0.8}
    fields.update(kwargs)
    return SpendMeter(**fields)


def test_price_model_uses_per_token_rates():
    assert _meter().price_model("fake-small", 2, 3) == pytest.approx(0.08)


def test_unknown_model_raises():
    with pytest.raises(KeyError):
        _meter().price_model("missing", 1, 1)


def test_record_at_the_cap_raises_and_does_not_keep_the_event():
    meter = _meter(run_cap_usd=1.0)
    meter.record(SpendEvent(kind="model", run_id="run", usd=0.6, model="fake-small"))
    assert meter.allow("run", 0.4) is False
    with pytest.raises(BudgetExceeded) as caught:
        meter.record(SpendEvent(kind="model", run_id="run", usd=0.4, model="fake-small"))
    assert caught.value.run_id == "run"
    assert caught.value.spent == pytest.approx(1.0)
    assert caught.value.cap == pytest.approx(1.0)
    assert ">= cap" in str(caught.value)
    assert meter.receipt("run")["spent_usd"] == pytest.approx(0.6)


def test_allow_is_false_exactly_at_the_cap():
    meter = _meter(run_cap_usd=1.0)
    meter.record(SpendEvent(kind="model", run_id="run", usd=0.4))
    assert meter.allow("run", 0.6) is False
    assert meter.allow("run", 0.59) is True


def test_day_cap_blocks_a_second_run():
    meter = _meter(run_cap_usd=10.0, day_cap_usd=1.0)
    meter.record(SpendEvent(kind="model", run_id="a", usd=0.6))
    assert meter.allow("b", 0.5) is False
    with pytest.raises(BudgetExceeded) as caught:
        meter.record(SpendEvent(kind="model", run_id="b", usd=0.5))
    assert caught.value.cap == pytest.approx(1.0)
    assert meter.receipt("a")["day_spent_usd"] == pytest.approx(0.6)


def test_warn_flag_follows_the_ratio():
    meter = _meter(run_cap_usd=1.0, warn_ratio=0.8)
    meter.record(SpendEvent(kind="model", run_id="run", usd=0.79))
    assert meter.receipt("run")["warn"] is False
    meter.record(SpendEvent(kind="model", run_id="run", usd=0.01))
    receipt = meter.receipt("run")
    assert receipt["warn"] is True
    assert receipt["cap_usd"] == pytest.approx(1.0)
    assert receipt["spent_usd"] == pytest.approx(0.8)


def test_identical_tool_loops_are_waste():
    meter = _meter()
    for _ in range(3):
        meter.record(SpendEvent(kind="tool", run_id="run", usd=0.2, tool="read", note="src/app.py"))
    meter.record(SpendEvent(kind="tool", run_id="run", usd=0.2, tool="read", note="README.md"))
    receipt = meter.receipt("run")
    assert receipt["spent_usd"] == pytest.approx(0.8)
    assert receipt["waste_usd"] == pytest.approx(0.4)
    assert receipt["waste"] == [
        {"tool": "read", "note": "src/app.py", "repeats": 2, "usd": pytest.approx(0.4)}
    ]


def test_receipt_lists_events_for_one_run_only():
    meter = _meter()
    meter.record(SpendEvent(kind="model", run_id="run", usd=0.1, model="fake-small", tokens_in=1, tokens_out=2))
    meter.record(SpendEvent(kind="model", run_id="other", usd=0.25))
    receipt = meter.receipt("run")
    assert receipt["run_id"] == "run"
    assert receipt["spent_usd"] == pytest.approx(0.1)
    assert receipt["events"][0]["model"] == "fake-small"
    assert receipt["events"][0]["tokens_out"] == 2
    assert receipt["day_spent_usd"] == pytest.approx(0.35)
