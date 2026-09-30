#!/usr/bin/env python3
"""Print which chapter test files are currently passing."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CHAPTERS = [
    ("01 tools", "tests/test_01_tools.py"),
    ("02 sandbox", "tests/test_02_sandbox.py"),
    ("03 permissions", "tests/test_03_permissions.py"),
    ("04 memory", "tests/test_04_memory.py"),
    ("05 spend", "tests/test_05_spend.py"),
    ("06 evals", "tests/test_06_evals.py"),
    ("capstone", "tests/test_capstone.py"),
]


def main() -> int:
    print("Build Your Own Agent Stack — progress")
    print()
    passed_all = True
    for name, path in CHAPTERS:
        proc = subprocess.run(
            [sys.executable, "-m", "pytest", str(ROOT / path), "-q"],
            cwd=ROOT,
            capture_output=True,
            text=True,
        )
        ok = proc.returncode == 0
        passed_all = passed_all and ok
        mark = "green" if ok else "red  "
        print(f"  {mark}  {name}")
    print()
    return 0 if passed_all else 1


if __name__ == "__main__":
    raise SystemExit(main())
