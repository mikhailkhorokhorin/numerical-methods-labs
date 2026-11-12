from bisect import bisect_left, bisect_right
from dataclasses import dataclass

from lab1.common import Vector
from lab3.common import check_increasing


@dataclass(frozen=True, slots=True)
class Derivatives:
    left: float
    right: float
    first: float
    second: float


def _slope(xs: Vector, ys: Vector, i: int) -> float:
    return (ys[i + 1] - ys[i]) / (xs[i + 1] - xs[i])


def derivatives(xs: Vector, ys: Vector, point: float) -> Derivatives:
    if len(xs) < 3 or len(xs) != len(ys):
        raise ValueError("numerical differentiation needs at least three nodes with values")
    check_increasing(xs)
    if not xs[0] <= point <= xs[-1]:
        raise ValueError("the point lies outside the table")
    last = len(xs) - 2
    left = min(max(bisect_left(xs, point) - 1, 0), last)
    right = min(max(bisect_right(xs, point) - 1, 0), last)
    i = min(left, last - 1)
    first_slope = _slope(xs, ys, i)
    second_slope = _slope(xs, ys, i + 1)
    curvature = (second_slope - first_slope) / (xs[i + 2] - xs[i])
    return Derivatives(
        left=_slope(xs, ys, left),
        right=_slope(xs, ys, right),
        first=first_slope + curvature * (2.0 * point - xs[i] - xs[i + 1]),
        second=2.0 * curvature,
    )
