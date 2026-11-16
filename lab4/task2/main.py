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
)
from lab4.common import max_error, runge_romberg_error
from lab4.task2.boundary import (
    BoundaryProblem,
    Condition,
    GridFunction,
    Shooting,
    finite_difference,
    shooting,
)

INPUT = Path(__file__).with_name("input.txt")


def p(x: float) -> float:
    return -(2.0 * x + 1.0) / x


def q(x: float) -> float:
    return 2.0 / x


def f(x: float) -> float:
    return 0.0


def exact(x: float) -> float:
    return math.exp(2.0 * x)


def read(reader: InputReader) -> tuple[BoundaryProblem, float, float]:
    left = reader.number()
    right = reader.number()
    left_condition = Condition(*reader.vector(3))
    right_condition = Condition(*reader.vector(3))
    h = reader.precision()
    eps = reader.precision()
    reader.finish()
    return BoundaryProblem(p, q, f, left, right, left_condition, right_condition), h, eps


def solve(problem: BoundaryProblem, h: float, eps: float) -> tuple[Shooting, GridFunction]:
    return shooting(problem, h, eps), finite_difference(problem, h)


def task(reader: InputReader) -> list[str]:
    problem, h, eps = read(reader)
    shot, difference = solve(problem, h, eps)
    coarse_shot, coarse_difference = solve(problem, 2.0 * h, eps)
    xs = difference.xs
    rows = [
        [format_number(x), format_number(a), format_number(b), format_number(exact(x))]
        for x, a, b in zip(xs, shot.solution.ys, difference.ys, strict=True)
    ]
    shots = [
        [str(k), format_number(item.parameter), format_scientific(item.residual)]
        for k, item in enumerate(shot.shots)
    ]
    errors = [
        [
            "shooting",
            format_scientific(runge_romberg_error(coarse_shot.solution.ys, shot.solution.ys, 4)),
            format_scientific(max_error(xs, shot.solution.ys, exact)),
        ],
        [
            "finite difference",
            format_scientific(runge_romberg_error(coarse_difference.ys, difference.ys, 2)),
            format_scientific(max_error(xs, difference.ys, exact)),
        ],
    ]
    return [
        "Shooting method, secant iterations:",
        *format_table(["k", "eta", "residual"], shots),
        "",
        *format_table(["x", "shooting", "finite difference", "exact"], rows),
        "",
        "Errors:",
        *format_table(["method", "Runge-Romberg", "max |y - y_exact|"], errors),
    ]


def figure(reader: InputReader) -> str:
    problem, h, eps = read(reader)
    shot, difference = solve(problem, h, eps)
    grid = linspace(problem.left, problem.right, 201)
    return chart(
        "x y'' - (2x + 1) y' + 2y = 0, y'(0) = 2, y(1) = e^2",
        [
            Series("exact: y = e^(2x)", grid, [exact(x) for x in grid]),
            Series("shooting", shot.solution.xs, shot.solution.ys, markers=True),
            Series("finite difference", difference.xs, difference.ys, markers=True),
        ],
        "x",
        "y",
    )


def figure_error(reader: InputReader) -> str:
    problem, h, eps = read(reader)
    shot, difference = solve(problem, h, eps)
    series = [
        Series(
            name,
            solution.xs[1:-1],
            [abs(y - exact(x)) for x, y in zip(solution.xs, solution.ys, strict=True)][1:-1],
        )
        for name, solution in (("shooting", shot.solution), ("finite difference", difference))
    ]
    return chart(f"Error at the inner nodes, h = {h:g}", series, "x", "|y - y_exact|", log_y=True)


ERROR_NAME = "plot_error.svg"
FIGURES = {PLOT_NAME: figure, ERROR_NAME: figure_error}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
