import math
from dataclasses import dataclass

from lab1.common import Matrix, Vector, copy_matrix, identity, is_symmetric, matrix_norm_inf

MAX_ROTATIONS = 100000
SYMMETRY_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class EigenSystem:
    values: Vector
    vectors: Matrix
    errors: Vector
    rotations: int


def _rotate_columns(matrix: Matrix, i: int, j: int, cosine: float, sine: float) -> None:
    for row in matrix:
        left = row[i]
        right = row[j]
        row[i] = cosine * left + sine * right
        row[j] = -sine * left + cosine * right


def _rotate_rows(matrix: Matrix, i: int, j: int, cosine: float, sine: float) -> None:
    top = matrix[i]
    bottom = matrix[j]
    for k in range(len(top)):
        upper = top[k]
        lower = bottom[k]
        top[k] = cosine * upper + sine * lower
        bottom[k] = -sine * upper + cosine * lower


def off_diagonal_norm(matrix: Matrix) -> float:
    total = 0.0
    for i, row in enumerate(matrix):
        for value in row[i + 1 :]:
            total += value * value
    return math.sqrt(total)


def rotation_method(matrix: Matrix, eps: float) -> EigenSystem:
    if not matrix or not is_symmetric(matrix, SYMMETRY_TOLERANCE * matrix_norm_inf(matrix)):
        raise ValueError("rotation method needs a symmetric matrix")
    n = len(matrix)
    a = copy_matrix(matrix)
    vectors = identity(n)
    errors = [off_diagonal_norm(a)]
    rotations = 0

    while errors[-1] > eps:
        if rotations == MAX_ROTATIONS:
            raise RuntimeError("rotation method did not converge")
        pivot_row = 0
        pivot_col = 1
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > abs(a[pivot_row][pivot_col]):
                    pivot_row = i
                    pivot_col = j
        pivot = a[pivot_row][pivot_col]
        difference = a[pivot_row][pivot_row] - a[pivot_col][pivot_col]
        angle = (
            math.copysign(math.pi / 4.0, pivot)
            if difference == 0.0
            else 0.5 * math.atan(2.0 * pivot / difference)
        )
        cosine = math.cos(angle)
        sine = math.sin(angle)
        _rotate_columns(a, pivot_row, pivot_col, cosine, sine)
        _rotate_rows(a, pivot_row, pivot_col, cosine, sine)
        a[pivot_row][pivot_col] = 0.0
        a[pivot_col][pivot_row] = 0.0
        _rotate_columns(vectors, pivot_row, pivot_col, cosine, sine)
        rotations += 1
        errors.append(off_diagonal_norm(a))

    return EigenSystem([a[i][i] for i in range(n)], vectors, errors, rotations)
