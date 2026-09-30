# Benchmark

Contract 1.1.0. Recorded model. No API key.

This page is the score. `make bench` runs the reference stack, runs the stubs, reruns the capstone, and fails if any line below is wrong.

Six weekend projects. Failing tests. No LangChain.

| Exam | Reference | Stubs on clone |
|---|---|---|
| 01 tools | pass | red |
| 02 sandbox | pass | red |
| 03 permissions | pass | red |
| 04 memory | pass | red |
| 05 spend | pass | red |
| 06 evals | pass | red |
| capstone | pass | red |

Reference: 64 passed

Stubs: 7 exam files red

The capstone is one run of `fixtures/traces/capstone.json` against `fixtures/tiny-repo`, with `favorite_color=blue` already in memory, `.env` denied, and a $0.05 cap.

| Check | Result |
|---|---|
| task | pass |
| policy | pass |
| spend | pass |
| memory | pass |

Capstone score: 1.00

`1.00` means four of four checks passed. A stub implementation does not get a partial score on this page. `make bench` is red until every exam file fails on the stubs and the reference stack is green.
