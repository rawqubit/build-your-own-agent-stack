# Trace scripts

Schema: `trace-script/v1`.

`FakeLLM` replays a JSON list. Each step is one model turn. There is no network call and no API key.

| Field | Type | Required |
|---|---|---|
| `content` | string | yes |
| `model` | string | yes |
| `usage.input_tokens` | integer | yes |
| `usage.output_tokens` | integer | yes |
| `tool_calls` | array | yes |

Each tool call has `name` (string) and `arguments` (object). An empty `tool_calls` array ends the loop after that turn.

| File | What it is |
|---|---|
| `capstone.json` | read `src/app.py`, then `.env`, then a final answer |
| `rm_attempt.json` | a `bash` call whose command is `rm -rf /` |
| `unknown_then_add.json` | an unknown tool name, then another call |
| `waste_reads.json` | the same `read` twice |

The loop prices `usage` with the `SpendMeter` table. It does not trust a cost field inside the script.
