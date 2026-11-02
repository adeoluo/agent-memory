from __future__ import annotations

import pytest

from agent_memory.evaluation.dataset import TOPICS, generate_dataset
from agent_memory.evaluation.harness import (
    Evidence,
    format_report,
    read_answer,
    run_benchmark,
)
from agent_memory.extraction import RuleExtractor


def test_dataset_is_deterministic_and_consistent() -> None:
    first = generate_dataset(users=3, sessions=8, seed=3)
    second = generate_dataset(users=3, sessions=8, seed=3)
    assert first == second
    assert generate_dataset(users=3, sessions=8, seed=4) != first
    extractor = RuleExtractor()
    for user in first.users:
        stated: dict[str, list[str]] = {}
        for turn in user.turns:
            for fact in extractor.extract(turn.content, turn.role).facts:
                stated.setdefault(fact.predicate, []).append(fact.object)
        for question in user.questions:
            values = stated[question.predicate]
            if question.mode == "current":
                assert values[-1] == question.answer
            else:
                assert values[-2] == question.answer
            assert question.answer in question.candidates
    assert {q.predicate.split(":")[-1] for q in first.questions} & set(TOPICS)


def test_reader_orders_by_time() -> None:
    evidence = [
        Evidence("I just moved to Tokyo.", 30.0),
        Evidence("I live in Lisbon.", 10.0),
        Evidence("I live in Lisbon.", 20.0),
        Evidence("ignored", 5.0, predicate="works_at", value="Hooli"),
    ]
    assert read_answer(evidence, "lives_in", "current") == "Tokyo"
    assert read_answer(evidence, "lives_in", "previous") == "Lisbon"
    assert read_answer(evidence[:1], "lives_in", "previous") is None
    assert read_answer([], "lives_in", "current") is None


def test_benchmark_reports_expected_ordering() -> None:
    report = run_benchmark(users=4, sessions=10, seeds=[1, 2], scaling=[8])
    conditions = report["conditions"]
    hybrid = conditions["full hybrid"]["accuracy"]["mean"]
    assert hybrid > conditions["no memory"]["accuracy"]["mean"]
    assert hybrid > conditions["full-context truncation (400 words)"]["accuracy"]["mean"]
    assert conditions["no memory"]["recall@1"] is None
    assert set(report["ablation"]) >= {"without lexical", "without recency"}
    assert [row["consolidation"] for row in report["scaling"]] == [False, True]
    text = format_report(report)
    assert "Scoring-term ablation" in text and "Scaling" in text


def test_weight_tuning_uses_disjoint_development_seeds() -> None:
    with pytest.raises(ValueError):
        run_benchmark(users=2, sessions=6, seeds=[1], dev_seeds=[1], scaling=[])
    report = run_benchmark(
        users=2, sessions=6, seeds=[1], dev_seeds=[2], tuning_grid=(0.0, 1.0), scaling=[]
    )
    assert report["tuning"]["dev_seeds"] == [2]
    assert "hybrid, weights tuned on development seeds" in report["conditions"]
    assert "Tuned weights" in format_report(report)
