import sys
from pathlib import Path

from lab1.common import InputReader, format_complex, format_matrix, run
from lab1.task5.qr import decompose_qr, qr_algorithm

INPUT = Path(__file__).with_name("input.txt")
PRECISIONS = [10.0**-power for power in range(1, 11)]


def task(reader: InputReader) -> list[str]:
    n = reader.size()
    matrix = reader.matrix(n)
    eps = reader.precision()
    reader.finish()

    qr = decompose_qr(matrix)
    eigen = qr_algorithm(matrix, eps)

    return [
        "Q =",
        *format_matrix(qr.q),
        "R =",
        *format_matrix(qr.r),
        "",
        "Eigenvalues:",
        *(f"lambda_{i + 1} = {format_complex(value)}" for i, value in enumerate(eigen.values)),
        f"Iterations: {eigen.iterations}",
        "",
        "Iterations depending on the precision:",
        f"{'eps':>7}  {'iterations':>10}",
        *(f"{value:7.0e}  {qr_algorithm(matrix, value).iterations:>10}" for value in PRECISIONS),
    ]


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
