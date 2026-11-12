from pathlib import Path

import pytest

from lab1.tests.support import assert_lab_output, assert_program_output, run_module
from lab2.common import decimals
from lab2.main import TASKS, main

LAB_DIR = Path(__file__).resolve().parents[1]


def test_decimals_follow_the_precision() -> None:
    assert decimals(1e-1) == 4
    assert decimals(1e-6) == 6
    assert decimals(1e-10) == 10
    assert decimals(5e-7) == 7


@pytest.mark.parametrize("task", ["task1", "task2"])
def test_every_task_prints_its_output_and_saves_its_plot(task: str, tmp_path: Path) -> None:
    assert_program_output(f"lab2.{task}.main", LAB_DIR / task, tmp_path)


def test_task_reports_errors(tmp_path: Path) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1.5 1\n0.001\n", encoding="utf-8")
    assert run_module("lab2.task1.main", str(path)) == (
        1,
        "",
        "error: the interval [a, b] must satisfy a < b\n",
    )
    assert not (tmp_path / "plot.svg").exists()


def test_lab_runs_all_tasks(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]
) -> None:
    assert_lab_output(TASKS, main, tmp_path, monkeypatch, capsys)
