from collections.abc import Callable

from lab1.common import Vector
from lab3.task5.integration import runge_romberg


def runge_romberg_error(coarse: Vector, fine: Vector, order: int) -> float:
    if len(fine) != 2 * len(coarse) - 1:
        raise ValueError("the fine grid must have half the step of the coarse grid")
    return max(abs(runge_romberg(value, fine[2 * i], 2.0, order)) for i, value in enumerate(coarse))


def max_error(xs: Vector, ys: Vector, exact: Callable[[float], float]) -> float:
    return max(abs(y - exact(x)) for x, y in zip(xs, ys, strict=True))
