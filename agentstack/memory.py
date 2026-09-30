"""04 — Memory. Implement FileMemory."""

from __future__ import annotations

from agentstack.types import MemoryHit


class FileMemory:
    """Durable retain / recall / forget / reflect.

    Invariant: a fact written in process A is recalled in process B.
    Forgotten keys never come back. Empty store says unknown — it does
    not invent. Namespaces do not leak.
    """

    def __init__(self, path: str):
        self.path = path
        raise NotImplementedError("04-memory: implement FileMemory.__init__")

    def retain(self, key: str, value: str, *, namespace: str, source: str = "") -> None:
        raise NotImplementedError("04-memory: implement FileMemory.retain")

    def recall(self, query: str, *, namespace: str, k: int = 5) -> list[MemoryHit]:
        raise NotImplementedError("04-memory: implement FileMemory.recall")

    def forget(self, key: str, *, namespace: str) -> bool:
        raise NotImplementedError("04-memory: implement FileMemory.forget")

    def reflect(self, *, namespace: str) -> str:
        raise NotImplementedError("04-memory: implement FileMemory.reflect")
