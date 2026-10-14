import random
from pathlib import Path

import pytest

from lab1.common import InputReader, Matrix, Task, Vector, solve_file


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
