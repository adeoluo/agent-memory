from __future__ import annotations

from agent_memory import AgentMemory, ForgettingSettings, MemorySettings
from agent_memory.consolidation import retention, summarize
from agent_memory.models import Episode, Status
from tests.conftest import DAY, T0, Clock


def episode(content: str, role: str = "user", **changes: object) -> Episode:
    base: dict[str, object] = {
        "id": 1,
        "namespace": "n",
        "content": content,
        "created_at": T0,
        "session_id": "s",
        "role": role,
        "importance": 0.8,
    }
    base.update(changes)
    return Episode(**base)  # type: ignore[arg-type]


def test_retention_decays_and_access_boosts() -> None:
    settings = ForgettingSettings(half_life_days=10)
    fresh = retention(episode("x"), T0, settings)
    assert fresh == 0.8
    assert retention(episode("x"), T0 + 10 * DAY, settings) == 0.4
    boosted = retention(episode("x", access_count=3), T0 + 10 * DAY, settings)
    assert boosted > 0.4
    touched = retention(episode("x", last_accessed=T0 + 10 * DAY), T0 + 10 * DAY, settings)
    assert touched == 0.8


def test_summarize_prefers_informative_user_sentences() -> None:
    episodes = [
        episode("Hello. I live in Lisbon. I work at Initech."),
        episode("Thanks for sharing that.", role="assistant"),
        episode("Hello again. My favorite drink is matcha."),
    ]
    summary = summarize(episodes, 2)
    assert "Hello." not in summary
    assert summary.count(".") == 2
    assert summarize([episode("Only the assistant spoke.", role="assistant")], 2)
    assert summarize([], 2) == ""


def test_consolidation_summarizes_and_forgets(clock: Clock) -> None:
    memory = AgentMemory(namespace="alice", clock=clock)
    for index in range(3):
        memory.add_turn(f"Small talk number {index} about the garden.", session_id="s1")
    memory.add_turn("My favorite editor is Helix.", session_id="s1")
    clock.advance(2)
    memory.add_turn("Recent chat that is too new to consolidate.", session_id="s2")

    report = memory.consolidate(now=clock.now + 6 * DAY)
    assert report.sessions_summarized == 1
    assert report.episodes_consolidated == 4
    assert report.episodes_forgotten == 0
    summaries = memory.facts(predicate="summary")
    assert summaries and summaries[0].subject == "session s1"
    assert memory.stats()["episodes_consolidated"] == 4

    late = memory.consolidate(now=clock.now + 400 * DAY)
    assert late.episodes_forgotten >= 4
    assert memory.current_fact("user", "prefers:editor") is not None
    assert any("Helix" in hit.text for hit in memory.recall("favorite editor", 5))


def test_unsummarized_episodes_are_never_forgotten(clock: Clock) -> None:
    memory = AgentMemory(namespace="a", clock=clock)
    memory.add_turn("An old thought about rivers.")
    settings_off = MemorySettings(consolidate_after_days=10_000)
    keeper = AgentMemory(namespace="a", settings=settings_off, store=memory.store, clock=clock)
    report = keeper.consolidate(now=clock.now + 1000 * DAY)
    assert report.episodes_forgotten == 0
    assert len(keeper.episodes()) == 1


def test_consolidation_extracts_when_write_time_extraction_is_off(clock: Clock) -> None:
    settings = MemorySettings(
        extract_on_write=False,
        forgetting=ForgettingSettings(enabled=False),
    )
    memory = AgentMemory(namespace="a", settings=settings, clock=clock)
    result = memory.add_turn("I live in Toronto.")
    assert result.facts == () and memory.facts() == []
    report = memory.consolidate(now=clock.now + 30 * DAY)
    assert report.facts_written == 2
    assert memory.current_fact("user", "lives_in") is not None
    assert report.episodes_forgotten == 0


def test_forgetting_superseded_history_is_optional(clock: Clock) -> None:
    settings = MemorySettings(forgetting=ForgettingSettings(forget_superseded_facts=True))
    memory = AgentMemory(namespace="a", settings=settings, clock=clock)
    memory.add_turn("I live in Berlin.")
    clock.advance(1)
    memory.add_turn("I just moved to Austin.")
    report = memory.consolidate(now=clock.now + 1000 * DAY)
    assert report.facts_forgotten == 1
    statuses = {f.status for f in memory.facts(predicate="lives_in", include_history=True)}
    assert statuses == {Status.ACTIVE}
