# 05 — Spend

The next paid call dies when it would touch the cap. Repeated identical tool calls are waste, and they still count as money.

## Build

`SpendMeter` in `agentstack/spend.py`. `BudgetExceeded` is already defined there. Raise that class. Do not invent a second one.

```python
SpendMeter(*, prices=None, run_cap_usd=1.0, day_cap_usd=10.0, warn_ratio=0.8)
price_model(model, tokens_in, tokens_out) -> float
record(event) -> None
allow(run_id, next_usd=0.0) -> bool
receipt(run_id) -> dict
```

`prices` maps a model name to `{"input": usd_per_token, "output": usd_per_token}`. A missing model raises `KeyError`. A missing rate is `0`.

## Caps

`allow` is `False` when `next_usd < 0`, or when this run's spend plus `next_usd` is greater than or equal to `run_cap_usd`, or when every run so far plus `next_usd` is greater than or equal to `day_cap_usd`.

`record` uses the same rule for `event.usd`. If the run cap would break, raise `BudgetExceeded(run_id, projected_run_spend, run_cap_usd)`. If the day cap would break, raise it with the projected day spend and `day_cap_usd`. Do not keep the rejected event. The exception text contains `>= cap`.

There is no clock. "Today" is every event recorded on this meter.

## Receipt

```text
run_id, spent_usd, cap_usd, day_spent_usd, day_cap_usd, warn, waste_usd, waste, events
```

`warn` is true when this run's spend is at least `warn_ratio * run_cap_usd`.

A tool event is waste when the same `(tool, note)` already occurred in that run. The first one is real. `waste` is a list of `{tool, note, repeats, usd}` for the extras only. `waste_usd` sums those extras. Model calls are not waste. `events` lists only that run, in order, with `kind`, `run_id`, `usd`, `tool`, `note`, `model`, `tokens_in`, `tokens_out`.

## Run

```bash
pytest tests/test_05_spend.py
```

`fixtures/traces/waste_reads.json` is the shape of the retry storm this chapter is about.
