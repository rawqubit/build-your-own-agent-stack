"""06 — score a frozen trace. Zero API keys."""

from __future__ import annotations

import os

from agentstack.evals import TraceEvaluator
from agentstack.types import TraceEvent


def _trace() -> list[TraceEvent]:
    return [
        TraceEvent(role="memory", content="favorite_color=blue"),
        TraceEvent(
            role="tool",
            content='print("hi")\n',
            tool="read",
            tool_args={"path": "src/app.py"},
            path="src/app.py",
            cost_usd=0.01,
        ),
        TraceEvent(role="assistant", content="favorite_color=blue and the file is small", cost_usd=0.02),
    ]


def _spec() -> dict:
    return {
        "must_call": ["read"],
        "must_not_call": ["rm"],
        "must_mention": ['print("hi")'],
        "must_not_mention": ["SUPERSECRET"],
        "max_usd": 0.05,
        "facts": {"favorite_color": "blue"},
    }


def test_golden_trace_passes_every_dimension():
    assert os.environ.get("OPENAI_API_KEY") in (None, "")
    report = TraceEvaluator().score(_trace(), _spec())
    assert report.passed is True
    assert report.score == 1.0
    assert [check.name for check in report.checks] == ["task", "policy", "spend", "memory"]
    assert all(check.passed for check in report.checks)


def test_missing_call_fails_only_the_task():
    trace = [TraceEvent(role="assistant", content='print("hi") favorite_color=blue', cost_usd=0.01)]
    report = TraceEvaluator().score(trace, _spec())
    by_name = {check.name: check for check in report.checks}
    assert report.passed is False
    assert report.score == 0.75
    assert by_name["task"].passed is False
    assert "read" in by_name["task"].detail
    assert by_name["policy"].passed is True
    assert by_name["spend"].passed is True
    assert by_name["memory"].passed is True


def test_rm_in_a_bash_command_fails_policy():
    trace = _trace() + [
        TraceEvent(role="tool", content="denied", tool="bash", tool_args={"command": "rm -rf /"})
    ]
    report = TraceEvaluator().score(trace, _spec())
    policy = next(check for check in report.checks if check.name == "policy")
    assert policy.passed is False
    assert "rm" in policy.detail


def test_over_budget_fails_spend():
    trace = _trace() + [TraceEvent(role="assistant", content="again", cost_usd=1.0)]
    report = TraceEvaluator().score(trace, _spec())
    spend = next(check for check in report.checks if check.name == "spend")
    assert spend.passed is False
    assert "spent $" in spend.detail


def test_trailing_punctuation_is_not_a_contradiction():
    trace = [TraceEvent(role="assistant", content="favorite_color=blue. done")]
    report = TraceEvaluator().score(trace, {"facts": {"favorite_color": "blue"}})
    memory = next(check for check in report.checks if check.name == "memory")
    assert memory.passed is True


def test_contradicted_fact_fails_memory():
    trace = [TraceEvent(role="assistant", content="favorite_color=red", tool="read", cost_usd=0.0)]
    spec = {"must_call": ["read"], "facts": {"favorite_color": "blue"}, "max_usd": 1}
    report = TraceEvaluator().score(trace, spec)
    memory = next(check for check in report.checks if check.name == "memory")
    assert memory.passed is False


def test_secret_text_fails_policy():
    trace = _trace() + [TraceEvent(role="tool", content="SUPERSECRET", tool="read")]
    report = TraceEvaluator().score(trace, _spec())
    policy = next(check for check in report.checks if check.name == "policy")
    assert policy.passed is False
    assert "SUPERSECRET" in policy.detail


def test_empty_spec_passes_with_no_facts_required():
    report = TraceEvaluator().score([], {})
    assert report.passed is True
    assert report.score == 1.0
    memory = next(check for check in report.checks if check.name == "memory")
    assert memory.detail == "no facts required"
