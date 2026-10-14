import sys
from pathlib import Path

from lab1.common import InputReader, format_vector, run
from lab1.task2.tridiagonal import TridiagonalSystem, meets_stability_condition, solve_tridiagonal

INPUT = Path(__file__).with_name("input.txt")


def task(reader: InputReader) -> list[str]:
    n = reader.size()
    lower = reader.vector(n - 1)
    diagonal = reader.vector(n)
    upper = reader.vector(n - 1)
    rhs = reader.vector(n)
    reader.finish()

    system = TridiagonalSystem(lower, diagonal, upper, rhs)
    solution = solve_tridiagonal(system)

    stable = "yes" if meets_stability_condition(system) else "no"
    return [f"x = {format_vector(solution)}", f"Stability condition: {stable}"]


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
