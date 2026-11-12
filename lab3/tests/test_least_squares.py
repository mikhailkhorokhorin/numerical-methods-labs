import pytest

from lab1.tests.support import (
    assert_expected_output,
    assert_expected_plot,
    assert_task_error,
    assert_vector_near,
)
from lab3.common import evaluate
from lab3.task3.least_squares import least_squares
from lab3.task3.main import INPUT, figure, task

XS = [-1.0, 0.0, 1.0, 2.0, 3.0, 5.0]
YS = [-0.86603, 0.0, 0.86603, 1.0, 0.0, -4.3301]


def test_exact_polynomial_data_is_fitted_exactly() -> None:
    coefficients = [1.0, -2.0, 0.5]
    ys = [evaluate(coefficients, x) for x in XS]
    approximation = least_squares(XS, ys, 2)
    assert_vector_near(approximation.coefficients, coefficients, 1e-10)
    assert approximation.squared_error == pytest.approx(0.0, abs=1e-18)


def test_normal_system_of_the_variant() -> None:
    approximation = least_squares(XS, YS, 1)
    assert approximation.matrix == [[6.0, 10.0], [10.0, 40.0]]
    assert approximation.rhs == pytest.approx([-3.3301, -17.9184], abs=1e-4)
    assert_vector_near(approximation.coefficients, [0.32843, -0.53007], 1e-5)
    assert approximation(1.0) == pytest.approx(0.32843 - 0.53007, abs=1e-5)


def test_higher_degree_reduces_the_error() -> None:
    errors = [least_squares(XS, YS, degree).squared_error for degree in (0, 1, 2, 3)]
    assert errors == sorted(errors, reverse=True)
    assert errors[2] == pytest.approx(0.2101, abs=5e-5)


def test_residuals_are_orthogonal_to_the_basis() -> None:
    approximation = least_squares(XS, YS, 2)
    residuals = [approximation(x) - y for x, y in zip(XS, YS, strict=True)]
    for power in range(3):
        assert sum(r * x**power for r, x in zip(residuals, XS, strict=True)) == pytest.approx(
            0.0, abs=1e-10
        )


def test_rejects_invalid_data() -> None:
    with pytest.raises(ValueError, match="equally many"):
        least_squares([0.0, 1.0], [1.0], 1)
    with pytest.raises(ValueError, match="more than 1 distinct points"):
        least_squares([1.0, 1.0, 1.0], [1.0, 2.0, 3.0], 1)
    with pytest.raises(ValueError, match="degree -1"):
        least_squares(XS, YS, -1)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2 0 1 0 1", "more than 2 distinct points"),
        ("3 0 1 2 0 1", "unexpected end of input"),
        ("3 0 1 2 0 1 4 5", "unexpected trailing input"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
