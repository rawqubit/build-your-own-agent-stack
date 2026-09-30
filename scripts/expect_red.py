#!/usr/bin/env python3
"""Exit 0 only when every exam file fails on the student stubs."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    env = os.environ.copy()
    env.pop("AGENTSTACK_PEEK", None)
    leaked = False
    files = sorted((ROOT / "tests").glob("test_*.py"))
    if not files:
        print("no tests found")
        return 1
    for path in files:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(path), "-q"],
            cwd=ROOT,
            env=env,
        )
        if proc.returncode == 0:
            print(f"green {path.name} — stubs must stay red on clone")
            leaked = True
        else:
            print(f"red   {path.name}")
    return 1 if leaked else 0


if __name__ == "__main__":
    raise SystemExit(main())
