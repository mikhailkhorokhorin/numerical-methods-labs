from bisect import bisect_right
from dataclasses import dataclass

from lab1.common import Vector
from lab1.task2.tridiagonal import TridiagonalSystem, solve_tridiagonal
from lab3.common import check_increasing


@dataclass(frozen=True, slots=True)
class Spline:
    nodes: Vector
    a: Vector
    b: Vector
    c: Vector
    d: Vector

    def __call__(self, x: float) -> float:
        if not self.nodes[0] <= x <= self.nodes[-1]:
            raise ValueError("the point lies outside the spline nodes")
        i = min(bisect_right(self.nodes, x) - 1, len(self.a) - 1)
        t = x - self.nodes[i]
        return self.a[i] + self.b[i] * t + self.c[i] * t**2 + self.d[i] * t**3


def natural_spline(xs: Vector, ys: Vector) -> Spline:
    if len(xs) < 2 or len(xs) != len(ys):
        raise ValueError("a spline needs at least two nodes with values")
    check_increasing(xs)
    n = len(xs) - 1
    h = [xs[i + 1] - xs[i] for i in range(n)]
    slopes = [(ys[i + 1] - ys[i]) / h[i] for i in range(n)]
    c = [0.0] * (n + 1)
    if n > 1:
        system = TridiagonalSystem(
            lower=h[1 : n - 1],
            diagonal=[2.0 * (h[i - 1] + h[i]) for i in range(1, n)],
            upper=h[1 : n - 1],
            rhs=[3.0 * (slopes[i] - slopes[i - 1]) for i in range(1, n)],
        )
        c[1:n] = solve_tridiagonal(system)
    return Spline(
        nodes=xs[:],
        a=ys[:n],
        b=[slopes[i] - h[i] * (c[i + 1] + 2.0 * c[i]) / 3.0 for i in range(n)],
        c=c[:n],
        d=[(c[i + 1] - c[i]) / (3.0 * h[i]) for i in range(n)],
    )
