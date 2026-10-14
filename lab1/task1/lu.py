from dataclasses import dataclass

from lab1.common import (
    Matrix,
    Vector,
    copy_matrix,
    identity,
    is_square,
    matrix_norm_inf,
    zeros,
)

SINGULARITY_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class LuDecomposition:
    lower: Matrix
    upper: Matrix
    permutation: list[int]
    sign: int


def decompose_lu(matrix: Matrix) -> LuDecomposition:
    if not matrix or not is_square(matrix):
        raise ValueError("LU decomposition needs a non-empty square matrix")
    n = len(matrix)
    threshold = SINGULARITY_TOLERANCE * matrix_norm_inf(matrix)
    lower = identity(n)
    upper = copy_matrix(matrix)
    permutation = list(range(n))
    sign = 1

    for k in range(n):
        pivot = k
        for i in range(k + 1, n):
            if abs(upper[i][k]) > abs(upper[pivot][k]):
                pivot = i
        if abs(upper[pivot][k]) <= threshold:
            raise ValueError("matrix is singular")
        if pivot != k:
            upper[k], upper[pivot] = upper[pivot], upper[k]
            for j in range(k):
                lower[k][j], lower[pivot][j] = lower[pivot][j], lower[k][j]
            permutation[k], permutation[pivot] = permutation[pivot], permutation[k]
            sign = -sign
        for i in range(k + 1, n):
            factor = upper[i][k] / upper[k][k]
            lower[i][k] = factor
            upper[i][k] = 0.0
            for j in range(k + 1, n):
                upper[i][j] -= factor * upper[k][j]
    return LuDecomposition(lower, upper, permutation, sign)


def solve_lu(lu: LuDecomposition, rhs: Vector) -> Vector:
    n = len(lu.upper)
    if len(rhs) != n:
        raise ValueError("right-hand side size does not match the matrix")
    solution = [0.0] * n
    for i in range(n):
        total = rhs[lu.permutation[i]]
        for j in range(i):
            total -= lu.lower[i][j] * solution[j]
        solution[i] = total
    for i in reversed(range(n)):
        total = solution[i]
        for j in range(i + 1, n):
            total -= lu.upper[i][j] * solution[j]
        solution[i] = total / lu.upper[i][i]
    return solution


def determinant(lu: LuDecomposition) -> float:
    result = float(lu.sign)
    for i in range(len(lu.upper)):
        result *= lu.upper[i][i]
    return result


def inverse(lu: LuDecomposition) -> Matrix:
    n = len(lu.upper)
    result = zeros(n, n)
    for j in range(n):
        unit = [0.0] * n
        unit[j] = 1.0
        for i, value in enumerate(solve_lu(lu, unit)):
            result[i][j] = value
    return result
