"""01 — Tools. Implement ToolBelt."""

from __future__ import annotations

from typing import Any, Callable

from agentstack.types import ToolResult, ToolSpec


class ToolBelt:
    """Typed registry + dispatcher.

    Invariant: unknown names, schema misses, hangs, and giant outputs
    become ToolResult errors. The loop never sees a raw traceback.
    """

    def register(self, spec: ToolSpec, handler: Callable[..., Any]) -> None:
        raise NotImplementedError("01-tools: implement ToolBelt.register")

    def call(self, name: str, args: dict[str, Any]) -> ToolResult:
        raise NotImplementedError("01-tools: implement ToolBelt.call")

    def names(self) -> list[str]:
        raise NotImplementedError("01-tools: implement ToolBelt.names")
