import math
from collections.abc import Callable

import pytest

from lab1.tests.support import (
    assert_expected_output,
    assert_expected_plot,
    assert_task_error,
    assert_vector_near,
)
from lab4.task1.cauchy import Solution
from lab4.task2 import boundary
from lab4.task2.boundary import (
    BoundaryProblem,
    Condition,
    finite_difference,
    shooting,
)
from lab4.task2.main import INPUT, exact, f, figure, p, q, task

VARIANT = BoundaryProblem(
    p, q, f, 0.0, 1.0, Condition(0.0, 1.0, 2.0), Condition(1.0, 0.0, math.e**2)
)
ROBIN = BoundaryProblem(
    lambda x: 0.0,
    lambda x: 1.0,
    lambda x: 0.0,
    0.0,
    1.0,
    Condition(1.0, 1.0, 1.0),
    Condition(2.0, 1.0, 2.0 * math.sin(1.0) + math.cos(1.0)),
)


def errors(xs: list[float], ys: list[float], solution: Callable[[float], float]) -> float:
    return max(abs(y - solution(x)) for x, y in zip(xs, ys, strict=True))


def test_exact_solution_satisfies_the_variant() -> None:
    for x in (0.25, 0.5, 1.0):
        y = exact(x)
        assert x * 4.0 * y - (2.0 * x + 1.0) * 2.0 * y + 2.0 * y == pytest.approx(0.0, abs=1e-12)
        assert 4.0 * y + p(x) * 2.0 * y + q(x) * y == pytest.approx(f(x), abs=1e-12)


def test_shooting_solves_the_variant() -> None:
    result = shooting(VARIANT, 0.1, 1e-9)
    assert result.solution.xs[0] == pytest.approx(0.0, abs=1e-15)
    assert result.solution.xs[-1] == 1.0
    assert result.shots[-1].parameter == pytest.approx(2.0 * math.e**2, abs=1e-2)
    assert abs(result.shots[-1].residual) <= 1e-9
    assert len(result.shots) == 3
    assert errors(result.solution.xs, result.solution.ys, exact) < 2e-3


def test_finite_difference_solves_the_variant_with_second_order() -> None:
    coarse = finite_difference(VARIANT, 0.1)
    fine = finite_difference(VARIANT, 0.05)
    coarse_error = errors(coarse.xs, coarse.ys, exact)
    fine_error = errors(fine.xs, fine.ys, exact)
    assert coarse_error < 3e-2
    assert coarse_error / fine_error == pytest.approx(4.0, rel=0.2)


def test_robin_conditions_at_both_ends() -> None:
    for solution in (shooting(ROBIN, 0.05, 1e-12).solution, finite_difference(ROBIN, 0.01)):
        assert errors(solution.xs, solution.ys, math.sin) < 1e-4


def test_shooting_finds_a_missing_value_when_the_right_condition_has_a_derivative() -> None:
    result = shooting(ROBIN, 0.05, 1e-12)
    assert result.shots[-1].parameter == pytest.approx(math.sin(1.0), abs=1e-6)


def test_finite_difference_with_dirichlet_conditions() -> None:
    problem = BoundaryProblem(
        lambda x: 0.0,
        lambda x: 0.0,
        lambda x: 2.0,
        0.0,
        1.0,
        Condition(1.0, 0.0, 0.0),
        Condition(1.0, 0.0, 1.0),
    )
    solution = finite_difference(problem, 0.5)
    assert_vector_near(solution.ys, [0.0, 0.25, 1.0], 1e-12)


def test_rejects_invalid_problems() -> None:
    with pytest.raises(ValueError, match="a < b"):
        shooting(
            BoundaryProblem(p, q, f, 1.0, 0.0, VARIANT.left_condition, VARIANT.right_condition),
            0.1,
            1e-6,
        )
    empty = Condition(0.0, 0.0, 1.0)
    with pytest.raises(ValueError, match="non-zero alpha or beta"):
        finite_difference(BoundaryProblem(p, q, f, 0.0, 1.0, empty, VARIANT.right_condition), 0.1)
    with pytest.raises(ValueError, match="at least two steps"):
        finite_difference(VARIANT, 1.0)


def test_shooting_stops_when_it_cannot_converge(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(boundary, "MAX_SHOTS", 2)
    with pytest.raises(RuntimeError, match="did not converge"):
        shooting(VARIANT, 0.1, 1e-9)


def test_shooting_reports_a_stalled_secant(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(
        boundary, "adams", lambda problem, h: Solution([1.0, 0.0], [[1.0, 1.0], [1.0, 1.0]])
    )
    with pytest.raises(ValueError, match="stalled"):
        shooting(VARIANT, 0.1, 1e-9)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("0 1 0 1 2 1 0 e^2 0.1", "unexpected end of input"),
        ("0 1 0 1 2 1 0 e^2 0.1 1e-6 0", "unexpected trailing input"),
        ("0 1 0 0 2 1 0 e^2 0.1 1e-6", "non-zero alpha or beta"),
        ("0 1 0 1 2 1 0 e^2 0.3 1e-6", "does not divide"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
