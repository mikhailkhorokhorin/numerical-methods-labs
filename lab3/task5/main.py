import math
import sys
from pathlib import Path

from lab1.common import (
    PLOT_NAME,
    InputReader,
    Series,
    chart,
    format_number,
    format_scientific,
    format_table,
    linspace,
    run,
    step_count,
)
from lab3.task5.integration import METHODS, runge_romberg

INPUT = Path(__file__).with_name("input.txt")


def function(x: float) -> float:
    return x**3 * math.sqrt(4.0 + x**2)


def antiderivative(x: float) -> float:
    u = 4.0 + x**2
    return u * math.sqrt(u) * (u / 5.0 - 4.0 / 3.0)


def read(reader: InputReader) -> tuple[float, float, float, float]:
    a = reader.number()
    b = reader.number()
    coarse_step = reader.precision()
    fine_step = reader.precision()
    reader.finish()
    return a, b, coarse_step, fine_step


def task(reader: InputReader) -> list[str]:
    a, b, coarse_step, fine_step = read(reader)

    exact = antiderivative(b) - antiderivative(a)
    rows = []
    for name, rule, order in METHODS:
        coarse = rule(function, a, b, coarse_step)
        fine = rule(function, a, b, fine_step)
        correction = runge_romberg(coarse, fine, coarse_step / fine_step, order)
        rows.append(
            [
                name,
                format_number(coarse),
                format_number(fine),
                format_scientific(abs(correction)),
                format_scientific(abs(exact - fine)),
                format_number(fine + correction),
                format_scientific(abs(exact - fine - correction)),
            ]
        )

    header = [
        "method",
        f"h = {coarse_step:g}",
        f"h = {fine_step:g}",
        "estimate",
        "error",
        "refined",
        "refined error",
    ]
    return [f"Exact value: {format_number(exact)}", *format_table(header, rows)]


def figure(reader: InputReader) -> str:
    a, b, coarse_step, _ = read(reader)
    n = step_count(a, b, coarse_step)
    nodes = [a + (b - a) * i / n for i in range(n + 1)]
    grid = linspace(a, b, 201)
    trapezoid = Series(
        f"trapezoids, h = {coarse_step:g}",
        [*nodes, b, a],
        [*(function(x) for x in nodes), 0.0, 0.0],
        filled=True,
    )
    return chart(
        f"y = x^3 sqrt(4 + x^2) on [{a:g}, {b:g}]",
        [Series("y = x^3 sqrt(4 + x^2)", grid, [function(x) for x in grid]), trapezoid],
        "x",
        "y",
    )


FIGURES = {PLOT_NAME: figure}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
