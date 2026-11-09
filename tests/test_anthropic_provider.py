"""Request shape of the Claude client, checked against a stubbed HTTP layer."""

from __future__ import annotations

import io
import json
import urllib.request
from typing import Any

import pytest

from agent_memory.provider import AnthropicProvider


class _Reply(io.BytesIO):
    def __enter__(self) -> _Reply:
        return self

    def __exit__(self, *exc: object) -> None:
        return None


def test_request_uses_current_model_and_api_version(monkeypatch: pytest.MonkeyPatch) -> None:
    captured: dict[str, Any] = {}

    def fake_urlopen(request: urllib.request.Request, timeout: float) -> _Reply:
        captured["url"] = request.full_url
        captured["headers"] = {k.lower(): v for k, v in request.header_items()}
        assert isinstance(request.data, bytes)
        captured["body"] = json.loads(request.data)
        blocks = [{"type": "thinking", "thinking": ""}, {"type": "text", "text": "hello"}]
        return _Reply(json.dumps({"content": blocks}).encode())

    monkeypatch.setenv("ANTHROPIC_API_KEY", "ak-test")
    monkeypatch.delenv("ANTHROPIC_MODEL", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", fake_urlopen)
    assert AnthropicProvider().complete("sys", "hi") == "hello"
    assert captured["url"] == "https://api.anthropic.com/v1/messages"
    assert captured["headers"]["anthropic-version"] == "2026-10-21"
    assert captured["headers"]["x-api-key"] == "ak-test"
    body = captured["body"]
    assert body["model"] == "claude-sonnet-5-5"
    assert body["max_tokens"] == 2048
    assert body["system"] == "sys"
    assert body["messages"] == [{"role": "user", "content": "hi"}]
    assert not {"temperature", "top_p", "top_k"} & body.keys()


def test_missing_key_is_an_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
    with pytest.raises((ValueError, RuntimeError)):
        AnthropicProvider()
