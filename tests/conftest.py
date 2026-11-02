from __future__ import annotations

from collections.abc import Iterator

import pytest

from agent_memory import AgentMemory

DAY = 86_400.0
T0 = 1_700_000_000.0


class Clock:
    def __init__(self, start: float = T0) -> None:
        self.now = start

    def __call__(self) -> float:
        return self.now

    def advance(self, days: float) -> None:
        self.now += days * DAY


@pytest.fixture
def clock() -> Clock:
    return Clock()


@pytest.fixture
def memory(clock: Clock) -> Iterator[AgentMemory]:
    with AgentMemory(namespace="alice", clock=clock) as instance:
        yield instance
