import pytest

from lab1.common import Matrix, identity, matmul, matvec, zeros
from lab1.task1.lu import LuDecomposition, decompose_lu, determinant, inverse, solve_lu
from lab1.task1.main import INPUT, task
from lab1.tests.support import (
    assert_expected_output,
    assert_matrix_near,
    assert_task_error,
    assert_vector_near,
    random_matrix,
    random_vector,
)

VARIANT = [
    [1.0, 4.0, -9.0, 7.0],
    [2.0, -2.0, -2.0, 3.0],
    [-1.0, 3.0, -9.0, -1.0],
    [-5.0, 2.0, 2.0, 1.0],
]
VARIANT_RHS = [-67.0, -57.0, -26.0, 52.0]


def assert_valid_factors(matrix: Matrix, lu: LuDecomposition) -> None:
    n = len(matrix)
    for i in range(n):
        assert lu.lower[i][i] == 1.0
        for j in range(i + 1, n):
            assert lu.lower[i][j] == 0.0
            assert lu.upper[j][i] == 0.0
            assert abs(lu.lower[j][i]) <= 1.0
    permuted = [matrix[index] for index in lu.permutation]
    assert_matrix_near(matmul(lu.lower, lu.upper), permuted, 1e-9)


def test_solves_variant() -> None:
    lu = decompose_lu(VARIANT)
    assert_valid_factors(VARIANT, lu)
    assert_vector_near(solve_lu(lu, VARIANT_RHS), [-5.0, 9.0, 7.0, -5.0], 1e-12)
    assert determinant(lu) == pytest.approx(935.0, abs=1e-9)
    assert_matrix_near(matmul(inverse(lu), VARIANT), identity(4), 1e-12)


def test_pivots_around_zero_diagonal() -> None:
    matrix = [[0.0, 1.0, 1.0], [1.0, 0.0, 1.0], [1.0, 1.0, 0.0]]
    lu = decompose_lu(matrix)
    assert_valid_factors(matrix, lu)
    assert_vector_near(solve_lu(lu, [2.0, 2.0, 2.0]), [1.0, 1.0, 1.0], 1e-12)
    assert determinant(lu) == pytest.approx(2.0, abs=1e-12)


@pytest.mark.parametrize("n", range(1, 9))
def test_solves_random_systems(n: int) -> None:
    matrix = random_matrix(n, n)
    expected = random_vector(n, 100 + n)
    lu = decompose_lu(matrix)
    assert_valid_factors(matrix, lu)
    assert_vector_near(solve_lu(lu, matvec(matrix, expected)), expected, 1e-8)
    assert_matrix_near(matmul(matrix, inverse(lu)), identity(n), 1e-9)


@pytest.mark.parametrize("matrix", [[[1.0, 2.0], [2.0, 4.0]], zeros(3, 3)])
def test_rejects_singular_matrices(matrix: Matrix) -> None:
    with pytest.raises(ValueError, match="matrix is singular"):
        decompose_lu(matrix)


def test_rejects_invalid_shapes() -> None:
    with pytest.raises(ValueError, match="non-empty square matrix"):
        decompose_lu(zeros(2, 3))
    with pytest.raises(ValueError, match="non-empty square matrix"):
        decompose_lu([])
    with pytest.raises(ValueError, match="right-hand side size"):
        solve_lu(decompose_lu(VARIANT), [0.0, 0.0, 0.0])


def test_main_prints_expected_output() -> None:
    assert_expected_output(task, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2\n1 2\n2 4\n1 1\n", "matrix is singular"),
        ("1\n2\n4\n5\n", "unexpected trailing input '5'"),
    ],
)
def test_reports_input_and_method_errors(text: str, message: str) -> None:
    assert_task_error(task, text, message)
