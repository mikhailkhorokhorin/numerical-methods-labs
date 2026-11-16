import sys
from pathlib import Path

from lab1.common import (
    PLOT_NAME,
    InputReader,
    Series,
    Vector,
    chart,
    format_matrix,
    format_number,
    linspace,
    run,
)
from lab3.common import format_polynomial, read_table
from lab3.task3.least_squares import Approximation, least_squares

INPUT = Path(__file__).with_name("input.txt")
DEGREES = (1, 2)


def read(reader: InputReader) -> tuple[Vector, Vector]:
    xs, ys = read_table(reader, 2)
    reader.finish()
    return xs, ys


def _approximation(degree: int, approximation: Approximation) -> list[str]:
    rhs = format_matrix([[value] for value in approximation.rhs])
    return [
        f"Degree {degree}, normal system:",
        *(
            f"{row}  |{value}"
            for row, value in zip(format_matrix(approximation.matrix), rhs, strict=True)
        ),
        f"F_{degree}(x) = {format_polynomial(approximation.coefficients)}",
        f"Sum of squared errors: {format_number(approximation.squared_error)}",
    ]


def task(reader: InputReader) -> list[str]:
    xs, ys = read(reader)
    lines: list[str] = []
    for degree in DEGREES:
        if lines:
            lines.append("")
        lines += _approximation(degree, least_squares(xs, ys, degree))
    return lines


def figure(reader: InputReader) -> str:
    xs, ys = read(reader)
    grid = linspace(min(xs), max(xs), 201)
    series = []
    for degree in DEGREES:
        approximation = least_squares(xs, ys, degree)
        series.append(Series(f"F_{degree}(x)", grid, [approximation(x) for x in grid]))
    return chart("Least squares approximation", [*series, Series("table", xs, ys, markers=True)])


FIGURES = {PLOT_NAME: figure}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
