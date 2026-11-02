# Threat Model

## Assets
Personal facts, preferences, and conversation history stored per namespace in a local SQLite file.

## Trust boundaries
1. The MCP client and the language model behind it (untrusted tool arguments).
2. Text being remembered (untrusted, may contain injected instructions).
3. The optional LLM provider used for extraction (third party).
4. The database file on disk.

## Threats and mitigations
| Threat | Mitigation |
|---|---|
| Cross-namespace read or delete through tool arguments | The MCP server is bound to one namespace at start-up; tools take no namespace argument; every SQL statement filters on namespace; tests cover lexical, vector, get, update, touch, and delete isolation |
| FTS5 query injection (operators such as `NEAR`, `*`, column filters) | Queries are reduced to alphanumeric tokens, each double-quoted and joined with `OR` |
| SQL injection | All values are bound parameters; namespaces are validated against a strict pattern |
| Prompt injection stored in memory and replayed to the model | Recalled memories are returned as data with kind, status, and explanation; clients should quote them as context, never as instructions |
| Resource exhaustion through `recall` | `k` is capped at 50 in the MCP server; candidate pools are bounded |
| Personal data sent to a third party | The default extractor is local; only `LLMExtractor` with a remote provider sends text out, and only when configured with an API key |
| Side channel through BM25 statistics | FTS5 document frequencies are table-wide, so other namespaces can slightly change scores (not content). Use one database file per user if this matters |
| Data at rest | The database is not encrypted; rely on disk encryption or file permissions. `forget` and `export` give users control over their data |
