# ADR-0002: Three memory kinds in one SQLite file, namespace on every row

- **Status:** Accepted
- **Date:** 2026-11-01

## Context
An agent needs to remember what was said (episodes), what is true about the user (facts), and how
the user wants to be treated (preferences). These have different shapes and lifecycles: episodes
are append-only and eventually forgotten, facts are versioned, preferences are overwritten with
provenance. The tool must run locally with no server, survive restarts, and keep users apart.

## Decision
- Store all three kinds in one SQLite database. A `memories` table holds the shared columns
  (namespace, kind, text, timestamps, importance, access counters, status); `episodes`, `facts`,
  and `preferences` hold the kind-specific columns and reference it with `ON DELETE CASCADE`.
- Index `memories.text` with an external-content **FTS5** table (Porter stemming), kept in sync by
  triggers, for BM25 lexical search.
- Store one float32 embedding per memory in a `vectors` table and search it by brute-force cosine
  similarity with numpy, cached per namespace and invalidated on write.
- Require a validated namespace on every store method and filter every query on it.
- Export and import a namespace as versioned JSON (`agent-memory/v1`), remapping identifiers and
  preserving supersession links.

## Alternatives considered
- **A vector database plus a relational database.** Better at very large scale, but two services
  to run and keep consistent, for a tool meant to be installed with `pip`.
- **A separate database file per namespace.** Strong isolation, but harder to manage and to query
  across namespaces for administration; row-level filtering is simpler and tested.
- **The `sqlite-vec` extension.** Faster vector search, but a native extension that is not always
  loadable from the system SQLite. Brute force is fast enough at the sizes measured.

## Consequences
- One file to back up, copy, or delete; works anywhere Python's `sqlite3` has FTS5.
- Deleting a memory removes its lexical and vector entries in the same transaction.
- FTS5 computes BM25 statistics over the whole table, so other namespaces can shift scores
  slightly (never content). Recorded in the threat model.
- Brute-force vector search is linear in namespace size (measured p95 under 10 ms at 6,600
  memories); an approximate index is on the roadmap.
