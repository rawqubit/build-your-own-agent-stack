"""Given agent loop. Do not edit.

Calls the six modules you implement. The capstone is ``run``.
"""

from __future__ import annotations

import shlex
from typing import Any

from agentstack.fake_llm import FakeLLM
from agentstack.types import Action, SpendEvent, TraceEvent

_READ = (
    "import pathlib, sys\n"
    "sys.stdout.write(pathlib.Path(sys.argv[1]).read_text())\n"
)


def run(
    *,
    script: list[dict[str, Any]],
    workspace: str,
    policy_path: str,
    memory_path: str,
    run_id: str = "run",
    model: str = "fake-small",
    prices: dict[str, dict[str, float]] | None = None,
    run_cap_usd: float = 1.0,
    spec: dict[str, Any] | None = None,
    namespace: str = "user",
):
    from agentstack.evals import TraceEvaluator
    from agentstack.memory import FileMemory
    from agentstack.permissions import CapabilityPermit
    from agentstack.sandbox import WorkspaceSandbox
    from agentstack.spend import SpendMeter
    from agentstack.tools import ToolBelt
    from agentstack.types import ToolSpec

    prices = prices or {"fake-small": {"input": 1e-7, "output": 1e-7}}
    llm = FakeLLM(script)
    sandbox = WorkspaceSandbox(workspace, allowed_bins=["python3", "cat", "ls", "pytest"])
    permit = CapabilityPermit(policy_path)
    memory = FileMemory(memory_path)
    meter = SpendMeter(prices=prices, run_cap_usd=run_cap_usd)
    belt = ToolBelt()

    def read(path: str) -> str:
        decision = permit.check(Action(kind="read", target=path))
        if not decision.allow:
            return f"denied: {decision.reason}"
        result = sandbox.run(["python3", "-c", _READ, path], cwd=workspace)
        if result.blocked or result.timed_out or result.exit_code != 0:
            return f"denied: {result.block_reason or result.stderr or 'read failed'}"
        return result.stdout

    def bash(command: str) -> str:
        argv = tuple(shlex.split(command))
        target = argv[0] if argv else command
        decision = permit.check(Action(kind="exec", target=target, argv=argv))
        if not decision.allow:
            return f"denied: {decision.reason}"
        result = sandbox.run(list(argv), cwd=workspace)
        if result.blocked or result.timed_out:
            return f"denied: {result.block_reason or 'timeout'}"
        return result.stdout if result.exit_code == 0 else result.stderr

    belt.register(ToolSpec("read", "Read a workspace file", _params("path")), read)
    belt.register(ToolSpec("bash", "Run one command", _params("command")), bash)

    trace = [TraceEvent(role="memory", content=memory.reflect(namespace=namespace))]
    for _ in range(8):
        step = llm.complete([])
        usage = step.get("usage") or {}
        chosen = step.get("model") or model
        usd = meter.price_model(
            chosen,
            int(usage.get("input_tokens") or 0),
            int(usage.get("output_tokens") or 0),
        )
        if not meter.allow(run_id, usd):
            trace.append(TraceEvent(role="system", content="budget stop"))
            break
        meter.record(
            SpendEvent(
                kind="model",
                run_id=run_id,
                usd=usd,
                tokens_in=int(usage.get("input_tokens") or 0),
                tokens_out=int(usage.get("output_tokens") or 0),
                model=chosen,
            )
        )
        calls = step.get("tool_calls") or []
        trace.append(TraceEvent(role="assistant", content=step.get("content") or "", cost_usd=usd))
        if not calls:
            break
        for call in calls:
            name = str(call.get("name") or "")
            args = dict(call.get("arguments") or {})
            result = belt.call(name, args)
            note = str(args.get("path") or args.get("command") or "")
            trace.append(
                TraceEvent(
                    role="tool",
                    content=result.content if result.ok else (result.error or ""),
                    tool=name,
                    tool_args=args,
                    path=args.get("path") if isinstance(args.get("path"), str) else None,
                )
            )
            if meter.allow(run_id, 0.0):
                meter.record(SpendEvent(kind="tool", run_id=run_id, usd=0.0, tool=name, note=note))
    return TraceEvaluator().score(trace, spec or {})


def _params(field: str) -> dict[str, Any]:
    return {
        "type": "object",
        "required": [field],
        "properties": {field: {"type": "string"}},
        "additionalProperties": False,
    }
