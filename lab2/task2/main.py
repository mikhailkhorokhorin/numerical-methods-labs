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
    format_vector,
    iterations_text,
    linspace,
    run,
)
from lab2.common import PRECISIONS, decimals
from lab2.task2.system import (
    NonlinearSystem,
    Region,
    Solution,
    center,
    contraction_factor,
    newton,
    simple_iteration,
)

INPUT = Path(__file__).with_name("input.txt")
PLOT_RANGE = (0.5, 3.0)


def system(a: float) -> NonlinearSystem:
    def function(x: Vector) -> Vector:
        x1, x2 = x
        return [math.exp(x1 * x2) + x1 - a, x1**2 - a * x2 - 1.0]

    def jacobian(x: Vector) -> list[Vector]:
        x1, x2 = x
        exponent = math.exp(x1 * x2)
        return [[x2 * exponent + 1.0, x1 * exponent], [2.0 * x1, -a]]

    return NonlinearSystem(function, jacobian)


def first_curve(a: float, x1: float) -> float:
    return math.log(a - x1) / x1 if x1 < a and x1 != 0.0 else math.nan


def second_curve(a: float, x1: float) -> float:
    return (x1**2 - 1.0) / a


def read(reader: InputReader) -> tuple[float, Region, float]:
    a = reader.number()
    region = [(reader.number(), reader.number()) for _ in range(2)]
    eps = reader.precision()
    reader.finish()
    return a, region, eps


def solve(a: float, region: Region, eps: float) -> tuple[Solution, Solution]:
    equations = system(a)
    return simple_iteration(equations, region, eps), newton(equations, center(region), eps)


def _trace(solution: Solution, error: str, digits: int) -> list[str]:
    rows = [["0", *(format_number(value, digits) for value in solution.start), "-"]]
    rows += [
        [str(k), *(format_number(value, digits) for value in step.x), format_scientific(step.error)]
        for k, step in enumerate(solution.iterations, start=1)
    ]
    return format_table(["k", "x1_k", "x2_k", error], rows)


def _analysis(a: float, region: Region) -> list[str]:
    rows = []
    for eps in PRECISIONS:
        simple, tangent = solve(a, region, eps)
        rows.append([f"{eps:.0e}", str(len(simple.iterations)), str(len(tangent.iterations))])
    return [
        "Iterations depending on the precision:",
        *format_table(["eps", "simple", "Newton"], rows),
    ]


def task(reader: InputReader) -> list[str]:
    a, region, eps = read(reader)
    simple, tangent = solve(a, region, eps)
    digits = decimals(eps)
    return [
        f"Simple iteration: x = {format_vector(simple.value, digits)}, "
        f"{iterations_text(len(simple.iterations))}",
        f"q = max ||phi'(x)|| = {format_number(contraction_factor(system(a), region))}",
        *_trace(simple, "q/(1-q)||x_k - x_(k-1)||", digits),
        "",
        f"Newton method: x = {format_vector(tangent.value, digits)}, "
        f"{iterations_text(len(tangent.iterations))}",
        *_trace(tangent, "||x_k - x_(k-1)||", digits),
        "",
        *_analysis(a, region),
    ]


ZOOM_NAME = "plot_zoom.svg"
ZOOM_MARGIN = 0.25


def _equations(a: float, xs: Vector) -> list[Series]:
    return [
        Series(f"equation 1: e^(x1 x2) + x1 - {a:g} = 0", xs, [first_curve(a, x) for x in xs]),
        Series(f"equation 2: x1^2 - {a:g} x2 - 1 = 0", xs, [second_curve(a, x) for x in xs]),
    ]


def _rectangle(label: str, region: Region) -> Series:
    (low1, high1), (low2, high2) = region
    return Series(
        label, [low1, high1, high1, low1, low1], [low2, low2, high2, high2, low2], filled=True
    )


def figure(reader: InputReader) -> str:
    a, region, eps = read(reader)
    solution = newton(system(a), center(region), eps).value
    (low1, high1), _ = region
    xs = linspace(min(PLOT_RANGE[0], low1), max(PLOT_RANGE[1], high1), 201)
    return chart(
        "Graphical solution of the system",
        [
            *_equations(a, xs),
            _rectangle("region G", region),
            Series("solution", [solution[0]], [solution[1]], markers=True),
        ],
        "x1",
        "x2",
    )


def _clip(value: float, low: float, high: float) -> float:
    return value if low <= value <= high else math.nan


def figure_zoom(reader: InputReader) -> str:
    a, region, eps = read(reader)
    start = center(region)
    solution = newton(system(a), start, eps).value
    (low1, high1), (low2, high2) = region
    pad1 = ZOOM_MARGIN * (high1 - low1)
    pad2 = ZOOM_MARGIN * (high2 - low2)
    xs = linspace(low1 - pad1, high1 + pad1, 201)
    curves = [
        Series(item.label, item.xs, [_clip(y, low2 - pad2, high2 + pad2) for y in item.ys])
        for item in _equations(a, xs)
    ]
    return chart(
        "Graphical solution of the system: region G",
        [
            *curves,
            _rectangle("region G", region),
            Series(
                f"initial guess ({start[0]:g}, {start[1]:g})", [start[0]], [start[1]], markers=True
            ),
            Series("solution", [solution[0]], [solution[1]], markers=True),
        ],
        "x1",
        "x2",
    )


FIGURES = {PLOT_NAME: figure, ZOOM_NAME: figure_zoom}


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], FIGURES))
