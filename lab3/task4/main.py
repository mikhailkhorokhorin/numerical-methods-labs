import sys
from bisect import bisect_right
from pathlib import Path

from lab1.common import PLOT_NAME, InputReader, Series, Vector, chart, format_number, run
from lab3.common import read_table
from lab3.task4.derivative import derivatives

INPUT = Path(__file__).with_name("input.txt")


def read(reader: InputReader) -> tuple[Vector, Vector, float]:
    xs, ys = read_table(reader, 3)
    point = reader.number()
    reader.finish()
    return xs, ys, point


def task(reader: InputReader) -> list[str]:
    xs, ys, point = read(reader)
    result = derivatives(xs, ys, point)
    at = format_number(point)
    return [
        f"Left difference:   y'({at}) = {format_number(result.left)}",
        f"Right difference:  y'({at}) = {format_number(result.right)}",
        f"Second order:      y'({at}) = {format_number(result.first)}",
        f"Second derivative: y''({at}) = {format_number(result.second)}",
    ]


def _value(xs: Vector, ys: Vector, point: float) -> float:
    i = min(max(bisect_right(xs, point) - 1, 0), len(xs) - 2)
    return ys[i] + (ys[i + 1] - ys[i]) * (point - xs[i]) / (xs[i + 1] - xs[i])


def figure(reader: InputReader) -> str:
    xs, ys, point = read(reader)
    result = derivatives(xs, ys, point)
    base = _value(xs, ys, point)
    ends = [xs[0], xs[-1]]
    slopes = [
        ("left difference", result.left),
        ("right difference", result.right),
        ("second order", result.first),
    ]
    lines = [
        Series(
            f"{name}: y' = {format_number(slope)}", ends, [base + slope * (x - point) for x in ends]
        )
        for name, slope in slopes
    ]
    return chart(
        f"Derivative at X* = {point:g} as the slope of a line",
        [Series("table", xs, ys, markers=True), *lines],
        "x",
        "y",
    )


FIGURES = {PLOT_NAME: figure}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
