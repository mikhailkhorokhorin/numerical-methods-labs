import random

import pytest

from lab1.common import Matrix, zeros
from lab1.task1.lu import decompose_lu, solve_lu
from lab1.task2.main import INPUT, task
from lab1.task2.tridiagonal import TridiagonalSystem, meets_stability_condition, solve_tridiagonal
from lab1.tests.support import (
    assert_expected_output,
    assert_task_error,
    assert_vector_near,
)

VARIANT = TridiagonalSystem(
    lower=[8.0, -3.0, -9.0, 1.0],
    diagonal=[16.0, -13.0, -21.0, 16.0, -9.0],
    upper=[-9.0, -5.0, 9.0, -5.0],
    rhs=[-27.0, -84.0, -225.0, -89.0, 69.0],
)


def to_matrix(system: TridiagonalSystem) -> Matrix:
    n = len(system.diagonal)
    result = zeros(n, n)
    for i in range(n):
        result[i][i] = system.diagonal[i]
        if i > 0:
            result[i][i - 1] = system.lower[i - 1]
        if i + 1 < n:
            result[i][i + 1] = system.upper[i]
    return result


def test_solves_variant() -> None:
    assert_vector_near(solve_tridiagonal(VARIANT), [0.0, 3.0, 9.0, -3.0, -8.0], 1e-12)
    assert meets_stability_condition(VARIANT)


@pytest.mark.parametrize("n", range(1, 13))
def test_matches_lu_on_random_systems(n: int) -> None:
    generator = random.Random(n)
    system = TridiagonalSystem(
        lower=[generator.uniform(-10.0, 10.0) for _ in range(n - 1)],
        diagonal=[25.0 + generator.uniform(-10.0, 10.0) for _ in range(n)],
        upper=[generator.uniform(-10.0, 10.0) for _ in range(n - 1)],
        rhs=[generator.uniform(-10.0, 10.0) for _ in range(n)],
    )
    expected = solve_lu(decompose_lu(to_matrix(system)), system.rhs)
    assert_vector_near(solve_tridiagonal(system), expected, 1e-10)


def test_solves_single_equation() -> None:
    system = TridiagonalSystem(lower=[], diagonal=[4.0], upper=[], rhs=[8.0])
    assert solve_tridiagonal(system) == [2.0]


@pytest.mark.parametrize(
    "system",
    [
        TridiagonalSystem(lower=[1.0], diagonal=[1.0, 2.0], upper=[], rhs=[1.0, 2.0]),
        TridiagonalSystem(lower=[], diagonal=[], upper=[], rhs=[]),
    ],
)
def test_rejects_inconsistent_sizes(system: TridiagonalSystem) -> None:
    with pytest.raises(ValueError, match="inconsistent sizes"):
        solve_tridiagonal(system)
    with pytest.raises(ValueError, match="inconsistent sizes"):
        meets_stability_condition(system)


def test_rejects_zero_denominator() -> None:
    system = TridiagonalSystem(lower=[1.0], diagonal=[0.0, 1.0], upper=[1.0], rhs=[1.0, 1.0])
    with pytest.raises(ValueError, match="zero denominator"):
        solve_tridiagonal(system)


def test_checks_stability_condition() -> None:
    weak = TridiagonalSystem(lower=[1.0], diagonal=[1.0, 1.0], upper=[1.0], rhs=[0.0, 0.0])
    violated = TridiagonalSystem(lower=[3.0], diagonal=[5.0, 1.0], upper=[1.0], rhs=[0.0, 0.0])
    decoupled = TridiagonalSystem(
        lower=[1.0, 0.0], diagonal=[1.0, 1.0, 1.0], upper=[1.0, 0.0], rhs=[1.0, 1.0, 1.0]
    )
    assert not meets_stability_condition(weak)
    assert not meets_stability_condition(violated)
    assert not meets_stability_condition(decoupled)
    with pytest.raises(ValueError, match="zero denominator"):
        solve_tridiagonal(decoupled)


def test_main_prints_expected_output() -> None:
    assert_expected_output(task, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("2\n1\n0 1\n1\n1 1\n", "zero denominator"),
    ],
)
def test_reports_input_and_method_errors(text: str, message: str) -> None:
    assert_task_error(task, text, message)
