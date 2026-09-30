#!/usr/bin/env python3
"""Fail unless the sdist is the exam and the wheel is the package."""

from __future__ import annotations

import tarfile
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

REQUIRED = (
    "VERSION",
    "CHANGELOG.md",
    "CITATION.cff",
    "README.md",
    "BENCHMARK.md",
    "LICENSE",
    "Makefile",
    "agentstack/_version.py",
    "agentstack/py.typed",
    "agentstack/loop.py",
    "agentstack/fake_llm.py",
    "tests/test_01_tools.py",
    "tests/test_capstone.py",
    "chapters/01-tools/README.md",
    "chapters/capstone/README.md",
    "solutions/tools.py",
    "solutions/sandbox.py",
    "fixtures/agent.toml",
    "fixtures/traces/capstone.json",
    "fixtures/traces/README.md",
    "scripts/demo.py",
    "scripts/benchmark.py",
    "scripts/check_version.py",
)

PITCH = "Six weekend projects. Failing tests. No LangChain."


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    dist = ROOT / "dist"
    archives = sorted(dist.glob(f"build_your_own_agent_stack-{version}.tar.gz"))
    wheels = sorted(dist.glob(f"build_your_own_agent_stack-{version}-*.whl"))
    if len(archives) != 1:
        print(f"expected one sdist for {version}, found {[p.name for p in archives]}")
        return 1
    if len(wheels) != 1:
        print(f"expected one wheel for {version}, found {[p.name for p in wheels]}")
        return 1

    archive = archives[0]
    with tarfile.open(archive, "r:gz") as tar:
        names = tar.getnames()
    prefix = f"build_your_own_agent_stack-{version}/"
    missing = [item for item in REQUIRED if prefix + item not in names]
    if missing:
        print(f"{archive.name} is missing:")
        for item in missing:
            print(f"  {item}")
        return 1
    metadata = next(name for name in names if name.endswith("/PKG-INFO"))
    with tarfile.open(archive, "r:gz") as tar:
        info = tar.extractfile(metadata)
        if info is None:
            print("PKG-INFO is empty")
            return 1
        pkg = info.read().decode("utf-8")
    if f"Version: {version}\n" not in pkg:
        print("PKG-INFO Version does not match VERSION")
        return 1
    if f"Summary: {PITCH}\n" not in pkg:
        print("PKG-INFO Summary is not the pitch")
        return 1

    wheel = wheels[0]
    with zipfile.ZipFile(wheel) as bundle:
        wheel_names = bundle.namelist()
        meta = next(name for name in wheel_names if name.endswith(".dist-info/METADATA"))
        wheel_meta = bundle.read(meta).decode("utf-8")
    for relative in ("agentstack/_version.py", "agentstack/py.typed", "agentstack/loop.py"):
        if relative not in wheel_names:
            print(f"{wheel.name} is missing {relative}")
            return 1
    if f"Version: {version}\n" not in wheel_meta:
        print("wheel METADATA Version does not match VERSION")
        return 1
    if f"Summary: {PITCH}\n" not in wheel_meta:
        print("wheel METADATA Summary is not the pitch")
        return 1
    if any(name.startswith("tests/") or name.startswith("solutions/") for name in wheel_names):
        print("wheel must not ship the exam or the solutions")
        return 1

    print(f"{archive.name}")
    print(f"{wheel.name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
