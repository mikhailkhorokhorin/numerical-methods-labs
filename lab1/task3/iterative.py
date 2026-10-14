import math
from collections.abc import Callable
from dataclasses import dataclass

from lab1.common import (
    Matrix,
    Vector,
    distance_inf,
    is_square,
    matrix_norm_inf,
    matvec,
    norm_inf,
)

MAX_ITERATIONS = 100000
MAX_ESTIMATE = 2**64


@dataclass(frozen=True, slots=True)
class IterationForm:
    alpha: Matrix
    beta: Vector


@dataclass(frozen=True, slots=True)
class IterationResult:
    solution: Vector
    iterations: int
    converged: bool


def _upper_norm_inf(matrix: Matrix) -> float:
    result = 0.0
    for i, row in enumerate(matrix):
        row_sum = 0.0
        for value in row[i + 1 :]:
            row_sum += abs(value)
        result = max(result, row_sum)
    return result


def _iterate(
    form: IterationForm, eps: float, factor: float, step: Callable[[Vector], Vector]
) -> IterationResult:
    solution = form.beta
    iterations = 0
    while iterations < MAX_ITERATIONS:
        following = step(solution)
        iterations += 1
        if not all(math.isfinite(value) for value in following):
            return IterationResult(solution, iterations, converged=False)
        error = factor * distance_inf(following, solution)
        solution = following
        if error <= eps:
            return IterationResult(solution, iterations, converged=True)
    return IterationResult(solution, iterations, converged=False)


def to_iteration_form(matrix: Matrix, rhs: Vector) -> IterationForm:
    if not matrix or not is_square(matrix) or len(rhs) != len(matrix):
        raise ValueError("iterative methods need a square matrix and a matching rhs")
    n = len(matrix)
    alpha = [[0.0] * n for _ in range(n)]
    beta = [0.0] * n
    for i in range(n):
        diagonal = matrix[i][i]
        if diagonal == 0.0:
            raise ValueError("zero on the main diagonal")
        beta[i] = rhs[i] / diagonal
        for j in range(n):
            alpha[i][j] = 0.0 if i == j else -matrix[i][j] / diagonal
    return IterationForm(alpha, beta)


def simple_iteration(matrix: Matrix, rhs: Vector, eps: float) -> IterationResult:
    form = to_iteration_form(matrix, rhs)
    alpha_norm = matrix_norm_inf(form.alpha)
    factor = alpha_norm / (1.0 - alpha_norm) if alpha_norm < 1.0 else 1.0

    def step(current: Vector) -> Vector:
        following = matvec(form.alpha, current)
        for i in range(len(following)):
            following[i] += form.beta[i]
        return following

    return _iterate(form, eps, factor, step)


def seidel(matrix: Matrix, rhs: Vector, eps: float) -> IterationResult:
    form = to_iteration_form(matrix, rhs)
    alpha_norm = matrix_norm_inf(form.alpha)
    factor = _upper_norm_inf(form.alpha) / (1.0 - alpha_norm) if alpha_norm < 1.0 else 1.0

    def step(current: Vector) -> Vector:
        following = current[:]
        for i, row in enumerate(form.alpha):
            value = form.beta[i]
            for j, coefficient in enumerate(row):
                value += coefficient * following[j]
            following[i] = value
        return following

    return _iterate(form, eps, factor, step)


def apriori_iterations(matrix: Matrix, rhs: Vector, eps: float) -> int | None:
    form = to_iteration_form(matrix, rhs)
    alpha_norm = matrix_norm_inf(form.alpha)
    beta_norm = norm_inf(form.beta)
    if alpha_norm >= 1.0:
        return None
    if alpha_norm == 0.0 or beta_norm == 0.0:
        return 0
    bound = (math.log(eps) - math.log(beta_norm) + math.log(1.0 - alpha_norm)) / math.log(
        alpha_norm
    )
    if not math.isfinite(bound) or bound >= MAX_ESTIMATE:
        return None
    return 0 if bound <= 1.0 else math.ceil(bound - 1.0)
