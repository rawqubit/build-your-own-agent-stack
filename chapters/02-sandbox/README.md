# 02 — Sandbox

This is a policy jail. It is not Firecracker, and it is not a production boundary. The exam is the policy: what you refuse to start.

## Build

`WorkspaceSandbox` in `agentstack/sandbox.py`.

```python
WorkspaceSandbox(workspace, allowed_bins=None)
run(argv, *, cwd=None, timeout_s=5.0, env=None, max_output_bytes=1_000_000) -> ExecResult
```

`argv` is executed directly. Do not pass it through a shell. `cwd` defaults to the workspace and must stay inside it. Create the workspace if it is missing.

## Refuse to start

Set `blocked=True`, `exit_code=126`, empty stdout/stderr, `bytes_written=0`, and one of these `block_reason` strings:

| Case | `block_reason` |
|---|---|
| no argv | `empty command` |
| basename is a network binary (`curl`, `wget`, `nc`, `ssh`, …) | `network binary denied` |
| `allowed_bins` is set and the basename is absent | `binary not in allow list` |
| `cwd` resolves outside the workspace | `cwd outside workspace` |
| an argument is `~…`, or a path that resolves outside the workspace, including one embedded in a `-c` string | `path outside workspace` |
| an argument names `.ssh`, `id_rsa`, or `id_ed25519` | `ssh key denied` |

Network binaries stay denied even when someone puts them in `allowed_bins`. `allowed_bins=None` means every non-network binary is eligible.

## After it starts

- Parent environment variables are not copied in. `PATH` may be kept so the binary can be found. Drop caller-supplied keys that look like secrets (`SECRET`, `TOKEN`, `PASSWORD`, `CREDENTIAL`, `API_KEY`, or a `_KEY` suffix).
- On timeout, kill the process, set `timed_out=True`, `exit_code=124`.
- Clip stdout and stderr to `max_output_bytes`.
- `bytes_written` is the total growth of files inside the workspace.

## Run

```bash
pytest tests/test_02_sandbox.py
```
