"""03 — Permissions. Implement CapabilityPermit."""

from __future__ import annotations

from agentstack.types import Action, Decision


class CapabilityPermit:
    """Default-deny capability policy loaded from agent.toml.

    Invariant: undeclared is denied. Dry-run returns the same decisions
    and changes nothing. Secrets stay invisible even under a broad allow.
    """

    def __init__(self, policy_path: str):
        self.policy_path = policy_path
        raise NotImplementedError("03-permissions: implement CapabilityPermit.__init__")

    def check(self, action: Action, *, dry_run: bool = False) -> Decision:
        raise NotImplementedError("03-permissions: implement CapabilityPermit.check")

    def audit(self) -> list[Decision]:
        raise NotImplementedError("03-permissions: implement CapabilityPermit.audit")
