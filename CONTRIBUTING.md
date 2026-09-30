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

## Releases

One number, in all of these, in the same change:

- `VERSION`
- `agentstack/_version.py`
- the `## [x.y.z]` heading in `CHANGELOG.md`
- `version:` in `CITATION.cff`
- the `contract-x.y.z` badge in `README.md`

The git tag is `v` plus that number. `python3 scripts/check_version.py` is the check. `make dist` builds the sdist (the exam archive) and the wheel (the importable package only).

## Running CI locally

```bash
python3 -m pip install -e ".[dev]"
make ci
```

`pytest` on the stubs is red. `AGENTSTACK_PEEK=1 pytest` on the solutions is green. `make bench` fails if [BENCHMARK.md](BENCHMARK.md) disagrees with that run.
