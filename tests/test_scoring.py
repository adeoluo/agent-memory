from __future__ import annotations

import pytest

from agent_memory import AgentMemory, MemoryKind, ScoringWeights
from agent_memory.models import Status
from agent_memory.scoring import matched_terms, recency
from tests.conftest import DAY, Clock


def test_recency_halves_every_half_life() -> None:
    assert recency(0.0, 30) == 1.0
    assert recency(30 * DAY, 30) == pytest.approx(0.5)
    assert recency(-5.0, 30) == 1.0
    assert recency(DAY, 0) == 0.0


def test_weights_without() -> None:
    weights = ScoringWeights().without("recency")
    assert weights.recency == 0.0 and weights.lexical == ScoringWeights().lexical
    with pytest.raises(ValueError):
        ScoringWeights().without("vibes")


def test_matched_terms_use_prefix_stems() -> None:
    assert matched_terms("preferred editors", "my editor preference") == ("preferred", "editors")


def test_recall_returns_explained_breakdowns(memory: AgentMemory, clock: Clock) -> None:
    memory.add_turn("My favorite editor is Neovim.")
    memory.add_turn("The weather has been strange this week.")
    clock.advance(1)
    hits = memory.recall("which editor is my favorite?", k=3)
    assert hits[0].memory.kind in {MemoryKind.EPISODIC, MemoryKind.SEMANTIC}
    assert all("weather" not in hit.text for hit in hits)
    top = hits[0]
    expected = (
        0.40 * top.score.lexical
        + 0.30 * top.score.semantic
        + 0.15 * top.score.recency
        + 0.15 * top.score.importance
    )
    assert top.score.total == pytest.approx(expected)
    assert "lexical match on 'editor'" in top.explanation
    assert "largest contribution" in top.explanation
    payload = top.to_dict()
    assert set(payload["components"]) == {"lexical", "semantic", "recency", "importance"}


def test_recency_breaks_ties_between_equal_matches(memory: AgentMemory, clock: Clock) -> None:
    memory.add_turn("note: the launch code word is apple", importance=0.5)
    clock.advance(60)
    newer = memory.add_turn("note: the launch code word is apple", importance=0.5)
    hits = memory.recall("launch code word", k=1)
    assert hits[0].id == newer.episode.id


def test_lexical_only_weights_do_not_use_vector_candidates(memory: AgentMemory) -> None:
    memory.add_turn("preferences preferring")
    lexical = ScoringWeights(lexical=1.0, semantic=0.0, recency=0.0, importance=0.0)
    assert memory.recall("prefer", 5, weights=lexical)
    assert memory.recall("zzzz unrelated", 5, weights=lexical) == []
    both_zero = ScoringWeights(lexical=0.0, semantic=0.0, recency=1.0, importance=0.0)
    assert memory.recall("preferences", 5, weights=both_zero)


def test_history_kinds_k_and_touch(memory: AgentMemory, clock: Clock) -> None:
    memory.add_turn("My favorite drink is coffee.")
    clock.advance(1)
    memory.add_turn("My new favorite drink is matcha.")
    current = memory.recall("favorite drink", 10, kinds=[MemoryKind.SEMANTIC])
    assert [hit.memory.object for hit in current] == ["matcha"]  # type: ignore[union-attr]
    history = memory.recall("favorite drink", 10, kinds=[MemoryKind.SEMANTIC], include_history=True)
    assert {hit.memory.status for hit in history} == {Status.ACTIVE, Status.SUPERSEDED}
    assert memory.recall("favorite drink", 0) == []
    fact = memory.get(current[0].id)
    assert fact is not None and fact.access_count == 2
    memory.recall("favorite drink", 10, touch=False)
    again = memory.get(current[0].id)
    assert again is not None and again.access_count == 2
    assert memory.recall("", 5) == []
