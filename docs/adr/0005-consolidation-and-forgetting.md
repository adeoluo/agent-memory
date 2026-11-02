# ADR-0005: Summarize before forgetting; decay by importance and idle time

- **Status:** Accepted
- **Date:** 2026-11-01

## Context
Episodic memory grows linearly with conversation. Without bounds, storage and recall latency grow
with it and old small talk crowds the candidate pool. Forgetting must not destroy information
that has not been captured elsewhere.

## Decision
A consolidation pass, run on demand (`agent-memory consolidate`) or on a schedule:

1. Takes unconsolidated episodes older than `consolidate_after_days` (7), grouped by session.
2. Writes an extractive session summary as a semantic fact: the user sentences with the highest
   inverse sentence frequency weight. When write-time extraction is disabled, it also extracts and
   merges facts from those episodes.
3. Marks the episodes consolidated, then deletes consolidated episodes whose retention
   `importance * 2 ** (-idle / half_life) * (1 + 0.5 * ln(1 + accesses))` is below 0.05
   (half-life 30 days). `idle` counts from the last access, so retrieval refreshes a memory.

Only consolidated episodes are eligible. Active facts and preferences are never forgotten;
superseded fact history is forgotten only when explicitly enabled.

## Consequences
- Measured at 200 sessions: 78% fewer stored memories, 74% less disk, p95 recall latency 2.5 ms
  instead of 9.8 ms, equal accuracy.
- Raw wording of old turns is lost after forgetting; facts and summaries remain. Deleting
  episodes also changes BM25 corpus statistics, which can reorder near-tied results.
- Extractive summaries are deterministic and cheap; an LLM summarizer would be more fluent and is
  a natural extension through the provider interface.
