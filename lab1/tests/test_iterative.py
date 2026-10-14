import pytest

from lab1.common import Matrix, Vector, matrix_norm_inf, matvec, zeros
from lab1.task3.iterative import (
    MAX_ITERATIONS,
    apriori_iterations,
    seidel,
    simple_iteration,
    to_iteration_form,
)
from lab1.task3.main import INPUT, task
from lab1.tests.support import (
    assert_expected_output,
    assert_task_error,
    assert_vector_near,
    diagonally_dominant,
    random_vector,
)

VARIANT = [
    [10.0, 0.0, 2.0, 4.0],
    [2.0, 16.0, -3.0, 8.0],
    [1.0, 5.0, 11.0, -4.0],
    [8.0, 1.0, 6.0, -17.0],
]
VARIANT_RHS = [110.0, 128.0, 102.0, 81.0]
VARIANT_SOLUTION = [9.0, 7.0, 6.0, 2.0]


def test_builds_iteration_form() -> None:
    form = to_iteration_form(VARIANT, VARIANT_RHS)
    assert form.alpha[0][0] == 0.0
    assert form.alpha[0][2] == -0.2
    assert form.alpha[3][0] == 8.0 / 17.0
    assert_vector_near(form.beta, [11.0, 8.0, 102.0 / 11.0, -81.0 / 17.0], 1e-15)
    assert matrix_norm_inf(form.alpha) == pytest.approx(10.0 / 11.0, abs=1e-15)


@pytest.mark.parametrize("eps", [1e-2, 1e-4, 1e-8])
def test_both_methods_solve_variant(eps: float) -> None:
    jacobi = simple_iteration(VARIANT, VARIANT_RHS, eps)
    gauss_seidel = seidel(VARIANT, VARIANT_RHS, eps)
    assert jacobi.converged
    assert gauss_seidel.converged
    assert_vector_near(jacobi.solution, VARIANT_SOLUTION, eps)
    assert_vector_near(gauss_seidel.solution, VARIANT_SOLUTION, eps)
    assert gauss_seidel.iterations < jacobi.iterations
    estimate = apriori_iterations(VARIANT, VARIANT_RHS, eps)
    assert estimate is not None
    assert jacobi.iterations <= estimate


def test_iterations_grow_as_precision_increases() -> None:
    precisions = [1e-1, 1e-3, 1e-5, 1e-7, 1e-9]
    jacobi = [simple_iteration(VARIANT, VARIANT_RHS, eps).iterations for eps in precisions]
    gauss_seidel = [seidel(VARIANT, VARIANT_RHS, eps).iterations for eps in precisions]
    assert jacobi == sorted(set(jacobi))
    assert gauss_seidel == sorted(set(gauss_seidel))


@pytest.mark.parametrize("n", range(1, 9))
def test_solves_random_dominant_systems(n: int) -> None:
    matrix = diagonally_dominant(n, n)
    expected = random_vector(n, 50 + n)
    rhs = matvec(matrix, expected)
    assert_vector_near(simple_iteration(matrix, rhs, 1e-10).solution, expected, 1e-8)
    assert_vector_near(seidel(matrix, rhs, 1e-10).solution, expected, 1e-8)


@pytest.mark.parametrize(
    ("matrix", "rhs", "eps", "expected"),
    [
        ([[2.0, 0.0], [0.0, 4.0]], [2.0, 4.0], 1e-6, 0),
        (VARIANT, [0.0, 0.0, 0.0, 0.0], 1e-6, 0),
        (VARIANT, VARIANT_RHS, 1e6, 0),
        ([[1.0, 2.0], [3.0, 1.0]], [1.0, 1.0], 1e-6, None),
        ([[1e-300, 0.0], [0.5, 1.0]], [1e100, 1.0], 1e-3, None),
    ],
)
def test_apriori_estimate_edge_cases(
    matrix: Matrix, rhs: Vector, eps: float, expected: int | None
) -> None:
    assert apriori_iterations(matrix, rhs, eps) == expected


def test_seidel_converges_where_simple_iteration_oscillates() -> None:
    matrix = [[1.0, 0.5, 0.5], [0.5, 1.0, 0.5], [0.5, 0.5, 1.0]]
    rhs = [2.0, 2.0, 2.0]
    assert matrix_norm_inf(to_iteration_form(matrix, rhs).alpha) >= 1.0
    jacobi = simple_iteration(matrix, rhs, 1e-10)
    assert not jacobi.converged
    assert jacobi.iterations == MAX_ITERATIONS
    gauss_seidel = seidel(matrix, rhs, 1e-10)
    assert gauss_seidel.converged
    assert_vector_near(gauss_seidel.solution, [1.0, 1.0, 1.0], 1e-8)


def test_stops_on_divergence() -> None:
    matrix = [[1.0, 2.0], [3.0, 1.0]]
    rhs = [1.0, 1.0]
    jacobi = simple_iteration(matrix, rhs, 1e-6)
    gauss_seidel = seidel(matrix, rhs, 1e-6)
    assert not jacobi.converged
    assert not gauss_seidel.converged
    assert jacobi.iterations < MAX_ITERATIONS
    assert gauss_seidel.iterations < MAX_ITERATIONS


@pytest.mark.parametrize(
    ("matrix", "rhs", "message"),
    [
        ([[0.0, 1.0], [1.0, 1.0]], [1.0, 1.0], "zero on the main diagonal"),
        (VARIANT, [0.0, 0.0, 0.0], "matching rhs"),
        (zeros(2, 3), [0.0, 0.0], "matching rhs"),
        ([], [], "matching rhs"),
    ],
)
def test_rejects_invalid_systems(matrix: Matrix, rhs: Vector, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        to_iteration_form(matrix, rhs)


def test_main_prints_expected_output() -> None:
    assert_expected_output(task, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2\n1 2\n3 1\n1 1\n0.001\n", "neither method converged"),
        ("2\n1 2\n3 1\n1 1\n0\n", "precision must be positive"),
    ],
)
def test_reports_input_and_method_errors(text: str, message: str) -> None:
    assert_task_error(task, text, message)
