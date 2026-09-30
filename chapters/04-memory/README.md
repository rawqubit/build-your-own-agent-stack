# 04 — Memory

A fact written through one `FileMemory` is visible to the next one that opens the same path. A forgotten key stays gone. An empty store says `unknown`. It does not invent a biography.

## Build

`FileMemory` in `agentstack/memory.py`.

```python
FileMemory(path)  # create a JSON object if the file is missing
retain(key, value, *, namespace, source="") -> None
recall(query, *, namespace, k=5) -> list[MemoryHit]
forget(key, *, namespace) -> bool
reflect(*, namespace) -> str
```

`retain` on an existing key overwrites value and source. `forget` returns `True` only when the key was there.

## Recall

Lowercase the query and split it into `[a-z0-9]` tokens. Treat `_` in a key as a space. Score is the fraction of query tokens that appear in `key + value`. Drop scores of zero. Sort by score descending, then key. Return at most `k`. An empty query returns `[]`. Namespaces do not appear in each other's results.

`MemoryHit.score` for a full overlap is `1.0`.

## Reflect

If the namespace has no facts, return the string `unknown`. Otherwise one `key=value` line per fact, keys sorted, joined with `\n`.

Load from disk on every call so a second instance, and a second process, see the latest file.

## Run

```bash
pytest tests/test_04_memory.py
```
