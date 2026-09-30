# 01 — Tools

The model will name a function. Your registry decides whether that name is real.

## Build

`ToolBelt` in `agentstack/tools.py`.

- `register(spec, handler)` stores a `ToolSpec` and a callable.
- `call(name, args)` always returns a `ToolResult`. A bad call does not raise.
- `names()` returns registered names, sorted. Empty before the first register.

## Fail closed

| Input | Result |
|---|---|
| unknown name | `ok=False`, error contains `unknown tool` |
| `args` is not a dict | error is `arguments must be an object` |
| missing required field | error contains `missing required: <field>` |
| wrong JSON type | error contains `<field>: expected <type>` |
| extra field, and `additionalProperties` is false or omitted | error contains `unexpected argument: <field>` |
| handler raises | `ok=False`, error is `<ExceptionName>: <message>` |
| slower than `spec.timeout_s` | `timed_out=True`, error contains `timeout`. The call returns. It does not promise the handler thread has stopped |
| UTF-8 output longer than `max_result_bytes` | `ok=True`, `truncated=True`, content clipped to that many bytes |

`parameters` is a small JSON Schema: an object with `properties`, `required`, and types `string`, `integer`, `number`, `boolean`. `true` is not an integer. `1.5` is not an integer. `number` accepts both.

The handler is called as `handler(**args)`. `None` becomes an empty content string.

## Run

```bash
pytest tests/test_01_tools.py
```
