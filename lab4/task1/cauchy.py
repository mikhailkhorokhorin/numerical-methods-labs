from collections.abc import Callable
from dataclasses import dataclass

from lab1.common import Vector, step_count

Rhs = Callable[[float, Vector], Vector]

ADAMS_WEIGHTS = (55.0, -59.0, 37.0, -9.0)


@dataclass(frozen=True, slots=True)
class CauchyProblem:
    rhs: Rhs
    start: float
    end: float
    initial: Vector


@dataclass(frozen=True, slots=True)
class Solution:
    xs: Vector
    states: list[Vector]

    def component(self, index: int) -> Vector:
        return [state[index] for state in self.states]


Method = Callable[[CauchyProblem, float], Solution]


def _grid(problem: CauchyProblem, h: float) -> tuple[Vector, float]:
    n = step_count(problem.start, problem.end, h)
    step = (problem.end - problem.start) / n
    return [problem.start + i * step for i in range(n + 1)], step


def _shift(state: Vector, slope: Vector, step: float) -> Vector:
    return [value + step * rate for value, rate in zip(state, slope, strict=True)]


def _runge_kutta_step(rhs: Rhs, x: float, state: Vector, step: float) -> Vector:
    k1 = rhs(x, state)
    k2 = rhs(x + step / 2.0, _shift(state, k1, step / 2.0))
    k3 = rhs(x + step / 2.0, _shift(state, k2, step / 2.0))
    k4 = rhs(x + step, _shift(state, k3, step))
    slope = [(a + 2.0 * b + 2.0 * c + d) / 6.0 for a, b, c, d in zip(k1, k2, k3, k4, strict=True)]
    return _shift(state, slope, step)


def euler(problem: CauchyProblem, h: float) -> Solution:
    xs, step = _grid(problem, h)
    states = [problem.initial[:]]
    for x in xs[:-1]:
        states.append(_shift(states[-1], problem.rhs(x, states[-1]), step))
    return Solution(xs, states)


def runge_kutta(problem: CauchyProblem, h: float) -> Solution:
    xs, step = _grid(problem, h)
    states = [problem.initial[:]]
    for x in xs[:-1]:
        states.append(_runge_kutta_step(problem.rhs, x, states[-1], step))
    return Solution(xs, states)


def adams(problem: CauchyProblem, h: float) -> Solution:
    xs, step = _grid(problem, h)
    states = [problem.initial[:]]
    slopes: list[Vector] = []
    for i, x in enumerate(xs[:-1]):
        slopes.append(problem.rhs(x, states[i]))
        if i < len(ADAMS_WEIGHTS) - 1:
            states.append(_runge_kutta_step(problem.rhs, x, states[i], step))
            continue
        history = slopes[-1 : -len(ADAMS_WEIGHTS) - 1 : -1]
        slope = [
            sum(weight * rates[k] for weight, rates in zip(ADAMS_WEIGHTS, history, strict=True))
            / 24.0
            for k in range(len(states[i]))
        ]
        states.append(_shift(states[i], slope, step))
    return Solution(xs, states)
