from collections.abc import Callable
from dataclasses import dataclass

from lab1.common import Vector, step_count
from lab1.task2.tridiagonal import TridiagonalSystem, solve_tridiagonal
from lab4.task1.cauchy import CauchyProblem, adams

Coefficient = Callable[[float], float]

MAX_SHOTS = 100


@dataclass(frozen=True, slots=True)
class Condition:
    alpha: float
    beta: float
    gamma: float

    def residual(self, y: float, derivative: float) -> float:
        return self.alpha * y + self.beta * derivative - self.gamma


@dataclass(frozen=True, slots=True)
class BoundaryProblem:
    p: Coefficient
    q: Coefficient
    f: Coefficient
    left: float
    right: float
    left_condition: Condition
    right_condition: Condition

    def rhs(self, x: float, state: Vector) -> Vector:
        y, derivative = state
        return [derivative, self.f(x) - self.p(x) * derivative - self.q(x) * y]


@dataclass(frozen=True, slots=True)
class GridFunction:
    xs: Vector
    ys: Vector


@dataclass(frozen=True, slots=True)
class Shot:
    parameter: float
    residual: float


@dataclass(frozen=True, slots=True)
class Shooting:
    solution: GridFunction
    shots: list[Shot]


def _check(problem: BoundaryProblem) -> None:
    if not problem.left < problem.right:
        raise ValueError("the segment [a, b] must satisfy a < b")
    for condition in (problem.left_condition, problem.right_condition):
        if condition.alpha == 0.0 and condition.beta == 0.0:
            raise ValueError("a boundary condition needs a non-zero alpha or beta")


def _initial(condition: Condition, parameter: float) -> Vector:
    if condition.beta == 0.0:
        return [condition.gamma / condition.alpha, parameter]
    return [parameter, (condition.gamma - condition.alpha * parameter) / condition.beta]


def shooting(problem: BoundaryProblem, h: float, eps: float) -> Shooting:
    _check(problem)

    def shoot(parameter: float) -> tuple[Shot, GridFunction]:
        initial = _initial(problem.right_condition, parameter)
        cauchy = CauchyProblem(problem.rhs, problem.right, problem.left, initial)
        solution = adams(cauchy, h)
        y, derivative = solution.states[-1]
        shot = Shot(parameter, problem.left_condition.residual(y, derivative))
        return shot, GridFunction(solution.xs[::-1], solution.component(0)[::-1])

    previous, _ = shoot(0.0)
    current, grid = shoot(1.0)
    shots = [previous, current]
    while abs(current.residual) > eps:
        if len(shots) == MAX_SHOTS:
            raise RuntimeError("the shooting method did not converge")
        if current.residual == previous.residual:
            raise ValueError("the secant method stalled on equal residuals")
        slope = (current.residual - previous.residual) / (current.parameter - previous.parameter)
        previous = current
        current, grid = shoot(current.parameter - current.residual / slope)
        shots.append(current)
    return Shooting(grid, shots)


def finite_difference(problem: BoundaryProblem, h: float) -> GridFunction:
    _check(problem)
    n = step_count(problem.left, problem.right, h)
    if n < 2:
        raise ValueError("the finite difference method needs at least two steps")
    step = (problem.right - problem.left) / n
    xs = [problem.left + i * step for i in range(n + 1)]
    lower = [0.0] * (n + 1)
    diagonal = [0.0] * (n + 1)
    upper = [0.0] * (n + 1)
    rhs = [0.0] * (n + 1)
    for i in range(1, n):
        p = problem.p(xs[i])
        lower[i] = 1.0 / step**2 - p / (2.0 * step)
        diagonal[i] = -2.0 / step**2 + problem.q(xs[i])
        upper[i] = 1.0 / step**2 + p / (2.0 * step)
        rhs[i] = problem.f(xs[i])

    left = problem.left_condition
    extra = -left.beta / (2.0 * step)
    factor = extra / upper[1] if extra != 0.0 else 0.0
    diagonal[0] = left.alpha - 3.0 * left.beta / (2.0 * step) - factor * lower[1]
    upper[0] = 4.0 * left.beta / (2.0 * step) - factor * diagonal[1]
    rhs[0] = left.gamma - factor * rhs[1]

    right = problem.right_condition
    extra = right.beta / (2.0 * step)
    factor = extra / lower[n - 1] if extra != 0.0 else 0.0
    diagonal[n] = right.alpha + 3.0 * right.beta / (2.0 * step) - factor * upper[n - 1]
    lower[n] = -4.0 * right.beta / (2.0 * step) - factor * diagonal[n - 1]
    rhs[n] = right.gamma - factor * rhs[n - 1]

    ys = solve_tridiagonal(TridiagonalSystem(lower[1:], diagonal, upper[:-1], rhs))
    return GridFunction(xs, ys)
