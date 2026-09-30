# 03 — Permissions

Undeclared means no. Dry-run returns the same decision and changes nothing.

## Build

`CapabilityPermit` in `agentstack/permissions.py`. Load `agent.toml` in `__init__`.

```python
check(action, *, dry_run=False) -> Decision
audit() -> list[Decision]
```

`audit` returns every decision from this process, in order, including dry-runs.

## Kinds

| `action.kind` | Section | What is matched |
|---|---|---|
| `read`, `write`, `fs` | `[fs]` | the target path |
| `exec`, `command`, `commands` | `[commands]` | the executable basename (`argv[0]`, else the first token of `target`) |
| `network`, `net` | `[network]` | the target |

Anything else is default deny.

## Order

Normalize `./` and `..` before matching, so `src/../.env` is `.env`.

1. On filesystem actions, a `[secrets].patterns` hit denies with `reason="secret pattern"` and `rule="secrets"`. A pattern with no slash matches the file name, so `*.pem` matches `cert.pem`.
2. The section `deny` list denies with `reason="denied by policy"` and `rule="<section>.deny"`.
3. The section `allow` list allows with `reason="allowed by policy"` and `rule="<section>.allow"`.
4. Otherwise `reason="default deny"` and `rule=None`.

Globs understand `*`, `?`, and `**`. Deny beats allow. Secrets beat a broad `**/*`.

`dry_run=True` sets `decision.dry_run` and does not write the policy file. The allow bit matches a live check of the same action.

## Run

```bash
pytest tests/test_03_permissions.py
```

The fixture is `fixtures/agent.toml`.
