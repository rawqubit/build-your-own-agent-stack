"""01 — tool registry. Schema, timeout, and size fail closed."""

from __future__ import annotations

import time

from agentstack.tools import ToolBelt
from agentstack.types import ToolSpec


def _add_spec(**overrides) -> ToolSpec:
    params = {
        "type": "object",
        "required": ["a", "b"],
        "properties": {"a": {"type": "integer"}, "b": {"type": "integer"}},
        "additionalProperties": False,
    }
    fields = {
        "name": "add",
        "description": "add two integers",
        "parameters": params,
        "timeout_s": 2.0,
        "max_result_bytes": 64,
    }
    fields.update(overrides)
    return ToolSpec(**fields)


def test_registered_call_returns_the_handler_result():
    belt = ToolBelt()
    belt.register(_add_spec(), lambda a, b: a + b)
    result = belt.call("add", {"a": 2, "b": 3})
    assert result.ok
    assert result.content == "5"
    assert result.error is None
    assert result.truncated is False
    assert result.timed_out is False


def test_names_are_sorted():
    belt = ToolBelt()
    belt.register(_add_spec(name="zeta"), lambda a, b: 0)
    belt.register(_add_spec(name="alpha"), lambda a, b: 0)
    assert belt.names() == ["alpha", "zeta"]
    assert ToolBelt().names() == []


def test_unknown_tool_is_an_error_result():
    result = ToolBelt().call("launch_missiles", {})
    assert result.ok is False
    assert result.error is not None and "unknown tool" in result.error


def test_arguments_must_be_an_object():
    belt = ToolBelt()
    belt.register(_add_spec(), lambda a, b: a + b)
    result = belt.call("add", None)  # type: ignore[arg-type]
    assert result.ok is False
    assert result.error == "arguments must be an object"


def test_missing_required_argument_fails_closed():
    belt = ToolBelt()
    belt.register(_add_spec(), lambda a, b: a + b)
    result = belt.call("add", {"a": 1})
    assert result.ok is False
    assert result.error is not None and "missing required: b" in result.error


def test_wrong_json_type_fails_closed():
    belt = ToolBelt()
    belt.register(_add_spec(), lambda a, b: a + b)
    result = belt.call("add", {"a": True, "b": 1})
    assert result.ok is False
    assert result.error is not None and "a: expected integer" in result.error
    floated = belt.call("add", {"a": 1.5, "b": 1})
    assert floated.ok is False


def test_unexpected_argument_fails_closed():
    belt = ToolBelt()
    belt.register(_add_spec(), lambda a, b: a + b)
    result = belt.call("add", {"a": 1, "b": 2, "c": 3})
    assert result.ok is False
    assert result.error is not None and "unexpected argument: c" in result.error


def test_handler_exception_becomes_an_error_result():
    belt = ToolBelt()

    def boom(a, b):
        raise RuntimeError("nope")

    belt.register(_add_spec(), boom)
    result = belt.call("add", {"a": 1, "b": 2})
    assert result.ok is False
    assert result.error is not None and "RuntimeError: nope" in result.error
    assert result.timed_out is False


def test_slow_handler_times_out():
    belt = ToolBelt()

    def nap(a, b):
        time.sleep(3)
        return 1

    belt.register(_add_spec(timeout_s=0.4), nap)
    result = belt.call("add", {"a": 1, "b": 2})
    assert result.ok is False
    assert result.timed_out is True
    assert result.error is not None and "timeout" in result.error


def test_giant_output_is_truncated():
    belt = ToolBelt()
    belt.register(_add_spec(max_result_bytes=4), lambda a, b: "abcdefghij")
    result = belt.call("add", {"a": 1, "b": 2})
    assert result.ok is True
    assert result.truncated is True
    assert len(result.content.encode("utf-8")) <= 4
    assert result.content == "abcd"
