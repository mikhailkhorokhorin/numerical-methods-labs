import math

import pytest

from lab1.tests.support import assert_expected_output, assert_expected_plot, assert_task_error
from lab2.task1 import equation
from lab2.task1.equation import contraction_factor, newton, simple_iteration
from lab2.task1.main import (
    INPUT,
    f,
    f_derivative,
    f_second,
    figure,
    phi,
    phi_derivative,
    task,
)

ROOT = 1.1493622273539823


def test_variant_functions_are_consistent() -> None:
    for x in (1.0, 1.25, 1.5):
        step = 1e-6
        assert f_derivative(x) == pytest.approx((f(x + step) - f(x - step)) / (2 * step), rel=1e-6)
        assert f_second(x) == pytest.approx(
            (f_derivative(x + step) - f_derivative(x - step)) / (2 * step), rel=1e-6
        )
        assert phi_derivative(x) == pytest.approx(
            (phi(x + step) - phi(x - step)) / (2 * step), rel=1e-6
        )
    assert f(ROOT) == pytest.approx(0.0, abs=1e-12)
    assert phi(ROOT) == pytest.approx(ROOT, abs=1e-12)


@pytest.mark.parametrize("eps", [1e-2, 1e-6, 1e-10])
def test_both_methods_find_the_variant_root(eps: float) -> None:
    simple = simple_iteration(phi, phi_derivative, 1.0, 1.5, eps)
    tangent = newton(f, f_derivative, f_second, 1.0, 1.5, eps)
    assert simple.start == 1.25
    assert tangent.start == 1.5
    assert simple.value == pytest.approx(ROOT, abs=eps)
    assert tangent.value == pytest.approx(ROOT, abs=eps)
    assert simple.iterations[-1].error <= eps
    assert tangent.iterations[-1].error <= eps


def test_newton_converges_quadratically() -> None:
    errors = [
        abs(step.x - ROOT) for step in newton(f, f_derivative, f_second, 1.0, 1.5, 1e-12).iterations
    ]
    assert errors[3] < 10 * errors[2] ** 2
    assert errors[2] < 10 * errors[1] ** 2


def test_contraction_factor_of_the_variant() -> None:
    assert contraction_factor(phi_derivative, 1.0, 1.5) == pytest.approx(phi_derivative(1.0))


def test_newton_starts_from_the_end_with_matching_signs() -> None:
    root = newton(lambda x: x * x - 2.0, lambda x: 2.0 * x, lambda x: 2.0, 0.0, 2.0, 1e-12)
    assert root.start == 2.0
    assert root.value == pytest.approx(math.sqrt(2.0), abs=1e-12)


def test_rejects_invalid_intervals_and_precision() -> None:
    with pytest.raises(ValueError, match="a < b"):
        simple_iteration(phi, phi_derivative, 1.5, 1.0, 1e-6)
    with pytest.raises(ValueError, match="precision must be positive"):
        newton(f, f_derivative, f_second, 1.0, 1.5, 0.0)


def test_simple_iteration_checks_the_convergence_conditions() -> None:
    with pytest.raises(ValueError, match="not a contraction"):
        simple_iteration(lambda x: 2.0 * x, lambda x: 2.0, 0.0, 1.0, 1e-6)
    with pytest.raises(ValueError, match="outside itself"):
        simple_iteration(lambda x: x / 2.0 + 1.0, lambda x: 0.5, 0.0, 1.0, 1e-6)


def test_newton_checks_its_conditions() -> None:
    with pytest.raises(ValueError, match="same sign"):
        newton(f, f_derivative, f_second, 0.0, 1.0, 1e-6)
    with pytest.raises(ValueError, match="no end"):
        newton(lambda x: x, lambda x: 1.0, lambda x: 0.0, -1.0, 1.0, 1e-6)
    with pytest.raises(ValueError, match="vanishes"):
        newton(lambda x: x**3 - 1.0, lambda x: 0.0, lambda x: 6.0 * x, 0.0, 2.0, 1e-6)


def test_methods_stop_after_too_many_iterations(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(equation, "MAX_ITERATIONS", 2)
    with pytest.raises(RuntimeError, match="simple iteration did not converge"):
        simple_iteration(phi, phi_derivative, 1.0, 1.5, 1e-15)
    with pytest.raises(RuntimeError, match="Newton method did not converge"):
        newton(f, f_derivative, f_second, 1.0, 1.5, 1e-15)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("1 1.5", "unexpected end of input"),
        ("1 1.5 0", "precision must be positive"),
        ("1 1.5 1e-6 7", "unexpected trailing input"),
        ("0 1 1e-6", "outside itself"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
