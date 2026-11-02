from __future__ import annotations

import json
from pathlib import Path

import pytest

from agent_memory.cli import main


def run(capsys: pytest.CaptureFixture[str], database: Path, *args: str) -> tuple[int, str]:
    code = main(["--database", str(database), "--namespace", "alice", *args])
    return code, capsys.readouterr().out


def test_cli_end_to_end(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    database = tmp_path / "memory.db"
    code, out = run(capsys, database, "add", "My favorite editor is Helix.")
    assert code == 0 and "stored episode 1" in out and "added fact" in out
    code, out = run(capsys, database, "add", "I live in Austin.", "--json")
    assert json.loads(out)["facts"] == ["user lives in Austin"]

    code, out = run(capsys, database, "recall", "favorite editor", "-k", "2")
    assert "1. [" in out and "score" in out
    code, out = run(capsys, database, "recall", "favorite editor", "--json", "--history")
    assert json.loads(out)[0]["explanation"]
    code, out = run(capsys, database, "recall", "zzzz")
    assert "no matching memories" in out

    code, out = run(capsys, database, "facts")
    assert "Helix" in out
    code, out = run(capsys, database, "facts", "--json", "--history", "--predicate", "lives_in")
    assert json.loads(out)[0]["object"] == "Austin"

    code, out = run(capsys, database, "stats")
    assert "episodes" in out
    code, out = run(capsys, database, "stats", "--json")
    assert json.loads(out)["facts_active"] == 2

    code, out = run(capsys, database, "consolidate")
    assert "summarized 0 sessions" in out
    code, out = run(capsys, database, "consolidate", "--json")
    assert json.loads(out)["sessions_summarized"] == 0

    export = tmp_path / "out.json"
    code, out = run(capsys, database, "export", str(export))
    assert "exported 4 memories" in out
    code = main(["--database", str(database), "--namespace", "bob", "import", str(export)])
    assert code == 0 and "imported 4" in capsys.readouterr().out

    code, out = run(capsys, database, "forget", "1")
    assert code == 0 and "forgot memory 1" in out
    code, _ = run(capsys, database, "forget", "1")
    assert code == 1


def test_cli_benchmark(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    output = tmp_path / "report.json"
    code = main(
        [
            "benchmark",
            "--users",
            "2",
            "--sessions",
            "6",
            "--scaling",
            "6",
            "--output",
            str(output),
        ]
    )
    assert code == 0
    assert "Memory conditions" in capsys.readouterr().out
    assert json.loads(output.read_text())["scaling"]


def test_module_entrypoint_version(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        main(["--version"])
    assert exit_info.value.code == 0
    assert "agent-memory" in capsys.readouterr().out
