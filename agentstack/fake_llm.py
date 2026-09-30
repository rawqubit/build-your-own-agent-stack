"""Recorded model. Given. Do not edit.

Replays a script. Does not read the network or an API key.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class FakeLLM:
    def __init__(
        self,
        script: list[dict[str, Any]] | None = None,
        *,
        path: str | None = None,
    ):
        if script is None:
            if not path:
                raise ValueError("FakeLLM needs a script or a path")
            script = json.loads(Path(path).read_text(encoding="utf-8"))
        self.script = list(script)
        self.calls = 0

    def complete(self, messages: list[dict[str, Any]] | None = None) -> dict[str, Any]:
        if self.calls >= len(self.script):
            return {
                "content": "",
                "model": "fake-small",
                "usage": {"input_tokens": 0, "output_tokens": 0},
                "tool_calls": [],
            }
        step = dict(self.script[self.calls])
        self.calls += 1
        return step
