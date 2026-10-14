import sys
from pathlib import Path

from lab1.common import InputReader, column, format_number, format_scientific, format_vector, run
from lab1.task4.rotation import rotation_method

INPUT = Path(__file__).with_name("input.txt")


def task(reader: InputReader) -> list[str]:
    n = reader.size()
    matrix = reader.matrix(n)
    eps = reader.precision()
    reader.finish()

    eigen = rotation_method(matrix, eps)

    return [
        *(
            f"lambda_{i + 1} = {format_number(value)}, "
            f"x_{i + 1} = {format_vector(column(eigen.vectors, i))}"
            for i, value in enumerate(eigen.values)
        ),
        "",
        f"Rotations: {eigen.rotations}",
        "Error after every rotation:",
        "  k  off(A)",
        *(f"{k:>3}  {format_scientific(error)}" for k, error in enumerate(eigen.errors)),
    ]


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
