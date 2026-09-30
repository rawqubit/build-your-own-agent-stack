# Capstone

`agentstack/loop.py` is given. It imports your six modules and drives `FakeLLM`.

A prior session stored `favorite_color=blue` and `boundary=never read .env`. The agent may read `src/app.py`. `.env` is a secret. Spend is capped at `$0.05`. The report passes only when `must_call` includes `read` and `must_not_call` includes `rm`.

`fixtures/tiny-repo` is the workspace. `fixtures/traces/capstone.json` is the script. `fixtures/agent.toml` is the policy. No API key.

```bash
pytest tests/test_capstone.py
```

If the chapters pass alone and this file does not, the modules do not agree. That is the point.
