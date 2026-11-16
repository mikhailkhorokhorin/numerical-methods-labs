import math

import pytest

from lab1.common import InputReader
from lab1.tests.support import assert_expected_output, assert_expected_plot, assert_task_error
from lab3.task4.derivative import derivatives
from lab3.task4.main import INPUT, figure, task

XS = [0.0, 0.2, 0.4, 0.6, 0.8]
YS = [0.0, 0.048856, 0.23869, 0.65596, 1.4243]


def test_variant_derivatives() -> None:
    result = derivatives(XS, YS, 0.4)
    assert result.left == pytest.approx((YS[2] - YS[1]) / 0.2)
    assert result.right == pytest.approx((YS[3] - YS[2]) / 0.2)
    assert result.first == pytest.approx((YS[3] - YS[1]) / 0.4)
    assert result.second == pytest.approx((YS[3] - 2.0 * YS[2] + YS[1]) / 0.04)
    exact = math.exp(0.4)
    assert result.first == pytest.approx(exact * (0.8 + 0.16), abs=0.1)
    assert result.second == pytest.approx(exact * (2.0 + 1.6 + 0.16), abs=0.1)


def test_quadratic_is_differentiated_exactly() -> None:
    xs = [0.0, 0.5, 1.5, 2.0]
    ys = [x**2 - 3.0 * x + 1.0 for x in xs]
    for point in (0.0, 0.3, 0.5, 1.0, 2.0):
        result = derivatives(xs, ys, point)
        assert result.first == pytest.approx(2.0 * point - 3.0)
        assert result.second == pytest.approx(2.0)


def test_one_sided_differences_inside_a_segment_and_at_the_ends() -> None:
    xs = [0.0, 1.0, 2.0]
    ys = [0.0, 1.0, 4.0]
    inside = derivatives(xs, ys, 0.5)
    assert inside.left == inside.right == 1.0
    assert derivatives(xs, ys, 0.0).left == 1.0
    assert derivatives(xs, ys, 2.0).right == 3.0


def test_rejects_invalid_tables_and_points() -> None:
    with pytest.raises(ValueError, match="at least three nodes"):
        derivatives([0.0, 1.0], [0.0, 1.0], 0.5)
    with pytest.raises(ValueError, match="at least three nodes"):
        derivatives([0.0, 1.0, 2.0], [0.0, 1.0], 0.5)
    with pytest.raises(ValueError, match="strictly increasing"):
        derivatives([0.0, 2.0, 1.0], [0.0, 1.0, 2.0], 0.5)
    with pytest.raises(ValueError, match="outside the table"):
        derivatives(XS, YS, 1.0)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)


def test_plot_draws_slopes_through_a_point_between_nodes() -> None:
    svg = figure(InputReader("3 0 1 2 0 1 4 0.5"))
    assert "Derivative at X* = 0.5" in svg
    assert "second order: y&#x27; = 1.0000" in svg


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2 0 1 0 1 0.5", "expected a size from 3"),
        ("3 0 1 2 0 1 4", "unexpected end of input"),
        ("3 0 1 2 0 1 4 3", "outside the table"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
