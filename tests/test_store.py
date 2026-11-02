from __future__ import annotations

from pathlib import Path

import pytest

from agent_memory import AgentMemory, HashingEmbedder
from agent_memory.models import Episode, Status
from agent_memory.store import MemoryStore, fts_query, validate_namespace

EMBED = HashingEmbedder()


def add(store: MemoryStore, namespace: str, text: str, at: float = 1.0) -> Episode:
    return store.insert_episode(
        namespace,
        text,
        session_id="s",
        role="user",
        created_at=at,
        importance=0.5,
        embedding=EMBED.embed(text),
    )


@pytest.mark.parametrize("namespace", ["", "a b", "x" * 129, "drop;table", "../etc"])
def test_invalid_namespaces_are_rejected(namespace: str) -> None:
    with pytest.raises(ValueError):
        validate_namespace(namespace)


def test_fts_query_is_quoted_and_safe() -> None:
    assert fts_query("the and of") is None
    query = fts_query('editor" OR NEAR(x) *')
    assert query is not None
    assert all(part.startswith('"') and part.endswith('"') for part in query.split(" OR "))
    store = MemoryStore()
    add(store, "a", 'weird "quoted" editor text')
    assert store.lexical_search("a", 'editor" OR *', 5, [Status.ACTIVE])


def test_namespaces_are_strictly_isolated() -> None:
    store = MemoryStore()
    secret = add(store, "bob", "bob's secret password is hunter2")
    add(store, "alice", "alice likes hunter2 crosswords")
    hits = store.lexical_search("alice", "secret password hunter2", 10, [Status.ACTIVE])
    assert secret.id not in {memory_id for memory_id, _ in hits}
    vector_hits = store.vector_search("alice", EMBED.embed("secret password"), 10)
    assert secret.id not in {memory_id for memory_id, _ in vector_hits}
    assert store.get("alice", secret.id) is None
    assert store.get_many("alice", [secret.id]) == {}
    deleted = store.delete("alice", [secret.id])
    assert deleted == 0
    store.set_status("alice", secret.id, Status.SUPERSEDED)
    store.touch("alice", [secret.id], 5.0)
    still = store.get("bob", secret.id)
    assert still is not None and still.status is Status.ACTIVE and still.access_count == 0
    with pytest.raises(KeyError):
        store.reinforce_fact("alice", secret.id, 0.9, 2.0)
    assert store.namespaces() == ["alice", "bob"]


def test_facade_isolation() -> None:
    alice = AgentMemory(namespace="alice")
    bob = alice.for_namespace("bob")
    alice.add_turn("My favorite editor is Emacs.")
    bob.add_turn("My favorite editor is Vim.")
    bob_hits = bob.recall("favorite editor Emacs", 10)
    assert bob_hits and all("Emacs" not in hit.text for hit in bob_hits)
    assert all("Vim" not in hit.text for hit in alice.recall("favorite editor Vim", 10))
    assert len(alice.facts()) == 1 and alice.facts()[0].object == "Emacs"
    alice_ids = [hit.id for hit in alice.recall("editor", 10)]
    assert not any(bob.forget(memory_id) for memory_id in alice_ids)


def test_delete_removes_lexical_and_vector_entries() -> None:
    store = MemoryStore()
    episode = add(store, "a", "temporary note about kayaks")
    assert store.lexical_search("a", "kayaks", 5, [Status.ACTIVE])
    assert store.vector_search("a", EMBED.embed("kayaks"), 5)
    deleted = store.delete("a", [episode.id])
    assert deleted == 1
    assert store.lexical_search("a", "kayaks", 5, [Status.ACTIVE]) == []
    assert store.vector_search("a", EMBED.embed("kayaks"), 5) == []
    assert store.embedding_of("a", episode.id) is None


def test_vector_search_handles_empty_and_mismatched_dimensions() -> None:
    store = MemoryStore()
    assert store.vector_search("a", EMBED.embed("x"), 5) == []
    add(store, "a", "something")
    assert store.vector_search("a", HashingEmbedder(dimension=16).embed("something"), 5) == []
    episode = add(store, "a", "something else")
    assert store.vector_search("a", EMBED.embed("something"), 5, allowed={episode.id})[0][0] == (
        episode.id
    )


def test_file_database_persists(tmp_path: Path) -> None:
    path = tmp_path / "nested" / "memory.db"
    with AgentMemory(path, namespace="alice") as memory:
        memory.add_turn("I live in Nairobi.", timestamp=10.0)
    with AgentMemory(path, namespace="alice") as memory:
        assert memory.current_fact("user", "lives_in") is not None
        assert memory.stats()["database_bytes"] > 0


def test_size_bytes_compacts() -> None:
    store = MemoryStore()
    episodes = [add(store, "a", f"note number {index} about gardening") for index in range(200)]
    before = store.size_bytes()
    store.delete("a", [episode.id for episode in episodes])
    assert store.size_bytes(compact=True) < before
    assert store.counts("a") == {"episodic.consolidated": 0}
