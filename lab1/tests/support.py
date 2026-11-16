import random
import shutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path
from types import ModuleType

import pytest

from lab1.common import PLOT_NAME, Figure, InputReader, Matrix, Task, Vector, solve_file

REPOSITORY = Path(__file__).resolve().parents[2]


def assert_vector_near(actual: Vector, expected: Vector, tolerance: float) -> None:
    assert actual == pytest.approx(expected, rel=0.0, abs=tolerance)


def assert_matrix_near(actual: Matrix, expected: Matrix, tolerance: float) -> None:
    assert len(actual) == len(expected)
    for actual_row, expected_row in zip(actual, expected, strict=True):
        assert_vector_near(actual_row, expected_row, tolerance)


def assert_expected_output(task: Task, input_path: Path) -> None:
    expected = input_path.with_name("output.txt").read_text(encoding="utf-8")
    assert "\n".join(solve_file(task, input_path)) + "\n" == expected


def assert_task_error(task: Task, text: str, message: str) -> None:
    with pytest.raises((ValueError, RuntimeError), match=message):
        task(InputReader(text))


def random_vector(n: int, seed: int) -> Vector:
    generator = random.Random(seed)
    return [generator.uniform(-10.0, 10.0) for _ in range(n)]


def random_matrix(n: int, seed: int) -> Matrix:
    generator = random.Random(seed)
    return [[generator.uniform(-10.0, 10.0) for _ in range(n)] for _ in range(n)]


def diagonally_dominant(n: int, seed: int) -> Matrix:
    result = random_matrix(n, seed)
    for i, row in enumerate(result):
        off_diagonal = 0.0
        for j, value in enumerate(row):
            if j != i:
                off_diagonal += abs(value)
        row[i] = (off_diagonal + 1.0) * (1.0 if row[i] >= 0.0 else -1.0)
    return result


def random_symmetric(n: int, seed: int) -> Matrix:
    base = random_matrix(n, seed)
    return [[(base[i][j] + base[j][i]) / 2.0 for j in range(n)] for i in range(n)]


def run_module(module: str, *args: str) -> tuple[int, str, str]:
    result = subprocess.run(
        [sys.executable, "-m", module, *args],
        capture_output=True,
        text=True,
        encoding="utf-8",
        cwd=REPOSITORY,
        check=False,
    )
    return result.returncode, result.stdout, result.stderr


def assert_expected_plot(figure: Figure, input_path: Path, name: str = PLOT_NAME) -> None:
    expected = input_path.with_name(name).read_text(encoding="utf-8")
    assert figure(InputReader(input_path.read_text(encoding="utf-8"))) == expected


def assert_program_output(module: str, task_dir: Path, tmp_path: Path) -> None:
    input_path = tmp_path / "input.txt"
    shutil.copy(task_dir / "input.txt", input_path)
    expected = (task_dir / "output.txt").read_text(encoding="utf-8")
    assert run_module(module, str(input_path)) == (0, expected, "")
    committed = sorted(path.name for path in task_dir.glob("*.svg"))
    assert sorted(path.name for path in tmp_path.glob("*.svg")) == committed
    for name in committed:
        written = (tmp_path / name).read_text(encoding="utf-8")
        assert written == (task_dir / name).read_text(encoding="utf-8")


def assert_lab_output(
    tasks: list[tuple[str, str, ModuleType]],
    main: Callable[[], int],
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    sections = []
    for index, (number, title, module) in enumerate(tasks, start=1):
        folder = tmp_path / f"task{index}"
        folder.mkdir()
        shutil.copy(module.INPUT, folder / "input.txt")
        expected = module.INPUT.with_name("output.txt").read_text(encoding="utf-8")
        monkeypatch.setattr(module, "INPUT", folder / "input.txt")
        sections.append(f"Task {number}. {title}\n{expected}")
    assert main() == 0
    assert capsys.readouterr() == ("\n".join(sections), "")
