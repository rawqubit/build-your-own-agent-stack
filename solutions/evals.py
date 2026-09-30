"""PEEK reference for 06 — evals. No model calls."""

from __future__ import annotations

import re
from typing import Any

from agentstack.types import Check, Report, TraceEvent


class TraceEvaluator:
    def score(self, trace: list[TraceEvent], spec: dict[str, Any]) -> Report:
        checks = [
            _task(trace, spec),
            _policy(trace, spec),
            _spend(trace, spec),
            _memory(trace, spec),
        ]
        passed_count = sum(1 for check in checks if check.passed)
        return Report(
            passed=all(check.passed for check in checks),
            score=passed_count / len(checks),
            checks=checks,
        )


def _task(trace: list[TraceEvent], spec: dict[str, Any]) -> Check:
    missing = [name for name in spec.get("must_call") or [] if not _called(trace, name)]
    absent = [text for text in spec.get("must_mention") or [] if text not in _text(trace)]
    problems = [f"missing call {name}" for name in missing] + [f"missing text {text}" for text in absent]
    if problems:
        return Check("task", False, "; ".join(problems))
    return Check("task", True, "task constraints held")


def _policy(trace: list[TraceEvent], spec: dict[str, Any]) -> Check:
    called = [name for name in spec.get("must_not_call") or [] if _called(trace, name)]
    leaked = [text for text in spec.get("must_not_mention") or [] if text in _text(trace)]
    problems = [f"forbidden call {name}" for name in called] + [f"leaked {text}" for text in leaked]
    if problems:
        return Check("policy", False, "; ".join(problems))
    return Check("policy", True, "policy constraints held")


def _spend(trace: list[TraceEvent], spec: dict[str, Any]) -> Check:
    spent = sum(event.cost_usd for event in trace)
    if "max_usd" not in spec or spec.get("max_usd") is None:
        return Check("spend", True, f"spent ${spent:.6f}")
    limit = float(spec["max_usd"])
    ok = spent <= limit
    return Check("spend", ok, f"spent ${spent:.6f} / ${limit:.2f}")


def _memory(trace: list[TraceEvent], spec: dict[str, Any]) -> Check:
    facts = spec.get("facts") or {}
    if not isinstance(facts, dict) or not facts:
        return Check("memory", True, "no facts required")
    text = _text(trace)
    lowered = text.lower()
    problems: list[str] = []
    for key, value in facts.items():
        rendered = str(value)
        if rendered.lower() not in lowered:
            problems.append(f"missing {key}")
            continue
        if re.fullmatch(r"\S+", rendered):
            pattern = rf"{re.escape(str(key))}\s*=\s*(\S+)"
            for found in re.findall(pattern, text, flags=re.IGNORECASE):
                found = found.strip(".,;:!?\"'")
                if found.lower() != rendered.lower():
                    problems.append(f"{key} contradicted")
                    break
    if problems:
        return Check("memory", False, "; ".join(problems))
    return Check("memory", True, "facts held")


def _text(trace: list[TraceEvent]) -> str:
    return "\n".join(event.content or "" for event in trace)


def _called(trace: list[TraceEvent], name: str) -> bool:
    for event in trace:
        if event.tool == name:
            return True
        blob = " ".join(str(value) for value in (event.tool_args or {}).values())
        if name in blob.split():
            return True
    return False
