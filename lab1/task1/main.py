import sys
from pathlib import Path

from lab1.common import InputReader, format_matrix, format_number, format_vector, run
from lab1.task1.lu import decompose_lu, determinant, inverse, solve_lu

INPUT = Path(__file__).with_name("input.txt")


def task(reader: InputReader) -> list[str]:
    n = reader.size()
    matrix = reader.matrix(n)
    rhs = reader.vector(n)
    reader.finish()

    lu = decompose_lu(matrix)
    solution = solve_lu(lu, rhs)
    inverted = inverse(lu)

    permutation = ", ".join(str(index + 1) for index in lu.permutation)
    return [
        f"P = ({permutation})",
        "L =",
        *format_matrix(lu.lower),
        "U =",
        *format_matrix(lu.upper),
        f"x = {format_vector(solution)}",
        f"det(A) = {format_number(determinant(lu))}",
        "A^-1 =",
        *format_matrix(inverted),
    ]


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
