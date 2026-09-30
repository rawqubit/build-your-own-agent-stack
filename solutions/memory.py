"""PEEK reference for 04 — memory."""

from __future__ import annotations

import json
import re
from pathlib import Path

from agentstack.types import MemoryHit


class FileMemory:
    def __init__(self, path: str):
        self.path = path
        store = Path(path)
        store.parent.mkdir(parents=True, exist_ok=True)
        if not store.exists():
            store.write_text("{}
", encoding="utf-8")

    def retain(self, key: str, value: str, *, namespace: str, source: str = "") -> None:
        data = self._load()
        data.setdefault(namespace, {})[key] = {"value": value, "source": source}
        self._save(data)

    def recall(self, query: str, *, namespace: str, k: int = 5) -> list[MemoryHit]:
        tokens = [part for part in re.split(r"[^a-z0-9]+", query.lower()) if part]
        if not tokens or k <= 0:
            return []
        hits: list[MemoryHit] = []
        for key, record in (self._load().get(namespace) or {}).items():
            value = str(record.get("value", ""))
            haystack = f"{key.replace('_', ' ')} {value}".lower()
            matched = sum(1 for token in tokens if token in haystack)
            if matched == 0:
                continue
            hits.append(
                MemoryHit(
                    key=key,
                    value=value,
                    score=matched / len(tokens),
                    namespace=namespace,
                    source=str(record.get("source", "")),
                )
            )
        hits.sort(key=lambda hit: (-hit.score, hit.key))
        return hits[:k]

    def forget(self, key: str, *, namespace: str) -> bool:
        data = self._load()
        bucket = data.get(namespace) or {}
        if key not in bucket:
            return False
        del bucket[key]
        data[namespace] = bucket
        self._save(data)
        return True

    def reflect(self, *, namespace: str) -> str:
        bucket = self._load().get(namespace) or {}
        if not bucket:
            return "unknown"
        lines = [f"{key}={bucket[key].get('value', '')}" for key in sorted(bucket)]
        return "\n".join(lines)

    def _load(self) -> dict:
        raw = Path(self.path).read_text(encoding="utf-8").strip()
        if not raw:
            return {}
        data = json.loads(raw)
        return data if isinstance(data, dict) else {}

    def _save(self, data: dict) -> None:
        path = Path(self.path)
        blob = json.dumps(data, indent=2, sort_keys=True) + "\n"
        temporary = path.with_suffix(path.suffix + ".tmp")
        temporary.write_text(blob, encoding="utf-8")
        temporary.replace(path)
