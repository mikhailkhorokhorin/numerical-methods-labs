from pathlib import Path

import pytest

from lab1.tests.support import assert_lab_output, assert_program_output, run_module
from lab4.common import max_error, runge_romberg_error
from lab4.main import TASKS, main

LAB_DIR = Path(__file__).resolve().parents[1]


def test_runge_romberg_error_compares_common_nodes() -> None:
    assert runge_romberg_error([0.0, 1.0], [0.0, 5.0, 4.0], 1) == 3.0
    assert runge_romberg_error([1.0, 2.0], [1.0, 9.0, 2.0], 2) == 0.0
    with pytest.raises(ValueError, match="half the step"):
        runge_romberg_error([0.0, 1.0], [0.0, 1.0], 2)


def test_max_error() -> None:
    assert max_error([0.0, 1.0], [0.5, 3.0], lambda x: 2.0 * x) == 1.0


@pytest.mark.parametrize("task", ["task1", "task2"])
def test_every_task_prints_its_output_and_saves_its_plot(task: str, tmp_path: Path) -> None:
    assert_program_output(f"lab4.{task}.main", LAB_DIR / task, tmp_path)


def test_task_reports_errors(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1 2\n6 8\n0.3\n", encoding="utf-8")
    assert run_module("lab4.task1.main", str(path)) == (
        1,
        "",
        "error: the step 0.3 does not divide the segment [1, 2]\n",
    )


def test_lab_runs_all_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert_lab_output(TASKS, main, tmp_path, monkeypatch, capsys)
