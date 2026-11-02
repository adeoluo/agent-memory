# Changelog

## v0.1.0 (2026-11-01)

First release.

- Episodic, semantic, and procedural memory in SQLite with FTS5 and a vector table, isolated by
  namespace.
- Write path: deterministic rule extractor, pluggable LLM extractor (Claude provider and an
  offline fake), fact deduplication and versioning (reinforce, add, supersede, contest).
- Read path: hybrid score over BM25, hashing-embedding similarity, recency, and importance, with a
  per-result explanation.
- Consolidation: extractive session summaries and exponential-decay forgetting.
- Interfaces: Python API, `agent-memory` command line (`add`, `recall`, `consolidate`, `stats`,
  `facts`, `forget`, `export`, `import`, `benchmark`), and an MCP server (`agent-memory mcp`) with
  `remember`, `recall`, `forget`, and `list_facts`.
- Benchmark harness with a deterministic multi-session dataset, four memory conditions, a
  scoring-term ablation, development-seed weight tuning, and scaling measurements.
