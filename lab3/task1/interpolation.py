from dataclasses import dataclass

from lab1.common import Vector
from lab3.common import multiply_linear


@dataclass(frozen=True, slots=True)
class Lagrange:
    nodes: Vector
    weights: Vector

    def __call__(self, x: float) -> float:
        total = 0.0
        for i, weight in enumerate(self.weights):
            term = weight
            for j, node in enumerate(self.nodes):
                if j != i:
                    term *= x - node
            total += term
        return total

    def coefficients(self) -> Vector:
        result = [0.0] * len(self.nodes)
        for i, weight in enumerate(self.weights):
            basis = [1.0]
            for j, node in enumerate(self.nodes):
                if j != i:
                    basis = multiply_linear(basis, node)
            for power, value in enumerate(basis):
                result[power] += weight * value
        return result


@dataclass(frozen=True, slots=True)
class Newton:
    nodes: Vector
    differences: Vector

    def __call__(self, x: float) -> float:
        result = 0.0
        for node, difference in zip(reversed(self.nodes), reversed(self.differences), strict=True):
            result = result * (x - node) + difference
        return result

    def coefficients(self) -> Vector:
        result = [0.0]
        for node, difference in zip(reversed(self.nodes), reversed(self.differences), strict=True):
            result = multiply_linear(result, node)
            result[0] += difference
        return result[: len(self.nodes)]


def _check(xs: Vector, ys: Vector) -> None:
    if not xs or len(xs) != len(ys):
        raise ValueError("interpolation needs equally many nodes and values")
    if len(set(xs)) != len(xs):
        raise ValueError("interpolation nodes must be distinct")


def omega_derivative(xs: Vector, i: int) -> float:
    result = 1.0
    for j, node in enumerate(xs):
        if j != i:
            result *= xs[i] - node
    return result


def lagrange(xs: Vector, ys: Vector) -> Lagrange:
    _check(xs, ys)
    return Lagrange(xs[:], [y / omega_derivative(xs, i) for i, y in enumerate(ys)])


def newton(xs: Vector, ys: Vector) -> Newton:
    _check(xs, ys)
    table = ys[:]
    differences = [table[0]]
    for order in range(1, len(xs)):
        table = [(table[i + 1] - table[i]) / (xs[i + order] - xs[i]) for i in range(len(table) - 1)]
        differences.append(table[0])
    return Newton(xs[:], differences)
