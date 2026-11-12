import math

import pytest

from lab1.tests.support import assert_expected_output, assert_task_error
from lab3.task5.integration import METHODS, rectangles, runge_romberg, simpson, trapezoids
from lab3.task5.main import INPUT, antiderivative, function, task


def test_antiderivative_matches_the_function() -> None:
    step = 1e-6
    for x in (1.0, 2.5, 5.0):
        slope = (antiderivative(x + step) - antiderivative(x - step)) / (2 * step)
        assert slope == pytest.approx(function(x), rel=1e-7)


def test_rules_are_exact_for_low_degree_polynomials() -> None:
    assert rectangles(lambda x: 3.0 * x + 1.0, 0.0, 2.0, 0.5) == pytest.approx(8.0)
    assert trapezoids(lambda x: 3.0 * x + 1.0, 0.0, 2.0, 0.5) == pytest.approx(8.0)
    assert simpson(lambda x: x**3 - x, 0.0, 2.0, 0.5) == pytest.approx(2.0)


def test_rules_converge_with_their_orders() -> None:
    exact = 1.0 - math.cos(1.0)
    for name, rule, order in METHODS:
        coarse = abs(rule(math.sin, 0.0, 1.0, 0.1) - exact)
        fine = abs(rule(math.sin, 0.0, 1.0, 0.05) - exact)
        assert coarse / fine == pytest.approx(2.0**order, rel=0.05), name


def test_reversed_limits_change_the_sign() -> None:
    assert simpson(math.exp, 1.0, 0.0, 0.25) == pytest.approx(-simpson(math.exp, 0.0, 1.0, 0.25))


def test_runge_romberg_refines_the_variant() -> None:
    exact = antiderivative(5.0) - antiderivative(1.0)
    for _, rule, order in METHODS:
        coarse = rule(function, 1.0, 5.0, 1.0)
        fine = rule(function, 1.0, 5.0, 0.5)
        refined = fine + runge_romberg(coarse, fine, 2.0, order)
        assert abs(refined - exact) < abs(fine - exact) / 100.0


def test_rejects_invalid_steps() -> None:
    with pytest.raises(ValueError, match="even number of steps"):
        simpson(math.sin, 0.0, 3.0, 1.0)
    with pytest.raises(ValueError, match="does not divide"):
        trapezoids(math.sin, 0.0, 1.0, 0.3)
    with pytest.raises(ValueError, match="coarse step larger"):
        runge_romberg(1.0, 2.0, 1.0, 2)


def test_task_prints_the_expected_output() -> None:
    assert_expected_output(task, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("1 5 1", "unexpected end of input"),
        ("1 5 1 0", "precision must be positive"),
        ("1 5 0.5 1", "coarse step larger"),
        ("1 4 1 0.5", "even number of steps"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
