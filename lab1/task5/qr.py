import cmath
import math
from dataclasses import dataclass

from lab1.common import Matrix, copy_matrix, identity, is_square, matmul

MAX_ITERATIONS = 100000

ComplexPair = tuple[complex, complex]


@dataclass(frozen=True, slots=True)
class QrDecomposition:
    q: Matrix
    r: Matrix


@dataclass(frozen=True, slots=True)
class QrEigenvalues:
    values: list[complex]
    iterations: int


def _column_tail(matrix: Matrix, col: int, from_row: int) -> float:
    total = 0.0
    for row in matrix[from_row:]:
        total += row[col] * row[col]
    return math.sqrt(total)


def _block_eigenvalues(matrix: Matrix, j: int) -> ComplexPair:
    a = matrix[j][j]
    b = matrix[j][j + 1]
    c = matrix[j + 1][j]
    d = matrix[j + 1][j + 1]
    half_trace = (a + d) / 2.0
    root = cmath.sqrt(complex((a - d) * (a - d) / 4.0 + b * c, 0.0))
    return half_trace + root, half_trace - root


def _is_stable(current: ComplexPair, last: ComplexPair | None, eps: float) -> bool:
    if last is None:
        return False
    return abs(current[0] - last[0]) <= eps and abs(current[1] - last[1]) <= eps


def _extract_eigenvalues(
    matrix: Matrix, eps: float, previous: list[ComplexPair | None]
) -> list[complex] | None:
    n = len(matrix)
    values: list[complex] = []
    converged = True
    j = 0
    while j < n:
        if j + 1 == n or _column_tail(matrix, j, j + 1) <= eps:
            values.append(complex(matrix[j][j], 0.0))
            j += 1
            continue
        current = _block_eigenvalues(matrix, j)
        isolated = (
            _column_tail(matrix, j, j + 2) <= eps and _column_tail(matrix, j + 1, j + 2) <= eps
        )
        stable = _is_stable(current, previous[j], eps)
        previous[j] = current
        converged = converged and isolated and stable
        values.extend(current)
        j += 2
    return values if converged else None


def decompose_qr(matrix: Matrix) -> QrDecomposition:
    if not matrix or not is_square(matrix):
        raise ValueError("QR decomposition needs a non-empty square matrix")
    n = len(matrix)
    q = identity(n)
    r = copy_matrix(matrix)
    for k in range(n - 1):
        norm = _column_tail(r, k, k)
        if norm == 0.0:
            continue
        v = [0.0] * n
        for i in range(k, n):
            v[i] = r[i][k]
        v[k] += math.copysign(norm, v[k])
        squared_norm = 0.0
        for i in range(k, n):
            squared_norm += v[i] * v[i]
        for j in range(n):
            dot = 0.0
            for i in range(k, n):
                dot += v[i] * r[i][j]
            factor = 2.0 * dot / squared_norm
            for i in range(k, n):
                r[i][j] -= factor * v[i]
        for row in q:
            dot = 0.0
            for j in range(k, n):
                dot += row[j] * v[j]
            factor = 2.0 * dot / squared_norm
            for j in range(k, n):
                row[j] -= factor * v[j]
        for i in range(k + 1, n):
            r[i][k] = 0.0
    return QrDecomposition(q, r)


def qr_algorithm(matrix: Matrix, eps: float) -> QrEigenvalues:
    if not matrix or not is_square(matrix):
        raise ValueError("QR algorithm needs a non-empty square matrix")
    a = copy_matrix(matrix)
    previous: list[ComplexPair | None] = [None] * len(matrix)
    for iteration in range(MAX_ITERATIONS + 1):
        values = _extract_eigenvalues(a, eps, previous)
        if values is not None:
            return QrEigenvalues(values, iteration)
        qr = decompose_qr(a)
        a = matmul(qr.r, qr.q)
    raise RuntimeError("QR algorithm did not converge")
