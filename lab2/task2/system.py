from collections.abc import Callable
from dataclasses import dataclass
from itertools import product

from lab1.common import Matrix, Vector, linspace, matmul, matrix_norm_inf, matvec, norm_inf
from lab1.task1.lu import LuDecomposition, decompose_lu, inverse, solve_lu

MAX_ITERATIONS = 10000
SAMPLES = 41

Region = list[tuple[float, float]]


@dataclass(frozen=True, slots=True)
class NonlinearSystem:
    function: Callable[[Vector], Vector]
    jacobian: Callable[[Vector], Matrix]


@dataclass(frozen=True, slots=True)
class Iteration:
    x: Vector
    error: float


@dataclass(frozen=True, slots=True)
class Solution:
    start: Vector
    iterations: list[Iteration]

    @property
    def value(self) -> Vector:
        return self.iterations[-1].x


def center(region: Region) -> Vector:
    return [(low + high) / 2.0 for low, high in region]


def _check(region: Region, eps: float) -> None:
    if not region or any(not low < high for low, high in region):
        raise ValueError("every range of the region must satisfy low < high")
    if eps <= 0.0:
        raise ValueError("precision must be positive")


def _decompose(matrix: Matrix) -> LuDecomposition:
    try:
        return decompose_lu(matrix)
    except ValueError:
        raise ValueError("the Jacobian matrix is singular") from None


def _evaluate(system: NonlinearSystem, x: Vector) -> Vector:
    values = system.function(x)
    if len(values) != len(x):
        raise ValueError("the system must have as many equations as unknowns")
    return values


def _grid(region: Region) -> list[Vector]:
    axes = [linspace(low, high, SAMPLES) for low, high in region]
    return [list(point) for point in product(*axes)]


def _inside(x: Vector, region: Region) -> bool:
    return all(low <= value <= high for value, (low, high) in zip(x, region, strict=True))


def _preconditioner(system: NonlinearSystem, region: Region) -> Matrix:
    middle = center(region)
    _evaluate(system, middle)
    return inverse(_decompose(system.jacobian(middle)))


def _factor(system: NonlinearSystem, region: Region, preconditioner: Matrix) -> float:
    result = 0.0
    for x in _grid(region):
        product_matrix = matmul(preconditioner, system.jacobian(x))
        derivative = [
            [(1.0 if i == j else 0.0) - value for j, value in enumerate(row)]
            for i, row in enumerate(product_matrix)
        ]
        result = max(result, matrix_norm_inf(derivative))
    return result


def contraction_factor(system: NonlinearSystem, region: Region) -> float:
    return _factor(system, region, _preconditioner(system, region))


def simple_iteration(system: NonlinearSystem, region: Region, eps: float) -> Solution:
    _check(region, eps)
    preconditioner = _preconditioner(system, region)

    def phi(x: Vector) -> Vector:
        shift = matvec(preconditioner, _evaluate(system, x))
        return [value - delta for value, delta in zip(x, shift, strict=True)]

    q = _factor(system, region, preconditioner)
    if q >= 1.0:
        raise ValueError(f"phi is not a contraction in the region: q = {q:.4f}")
    if not all(_inside(phi(x), region) for x in _grid(region)):
        raise ValueError("phi maps the region outside itself")
    start = center(region)
    x = start
    iterations: list[Iteration] = []
    while len(iterations) < MAX_ITERATIONS:
        following = phi(x)
        error = q / (1.0 - q) * norm_inf([a - b for a, b in zip(following, x, strict=True)])
        iterations.append(Iteration(following, error))
        x = following
        if error <= eps:
            return Solution(start, iterations)
    raise RuntimeError("simple iteration did not converge")


def newton(system: NonlinearSystem, start: Vector, eps: float) -> Solution:
    if eps <= 0.0:
        raise ValueError("precision must be positive")
    x = start
    iterations: list[Iteration] = []
    while len(iterations) < MAX_ITERATIONS:
        rhs = [-value for value in _evaluate(system, x)]
        delta = solve_lu(_decompose(system.jacobian(x)), rhs)
        following = [value + step for value, step in zip(x, delta, strict=True)]
        iterations.append(Iteration(following, norm_inf(delta)))
        x = following
        if iterations[-1].error <= eps:
            return Solution(start, iterations)
    raise RuntimeError("the Newton method did not converge")
