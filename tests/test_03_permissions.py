"""03 — default-deny capability policy."""

from __future__ import annotations

from pathlib import Path

from agentstack.permissions import CapabilityPermit
from agentstack.types import Action

ROOT = Path(__file__).resolve().parents[1]
POLICY = ROOT / "fixtures" / "agent.toml"


def _permit() -> CapabilityPermit:
    return CapabilityPermit(str(POLICY))


def test_src_read_is_allowed():
    decision = _permit().check(Action(kind="read", target="src/app.py"))
    assert decision.allow is True
    assert decision.rule == "fs.allow"
    assert decision.dry_run is False


def test_dot_slash_src_is_the_same_allow():
    decision = _permit().check(Action(kind="read", target="./src/app.py"))
    assert decision.allow is True


def test_env_is_a_secret_even_with_a_broad_shape():
    decision = _permit().check(Action(kind="read", target=".env"))
    assert decision.allow is False
    assert decision.rule == "secrets"
    nested = _permit().check(Action(kind="read", target="src/../.env"))
    assert nested.allow is False
    assert nested.rule == "secrets"


def test_undeclared_file_is_default_deny():
    decision = _permit().check(Action(kind="read", target="notes/todo.md"))
    assert decision.allow is False
    assert decision.reason == "default deny"
    assert decision.rule is None


def test_rm_is_denied_and_ls_is_allowed():
    permit = _permit()
    denied = permit.check(Action(kind="exec", target="rm", argv=("rm", "-rf", "/")))
    allowed = permit.check(Action(kind="exec", target="ls", argv=("ls",)))
    assert denied.allow is False
    assert denied.rule == "commands.deny"
    assert allowed.allow is True
    assert allowed.rule == "commands.allow"


def test_bin_rm_uses_the_executable_name():
    decision = _permit().check(Action(kind="exec", target="/bin/rm", argv=("/bin/rm", "-rf", "/")))
    assert decision.allow is False
    assert decision.rule == "commands.deny"


def test_unknown_command_is_default_deny():
    decision = _permit().check(Action(kind="exec", target="nc", argv=("nc",)))
    assert decision.allow is False
    assert decision.reason == "default deny"


def test_network_allow_list_empty_means_closed():
    decision = _permit().check(Action(kind="network", target="example.com"))
    assert decision.allow is False
    assert decision.reason == "default deny"


def test_dry_run_matches_and_writes_nothing():
    before = POLICY.stat().st_mtime_ns
    action = Action(kind="write", target=".env")
    permit = _permit()
    preview = permit.check(action, dry_run=True)
    live = permit.check(action, dry_run=False)
    assert preview.allow is False
    assert preview.allow == live.allow
    assert preview.reason == live.reason
    assert preview.dry_run is True
    assert live.dry_run is False
    assert POLICY.stat().st_mtime_ns == before
    assert [item.dry_run for item in permit.audit()] == [True, False]


def test_broad_allow_still_hides_secrets(tmp_path):
    policy = tmp_path / "agent.toml"
    policy.write_text(
        "\n".join(
            [
                "[fs]",
                'allow = ["**/*"]',
                "deny = []",
                "",
                "[commands]",
                "allow = []",
                "deny = []",
                "",
                "[network]",
                "allow = []",
                "",
                "[secrets]",
                'patterns = [".env", "*.pem", "id_rsa", "id_ed25519"]',
                "",
            ]
        ),
        encoding="utf-8",
    )
    permit = CapabilityPermit(str(policy))
    assert permit.check(Action(kind="read", target="src/app.py")).allow is True
    assert permit.check(Action(kind="read", target=".env")).rule == "secrets"
    assert permit.check(Action(kind="read", target="keys/id_rsa")).rule == "secrets"
    assert permit.check(Action(kind="read", target="cert.pem")).rule == "secrets"
    assert permit.check(Action(kind="read", target="README.md")).allow is True
