"""Shared types. Given. Do not edit."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class ToolSpec:
    name: str
    description: str
    parameters: dict[str, Any]
    timeout_s: float = 5.0
    side_effect: str = "none"
    max_result_bytes: int = 8_192


@dataclass
class ToolResult:
    name: str
    ok: bool
    content: str
    error: str | None = None
    truncated: bool = False
    timed_out: bool = False


@dataclass
class ExecResult:
    argv: list[str]
    cwd: str
    exit_code: int
    stdout: str
    stderr: str
    timed_out: bool
    bytes_written: int
    blocked: bool = False
    block_reason: str | None = None


@dataclass(frozen=True)
class Action:
    kind: str
    target: str
    argv: tuple[str, ...] = ()


@dataclass
class Decision:
    allow: bool
    action: Action
    reason: str
    rule: str | None = None
    dry_run: bool = False


@dataclass(frozen=True)
class MemoryHit:
    key: str
    value: str
    score: float
    namespace: str
    source: str = ""


@dataclass
class SpendEvent:
    kind: str
    run_id: str
    usd: float
    tokens_in: int = 0
    tokens_out: int = 0
    model: str | None = None
    tool: str | None = None
    note: str = ""


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""


@dataclass
class Report:
    passed: bool
    score: float
    checks: list[Check] = field(default_factory=list)


@dataclass
class TraceEvent:
    role: str
    content: str = ""
    tool: str | None = None
    tool_args: dict[str, Any] = field(default_factory=dict)
    cost_usd: float = 0.0
    path: str | None = None
