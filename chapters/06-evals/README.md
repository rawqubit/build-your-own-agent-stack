# 06 — Evals

Score a trace that is already on disk. Do not call a model. Do not look at `OPENAI_API_KEY`.

## Build

`TraceEvaluator` in `agentstack/evals.py`.

```python
score(trace: list[TraceEvent], spec: dict) -> Report
```

Always return these checks, in this order: `task`, `policy`, `spend`, `memory`.

`report.passed` is true only when every check passed. `report.score` is `passed_count / 4`.

## Spec

| Key | Check | Passes when |
|---|---|---|
| `must_call` | task | every name appears as `event.tool`, or as a whole word inside tool-argument values |
| `must_mention` | task | every string is a substring of some `event.content` |
| `must_not_call` | policy | none of those names appear the same way |
| `must_not_mention` | policy | none of those strings appear in content |
| `max_usd` | spend | `sum(event.cost_usd) <= max_usd`. Detail looks like `spent $0.030000 / $0.05`. If the key is absent, the check passes and the detail is `spent $<amount>` |
| `facts` | memory | each value occurs in the trace. A single-token value also fails the check when the trace contains `key=<other>`. Trailing punctuation on that token is ignored, so `key=blue.` still matches `blue`. If `facts` is missing or empty, the detail is `no facts required` |

A failing detail names the miss (`missing call read`, `forbidden call rm`, `leaked …`, `missing favorite_color`, `favorite_color contradicted`). A passing task or policy detail can say the constraints held.

`bash` with `{"command": "rm -rf /"}` counts as a call to `rm` even when the sandbox refused to run it. Attempting the call is the failure.

## Run

```bash
pytest tests/test_06_evals.py
```
