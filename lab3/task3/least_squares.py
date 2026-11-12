from dataclasses import dataclass

from lab1.common import Matrix, Vector
from lab1.task1.lu import decompose_lu, solve_lu
from lab3.common import evaluate


@dataclass(frozen=True, slots=True)
class Approximation:
    matrix: Matrix
    rhs: Vector
    coefficients: Vector
    squared_error: float

    def __call__(self, x: float) -> float:
        return evaluate(self.coefficients, x)


def least_squares(xs: Vector, ys: Vector, degree: int) -> Approximation:
    if len(xs) != len(ys):
        raise ValueError("least squares needs equally many points and values")
    if degree < 0 or len(set(xs)) <= degree:
        raise ValueError(
            f"a polynomial of degree {degree} needs more than {degree} distinct points"
        )
    size = degree + 1
    powers = [sum(x**k for x in xs) for k in range(2 * size - 1)]
    matrix = [[powers[i + j] for j in range(size)] for i in range(size)]
    rhs = [sum(y * x**i for x, y in zip(xs, ys, strict=True)) for i in range(size)]
    coefficients = solve_lu(decompose_lu(matrix), rhs)
    squared_error = sum((evaluate(coefficients, x) - y) ** 2 for x, y in zip(xs, ys, strict=True))
    return Approximation(matrix, rhs, coefficients, squared_error)
