from collections.abc import Callable
from dataclasses import dataclass

from lab1.common import linspace

Function = Callable[[float], float]

MAX_ITERATIONS = 10000
SAMPLES = 1001


@dataclass(frozen=True, slots=True)
class Iteration:
    x: float
    error: float


@dataclass(frozen=True, slots=True)
class Root:
    start: float
    iterations: list[Iteration]

    @property
    def value(self) -> float:
        return self.iterations[-1].x


def _check(a: float, b: float, eps: float) -> None:
    if not a < b:
        raise ValueError("the interval [a, b] must satisfy a < b")
    if eps <= 0.0:
        raise ValueError("precision must be positive")


def contraction_factor(phi_derivative: Function, a: float, b: float) -> float:
    return max(abs(phi_derivative(x)) for x in linspace(a, b, SAMPLES))


def simple_iteration(
    phi: Function, phi_derivative: Function, a: float, b: float, eps: float
) -> Root:
    _check(a, b, eps)
    q = contraction_factor(phi_derivative, a, b)
    if q >= 1.0:
        raise ValueError(f"phi is not a contraction on [a, b]: q = {q:.4f}")
    if not all(a <= phi(x) <= b for x in linspace(a, b, SAMPLES)):
        raise ValueError("phi maps [a, b] outside itself")
    start = (a + b) / 2.0
    x = start
    iterations: list[Iteration] = []
    while len(iterations) < MAX_ITERATIONS:
        following = phi(x)
        error = q / (1.0 - q) * abs(following - x)
        iterations.append(Iteration(following, error))
        x = following
        if error <= eps:
            return Root(start, iterations)
    raise RuntimeError("simple iteration did not converge")


def newton(
    f: Function, derivative: Function, second: Function, a: float, b: float, eps: float
) -> Root:
    _check(a, b, eps)
    if f(a) * f(b) > 0.0:
        raise ValueError("f has the same sign at both ends of [a, b]")
    start = next((x for x in (a, b) if f(x) * second(x) > 0.0), None)
    if start is None:
        raise ValueError("no end of [a, b] satisfies f(x0) f''(x0) > 0")
    x = start
    iterations: list[Iteration] = []
    while len(iterations) < MAX_ITERATIONS:
        slope = derivative(x)
        if slope == 0.0:
            raise ValueError("f'(x) vanishes during the Newton iterations")
        following = x - f(x) / slope
        error = abs(following - x)
        iterations.append(Iteration(following, error))
        x = following
        if error <= eps:
            return Root(start, iterations)
    raise RuntimeError("the Newton method did not converge")
