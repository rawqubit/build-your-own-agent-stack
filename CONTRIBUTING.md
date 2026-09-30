# Contributing

This repo is an exam. PRs that make the exam easier in the wrong way will be closed.

## Accept

- Clearer chapter READMEs
- Extra hidden tests that still fit a weekend
- Bugfixes in given files (`types.py`, `fake_llm.py`, `loop.py`)
- Reference-solution fixes that keep the public API stable

## Reject

- LangChain / CrewAI / AutoGen / PydanticAI helpers
- A "hello LLM" chapter
- Tests that require a paid API key
- Notebooks
- Chapter 07

## Running CI locally

```bash
python3 -m pip install -e ".[dev]"
pytest                         # student stubs: red
AGENTSTACK_PEEK=1 pytest       # solutions: green
```
