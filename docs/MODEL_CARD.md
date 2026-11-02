# Model Card: extractors and embedder

Agent Memory ships no trained neural model. This card describes the components that play a model's
role: the fact extractors and the embedder.

## Components
- **`RuleExtractor` (default).** Deterministic regular-expression patterns over first-person
  sentences: preferences ("my favorite X is Y", "I prefer Y for my X", "for X, I use Y"),
  biography ("I live in", "I moved to", "I work at", "I joined", "my name is"), multi-valued facts
  (allergies, languages, pets), and instructions ("please answer in", "use metric units").
  Confidence is 0.9 by default, 0.95 with update cues ("actually", "switched", "now"), and 0.5
  with hedges ("maybe", "I think"). Assistant turns are ignored.
- **`LLMExtractor`.** Sends one turn to a `Provider` with a fixed system prompt and parses a JSON
  list of facts and preferences; malformed replies yield an empty extraction and are counted.
  `AnthropicProvider` calls the Claude Messages API (`ANTHROPIC_MODEL`, default
  `claude-sonnet-4-5`); `FakeProvider` is offline and deterministic for tests.
- **`HashingEmbedder`.** Signed feature hashing (BLAKE2b) of word unigrams (weight 1.0), word
  bigrams (0.5), and character trigrams (0.35) into 256 dimensions, L2-normalized.

## Intended use
Personal and agent memory for assistants, coding agents, and chat applications, running locally.

## Performance
On the synthetic benchmark the rule extractor recovers every scripted statement and ignores every
scripted distractor, because the generator's phrasings are within its patterns. This is **not** an
estimate of recall on real conversations. The `LLMExtractor` path has been exercised only with the
offline fake provider in this repository.

## Limitations
- The rule extractor misses implicit statements ("ugh, Vim again, I miss VS Code"), negations
  ("I no longer drink coffee"), and third-person facts about the user.
- The hashing embedder relates shared stems and spellings, not meanings: "food" and "cuisine" have
  near-zero similarity.
- An LLM extractor can hallucinate facts; confidence values it returns are not calibrated.

## Ethical considerations
Memory systems store personal data by design. Namespaces isolate users, export and `forget` give
users control, and nothing leaves the machine unless an LLM provider is configured, in which case
each turn is sent to that provider for extraction.
