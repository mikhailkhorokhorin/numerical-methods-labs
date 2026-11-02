import subprocess
import sys
from pathlib import Path

import pytest

from lab1.main import TASKS

LAB_DIR = Path(__file__).resolve().parents[1]


def run_module(module: str, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, "-m", module, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=LAB_DIR.parent,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def expected_output(task: str) -> str:
    return (LAB_DIR / task / "output.txt").read_text(encoding="utf-8")


@pytest.mark.parametrize("task", [f"task{number}" for number in range(1, 6)])
def test_every_task_prints_its_expected_output(task: str) -> None:
    assert run_module(f"lab1.{task}.main") == (0, expected_output(task), "")


def test_task_reads_another_input_file(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("2\n0\n4 2\n0\n8 2\n", encoding="utf-8")
    expected = "x = (2.0000, 1.0000)\nStability condition: no\n"
    assert run_module("lab1.task2.main", str(path)) == (0, expected, "")


def test_task_reports_errors(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("2\n1 2\n2 4\n1 1\n", encoding="utf-8")
    assert run_module("lab1.task1.main", str(path)) == (1, "", "error: matrix is singular\n")


def test_lab_runs_all_tasks() -> None:
    sections = [
        f"Task {number}. {title}\n{expected_output(f'task{index}')}"
        for index, (number, title, _) in enumerate(TASKS, start=1)
    ]
    assert run_module("lab1.main") == (0, "\n".join(sections), "")
