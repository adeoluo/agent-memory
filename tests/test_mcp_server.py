from __future__ import annotations

import asyncio
from typing import Any

from mcp import Client

from agent_memory import AgentMemory
from agent_memory.mcp_server import build_server


def structured(result: Any) -> Any:
    assert not result.is_error
    content = result.structured_content
    return content.get("result", content)


async def exercise(memory: AgentMemory, other: AgentMemory) -> None:
    async with Client(build_server(memory)) as client:
        tools = {tool.name for tool in (await client.list_tools()).tools}
        assert tools == {"remember", "recall", "forget", "list_facts"}

        stored = structured(await client.call_tool("remember", {"text": "I live in Lisbon."}))
        assert stored["facts"] == ["user lives in Lisbon"]
        structured(await client.call_tool("remember", {"text": "I just moved to Tokyo."}))

        hits = structured(await client.call_tool("recall", {"query": "where do I live", "k": 99}))
        assert hits and all("explanation" in hit for hit in hits)
        assert all("Ottawa" not in hit["text"] for hit in hits)

        facts = structured(await client.call_tool("list_facts", {"include_history": True}))
        assert {(f["object"], f["status"]) for f in facts} == {
            ("Lisbon", "superseded"),
            ("Tokyo", "active"),
        }
        active = structured(await client.call_tool("list_facts", {"subject": "user"}))
        assert [fact["object"] for fact in active] == ["Tokyo"]

        forgotten = structured(
            await client.call_tool("forget", {"memory_id": stored["episode_id"]})
        )
        assert forgotten == {"memory_id": stored["episode_id"], "forgotten": True}
        foreign = other.add_turn("I live in Ottawa.").episode.id
        refused = structured(await client.call_tool("forget", {"memory_id": foreign}))
        assert refused["forgotten"] is False
    assert other.get(foreign) is not None


def test_mcp_tools_round_trip() -> None:
    memory = AgentMemory(namespace="alice")
    asyncio.run(exercise(memory, memory.for_namespace("bob")))
