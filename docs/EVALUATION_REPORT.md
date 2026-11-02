# Evaluation Report

## Setup
- **Harness:** `agent_memory.evaluation.harness`, run by `benchmarks/run_benchmark.py` (`make evaluation`).
- **Data:** see the [data card](DATA_CARD.md). Test seeds 7, 8, 9; development seeds 101, 102 for
  weight tuning only.
- **Reader:** deterministic. It is told which attribute is asked about, extracts statements about
  it from what the memory condition shows (top 5 memories, or the truncated window), orders them by
  time, and answers with the latest value or the value before the latest change.
- **Metrics:** answer accuracy (overall, current, previous, paraphrased subset); recall@k, the share
  of questions where at least one of the top `k` memories states the gold value; ingest time per
  turn; recall latency p50 and p95; database size after `VACUUM`.
- **Hardware:** Apple silicon laptop, Python 3.11, in-memory SQLite. Accuracy is deterministic per
  seed; latency varies by machine.

## Results
See the [README](../README.md#results) for the tables and
[`benchmarks/results.md`](../benchmarks/results.md) for every column. Headline numbers (mean ±
standard deviation across three seeds):

| Condition | Accuracy |
|---|---|
| No memory | 0.172 ± 0.012 |
| Full-context truncation, 1,600 words | 0.573 ± 0.013 |
| Hybrid over raw episodes only | 0.597 ± 0.030 |
| Lexical only, full store | 0.974 ± 0.030 |
| Full hybrid, default weights | 0.957 ± 0.014 |
| Hybrid, weights tuned on development seeds | 0.981 ± 0.018 |

## Findings
1. Fact extraction with versioning is responsible for most of the gain (0.597 to 0.957).
2. On this data BM25 alone is as good as the default hybrid; the semantic and recency terms do not
   help on the full store and recency hurts on both stores. The semantic and importance terms help
   on the episodes-only store (+2.4 and +2.1 points).
3. Consolidation keeps storage and tail latency nearly flat as sessions grow (200 sessions: 2.6 MB
   versus 10.2 MB, p95 2.5 ms versus 9.8 ms) at equal accuracy.

## Threats to validity
- Synthetic templates overlap with the rule extractor's patterns.
- The reader is an oracle-parsed deterministic reader, not a language model.
- Three seeds give a rough spread, not tight confidence intervals.
- No comparison with other memory systems (Mem0, Zep, Letta) has been run.
