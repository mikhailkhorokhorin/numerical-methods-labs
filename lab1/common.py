import math
import sys
from collections.abc import Callable
from pathlib import Path

Vector = list[float]
Matrix = list[list[float]]

PRECISION = 4
ZERO_THRESHOLD = 5e-5


def zeros(rows: int, cols: int) -> Matrix:
    return [[0.0] * cols for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for i in range(size):
        result[i][i] = 1.0
    return result


def copy_matrix(matrix: Matrix) -> Matrix:
    return [row[:] for row in matrix]


def is_square(matrix: Matrix) -> bool:
    return all(len(row) == len(matrix) for row in matrix)


def column(matrix: Matrix, col: int) -> Vector:
    return [row[col] for row in matrix]


def transposed(matrix: Matrix) -> Matrix:
    cols = len(matrix[0]) if matrix else 0
    return [[row[j] for row in matrix] for j in range(cols)]


def matmul(lhs: Matrix, rhs: Matrix) -> Matrix:
    if any(len(row) != len(rhs) for row in lhs):
        raise ValueError("matrix sizes do not match")
    cols = len(rhs[0]) if rhs else 0
    result = zeros(len(lhs), cols)
    for row, out in zip(lhs, result, strict=True):
        for value, other in zip(row, rhs, strict=True):
            for j in range(cols):
                out[j] += value * other[j]
    return result


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix and vector sizes do not match")
    result = [0.0] * len(matrix)
    for i, row in enumerate(matrix):
        for value, component in zip(row, vector, strict=True):
            result[i] += value * component
    return result


def norm_inf(vector: Vector) -> float:
    result = 0.0
    for value in vector:
        result = max(result, abs(value))
    return result


def matrix_norm_inf(matrix: Matrix) -> float:
    result = 0.0
    for row in matrix:
        row_sum = 0.0
        for value in row:
            row_sum += abs(value)
        result = max(result, row_sum)
    return result


def distance_inf(lhs: Vector, rhs: Vector) -> float:
    if len(lhs) != len(rhs):
        raise ValueError("vector sizes do not match")
    result = 0.0
    for left, right in zip(lhs, rhs, strict=True):
        result = max(result, abs(left - right))
    return result


def is_symmetric(matrix: Matrix, tolerance: float = 0.0) -> bool:
    if not is_square(matrix):
        return False
    n = len(matrix)
    return all(
        abs(matrix[i][j] - matrix[j][i]) <= tolerance for i in range(n) for j in range(i + 1, n)
    )


class InputReader:
    def __init__(self, text: str) -> None:
        self._tokens = text.split()
        self._position = 0

    def _next(self) -> str:
        if self._position == len(self._tokens):
            raise ValueError("unexpected end of input")
        token = self._tokens[self._position]
        self._position += 1
        return token

    def size(self) -> int:
        token = self._next()
        if not token.isdigit() or not 1 <= int(token) <= 1000:
            raise ValueError(f"expected a matrix size from 1 to 1000, got '{token}'")
        return int(token)

    def number(self) -> float:
        token = self._next()
        try:
            value = float(token)
        except ValueError:
            raise ValueError(f"expected a number, got '{token}'") from None
        if not math.isfinite(value) or abs(value) > 1e100:
            raise ValueError(f"numbers must lie in [-1e100, 1e100], got '{token}'")
        return value

    def precision(self) -> float:
        value = self.number()
        if value <= 0.0:
            raise ValueError("precision must be positive")
        return value

    def vector(self, size: int) -> Vector:
        return [self.number() for _ in range(size)]

    def matrix(self, size: int) -> Matrix:
        return [self.vector(size) for _ in range(size)]

    def finish(self) -> None:
        if self._position < len(self._tokens):
            raise ValueError(f"unexpected trailing input '{self._tokens[self._position]}'")


def format_number(value: float) -> str:
    return f"{0.0 if abs(value) < ZERO_THRESHOLD else value:.{PRECISION}f}"


def format_scientific(value: float) -> str:
    return f"{value:.{PRECISION}e}"


def format_complex(value: complex) -> str:
    if abs(value.imag) < ZERO_THRESHOLD:
        return format_number(value.real)
    sign = " - " if value.imag < 0.0 else " + "
    return f"{format_number(value.real)}{sign}{format_number(abs(value.imag))}i"


def format_vector(vector: Vector) -> str:
    return "(" + ", ".join(format_number(value) for value in vector) + ")"


def format_matrix(matrix: Matrix) -> list[str]:
    cells = [[format_number(value) for value in row] for row in matrix]
    width = max((len(cell) for row in cells for cell in row), default=0)
    return ["".join(f"  {cell:>{width}}" for cell in row) for row in cells]


Task = Callable[[InputReader], list[str]]


def solve_file(task: Task, path: Path) -> list[str]:
    return task(InputReader(path.read_text(encoding="utf-8")))


def run(task: Task, default_input: Path, args: list[str]) -> int:
    path = Path(args[0]) if args else default_input
    try:
        lines = solve_file(task, path)
    except (OSError, ValueError, ArithmeticError, RuntimeError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0
