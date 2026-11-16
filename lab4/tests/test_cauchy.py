import math

import pytest

from lab1.common import Vector
from lab1.tests.support import assert_expected_output, assert_expected_plot, assert_task_error
from lab4.task1.cauchy import CauchyProblem, Method, adams, euler, runge_kutta
from lab4.task1.main import ERROR_NAME, INPUT, METHODS, exact, figure, figure_error, rhs, task

VARIANT = CauchyProblem(rhs, 1.0, 2.0, [6.0, 8.0])


def oscillator(x: float, state: Vector) -> Vector:
    return [state[1], -state[0]]


OSCILLATOR = CauchyProblem(oscillator, 0.0, 1.0, [0.0, 1.0])


def test_exact_solution_satisfies_the_variant() -> None:
    step = 1e-4
    for x in (1.0, 1.5, 2.0):
        first = (exact(x + step) - exact(x - step)) / (2 * step)
        second = (exact(x + step) - 2.0 * exact(x) + exact(x - step)) / step**2
        assert rhs(x, [exact(x), first])[1] == pytest.approx(second, rel=1e-6)
    assert exact(1.0) == 6.0


@pytest.mark.parametrize(("name", "method", "order"), METHODS)
def test_methods_converge_with_their_orders(name: str, method: Method, order: int) -> None:
    errors = []
    for h in (0.1, 0.05):
        solution = method(OSCILLATOR, h)
        errors.append(
            max(
                abs(y - math.sin(x))
                for x, y in zip(solution.xs, solution.component(0), strict=True)
            )
        )
    assert errors[0] / errors[1] == pytest.approx(2.0**order, rel=0.25), name


def test_variant_is_solved_accurately() -> None:
    for method, tolerance in ((euler, 0.3), (runge_kutta, 1e-4), (adams, 1e-4)):
        solution = method(VARIANT, 0.1)
        assert len(solution.xs) == 11
        assert solution.xs[-1] == pytest.approx(2.0)
        assert (
            max(abs(y - exact(x)) for x, y in zip(solution.xs, solution.component(0), strict=True))
            < tolerance
        )


def test_adams_starts_with_runge_kutta() -> None:
    first = adams(VARIANT, 0.1)
    second = runge_kutta(VARIANT, 0.1)
    assert first.states[:4] == second.states[:4]
    assert first.states[4] != second.states[4]


def test_adams_never_evaluates_the_last_node() -> None:
    calls: list[float] = []

    def tracked(x: float, state: Vector) -> Vector:
        calls.append(x)
        return [state[1], 1.0 / x]

    solution = adams(CauchyProblem(tracked, 1.0, 0.0, [0.0, 0.0]), 0.1)
    assert solution.xs[-1] == pytest.approx(0.0, abs=1e-15)
    assert min(calls) == pytest.approx(0.1)


def test_backward_integration() -> None:
    solution = runge_kutta(
        CauchyProblem(oscillator, 1.0, 0.0, [math.sin(1.0), math.cos(1.0)]), 0.05
    )
    assert solution.states[-1] == pytest.approx([0.0, 1.0], abs=1e-6)


def test_rejects_steps_that_do_not_divide_the_segment() -> None:
    with pytest.raises(ValueError, match="does not divide"):
        euler(VARIANT, 0.3)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)
    assert_expected_plot(figure_error, INPUT, ERROR_NAME)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("1 2 6 8", "unexpected end of input"),
        ("1 2 6 8 0.1 3", "unexpected trailing input"),
        ("1 2 6 8 0.3", "does not divide"),
        ("1 2 6 8 0.2", "does not divide"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
