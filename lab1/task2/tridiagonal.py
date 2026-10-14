from dataclasses import dataclass

from lab1.common import Vector

SINGULARITY_TOLERANCE = 1e-12


@dataclass(frozen=True, slots=True)
class TridiagonalSystem:
    lower: Vector
    diagonal: Vector
    upper: Vector
    rhs: Vector


def _validate(system: TridiagonalSystem) -> None:
    n = len(system.diagonal)
    if n == 0 or len(system.rhs) != n or len(system.lower) + 1 != n or len(system.upper) + 1 != n:
        raise ValueError("tridiagonal system has inconsistent sizes")


def _lower_at(system: TridiagonalSystem, row: int) -> float:
    return 0.0 if row == 0 else system.lower[row - 1]


def _upper_at(system: TridiagonalSystem, row: int) -> float:
    return 0.0 if row + 1 == len(system.diagonal) else system.upper[row]


def solve_tridiagonal(system: TridiagonalSystem) -> Vector:
    _validate(system)
    n = len(system.diagonal)
    scale = 0.0
    for i in range(n):
        scale = max(
            scale,
            abs(_lower_at(system, i)),
            abs(system.diagonal[i]),
            abs(_upper_at(system, i)),
        )

    p = [0.0] * n
    q = [0.0] * n
    for i in range(n):
        a = _lower_at(system, i)
        previous_p = 0.0 if i == 0 else p[i - 1]
        previous_q = 0.0 if i == 0 else q[i - 1]
        denominator = system.diagonal[i] + a * previous_p
        if abs(denominator) <= SINGULARITY_TOLERANCE * scale:
            raise ValueError("zero denominator in the Thomas algorithm")
        p[i] = -_upper_at(system, i) / denominator
        q[i] = (system.rhs[i] - a * previous_q) / denominator

    solution = [0.0] * n
    solution[n - 1] = q[n - 1]
    for i in reversed(range(n - 1)):
        solution[i] = p[i] * solution[i + 1] + q[i]
    return solution


def meets_stability_condition(system: TridiagonalSystem) -> bool:
    _validate(system)
    if 0.0 in system.lower or 0.0 in system.upper:
        return False
    strict = False
    for i in range(len(system.diagonal)):
        diagonal = abs(system.diagonal[i])
        off_diagonal = abs(_lower_at(system, i)) + abs(_upper_at(system, i))
        if diagonal < off_diagonal:
            return False
        strict = strict or diagonal > off_diagonal
    return strict
