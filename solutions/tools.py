"""PEEK reference for 01 — tools."""

from __future__ import annotations

import threading
from typing import Any, Callable

from agentstack.types import ToolResult, ToolSpec

_TYPES = {
    "string": str,
    "boolean": bool,
}


class ToolBelt:
    def __init__(self) -> None:
        self._tools: dict[str, tuple[ToolSpec, Callable[..., Any]]] = {}

    def register(self, spec: ToolSpec, handler: Callable[..., Any]) -> None:
        self._tools[spec.name] = (spec, handler)

    def names(self) -> list[str]:
        return sorted(self._tools)

    def call(self, name: str, args: dict[str, Any]) -> ToolResult:
        if name not in self._tools:
            return ToolResult(name=name, ok=False, content="", error=f"unknown tool: {name}")
        spec, handler = self._tools[name]
        if not isinstance(args, dict):
            return ToolResult(name=name, ok=False, content="", error="arguments must be an object")
        try:
            clean = _validate(spec, args)
        except ValueError as exc:
            return ToolResult(name=name, ok=False, content="", error=str(exc))

        box: dict[str, Any] = {}

        def run() -> None:
            try:
                box["value"] = handler(**clean)
            except Exception as exc:  # noqa: BLE001 — callers never see a traceback
                box["error"] = exc

        worker = threading.Thread(target=run, daemon=True)
        worker.start()
        worker.join(spec.timeout_s)
        if worker.is_alive():
            return ToolResult(
                name=name,
                ok=False,
                content="",
                error=f"timeout after {spec.timeout_s:g}s",
                timed_out=True,
            )
        if "error" in box:
            exc = box["error"]
            return ToolResult(
                name=name,
                ok=False,
                content="",
                error=f"{type(exc).__name__}: {exc}",
            )
        text = "" if box.get("value") is None else str(box["value"])
        raw = text.encode("utf-8")
        truncated = len(raw) > spec.max_result_bytes
        if truncated:
            text = raw[: spec.max_result_bytes].decode("utf-8", errors="ignore")
        return ToolResult(name=name, ok=True, content=text, truncated=truncated)


def _validate(spec: ToolSpec, args: dict[str, Any]) -> dict[str, Any]:
    schema = spec.parameters or {}
    props: dict[str, Any] = schema.get("properties") or {}
    required = list(schema.get("required") or [])
    additional = schema.get("additionalProperties", False)
    missing = [key for key in required if key not in args]
    if missing:
        raise ValueError("missing required: " + ", ".join(missing))
    clean: dict[str, Any] = {}
    for key, value in args.items():
        if key not in props:
            if additional is False:
                raise ValueError(f"unexpected argument: {key}")
            clean[key] = value
            continue
        expected = (props.get(key) or {}).get("type")
        if expected and not _matches(expected, value):
            raise ValueError(f"{key}: expected {expected}")
        clean[key] = value
    return clean


def _matches(expected: str, value: Any) -> bool:
    if expected == "integer":
        return isinstance(value, int) and not isinstance(value, bool)
    if expected == "number":
        return isinstance(value, (int, float)) and not isinstance(value, bool)
    python_type = _TYPES.get(expected)
    if python_type is None:
        return True
    return isinstance(value, python_type)
