import sys
from itertools import pairwise
from pathlib import Path

from lab1.common import (
    PLOT_NAME,
    InputReader,
    Series,
    Vector,
    chart,
    format_number,
    format_table,
    linspace,
    run,
)
from lab3.common import read_table
from lab3.task2.spline import natural_spline

INPUT = Path(__file__).with_name("input.txt")


def read(reader: InputReader) -> tuple[Vector, Vector, float]:
    xs, ys = read_table(reader, 2)
    point = reader.number()
    reader.finish()
    return xs, ys, point


def task(reader: InputReader) -> list[str]:
    xs, ys, point = read(reader)
    spline = natural_spline(xs, ys)
    rows = [
        [str(i + 1), *(format_number(value) for value in row)]
        for i, row in enumerate(
            zip(xs, xs[1:], spline.a, spline.b, spline.c, spline.d, strict=False)
        )
    ]
    return [
        "Spline coefficients:",
        *format_table(["i", "x_(i-1)", "x_i", "a_i", "b_i", "c_i", "d_i"], rows),
        "",
        f"f(X*) = S({format_number(point)}) = {format_number(spline(point))}",
    ]


def figure(reader: InputReader) -> str:
    xs, ys, point = read(reader)
    spline = natural_spline(xs, ys)
    series = []
    for i, (left, right) in enumerate(pairwise(xs), start=1):
        grid = linspace(left, right, 51)
        series.append(Series(f"S_{i}(x) on [{left:g}, {right:g}]", grid, [spline(x) for x in grid]))
    value = spline(point)
    return chart(
        "Natural cubic spline",
        [
            *series,
            Series("nodes", xs, ys, markers=True),
            Series(f"S({point:g}) = {format_number(value)}", [point], [value], markers=True),
        ],
        "x",
        "S(x)",
    )


FIGURES = {PLOT_NAME: figure}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
