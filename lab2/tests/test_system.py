import pytest

from lab1.common import Matrix, Vector
from lab1.tests.support import (
    assert_expected_output,
    assert_expected_plot,
    assert_task_error,
    assert_vector_near,
)
from lab2.task2 import system as module
from lab2.task2.main import INPUT, figure, first_curve, second_curve, system, task
from lab2.task2.system import (
    NonlinearSystem,
    center,
    contraction_factor,
    newton,
    simple_iteration,
)

REGION = [(1.6, 1.8), (0.4, 0.6)]
SOLUTION = [1.7125172043309800, 0.4831787937823988]


def linear(x: Vector) -> Vector:
    return [2.0 * x[0] + x[1] - 3.0, x[0] - x[1]]


def linear_jacobian(x: Vector) -> Matrix:
    return [[2.0, 1.0], [1.0, -1.0]]


LINEAR = NonlinearSystem(linear, linear_jacobian)


def test_variant_jacobian_matches_finite_differences() -> None:
    equations = system(4.0)
    step = 1e-6
    x = [1.7, 0.5]
    jacobian = equations.jacobian(x)
    for j in range(2):
        forward = x[:]
        backward = x[:]
        forward[j] += step
        backward[j] -= step
        column = [
            (a - b) / (2 * step)
            for a, b in zip(equations.function(forward), equations.function(backward), strict=True)
        ]
        assert [row[j] for row in jacobian] == pytest.approx(column, rel=1e-6)


@pytest.mark.parametrize("eps", [1e-3, 1e-6, 1e-10])
def test_both_methods_solve_the_variant(eps: float) -> None:
    equations = system(4.0)
    simple = simple_iteration(equations, REGION, eps)
    tangent = newton(equations, center(REGION), eps)
    assert simple.start == tangent.start == pytest.approx([1.7, 0.5])
    assert_vector_near(simple.value, SOLUTION, eps)
    assert_vector_near(tangent.value, SOLUTION, eps)
    assert_vector_near(equations.function(tangent.value), [0.0, 0.0], 10 * eps)


def test_solution_lies_on_both_curves() -> None:
    assert first_curve(4.0, SOLUTION[0]) == pytest.approx(SOLUTION[1], abs=1e-12)
    assert second_curve(4.0, SOLUTION[0]) == pytest.approx(SOLUTION[1], abs=1e-12)
    assert first_curve(4.0, 4.5) != first_curve(4.0, 4.5)


def test_newton_solves_a_linear_system_in_one_step() -> None:
    solution = newton(LINEAR, [10.0, -10.0], 1e-12)
    assert_vector_near(solution.iterations[0].x, [1.0, 1.0], 1e-12)
    assert len(solution.iterations) == 2


def test_contraction_factor_is_zero_for_a_linear_system() -> None:
    assert contraction_factor(LINEAR, [(0.0, 2.0), (0.0, 2.0)]) == pytest.approx(0.0, abs=1e-15)
    assert simple_iteration(LINEAR, [(0.0, 2.0), (0.0, 2.0)], 1e-12).value == pytest.approx(
        [1.0, 1.0]
    )


def test_rejects_invalid_regions_and_precision() -> None:
    with pytest.raises(ValueError, match="low < high"):
        simple_iteration(system(4.0), [(1.8, 1.6), (0.4, 0.6)], 1e-6)
    with pytest.raises(ValueError, match="low < high"):
        simple_iteration(system(4.0), [], 1e-6)
    with pytest.raises(ValueError, match="precision must be positive"):
        simple_iteration(system(4.0), REGION, -1.0)
    with pytest.raises(ValueError, match="precision must be positive"):
        newton(system(4.0), [1.7, 0.5], 0.0)


def test_checks_the_convergence_conditions() -> None:
    with pytest.raises(ValueError, match="not a contraction"):
        simple_iteration(system(4.0), [(1.0, 3.0), (0.0, 1.0)], 1e-6)
    shifted = NonlinearSystem(lambda x: [x[0] - 5.0, x[1] - 5.0], linear_jacobian)
    with pytest.raises(ValueError, match="outside itself"):
        simple_iteration(shifted, [(0.0, 1.0), (0.0, 1.0)], 1e-6)


def test_reports_singular_jacobians_and_wrong_sizes() -> None:
    singular = NonlinearSystem(linear, lambda x: [[1.0, 1.0], [1.0, 1.0]])
    with pytest.raises(ValueError, match="Jacobian matrix is singular"):
        newton(singular, [0.0, 0.0], 1e-6)
    with pytest.raises(ValueError, match="Jacobian matrix is singular"):
        contraction_factor(singular, REGION)
    wrong = NonlinearSystem(lambda x: [x[0]], linear_jacobian)
    with pytest.raises(ValueError, match="as many equations as unknowns"):
        newton(wrong, [0.0, 0.0], 1e-6)


def test_methods_stop_after_too_many_iterations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(module, "MAX_ITERATIONS", 1)
    with pytest.raises(RuntimeError, match="simple iteration did not converge"):
        simple_iteration(system(4.0), REGION, 1e-15)
    with pytest.raises(RuntimeError, match="Newton method did not converge"):
        newton(system(4.0), center(REGION), 1e-15)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("4 1.6 1.8 0.4", "unexpected end of input"),
        ("4 1.6 1.8 0.4 0.6 1e-6 1", "unexpected trailing input"),
        ("4 1 3 0 1 1e-6", "not a contraction"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
