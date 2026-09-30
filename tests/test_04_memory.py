"""04 — durable memory. Recall is not invention."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from agentstack.memory import FileMemory

ROOT = Path(__file__).resolve().parents[1]


def test_retain_then_recall_scores_the_match(tmp_path):
    memory = FileMemory(str(tmp_path / "mem.json"))
    memory.retain("favorite_color", "blue", namespace="user", source="prior")
    hits = memory.recall("favorite color", namespace="user")
    assert len(hits) == 1
    assert hits[0].key == "favorite_color"
    assert hits[0].value == "blue"
    assert hits[0].namespace == "user"
    assert hits[0].source == "prior"
    assert hits[0].score == 1.0


def test_a_second_process_sees_the_same_fact(tmp_path):
    path = tmp_path / "mem.json"
    FileMemory(str(path)).retain("favorite_color", "blue", namespace="user", source="prior")
    code = """
import os, sys
root, scripts, store = sys.argv[1:]
sys.path[:0] = [root, scripts]
if os.environ.get("AGENTSTACK_PEEK") == "1":
    import peek
    peek.install()
from agentstack.memory import FileMemory
hits = FileMemory(store).recall("favorite color", namespace="user")
if len(hits) != 1 or hits[0].value != "blue" or hits[0].source != "prior":
    raise SystemExit(repr(hits))
"""
    proc = subprocess.run(
        [sys.executable, "-c", code, str(ROOT), str(ROOT / "scripts"), str(path)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert proc.returncode == 0, proc.stderr or proc.stdout


def test_a_new_instance_sees_the_same_fact(tmp_path):
    path = str(tmp_path / "mem.json")
    FileMemory(path).retain("favorite_color", "blue", namespace="user")
    hits = FileMemory(path).recall("blue", namespace="user")
    assert [hit.value for hit in hits] == ["blue"]


def test_forget_stays_forgotten(tmp_path):
    path = str(tmp_path / "mem.json")
    first = FileMemory(path)
    first.retain("favorite_color", "blue", namespace="user")
    assert first.forget("favorite_color", namespace="user") is True
    assert first.forget("favorite_color", namespace="user") is False
    assert FileMemory(path).recall("color", namespace="user") == []
    assert FileMemory(path).reflect(namespace="user") == "unknown"


def test_namespaces_do_not_leak(tmp_path):
    memory = FileMemory(str(tmp_path / "mem.json"))
    memory.retain("favorite_color", "blue", namespace="user")
    assert memory.recall("color", namespace="system") == []
    assert memory.reflect(namespace="system") == "unknown"
    assert "favorite_color=blue" in memory.reflect(namespace="user")


def test_empty_store_does_not_invent(tmp_path):
    memory = FileMemory(str(tmp_path / "mem.json"))
    assert memory.recall("favorite color", namespace="user") == []
    assert memory.recall("", namespace="user") == []
    assert memory.reflect(namespace="user") == "unknown"


def test_recall_orders_by_score_and_respects_k(tmp_path):
    memory = FileMemory(str(tmp_path / "mem.json"))
    memory.retain("color", "blue", namespace="user")
    memory.retain("favorite_color", "blue", namespace="user")
    hits = memory.recall("favorite color", namespace="user", k=1)
    assert [hit.key for hit in hits] == ["favorite_color"]


def test_retain_overwrites_the_same_key(tmp_path):
    memory = FileMemory(str(tmp_path / "mem.json"))
    memory.retain("favorite_color", "blue", namespace="user")
    memory.retain("favorite_color", "green", namespace="user", source="edit")
    hits = memory.recall("color", namespace="user")
    assert len(hits) == 1
    assert hits[0].value == "green"
    assert hits[0].source == "edit"


def test_reflect_lists_only_stored_facts_sorted(tmp_path):
    memory = FileMemory(str(tmp_path / "mem.json"))
    memory.retain("zeta", "1", namespace="user")
    memory.retain("alpha", "2", namespace="user")
    assert memory.reflect(namespace="user") == "alpha=2\nzeta=1"
