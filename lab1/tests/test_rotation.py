from itertools import pairwise

import pytest

from lab1.common import Matrix, column, identity, matmul, matvec, transposed, zeros
from lab1.task4.main import INPUT, task
from lab1.task4.rotation import EigenSystem, off_diagonal_norm, rotation_method
from lab1.tests.support import (
    assert_expected_output,
    assert_matrix_near,
    assert_task_error,
    assert_vector_near,
    random_symmetric,
)

VARIANT = [[3.0, 2.0, 6.0], [2.0, -3.0, -7.0], [6.0, -7.0, 3.0]]


def assert_eigenpairs(matrix: Matrix, eigen: EigenSystem, tolerance: float) -> None:
    n = len(matrix)
    assert_matrix_near(matmul(transposed(eigen.vectors), eigen.vectors), identity(n), 1e-12)
    for i, value in enumerate(eigen.values):
        vector = column(eigen.vectors, i)
        assert_vector_near(matvec(matrix, vector), [value * x for x in vector], tolerance)


def test_solves_variant() -> None:
    eigen = rotation_method(VARIANT, 1e-10)
    assert_vector_near(sorted(eigen.values), [-9.70682766, 2.47747768, 10.22934998], 1e-8)
    assert_eigenpairs(VARIANT, eigen, 1e-9)


def test_error_decreases_with_every_rotation() -> None:
    eps = 1e-12
    eigen = rotation_method(VARIANT, eps)
    assert len(eigen.errors) == eigen.rotations + 1
    assert eigen.errors[0] == off_diagonal_norm(VARIANT)
    assert eigen.errors[-1] <= eps
    assert all(after < before for before, after in pairwise(eigen.errors))


def test_more_rotations_for_higher_precision() -> None:
    assert rotation_method(VARIANT, 1e-2).rotations < rotation_method(VARIANT, 1e-10).rotations


@pytest.mark.parametrize("n", range(1, 8))
def test_solves_random_symmetric_matrices(n: int) -> None:
    matrix = random_symmetric(n, n)
    assert_eigenpairs(matrix, rotation_method(matrix, 1e-12), 1e-9)


def test_handles_equal_diagonal_entries() -> None:
    eigen = rotation_method([[2.0, -1.0], [-1.0, 2.0]], 1e-12)
    assert eigen.rotations == 1
    assert_vector_near(sorted(eigen.values), [1.0, 3.0], 1e-12)


def test_diagonal_matrix_needs_no_rotations() -> None:
    eigen = rotation_method([[5.0, 0.0], [0.0, -1.0]], 1e-6)
    assert eigen.rotations == 0
    assert eigen.values == [5.0, -1.0]
    assert eigen.vectors == identity(2)


@pytest.mark.parametrize("matrix", [[[1.0, 2.0], [3.0, 4.0]], zeros(2, 3), []])
def test_rejects_non_symmetric_matrices(matrix: Matrix) -> None:
    with pytest.raises(ValueError, match="needs a symmetric matrix"):
        rotation_method(matrix, 1e-6)


def test_main_prints_expected_output() -> None:
    assert_expected_output(task, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2\n1 2\n3 4\n0.001\n", "needs a symmetric matrix"),
    ],
)
def test_reports_input_and_method_errors(text: str, message: str) -> None:
    assert_task_error(task, text, message)
