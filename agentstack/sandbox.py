"""02 — Sandbox. Implement WorkspaceSandbox."""

from __future__ import annotations

from agentstack.types import ExecResult


class WorkspaceSandbox:
    """Subprocess jail rooted at `workspace`.

    Invariant: nothing outside the workspace is readable or writable.
    Network binaries are denied. Hung processes die at timeout.
    This is a policy jail, not Firecracker. That's the point of the exam.
    """

    def __init__(self, workspace: str, *, allowed_bins: list[str] | None = None):
        self.workspace = workspace
        self.allowed_bins = allowed_bins
        raise NotImplementedError("02-sandbox: implement WorkspaceSandbox.__init__")

    def run(
        self,
        argv: list[str],
        *,
        cwd: str | None = None,
        timeout_s: float = 5.0,
        env: dict[str, str] | None = None,
        max_output_bytes: int = 1_000_000,
    ) -> ExecResult:
        raise NotImplementedError("02-sandbox: implement WorkspaceSandbox.run")
