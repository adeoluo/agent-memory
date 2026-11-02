# Architecture

This document describes how Agent Memory is put together: the modules, the storage schema, the
write and read paths, consolidation, and the interfaces. Design rationale lives in the
[ADRs](adr/).

## System diagram

```mermaid
---
title: System Architecture - Agent Memory
config:
  theme: base
  themeVariables:
    fontFamily: "Inter, system-ui, sans-serif"
    primaryColor: "#F8FAFC"
    primaryBorderColor: "#1E293B"
    primaryTextColor: "#1E293B"
    lineColor: "#64748B"
    clusterBkg: "#EEF2FF"
    clusterBorder: "#94A3B8"
---
flowchart LR
    classDef edge     fill:#F59E0B,stroke:#1E293B,color:#1E293B,stroke-width:1px;
    classDef core     fill:#6366F1,stroke:#1E293B,color:#ffffff,stroke-width:1px;
    classDef data     fill:#10B981,stroke:#1E293B,color:#ffffff,stroke-width:1px;
    classDef control  fill:#0EA5E9,stroke:#1E293B,color:#ffffff,stroke-width:1px;
    classDef danger   fill:#FEE2E2,stroke:#EF4444,color:#1E293B,stroke-width:1px;

    Agent(["Agent or MCP client<br/>(Claude Desktop, VS Code)"]):::edge
    LLM[["Language model provider<br/>(Claude, or offline fake)"]]:::edge

    subgraph Interfaces["Interfaces (bound to one namespace)"]
        direction TB
        API["Python API<br/>AgentMemory"]:::core
        CLI["CLI<br/>add | recall | consolidate | stats"]:::core
        MCP["MCP server<br/>remember | recall | forget | list_facts"]:::core
    end

    subgraph Write["Write path"]
        direction TB
        Extract["Extractor<br/>rules (default) or LLM"]:::control
        Merge["Merge and resolve conflicts<br/>reinforce, add, supersede, contest"]:::control
    end

    subgraph Read["Read path: hybrid scorer"]
        direction TB
        Candidates["Candidates<br/>FTS5 BM25 + vector top-N"]:::core
        Score["Weighted score<br/>lexical, semantic,<br/>recency, importance<br/>+ explanation"]:::core
    end

    subgraph Maintenance["Consolidation job"]
        direction TB
        Summarize["Summarize old sessions<br/>into semantic facts"]:::core
        Forget["Forget by decay<br/>importance and idle time"]:::danger
    end

    subgraph Storage["SQLite (namespace column on every row)"]
        direction TB
        Episodic[("Episodic<br/>timestamped turns")]:::data
        Semantic[("Semantic<br/>facts + superseded history")]:::data
        Procedural[("Procedural<br/>preferences + provenance")]:::data
        Index[("FTS5 index<br/>+ vector table")]:::data
    end

    Agent --> MCP
    Agent --> API
    Agent --> CLI
    Interfaces -->|turn| Extract
    Extract -.->|prompt| LLM
    Extract -->|candidate facts| Merge
    Interfaces -->|episode| Episodic
    Merge --> Semantic
    Merge --> Procedural
    Interfaces -->|query| Candidates
    Index --> Candidates
    Candidates --> Score
    Score -->|memories + why| Interfaces
    Episodic --> Summarize --> Semantic
    Summarize --> Forget --> Episodic
```

A rendered copy is in [architecture/architecture.svg](architecture/architecture.svg).

## Modules

| Module | Responsibility |
|---|---|
| `models.py` | Frozen dataclasses for `Episode`, `Fact`, `Preference`, `RetrievedMemory`, `ScoreBreakdown`, and reports |
| `settings.py` | `MemorySettings`, `ScoringWeights`, `ForgettingSettings` with documented defaults |
| `text.py` | Tokenization, stopwords, value normalization, sentence splitting |
| `embedding.py` | `Embedder` protocol and the feature-hashing `HashingEmbedder` (numpy) |
| `extraction.py` | `Extractor` protocol, `RuleExtractor`, `LLMExtractor`, JSON parsing of model replies |
| `provider.py` | `Provider` protocol and `AnthropicProvider` (Claude Messages API over HTTPS) |
| `fake_provider.py` | Offline deterministic `FakeProvider` used by tests |
| `store.py` | SQLite schema, FTS5 and vector search, namespace validation and filtering |
| `merge.py` | Fact and preference deduplication and conflict resolution |
| `scoring.py` | The hybrid score, candidate generation, and explanations |
| `consolidation.py` | Session summaries, retention, forgetting |
| `memory.py` | `AgentMemory`, the namespace-scoped facade used by every interface |
| `cli.py` | `agent-memory` command line |
| `mcp_server.py` | MCP server built on the official `mcp` SDK |
| `evaluation/` | Synthetic dataset generator and benchmark harness |

Dependencies point one way: interfaces depend on `memory.py`, which depends on the store,
merger, scorer, and consolidation functions, which depend only on models, settings, text, and
embedding. There are no import cycles.

## Storage schema

```mermaid
erDiagram
    memories ||--o| episodes : "kind = episodic"
    memories ||--o| facts : "kind = semantic"
    memories ||--o| preferences : "kind = procedural"
    memories ||--o| vectors : embedding
    memories ||--|| memories_fts : "FTS5 external content"
    memories {
        int id PK
        text namespace
        text kind
        text text
        real created_at
        real importance
        int access_count
        real last_accessed
        text status
    }
    episodes {
        int memory_id PK
        text session_id
        text role
        int consolidated
    }
    facts {
        int memory_id PK
        text subject
        text predicate
        text object
        real confidence
        real updated_at
        int evidence_count
        int superseded_by
    }
    preferences {
        int memory_id PK
        text key
        text value
        text provenance
        int superseded_by
    }
    vectors {
        int memory_id PK
        blob embedding
    }
```

Triggers keep `memories_fts` in sync with `memories.text`; detail rows and vectors are removed by
`ON DELETE CASCADE`.

## Write path

```mermaid
sequenceDiagram
    participant C as Caller
    participant M as AgentMemory
    participant X as Extractor
    participant G as FactMerger
    participant S as MemoryStore
    C->>M: add_turn(text, role, session_id)
    M->>X: extract(text, role)
    X-->>M: candidate facts and preferences
    M->>S: insert episode (text, embedding, importance)
    loop each candidate fact
        M->>G: merge(candidate, observed_at)
        G->>S: active facts for (subject, predicate)
        G->>S: reinforce, add, supersede, or store as history
    end
    M-->>C: IngestResult (episode, facts, actions)
```

## Read path

1. Build an FTS5 query from the content tokens of the question and take the top candidates by
   BM25 within the namespace and the requested statuses.
2. Embed the question and take the top candidates by cosine similarity from the namespace's
   vectors.
3. For the union, compute the four terms (lexical, semantic, recency, importance), the weighted
   total, the matched terms, and an explanation.
4. Sort by total, return the top `k`, and record the access (used by forgetting).

## Consolidation

A pass selects unconsolidated episodes older than the threshold, writes one extractive summary
fact per session, marks the episodes consolidated, and deletes consolidated episodes whose
decayed retention is below the threshold. See [ADR-0005](adr/0005-consolidation-and-forgetting.md).

## Interfaces

- **Python:** `AgentMemory` and the types exported from `agent_memory`.
- **Command line:** `agent-memory add | recall | consolidate | stats | facts | forget | export |
  import | mcp | benchmark`.
- **MCP:** `agent-memory mcp` over standard input and output, bound to one namespace, with the
  tools `remember`, `recall`, `forget`, and `list_facts`.
