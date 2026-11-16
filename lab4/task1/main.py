import math
import sys
from pathlib import Path

from lab1.common import (
    PLOT_NAME,
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
from lab4.common import max_error, runge_romberg_error
from lab4.task1.cauchy import CauchyProblem, Method, adams, euler, runge_kutta

INPUT = Path(__file__).with_name("input.txt")
METHODS: list[tuple[str, Method, int]] = [
    ("Euler", euler, 1),
    ("Runge-Kutta", runge_kutta, 4),
    ("Adams", adams, 4),
]


def rhs(x: float, state: Vector) -> Vector:
    y, z = state
    return [z, (3.0 * x * z - 4.0 * y + 5.0 * x) / x**2]


def exact(x: float) -> float:
    return 5.0 * x + x**2 + x**2 * math.log(abs(x))


def read(reader: InputReader) -> tuple[CauchyProblem, float]:
    start = reader.number()
    end = reader.number()
    initial = reader.vector(2)
    h = reader.precision()
    reader.finish()
    return CauchyProblem(rhs, start, end, initial), h


def task(reader: InputReader) -> list[str]:
    problem, h = read(reader)
    solutions = [method(problem, h) for _, method, _ in METHODS]
    xs = solutions[0].xs
    values = [solution.component(0) for solution in solutions]
    rows = [
        [format_number(x), *(format_number(ys[i]) for ys in values), format_number(exact(x))]
        for i, x in enumerate(xs)
    ]
    errors = [
        [
            name,
            format_scientific(
                runge_romberg_error(method(problem, 2.0 * h).component(0), ys, order)
            ),
            format_scientific(max_error(xs, ys, exact)),
        ]
        for (name, method, order), ys in zip(METHODS, values, strict=True)
    ]
    return [
        *format_table(["x", *(name for name, _, _ in METHODS), "exact"], rows),
        "",
        "Errors:",
        *format_table(["method", "Runge-Romberg", "max |y - y_exact|"], errors),
    ]


def figure(reader: InputReader) -> str:
    problem, h = read(reader)
    grid = linspace(problem.start, problem.end, 201)
    series = [Series("exact", grid, [exact(x) for x in grid])]
    for name, method, _ in METHODS:
        solution = method(problem, h)
        series.append(Series(name, solution.xs, solution.component(0), markers=True))
    return chart("x^2 y'' - 3x y' + 4y - 5x = 0", series)


FIGURES = {PLOT_NAME: figure}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
