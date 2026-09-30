#!/usr/bin/env python3
"""Fail unless every published version string is the one in VERSION."""

from __future__ import annotations

import ast
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SEMVER = re.compile(r"^[0-9]+\.[0-9]+\.[0-9]+$")
PITCH = "Six weekend projects. Failing tests. No LangChain."


def main() -> int:
    version = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
    errors: list[str] = []
    if not SEMVER.fullmatch(version):
        errors.append(f"VERSION is not major.minor.patch: {version!r}")

    module = ast.parse((ROOT / "agentstack" / "_version.py").read_text(encoding="utf-8"))
    found = None
    for node in module.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == "__version__":
                    if isinstance(node.value, ast.Constant) and isinstance(node.value.value, str):
                        found = node.value.value
    if found != version:
        errors.append(f"agentstack/_version.py has {found!r}, VERSION has {version!r}")

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    if f"## [{version}]" not in changelog:
        errors.append(f"CHANGELOG.md is missing ## [{version}]")

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    if f"version: {version}\n" not in citation:
        errors.append(f"CITATION.cff version is not {version}")
    if f"abstract: {PITCH}\n" not in citation:
        errors.append("CITATION.cff abstract is not the pitch")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if PITCH not in readme:
        errors.append("README.md is missing the pitch")
    if f"contract-{version}" not in readme:
        errors.append(f"README.md badge does not name contract-{version}")
    if f"build_your_own_agent_stack-{version}.tar.gz" not in readme:
        errors.append("README.md does not name the sdist")
    if f"build_your_own_agent_stack-{version}-py3-none-any.whl" not in readme:
        errors.append("README.md does not name the wheel")

    project = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
    if f'description = "{PITCH}"' not in project:
        errors.append("pyproject.toml description is not the pitch")
    if 'dynamic = ["version"]' not in project:
        errors.append('pyproject.toml must declare dynamic = ["version"]')
    if re.search(r'(?m)^version\s*=\s*"', project):
        errors.append("pyproject.toml must not pin a second version string")

    sys.path.insert(0, str(ROOT))
    import agentstack

    if agentstack.__version__ != version:
        errors.append(f"import agentstack.__version__ is {agentstack.__version__!r}")

    if errors:
        print("version check failed")
        for error in errors:
            print(f"  {error}")
        return 1
    print(f"version {version} matches VERSION, package, changelog, citation, and README")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
