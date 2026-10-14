import pytest

from lab1.common import Matrix, identity, matmul, transposed, zeros
from lab1.task1.lu import decompose_lu, determinant
from lab1.task4.rotation import rotation_method
from lab1.task5.main import INPUT, task
from lab1.task5.qr import decompose_qr, qr_algorithm
from lab1.tests.support import (
    assert_expected_output,
    assert_matrix_near,
    assert_task_error,
    random_matrix,
    random_symmetric,
)

VARIANT = [[-6.0, -3.0, 7.0], [9.0, 1.0, -6.0], [3.0, -5.0, 5.0]]


def assert_values(actual: list[complex], expected: list[complex], tolerance: float) -> None:
    def key(value: complex) -> tuple[float, float]:
        return value.real, value.imag

    assert len(actual) == len(expected)
    for lhs, rhs in zip(sorted(actual, key=key), sorted(expected, key=key), strict=True):
        assert abs(lhs - rhs) <= tolerance


def assert_valid_decomposition(matrix: Matrix) -> None:
    qr = decompose_qr(matrix)
    n = len(matrix)
    assert_matrix_near(matmul(transposed(qr.q), qr.q), identity(n), 1e-12)
    assert_matrix_near(matmul(qr.q, qr.r), matrix, 1e-10)
    assert all(qr.r[i][j] == 0.0 for i in range(n) for j in range(i))


@pytest.mark.parametrize(
    "matrix",
    [VARIANT, [[0.0, 1.0], [0.0, 2.0]], *(random_matrix(n, n) for n in range(1, 8))],
)
def test_decomposes_matrices(matrix: Matrix) -> None:
    assert_valid_decomposition(matrix)


def test_finds_eigenvalues_of_variant() -> None:
    eigen = qr_algorithm(VARIANT, 1e-10)
    expected = [complex(-7.38877383, 0.0), complex(-0.05454841, 0.0), complex(7.44332223, 0.0)]
    assert_values(eigen.values, expected, 1e-7)


def test_isolates_close_moduli_as_a_block() -> None:
    a = VARIANT
    for _ in range(5):
        qr = decompose_qr(a)
        a = matmul(qr.r, qr.q)
    assert abs(a[1][0]) > 1.0
    assert abs(a[2][1]) < 1e-9
    assert qr_algorithm(VARIANT, 1e-6).iterations == 5


def test_more_iterations_for_higher_precision() -> None:
    assert qr_algorithm(VARIANT, 1e-2).iterations < qr_algorithm(VARIANT, 1e-8).iterations


def test_finds_imaginary_pair() -> None:
    eigen = qr_algorithm([[0.0, -1.0], [1.0, 0.0]], 1e-10)
    assert_values(eigen.values, [complex(0.0, 1.0), complex(0.0, -1.0)], 1e-12)


def test_triangular_matrix_needs_no_iterations() -> None:
    eigen = qr_algorithm([[1.0, 2.0], [0.0, 3.0]], 1e-6)
    assert eigen.iterations == 0
    assert eigen.values == [complex(1.0, 0.0), complex(3.0, 0.0)]


@pytest.mark.parametrize("n", range(2, 7))
def test_matches_rotation_method_on_symmetric_matrices(n: int) -> None:
    matrix = random_symmetric(n, n)
    expected = [complex(value, 0.0) for value in rotation_method(matrix, 1e-12).values]
    assert_values(qr_algorithm(matrix, 1e-10).values, expected, 1e-7)


@pytest.mark.parametrize("n", range(2, 7))
def test_eigenvalues_match_trace_and_determinant(n: int) -> None:
    matrix = random_matrix(n, 10 + n)
    values = qr_algorithm(matrix, 1e-10).values
    total = complex(0.0, 0.0)
    product = complex(1.0, 0.0)
    trace = 0.0
    for i, value in enumerate(values):
        total += value
        product *= value
        trace += matrix[i][i]
    det = determinant(decompose_lu(matrix))
    assert abs(total - trace) <= 1e-7
    assert abs(product - det) <= 1e-6 * max(1.0, abs(det))


def test_fails_when_eigenvalues_have_equal_moduli() -> None:
    cyclic = [[0.0, 0.0, 1.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]]
    with pytest.raises(RuntimeError, match="did not converge"):
        qr_algorithm(cyclic, 1e-6)


@pytest.mark.parametrize("matrix", [zeros(2, 3), []])
def test_rejects_invalid_shapes(matrix: Matrix) -> None:
    with pytest.raises(ValueError, match="non-empty square matrix"):
        decompose_qr(matrix)
    with pytest.raises(ValueError, match="non-empty square matrix"):
        qr_algorithm(matrix, 1e-6)


def test_main_prints_expected_output() -> None:
    assert_expected_output(task, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2\n1 2\n3 4\n", "unexpected end of input"),
    ],
)
def test_reports_input_and_method_errors(text: str, message: str) -> None:
    assert_task_error(task, text, message)
