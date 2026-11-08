# AGENTS.md

Working notes for coding agents and contributors in **Agent Memory**. The [README](README.md)
explains what the project does and why; this file explains how to change it safely.

## Project

Long-term memory for AI agents: episodic, semantic, and procedural memory in SQLite, a write path that extracts and versions facts, a hybrid retriever that explains every result, a consolidation job that summarizes and forgets, and a Model Context Protocol server so it plugs into Claude Desktop or VS Code.

## Layout

- `benchmarks/`: benchmark scripts and recorded results
- `docker-compose.yml`: local container setup
- `docs/`: documentation, architecture diagram source and render, design records
- `scripts/`: maintenance scripts (release, assets, data)
- `src/`: library and service source
- `tests/`: test suite

Key modules:

- `src/agent_memory/__init__.py`: Long-term memory for AI agents.
- `src/agent_memory/cli.py`: Command-line interface: ``agent-memory add | recall | consolidate | stats | ...
- `src/agent_memory/consolidation.py`: Consolidation: summarize old episodes into semantic memory, then forget by decay.
- `src/agent_memory/embedding.py`: Embedding interface and a deterministic feature-hashing embedder built on numpy.
- `src/agent_memory/evaluation/__init__.py`: Benchmark harness and synthetic dataset.
- `src/agent_memory/evaluation/dataset.py`: Deterministic synthetic multi-session dialogue dataset with temporal ground truth.
- `src/agent_memory/evaluation/harness.py`: Benchmark harness: memory conditions, retrieval ablations, and scaling measurements.
- `src/agent_memory/extraction.py`: Candidate extraction: turn a conversation turn into candidate facts and preferences.
- `src/agent_memory/fake_provider.py`: Deterministic offline provider for tests and continuous integration.
- `src/agent_memory/mcp_server.py`: Model Context Protocol server exposing memory tools to MCP clients.
- `src/agent_memory/memory.py`: The public facade: a namespace-scoped long-term memory for one user or agent.
- `src/agent_memory/merge.py`: Write-path deduplication and conflict resolution for facts and preferences.
- `src/agent_memory/models.py`: Typed records for the three memory kinds and for retrieval results.
- `src/agent_memory/provider.py`: Language-model provider interface and a Claude implementation.
- `src/agent_memory/scoring.py`: The hybrid retrieval score and its per-result explanations.
- `src/agent_memory/settings.py`: Tunable settings for scoring, fact merging, consolidation, and forgetting.
- `src/agent_memory/store.py`: SQLite persistence: memories, FTS5 lexical index, vector table, and namespace isolation.
- `src/agent_memory/text.py`: Tokenization and normalization shared by extraction, embedding, and lexical search.

## Commands

| Command | Purpose |
|---|---|
| `make help` | Show this help |
| `make setup` | Install dependencies and pre-commit hooks |
| `make format` | Format automatically |
| `make lint` | Lint (no fixes) |
| `make type` | Type-check |
| `make test` | Run tests |
| `make coverage` | Tests with coverage gate |
| `make evaluation` | Reproduce the results tables (benchmarks/results.md) |
| `make run` | Serve the Model Context Protocol server on standard input and output |
| `make diagram` | Render architecture diagram to SVG |
| `make docker-build` | Build the image |
| `make docker-up` | Build and start the MCP server container |
| `make clean` | Remove caches and artifacts |
| `make all` | Full local gate (mirror of continuous integration) |
| `make build` | Build the wheel and source distribution into dist/ |
| `make changelog` | Regenerate CHANGELOG.md from Conventional Commits (git-cliff) |
| `make cut-release` | Cut a release locally: version bump, changelog, tag, GitHub release (RELEASE_VERSION=vX.Y.Z optional) |

Run the full local gate (`make all`) before committing; CI runs the same checks.

## Conventions

- Commits follow Conventional Commits (`feat:`, `fix:`, `perf:`, `refactor:`, `docs:`, `test:`, `ci:`, `chore:`).
  The changelog and the next version number are derived from them.
- Every number quoted in the README is produced by a command in this repository. When behavior
  changes, rerun that command and update the number in the same commit.
- When a component is added, removed or renamed, update `docs/architecture/architecture.mmd`
  and re-render `architecture.svg` so the diagram matches the code.
- README sections keep their fixed order. Prose avoids em and en dashes and promotional wording.
- Tests accompany behavior changes; a bug fix comes with a test that fails without it.
- Releases are cut with `make cut-release`.

## Python notes

- Python is managed with `uv`; run commands through `uv run` so the locked environment is used.
- Lint and format with `ruff`; type-check with `mypy`; tests use `pytest`.
- Public functions carry type hints and a docstring that states the contract, not the steps.
