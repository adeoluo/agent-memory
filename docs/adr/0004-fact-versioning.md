# ADR-0004: Reinforce, add, supersede, or contest; never delete history on write

- **Status:** Accepted
- **Date:** 2026-11-01

## Context
Users restate facts, change their minds, hedge, and sometimes information arrives out of order
(an import, or a delayed batch). A memory that overwrites in place cannot answer "what did I use
before?" and one that only appends returns contradictory facts with equal weight.

## Decision
Facts are keyed by `(subject, predicate)`. For each candidate:

1. **Reinforce** an active fact with the same normalized object: combine confidences as
   independent evidence, `1 - (1 - c_old)(1 - c_new)`, increment the evidence count, and move the
   last-observed time forward.
2. **Add** alongside existing values when the predicate is multi-valued (`allergic_to`,
   `has_pet`, `speaks`, and others; configurable).
3. **Supersede** the current value when the candidate is at least as new and
   `c_new + margin >= c_old` (margin 0.2), or when it is older but more confident by at least the
   margin. The old row becomes `superseded` and points to its replacement.
4. Otherwise store the candidate as **contested** (newer but much weaker, such as a hedged
   "maybe I prefer Emacs") or as **superseded** history (older and not stronger).

Preferences follow the same pattern without confidence: the newest explicit value wins and older
values are kept as superseded history with their provenance.

## Consequences
- Default retrieval sees only active facts, so "current" questions do not surface stale values.
- `fact_history` and `recall(include_history=True)` answer temporal questions.
- A hedge cannot silently overwrite a confident statement, and the hedge is still recorded.
- History grows with every change; `ForgettingSettings.forget_superseded_facts` can prune it.
