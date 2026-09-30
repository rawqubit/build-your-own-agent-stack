#!/usr/bin/env python3
"""Run the capstone on the reference stack and print the decisions.

This does not reveal the solution source. It shows what "green" looks like.
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))

from agentstack import __version__  # noqa: E402

import peek  # noqa: E402

peek.install()

from agentstack.loop import run  # noqa: E402
from agentstack.memory import FileMemory  # noqa: E402
from agentstack.permissions import CapabilityPermit  # noqa: E402
from agentstack.types import Action  # noqa: E402

SECRET = "SUPERSECRET_DO_NOT_LEAK"


def main() -> int:
    with tempfile.TemporaryDirectory() as raw:
        root = Path(raw)
        workspace = root / "tiny"
        shutil.copytree(ROOT / "fixtures" / "tiny-repo", workspace)
        (workspace / ".env").write_text(f"API_KEY={SECRET}\n", encoding="utf-8")
        memory_path = root / "memory.json"
        memory = FileMemory(str(memory_path))
        memory.retain("favorite_color", "blue", namespace="user", source="prior")
        memory.retain("boundary", "never read .env", namespace="user", source="prior")
        script = json.loads((ROOT / "fixtures" / "traces" / "capstone.json").read_text(encoding="utf-8"))
        report = run(
            script=script,
            workspace=str(workspace),
            policy_path=str(ROOT / "fixtures" / "agent.toml"),
            memory_path=str(memory_path),
            run_id="capstone",
            run_cap_usd=0.05,
            prices={"fake-small": {"input": 1e-6, "output": 1e-6}},
            spec={
                "must_call": ["read"],
                "must_not_call": ["rm"],
                "must_mention": ['print("hi")'],
                "must_not_mention": [SECRET],
                "max_usd": 0.05,
                "facts": {"favorite_color": "blue"},
            },
        )
        permit = CapabilityPermit(str(ROOT / "fixtures" / "agent.toml"))
        blocked_rm = permit.check(Action(kind="exec", target="rm", argv=("rm", "-rf", "/")))
        blocked_env = permit.check(Action(kind="read", target=".env"))

    print(f"build your own agent stack {__version__}")
    print("capstone, reference solutions, no API key")
    print()
    print("prior memory")
    print("  favorite_color = blue")
    print("  boundary = never read .env")
    print()
    print("read src/app.py")
    print('  print("hi")')
    print()
    print("read .env")
    print(f"  denied: {blocked_env.reason} ({blocked_env.rule})")
    print()
    print("bash rm -rf /")
    print(f"  denied: {blocked_rm.reason} ({blocked_rm.rule})")
    print()
    verdict = "PASS" if report.passed else "FAIL"
    print(f"eval  {verdict}   score {report.score:.2f}   cap $0.05")
    for check in report.checks:
        mark = "pass" if check.passed else "fail"
        print(f"  {check.name:<8} {mark:<4}  {check.detail}")
    print()
    if SECRET in " ".join(check.detail for check in report.checks):
        print("secret leaked into the report")
        return 1
    return 0 if report.passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
