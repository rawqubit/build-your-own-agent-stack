"""Install PEEK solutions over the student package."""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
_INSTALLED = False


def install() -> None:
    global _INSTALLED
    if _INSTALLED:
        return
    import agentstack.evals as evals
    import agentstack.memory as memory
    import agentstack.permissions as permissions
    import agentstack.sandbox as sandbox
    import agentstack.spend as spend
    import agentstack.tools as tools

    tools.ToolBelt = _load("solutions_tools", "tools.py").ToolBelt
    sandbox.WorkspaceSandbox = _load("solutions_sandbox", "sandbox.py").WorkspaceSandbox
    permissions.CapabilityPermit = _load("solutions_permissions", "permissions.py").CapabilityPermit
    memory.FileMemory = _load("solutions_memory", "memory.py").FileMemory
    spend.SpendMeter = _load("solutions_spend", "spend.py").SpendMeter
    evals.TraceEvaluator = _load("solutions_evals", "evals.py").TraceEvaluator
    _INSTALLED = True


def _load(alias: str, filename: str):
    path = ROOT / "solutions" / filename
    spec = importlib.util.spec_from_file_location(alias, path)
    if spec is None or spec.loader is None:
        raise ImportError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
