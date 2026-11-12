import math
import sys
from pathlib import Path

from lab1.common import (
    InputReader,
    Series,
    Vector,
    chart,
    format_number,
    format_scientific,
    format_table,
    linspace,
    run,
)
from lab3.common import format_polynomial
from lab3.task1.interpolation import lagrange, newton, omega_derivative

INPUT = Path(__file__).with_name("input.txt")
LABELS = ("a", "b")


def function(x: float) -> float:
    return x * math.cos(x)


def read(reader: InputReader) -> tuple[list[Vector], float]:
    n = reader.size()
    node_sets = [reader.vector(n) for _ in LABELS]
    point = reader.number()
    reader.finish()
    return node_sets, point


def _interpolate(label: str, xs: Vector, point: float) -> list[str]:
    ys = [function(x) for x in xs]
    lagrange_polynomial = lagrange(xs, ys)
    newton_polynomial = newton(xs, ys)
    rows = [
        [
            str(i),
            format_number(x),
            format_number(y),
            format_number(omega_derivative(xs, i)),
            format_number(lagrange_polynomial.weights[i]),
            format_number(newton_polynomial.differences[i]),
        ]
        for i, (x, y) in enumerate(zip(xs, ys, strict=True))
    ]
    value = lagrange_polynomial(point)
    return [
        f"{label}) Nodes:",
        *format_table(["i", "x_i", "y_i", "w'(x_i)", "y_i/w'(x_i)", "y(x_0..x_i)"], rows),
        f"L(x) = {format_polynomial(lagrange_polynomial.coefficients())}",
        f"P(x) = {format_polynomial(newton_polynomial.coefficients())}",
        f"L(X*) = {format_number(value)}, P(X*) = {format_number(newton_polynomial(point))}",
        f"Error: |y(X*) - L(X*)| = {format_scientific(abs(function(point) - value))}",
    ]


def task(reader: InputReader) -> list[str]:
    node_sets, point = read(reader)
    lines = [f"X* = {format_number(point)}, y(X*) = {format_number(function(point))}"]
    for label, xs in zip(LABELS, node_sets, strict=True):
        lines += ["", *_interpolate(label, xs, point)]
    return lines


def figure(reader: InputReader) -> str:
    node_sets, point = read(reader)
    every = [x for xs in node_sets for x in xs] + [point]
    grid = linspace(min(every), max(every), 161)
    series = [Series("y = x cos(x)", grid, [function(x) for x in grid])]
    for label, xs in zip(LABELS, node_sets, strict=True):
        polynomial = lagrange(xs, [function(x) for x in xs])
        series.append(Series(f"L(x), nodes {label})", grid, [polynomial(x) for x in grid]))
    for label, xs in zip(LABELS, node_sets, strict=True):
        series.append(Series(f"nodes {label})", xs, [function(x) for x in xs], markers=True))
    return chart("Lagrange interpolation of y = x cos(x)", series)


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], figure))
