"""Reproduce the results in the README: ``uv run python benchmarks/run_benchmark.py``.

Writes ``benchmarks/results.json`` (raw numbers) and ``benchmarks/results.md`` (tables).
Accuracy and recall are deterministic for a given seed; latency depends on the machine.
"""

from __future__ import annotations

import json
import platform
import sys
from pathlib import Path

from agent_memory.evaluation.harness import format_report, run_benchmark

HERE = Path(__file__).parent


def main() -> None:
    report = run_benchmark(
        users=12,
        sessions=20,
        seeds=[7, 8, 9],
        dev_seeds=[101, 102],
        scaling=[10, 25, 50, 100, 200],
        progress=lambda message: print(f"running {message}", file=sys.stderr),
    )
    report["machine"] = {"python": platform.python_version(), "platform": platform.platform()}
    (HERE / "results.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
    table = format_report(report)
    (HERE / "results.md").write_text(table + "\n", encoding="utf-8")
    print(table)


if __name__ == "__main__":
    main()
