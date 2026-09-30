"""02 — workspace jail. Paths, binaries, time, and env."""

from __future__ import annotations

import os

from agentstack.sandbox import WorkspaceSandbox


def _box(tmp_path, **kwargs) -> WorkspaceSandbox:
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    (workspace / "src").mkdir()
    (workspace / "src" / "app.py").write_text('print("hi")\n', encoding="utf-8")
    return WorkspaceSandbox(str(workspace), allowed_bins=["python3", "cat", "ls"], **kwargs)


def test_empty_command_is_blocked(tmp_path):
    box = _box(tmp_path)
    result = box.run([], cwd=box.workspace)
    assert result.blocked is True
    assert result.block_reason == "empty command"
    assert result.exit_code == 126
    assert result.stdout == ""
    assert result.stderr == ""
    assert result.bytes_written == 0


def test_unset_allow_list_still_runs_a_local_binary(tmp_path):
    box = WorkspaceSandbox(str(tmp_path / "workspace"))
    result = box.run(["ls"], cwd=box.workspace)
    assert result.blocked is False
    assert result.exit_code == 0


def test_reads_a_file_inside_the_workspace(tmp_path):
    box = _box(tmp_path)
    result = box.run(
        ["python3", "-c", "import pathlib,sys; sys.stdout.write(pathlib.Path(sys.argv[1]).read_text())", "src/app.py"],
        cwd=box.workspace,
    )
    assert result.blocked is False
    assert result.exit_code == 0
    assert 'print("hi")' in result.stdout
    assert result.timed_out is False


def test_counts_bytes_written_inside_the_workspace(tmp_path):
    box = _box(tmp_path)
    result = box.run(
        ["python3", "-c", "open('note.txt','w').write('hello')"],
        cwd=box.workspace,
    )
    assert result.exit_code == 0
    assert result.bytes_written >= 5
    assert (tmp_path / "workspace" / "note.txt").read_text(encoding="utf-8") == "hello"


def test_shell_metacharacters_are_not_interpreted(tmp_path):
    box = _box(tmp_path)
    result = box.run(["python3", "-c", "print('a && b')"], cwd=box.workspace)
    assert result.exit_code == 0
    assert "a && b" in result.stdout


def test_parent_escape_is_blocked(tmp_path):
    secret = tmp_path / "secret.txt"
    secret.write_text("top-secret", encoding="utf-8")
    box = _box(tmp_path)
    result = box.run(["python3", "-c", "print(1)", "../secret.txt"], cwd=box.workspace)
    assert result.blocked is True
    assert result.block_reason == "path outside workspace"
    assert result.exit_code == 126
    assert "top-secret" not in result.stdout
    assert secret.read_text(encoding="utf-8") == "top-secret"


def test_absolute_path_outside_is_blocked_and_not_created(tmp_path):
    box = _box(tmp_path)
    target = tmp_path / "outside.txt"
    result = box.run(
        ["python3", "-c", f"open({str(target)!r},'w').write('x')"],
        cwd=box.workspace,
    )
    assert result.blocked is True
    assert result.block_reason == "path outside workspace"
    assert not target.exists()


def test_passwd_read_hidden_in_code_is_blocked(tmp_path):
    box = _box(tmp_path)
    result = box.run(
        ["python3", "-c", "print(open('/etc/passwd').read())"],
        cwd=box.workspace,
    )
    assert result.blocked is True
    assert "root:" not in result.stdout


def test_ssh_key_shape_is_denied(tmp_path):
    box = _box(tmp_path)
    result = box.run(["python3", "-c", "print(1)", "~/.ssh/id_rsa"], cwd=box.workspace)
    assert result.blocked is True
    assert result.block_reason == "ssh key denied"


def test_network_binary_is_denied_even_if_allow_listed(tmp_path):
    workspace = tmp_path / "workspace"
    box = WorkspaceSandbox(str(workspace), allowed_bins=["curl", "python3"])
    result = box.run(["curl", "https://example.com"], cwd=box.workspace)
    assert result.blocked is True
    assert result.block_reason == "network binary denied"


def test_binary_outside_the_allow_list_is_denied(tmp_path):
    box = _box(tmp_path)
    result = box.run(["rm", "-rf", box.workspace], cwd=box.workspace)
    assert result.blocked is True
    assert result.block_reason == "binary not in allow list"


def test_cwd_outside_the_workspace_is_denied(tmp_path):
    box = _box(tmp_path)
    result = box.run(["python3", "-c", "print(1)"], cwd=str(tmp_path))
    assert result.blocked is True
    assert result.block_reason == "cwd outside workspace"


def test_hung_process_dies_at_the_timeout(tmp_path):
    box = _box(tmp_path)
    result = box.run(
        ["python3", "-c", "import time; time.sleep(30)"],
        cwd=box.workspace,
        timeout_s=0.4,
    )
    assert result.timed_out is True
    assert result.blocked is False
    assert result.exit_code == 124


def test_parent_environment_is_not_inherited(tmp_path, monkeypatch):
    box = _box(tmp_path)
    monkeypatch.setenv("AGENTSTACK_PARENT", "from-parent")
    monkeypatch.setenv("AGENTSTACK_SECRET", "hunter2")
    result = box.run(
        [
            "python3",
            "-c",
            "import os; print(os.environ.get('AGENTSTACK_PARENT','')); print(os.environ.get('SAFE',''))",
        ],
        cwd=box.workspace,
        env={"SAFE": "ok", "AWS_SECRET_ACCESS_KEY": "nope"},
    )
    assert result.exit_code == 0
    assert "from-parent" not in result.stdout
    assert "hunter2" not in result.stdout
    assert "nope" not in result.stdout
    assert "ok" in result.stdout


def test_output_is_clipped(tmp_path):
    box = _box(tmp_path)
    result = box.run(
        ["python3", "-c", "print('x' * 1000)"],
        cwd=box.workspace,
        max_output_bytes=32,
    )
    assert result.exit_code == 0
    assert len(result.stdout.encode("utf-8")) <= 32
