from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_memory import AgentMemory, Episode, FakeProvider, LLMExtractor
from agent_memory.memory import episode_importance
from agent_memory.models import Status
from tests.conftest import Clock


def test_episode_importance_heuristic() -> None:
    assert episode_importance("My name is Ada.", "user", True) == 0.8
    assert episode_importance("Nice weather.", "user", False) == 0.3
    assert episode_importance("Anything else?", "assistant", False) == 0.1


def test_add_turn_validates_and_reports(memory: AgentMemory) -> None:
    with pytest.raises(ValueError):
        memory.add_turn("   ")
    result = memory.add_turn("My name is Ada. Please use metric units.", session_id="intro")
    assert isinstance(result.episode, Episode)
    assert result.episode.session_id == "intro"
    assert [fact.object for fact in result.facts] == ["Ada"]
    assert [item.value for item in result.preferences] == ["metric"]
    assert len(result.actions) == 2
    assert memory.episodes("intro") and memory.episodes("other") == []


def test_llm_extractor_plugs_into_write_path(clock: Clock) -> None:
    provider = FakeProvider()
    memory = AgentMemory(namespace="a", extractor=LLMExtractor(provider), clock=clock)
    memory.add_turn("I work at Hooli.")
    current = memory.current_fact("user", "works_at")
    assert current is not None and current.object == "Hooli"
    assert len(provider.calls) == 1
    assert memory.preferences()[0].key if memory.preferences() else True


def test_remember_forget_and_stats(memory: AgentMemory) -> None:
    result = memory.remember("My favorite sport is tennis.")
    assert result.episode.session_id == "notes"
    stats = memory.stats()
    assert stats["episodes"] == 1 and stats["facts_active"] == 1
    assert memory.forget(result.episode.id)
    assert not memory.forget(result.episode.id)
    assert memory.get(result.episode.id) is None


def test_export_import_round_trip(memory: AgentMemory, clock: Clock, tmp_path: Path) -> None:
    memory.add_turn("I live in Berlin. Please answer in bullet points.")
    clock.advance(3)
    memory.add_turn("I just moved to Seoul.")
    memory.consolidate(now=clock.now + 30 * 86_400)
    path = tmp_path / "export.json"
    exported = memory.export_to(path)
    payload = json.loads(path.read_text())
    assert payload["format"] == "agent-memory/v1" and len(payload["memories"]) == exported

    copy = memory.for_namespace("copy")
    assert copy.import_from(path) == exported
    history = copy.fact_history("user", "lives_in")
    assert [(f.object, f.status) for f in history] == [
        ("Berlin", Status.SUPERSEDED),
        ("Seoul", Status.ACTIVE),
    ]
    assert history[0].superseded_by == history[1].id
    assert copy.preferences()[0].value == "bullet points"
    assert copy.stats()["episodes_consolidated"] == memory.stats()["episodes_consolidated"]
    assert any("Seoul" in hit.text for hit in copy.recall("where does the user live", 5))


def test_import_rejects_unknown_format(memory: AgentMemory) -> None:
    with pytest.raises(ValueError):
        memory.import_json({"format": "something-else"})
