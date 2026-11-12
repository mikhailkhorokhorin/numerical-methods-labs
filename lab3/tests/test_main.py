from pathlib import Path

import pytest

from lab1.tests.support import assert_lab_output, assert_program_output, run_module
from lab3.main import TASKS, main

LAB_DIR = Path(__file__).resolve().parents[1]


@pytest.mark.parametrize("task", [f"task{number}" for number in range(1, 6)])
def test_every_task_prints_its_output_and_saves_its_plot(task: str, tmp_path: Path) -> None:
    assert_program_output(f"lab3.{task}.main", LAB_DIR / task, tmp_path)


def test_task_reads_another_input_file(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("3\n0 1 2\n0 1 4\n1\n", encoding="utf-8")
    expected = (
        "Left difference:   y'(1.0000) = 1.0000\n"
        "Right difference:  y'(1.0000) = 3.0000\n"
        "Second order:      y'(1.0000) = 2.0000\n"
        "Second derivative: y''(1.0000) = 2.0000\n"
    )
    assert run_module("lab3.task4.main", str(path)) == (0, expected, "")


def test_task_reports_errors(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("2\n0 1\n0 1\n5\n", encoding="utf-8")
    assert run_module("lab3.task2.main", str(path)) == (
        1,
        "",
        "error: the point lies outside the spline nodes\n",
    )


def test_lab_runs_all_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert_lab_output(TASKS, main, tmp_path, monkeypatch, capsys)
