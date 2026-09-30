"""PEEK reference for 03 — permissions. Default deny."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

from agentstack.types import Action, Decision

_KINDS = {
    "read": "fs",
    "write": "fs",
    "fs": "fs",
    "exec": "commands",
    "command": "commands",
    "commands": "commands",
    "network": "network",
    "net": "network",
}


class CapabilityPermit:
    def __init__(self, policy_path: str):
        self.policy_path = policy_path
        with open(policy_path, "rb") as handle:
            self.policy = tomllib.load(handle)
        self._log: list[Decision] = []

    def check(self, action: Action, *, dry_run: bool = False) -> Decision:
        allow, reason, rule = self._decide(action)
        decision = Decision(
            allow=allow,
            action=action,
            reason=reason,
            rule=rule,
            dry_run=dry_run,
        )
        self._log.append(decision)
        return decision

    def audit(self) -> list[Decision]:
        return list(self._log)

    def _decide(self, action: Action) -> tuple[bool, str, str | None]:
        section = _KINDS.get(action.kind)
        if section is None:
            return False, "default deny", None
        if section == "commands":
            target = _command_name(action)
            targets = [target]
        else:
            target = _norm(action.target)
            targets = [target]
        if section == "fs" and _secret(targets[0], self.policy.get("secrets") or {}):
            return False, "secret pattern", "secrets"
        rules = self.policy.get(section) or {}
        for pattern in rules.get("deny") or []:
            if any(_glob_match(pattern, item) for item in targets):
                return False, "denied by policy", f"{section}.deny"
        for pattern in rules.get("allow") or []:
            if any(_glob_match(pattern, item) for item in targets):
                return True, "allowed by policy", f"{section}.allow"
        return False, "default deny", None


def _command_name(action: Action) -> str:
    raw = action.argv[0] if action.argv else (action.target.split() or [""])[0]
    return Path(raw).name


def _secret(path: str, secrets: dict) -> bool:
    name = Path(path).name
    for pattern in secrets.get("patterns") or []:
        if _glob_match(pattern, path) or _glob_match(pattern, name):
            return True
    return False


def _norm(path: str) -> str:
    raw = path.replace("\\", "/").strip()
    absolute = raw.startswith("/")
    pieces: list[str] = []
    for part in raw.split("/"):
        if part in ("", "."):
            continue
        if part == "..":
            if pieces and pieces[-1] != "..":
                pieces.pop()
            else:
                pieces.append("..")
            continue
        pieces.append(part)
    joined = "/".join(pieces)
    return "/" + joined if absolute else joined


def _glob_match(pattern: str, path: str) -> bool:
    pat = _norm(pattern)
    candidate = _norm(path)
    if re.fullmatch(_glob_to_re(pat), candidate):
        return True
    if "/" not in pat and re.fullmatch(_glob_to_re(pat), Path(candidate).name):
        return True
    return False


def _glob_to_re(pattern: str) -> str:
    out: list[str] = []
    index = 0
    while index < len(pattern):
        if pattern.startswith("**/", index):
            out.append("(?:.*/)?")
            index += 3
            continue
        if pattern.startswith("**", index):
            out.append(".*")
            index += 2
            continue
        char = pattern[index]
        if char == "*":
            out.append("[^/]*")
        elif char == "?":
            out.append("[^/]")
        else:
            out.append(re.escape(char))
        index += 1
    return "".join(out)
