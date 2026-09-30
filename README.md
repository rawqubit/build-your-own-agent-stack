# Build Your Own Agent Stack

Six weekend projects. Failing tests. No LangChain.

Everyone teaches you to build the loop. This repo makes you build the stack the loop runs on.

```bash
python3 -m pip install -e ".[dev]"
pytest
# red. that's the point. pick chapter 01.
```

You can already call an LLM in a loop. That's not the hard part.
The hard part is: the agent remembers the wrong thing, shells out as root,
burns $200 on a retry storm, and you cannot prove any of it in CI.

This repo is the missing exam.

## The six weekends

| # | You build | You can do after | Tests |
|---|---|---|---|
| [01 Tools](chapters/01-tools/README.md) | typed registry + timeouts | wrap any function as a tool; schema errors fail closed | `pytest tests/test_01_tools.py` |
| [02 Sandbox](chapters/02-sandbox/README.md) | subprocess jail | a prompt cannot `rm -rf` or read `~/.ssh` | `pytest tests/test_02_sandbox.py` |
| [03 Permissions](chapters/03-permissions/README.md) | `agent.toml` default-deny | dry-run "what would have been blocked" | `pytest tests/test_03_permissions.py` |
| [04 Memory](chapters/04-memory/README.md) | retain / recall / forget / reflect | persist a fact across processes; refuse to invent | `pytest tests/test_04_memory.py` |
| [05 Spend](chapters/05-spend/README.md) | ledger + cap + waste | kill a run at $1.00 and print a receipt | `pytest tests/test_05_spend.py` |
| [06 Evals](chapters/06-evals/README.md) | trace scorer | pytest a golden trace with zero API keys | `pytest tests/test_06_evals.py` |

Capstone: `agentstack/loop.py` is given (~80 lines). It imports *your* six modules.
`pytest tests/test_capstone.py` goes green only when all six contracts hold.

## Rules

- Python 3.12+, MIT, `pytest` is the only required dev dependency.
- No agent frameworks. No notebooks. No "hello LLM" chapter.
- Default tests use `FakeLLM` recorded traces. `OPENAI_API_KEY` must be unset.
- Do not edit files under `tests/`. Implement files under `agentstack/`.
- Solutions live in `solutions/` and are labeled PEEK. Use them after you are green, or after you are stuck.

```bash
# run the reference solutions against the same tests
AGENTSTACK_PEEK=1 pytest
```

## Why not the other from-scratch repos

| Repo | What it is | What it skips |
|---|---|---|
| [build-your-own-x](https://github.com/codecrafters-io/build-your-own-x) | curated links + a paid "build Claude Code" | sandbox, spend, forget-memory, eval product |
| [ai-engineering-from-scratch](https://github.com/rohitg00/ai-engineering-from-scratch) | 500+ lesson mega-course | weekend-sized, test-gated chapters |
| [pguso/agents-from-scratch](https://github.com/pguso/agents-from-scratch) | chat → tools → ReAct → basic memory | real jail, budget kill-switch, capability policy |
| most "build a coding agent" courses | the loop | the six libraries the loop sits on |

This is CodeCrafters-shaped (red tests on clone) and agent-stack-shaped (not chatbot-shaped).

## Repo map

```
agentstack/           # you implement tools/sandbox/permissions/memory/spend/evals
                      # types.py, fake_llm.py, loop.py are given — do not edit
chapters/             # weekend briefs
tests/                # frozen exams
solutions/            # PEEK
fixtures/             # agent.toml, tiny-repo, recorded traces
```

## How to work a weekend

1. Read the chapter README (≤ one screen).
2. Run that chapter's tests. They fail.
3. Implement the stub until they pass. Do not touch `tests/`.
4. Only then open `solutions/`.

```bash
make test-01   # then test-02 … test-06, then make test-capstone
```

## Capstone scenario

A prior session stored `favorite_color=blue` and `never read .env`.
The agent may read `src/app.py`. It must be denied `.env`.
Spend is capped at $0.05. The eval report has to pass `must_call=read` and `must_not_call=rm`.

If that one file is green, you built a stack. If the chapters are isolated homework, it is impossible — which is the point.

## License

MIT.
