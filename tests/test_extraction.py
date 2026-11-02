from __future__ import annotations

import json

import pytest

from agent_memory import FakeProvider, LLMExtractor, RuleExtractor
from agent_memory.extraction import parse_extraction


def facts(text: str) -> list[tuple[str, str, float]]:
    return [(f.predicate, f.object, f.confidence) for f in RuleExtractor().extract(text).facts]


@pytest.mark.parametrize(
    ("text", "predicate", "value"),
    [
        ("My favorite editor is Neovim.", "prefers:editor", "Neovim"),
        ("I prefer green tea for my drink.", "prefers:drink", "green tea"),
        ("For note-taking app, I usually go with Obsidian.", "prefers:note-taking app", "Obsidian"),
        ("Actually, I switched to VS Code for my editor.", "prefers:editor", "VS Code"),
        ("These days my favorite cuisine is Thai.", "prefers:cuisine", "Thai"),
        ("For sport, I have now settled on climbing.", "prefers:sport", "climbing"),
        ("I live in Lisbon.", "lives_in", "Lisbon"),
        ("I just moved to Tokyo for a new job.", "lives_in", "Tokyo"),
        ("I work at Acme Robotics.", "works_at", "Acme Robotics"),
        ("I just joined Globex!", "works_at", "Globex"),
        ("My name is Ada Lovelace.", "name", "Ada Lovelace"),
        ("I'm allergic to peanuts.", "allergic_to", "peanuts"),
        ("I speak Yoruba.", "speaks", "Yoruba"),
        ("I have a dog named Rex.", "has_pet", "dog named Rex"),
    ],
)
def test_rule_patterns(text: str, predicate: str, value: str) -> None:
    found = facts(text)
    assert (predicate, value) in [(p, v) for p, v, _ in found]


@pytest.mark.parametrize(
    "text",
    [
        "My sister swears by Emacs for her editor.",
        "What do you think about Rust as a programming language?",
        "I might try Helix as a editor at some point, not sure yet.",
        "My coworker keeps telling me Vim is the best editor.",
        "The weather has been strange this week.",
    ],
)
def test_distractors_are_not_extracted(text: str) -> None:
    assert facts(text) == []


def test_confidence_reflects_hedges_and_updates() -> None:
    assert facts("My favorite drink is coffee.")[0][2] == pytest.approx(0.9)
    assert facts("Maybe my favorite drink is coffee.")[0][2] == pytest.approx(0.5)
    assert facts("Actually my favorite drink is tea now.")[0][2] == pytest.approx(0.95)


def test_assistant_turns_are_ignored() -> None:
    assert RuleExtractor().extract("My favorite editor is Vim.", role="assistant").empty


def test_instruction_preferences() -> None:
    extraction = RuleExtractor().extract(
        "Please always answer in bullet points. Please use metric units. "
        "Please address me as Dr. Ade."
    )
    found = {(p.key, p.value) for p in extraction.preferences}
    assert ("response_style", "bullet points") in found
    assert ("units", "metric") in found
    assert ("address_as", "Dr") in {(k, v.split(".")[0]) for k, v in found}


def test_llm_extractor_with_fake_provider_matches_rules() -> None:
    provider = FakeProvider()
    extractor = LLMExtractor(provider)
    text = "My favorite editor is Neovim. Please answer in Spanish."
    result = extractor.extract(text)
    assert [(f.predicate, f.object) for f in result.facts] == [("prefers:editor", "Neovim")]
    assert [(p.key, p.value) for p in result.preferences] == [("response_style", "Spanish")]
    assert len(provider.calls) == 1
    assert "<turn>" in provider.calls[0][1]


def test_llm_extractor_skips_non_user_turns() -> None:
    provider = FakeProvider()
    assert LLMExtractor(provider).extract("My favorite editor is Vim.", "assistant").empty
    assert provider.calls == []
    keep_all = LLMExtractor(provider, user_turns_only=False)
    assert keep_all.extract("My favorite editor is Vim.", "assistant").empty
    assert len(provider.calls) == 1


def test_llm_extractor_counts_malformed_replies() -> None:
    extractor = LLMExtractor(FakeProvider(lambda system, prompt: "I cannot do that."))
    assert extractor.extract("My favorite editor is Vim.").empty
    assert extractor.failures == 1


def test_parse_extraction_validates_and_clamps() -> None:
    payload = json.dumps(
        {
            "facts": [
                {"subject": "user", "predicate": "Lives_In", "object": "Oslo", "confidence": 3},
                {"subject": "user", "predicate": "", "object": "x"},
                "not a dict",
                {"subject": "user", "predicate": "likes", "object": "tea", "confidence": "high"},
            ],
            "preferences": [
                {"key": "Units", "value": "metric"},
                {"key": "", "value": "x"},
                7,
            ],
        }
    )
    result = parse_extraction("Here you go: " + payload + " done")
    assert [(f.predicate, f.object, f.confidence) for f in result.facts] == [
        ("lives_in", "Oslo", 1.0),
        ("likes", "tea", 0.5),
    ]
    assert [(p.key, p.value, p.confidence) for p in result.preferences] == [
        ("units", "metric", 0.8)
    ]


@pytest.mark.parametrize("payload", ["", "no json", "{not json}", "[1, 2]", "{]"])
def test_parse_extraction_rejects_garbage(payload: str) -> None:
    assert parse_extraction(payload).empty


def test_fake_provider_handles_prompt_without_markers() -> None:
    reply = FakeProvider().complete("system", "My favorite drink is tea.")
    assert json.loads(reply)["facts"][0]["object"] == "tea"
