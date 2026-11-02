# ADR-0003: One additive, explainable retrieval score

- **Status:** Accepted
- **Date:** 2026-11-01

## Context
Lexical search finds exact names ("Neovim", "Lisbon") but misses morphology and paraphrase.
Embedding search finds related wording but also returns plausible but wrong neighbors. Neither
knows whether a memory is recent or important. Callers (and the model reading the results) need
to know *why* something was retrieved in order to trust it.

## Decision
Score each candidate with a weighted sum of four terms in `[0, 1]`:

```
score = w_lex * L + w_sem * S + w_rec * R + w_imp * I
```

- `L`: FTS5 BM25 divided by the best BM25 among the query's candidates.
- `S`: cosine similarity of embeddings, clipped at 0.
- `R`: `2 ** (-age / half_life)` on the time the evidence was last observed.
- `I`: importance, multiplied by confidence for facts.

Default weights are 0.40, 0.30, 0.15, 0.15, chosen a priori (lexical first, semantic second,
priors last). Candidates come only from channels with positive weight. Each result carries the
four raw terms, the matched query terms, and a sentence naming the largest contribution.

## Alternatives considered
- **Reciprocal rank fusion.** Few parameters, but it discards score magnitudes and
  has no natural place for recency and importance, and its output is harder to explain.
- **A learned ranker.** Better with labeled data, which a fresh memory store does not have.
- **Multiplicative recency decay.** Makes very old but exact matches unreachable; additive terms
  degrade gracefully.

## Consequences
- The score is easy to explain and to ablate; the benchmark removes each term in turn.
- The benchmark shows that on its synthetic data BM25 alone matches the hybrid and that recency
  hurts, because supersession already handles currentness. A grid search on held-out seeds picks
  `lexical=0.15, importance=0.15`. We keep the a priori defaults (synthetic questions share far
  more vocabulary with the evidence than real conversations do) and document how to override them.
