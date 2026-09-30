# Changelog

All notable changes to this exam are documented in this file.

The version is [semantic](https://semver.org/spec/v2.0.0.html). The git tag is `v` plus the version in `VERSION`. The test contract does not change inside a major version.

## [1.1.0] - 2026-09-30

The benchmark. Same six exams. A published score.

### Added

- `BENCHMARK.md` and `make bench`. The reference stack must score 1.00 on the capstone, every exam file must pass under `AGENTSTACK_PEEK=1`, and every exam file must fail on the stubs.
- Two sandbox cases the chapter already required: an empty command is refused, and `allowed_bins=None` still runs a non-network binary.

### Contract

- Student modules are unchanged. The two new sandbox tests lock behavior the chapter already described.

## [1.0.0] - 2026-09-30

First frozen contract.

### Added

- Six weekend exams: tools, sandbox, permissions, memory, spend, evals.
- Given loop (`agentstack/loop.py`) and recorded model (`agentstack/fake_llm.py`).
- Capstone scenario over `fixtures/tiny-repo` and `fixtures/traces/capstone.json`.
- Reference solutions, loaded only when `AGENTSTACK_PEEK=1`.
- Source archive (`sdist`) and wheel as the release artifacts. The sdist is the exam. The wheel is the importable package.

### Contract

- Python 3.12+.
- Trace scripts follow `fixtures/traces/README.md` schema `trace-script/v1`.
- Policy files follow `fixtures/agent.toml` format `policy/v1`.
