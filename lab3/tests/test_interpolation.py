import math

import pytest

from lab1.tests.support import (
    assert_expected_output,
    assert_expected_plot,
    assert_task_error,
    assert_vector_near,
)
from lab3.common import evaluate
from lab3.task1.interpolation import lagrange, newton, omega_derivative
from lab3.task1.main import ERROR_NAME, INPUT, figure, figure_error, function, task

NODES = [0.0, math.pi / 6.0, math.pi / 3.0, math.pi / 2.0]
CUBIC = [2.0, -1.0, 0.5, 3.0]


def test_polynomials_pass_through_the_nodes() -> None:
    values = [function(x) for x in NODES]
    for polynomial in (lagrange(NODES, values), newton(NODES, values)):
        for x, y in zip(NODES, values, strict=True):
            assert polynomial(x) == pytest.approx(y, abs=1e-14)


def test_lagrange_and_newton_give_the_same_polynomial() -> None:
    values = [function(x) for x in NODES]
    first = lagrange(NODES, values)
    second = newton(NODES, values)
    assert_vector_near(first.coefficients(), second.coefficients(), 1e-12)
    for x in (0.1, 0.7, 1.3):
        assert first(x) == pytest.approx(second(x), abs=1e-14)
        assert evaluate(first.coefficients(), x) == pytest.approx(first(x), abs=1e-14)


def test_cubic_is_reproduced_exactly() -> None:
    xs = [-1.0, 0.5, 2.0, 3.0]
    ys = [evaluate(CUBIC, x) for x in xs]
    assert_vector_near(lagrange(xs, ys).coefficients(), CUBIC, 1e-12)
    assert_vector_near(newton(xs, ys).coefficients(), CUBIC, 1e-12)
    assert newton(xs, ys).differences[-1] == pytest.approx(CUBIC[-1])


def test_weights_and_variant_errors() -> None:
    values = [function(x) for x in NODES]
    assert omega_derivative(NODES, 0) == pytest.approx(-(math.pi**3) / 36.0)
    assert lagrange(NODES, values).weights[0] == 0.0
    point = math.pi / 4.0
    assert abs(function(point) - lagrange(NODES, values)(point)) == pytest.approx(
        5.7705e-3, rel=1e-4
    )


def test_single_node_gives_a_constant() -> None:
    assert lagrange([1.0], [5.0])(10.0) == 5.0
    assert newton([1.0], [5.0]).coefficients() == [5.0]


def test_rejects_invalid_nodes() -> None:
    with pytest.raises(ValueError, match="equally many"):
        lagrange([0.0, 1.0], [1.0])
    with pytest.raises(ValueError, match="equally many"):
        newton([], [])
    with pytest.raises(ValueError, match="distinct"):
        newton([0.0, 0.0], [1.0, 2.0])


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)
    assert_expected_plot(figure_error, INPUT, ERROR_NAME)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2 0 1 0 1", "unexpected end of input"),
        ("2 0 1 0 1 0.5 1", "unexpected trailing input"),
        ("2 0 0 0 1 0.5", "distinct"),
        ("2 0 pi 0 1 x", "expected a number, got 'x'"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
