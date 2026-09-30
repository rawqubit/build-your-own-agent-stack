"""PEEK reference for 02 — sandbox. A policy jail, not a VM."""

from __future__ import annotations

import os
import re
import subprocess
from pathlib import Path

from agentstack.types import ExecResult

_NET_BINS = {
    "curl",
    "dig",
    "ftp",
    "nc",
    "ncat",
    "nmap",
    "nslookup",
    "ping",
    "scp",
    "sftp",
    "socat",
    "ssh",
    "telnet",
    "wget",
}
_SSH = re.compile(r"(^|[/\\])(\.ssh|id_rsa|id_ed25519)([/\\]|$)")
_EMBEDDED = re.compile(
    r"~[A-Za-z0-9_./-]*"
    r"|\.\.(?:/[A-Za-z0-9._-]*)+"
    r"|/(?:[A-Za-z0-9._-]+/)[A-Za-z0-9._/-]*"
)
_SECRET_KEY = re.compile(r"(SECRET|TOKEN|PASSWORD|PASSWD|CREDENTIAL|API_KEY)|_KEY$", re.I)
_PATH_TOKEN = re.compile(r"^[~./A-Za-z0-9_-][~./A-Za-z0-9_-]*$")


class WorkspaceSandbox:
    def __init__(self, workspace: str, *, allowed_bins: list[str] | None = None):
        self.workspace = str(Path(workspace).resolve())
        Path(self.workspace).mkdir(parents=True, exist_ok=True)
        self.allowed_bins = list(allowed_bins) if allowed_bins is not None else None

    def run(
        self,
        argv: list[str],
        *,
        cwd: str | None = None,
        timeout_s: float = 5.0,
        env: dict[str, str] | None = None,
        max_output_bytes: int = 1_000_000,
    ) -> ExecResult:
        requested = list(argv)
        base = self._resolve_cwd(cwd)
        if not requested:
            return self._block(requested, base, "empty command")
        binary = Path(requested[0]).name
        if binary in _NET_BINS:
            return self._block(requested, base, "network binary denied")
        if self.allowed_bins is not None and binary not in self.allowed_bins:
            return self._block(requested, base, "binary not in allow list")
        if base is None or not self._inside(base):
            return self._block(requested, str(cwd or self.workspace), "cwd outside workspace")
        for arg in requested:
            reason = self._arg_reason(arg, base)
            if reason:
                return self._block(requested, str(base), reason)

        before = self._sizes()
        try:
            proc = subprocess.run(
                requested,
                cwd=str(base),
                env=self._env(env),
                capture_output=True,
                timeout=timeout_s,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            stdout = _clip(exc.stdout, max_output_bytes)
            stderr = _clip(exc.stderr, max_output_bytes)
            return ExecResult(
                argv=requested,
                cwd=str(base),
                exit_code=124,
                stdout=stdout,
                stderr=stderr,
                timed_out=True,
                bytes_written=self._written(before),
            )
        return ExecResult(
            argv=requested,
            cwd=str(base),
            exit_code=proc.returncode,
            stdout=_clip(proc.stdout, max_output_bytes),
            stderr=_clip(proc.stderr, max_output_bytes),
            timed_out=False,
            bytes_written=self._written(before),
        )

    def _resolve_cwd(self, cwd: str | None) -> Path | None:
        raw = Path(cwd) if cwd else Path(self.workspace)
        if not raw.is_absolute():
            raw = Path(self.workspace) / raw
        try:
            return raw.resolve()
        except OSError:
            return None

    def _inside(self, path: Path) -> bool:
        try:
            path.resolve().relative_to(self.workspace)
            return True
        except (OSError, ValueError):
            return False

    def _arg_reason(self, arg: str, cwd: Path) -> str | None:
        if _SSH.search(arg):
            return "ssh key denied"
        if "~" in arg:
            return "path outside workspace"
        for raw in _candidates(arg):
            path = Path(raw)
            if not path.is_absolute():
                path = cwd / path
            if not self._inside(path):
                return "path outside workspace"
        return None

    def _env(self, extra: dict[str, str] | None) -> dict[str, str]:
        clean = {
            "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
            "HOME": self.workspace,
            "LANG": "C.UTF-8",
            "LC_ALL": "C.UTF-8",
        }
        for key, value in (extra or {}).items():
            if _SECRET_KEY.search(key):
                continue
            clean[key] = value
        return clean

    def _sizes(self) -> dict[str, int]:
        sizes: dict[str, int] = {}
        for path in Path(self.workspace).rglob("*"):
            if path.is_file():
                sizes[str(path)] = path.stat().st_size
        return sizes

    def _written(self, before: dict[str, int]) -> int:
        total = 0
        for path, size in self._sizes().items():
            total += max(0, size - before.get(path, 0))
        return total

    def _block(self, argv: list[str], cwd: str | Path, reason: str) -> ExecResult:
        return ExecResult(
            argv=list(argv),
            cwd=str(cwd),
            exit_code=126,
            stdout="",
            stderr="",
            timed_out=False,
            bytes_written=0,
            blocked=True,
            block_reason=reason,
        )


def _candidates(arg: str) -> list[str]:
    found = list(_EMBEDDED.findall(arg))
    if _PATH_TOKEN.fullmatch(arg) and ("/" in arg or arg.startswith(".")):
        found.append(arg)
    if arg == "/":
        found.append("/")
    return found


def _clip(payload: bytes | None, limit: int) -> str:
    data = payload or b""
    return data[:limit].decode("utf-8", errors="replace")
