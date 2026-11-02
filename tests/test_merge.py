from __future__ import annotations

import pytest

from agent_memory import AgentMemory, MemorySettings
from agent_memory.merge import combine_confidence
from agent_memory.models import Status
from tests.conftest import DAY, T0, Clock


def test_combine_confidence() -> None:
    assert combine_confidence(0.9, 0.9) == pytest.approx(0.99)


def test_restating_a_fact_reinforces_it(memory: AgentMemory, clock: Clock) -> None:
    memory.add_turn("My favorite editor is Vim.")
    clock.advance(2)
    result = memory.add_turn("my favorite editor is vim!")
    assert result.actions[0].startswith("reinforced fact")
    [fact] = memory.fact_history("user", "prefers:editor")
    assert fact.evidence_count == 2
    assert fact.confidence == pytest.approx(0.99)
    assert fact.updated_at == clock.now


def test_newer_evidence_supersedes_and_keeps_history(memory: AgentMemory, clock: Clock) -> None:
    memory.add_turn("My favorite editor is Vim.")
    clock.advance(5)
    result = memory.add_turn("Actually, I switched to Neovim for my editor.")
    assert "superseded" in result.actions[0]
    history = memory.fact_history("user", "prefers:editor")
    assert [(f.object, f.status) for f in history] == [
        ("Vim", Status.SUPERSEDED),
        ("Neovim", Status.ACTIVE),
    ]
    assert history[0].superseded_by == history[1].id
    current = memory.current_fact("user", "prefers:editor")
    assert current is not None and current.object == "Neovim"


def test_weak_newer_evidence_is_contested(memory: AgentMemory, clock: Clock) -> None:
    memory.add_turn("Actually my favorite editor is Vim now.")
    clock.advance(1)
    result = memory.add_turn("Maybe I prefer Emacs for my editor.")
    assert "contested" in result.actions[0]
    current = memory.current_fact("user", "prefers:editor")
    assert current is not None and current.object == "Vim"
    contested = [f for f in memory.facts(include_history=True) if f.status is Status.CONTESTED]
    assert contested[0].object == "Emacs" and contested[0].superseded_by == current.id


def test_out_of_order_evidence(memory: AgentMemory) -> None:
    memory.add_fact("user", "lives_in", "Berlin", confidence=0.6, timestamp=T0 + 10 * DAY)
    older = memory.add_fact("user", "lives_in", "Austin", confidence=0.7, timestamp=T0)
    assert "history" in older.action
    current = memory.current_fact("user", "lives_in")
    assert current is not None and current.object == "Berlin"
    stronger = memory.add_fact("user", "lives_in", "Seoul", confidence=0.95, timestamp=T0 + DAY)
    assert "superseded" in stronger.action
    current = memory.current_fact("user", "lives_in")
    assert current is not None and current.object == "Seoul"


def test_multi_valued_predicates_accumulate(memory: AgentMemory) -> None:
    memory.add_turn("I'm allergic to peanuts.")
    memory.add_turn("I'm allergic to shellfish.")
    values = sorted(f.object for f in memory.facts(predicate="allergic_to"))
    assert values == ["peanuts", "shellfish"]


def test_custom_single_valued_configuration(clock: Clock) -> None:
    settings = MemorySettings(multi_valued_predicates=frozenset())
    memory = AgentMemory(namespace="n", settings=settings, clock=clock)
    memory.add_turn("I'm allergic to peanuts.")
    clock.advance(1)
    memory.add_turn("I'm allergic to shellfish.")
    assert [f.object for f in memory.facts(predicate="allergic_to")] == ["shellfish"]


def test_preferences_supersede_and_dedupe(memory: AgentMemory, clock: Clock) -> None:
    first = memory.set_preference("response_style", "bullet points")
    assert first.provenance == "explicit"
    again = memory.set_preference("response_style", "Bullet points.")
    assert again.id == first.id
    clock.advance(1)
    result = memory.add_turn("Please answer in short paragraphs.")
    assert "superseding" in result.actions[0]
    [active] = memory.preferences()
    assert active.value == "short paragraphs"
    assert active.provenance.startswith("extracted from episode")
    assert len(memory.preferences(include_history=True)) == 2
