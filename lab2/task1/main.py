import math
import sys
from pathlib import Path

from lab1.common import (
    InputReader,
    Series,
    chart,
    format_number,
    format_scientific,
    format_table,
    iterations_text,
    linspace,
    run,
)
from lab2.common import PRECISIONS, decimals
from lab2.task1.equation import Root, contraction_factor, newton, simple_iteration

INPUT = Path(__file__).with_name("input.txt")
PLOT_RANGE = (0.0, 1.6)
LN10 = math.log(10.0)


def f(x: float) -> float:
    return math.log10(2.0 * x + 1.0) - x**3 + 1.0


def f_derivative(x: float) -> float:
    return 2.0 / ((2.0 * x + 1.0) * LN10) - 3.0 * x**2


def f_second(x: float) -> float:
    return -4.0 / ((2.0 * x + 1.0) ** 2 * LN10) - 6.0 * x


def phi(x: float) -> float:
    return math.cbrt(1.0 + math.log10(2.0 * x + 1.0))


def phi_derivative(x: float) -> float:
    return 2.0 / (3.0 * (2.0 * x + 1.0) * LN10 * phi(x) ** 2)


def read(reader: InputReader) -> tuple[float, float, float]:
    a = reader.number()
    b = reader.number()
    eps = reader.precision()
    reader.finish()
    return a, b, eps


def solve(a: float, b: float, eps: float) -> tuple[Root, Root]:
    return (
        simple_iteration(phi, phi_derivative, a, b, eps),
        newton(f, f_derivative, f_second, a, b, eps),
    )


def _trace(root: Root, error: str, digits: int) -> list[str]:
    rows = [["0", format_number(root.start, digits), "-"]]
    rows += [
        [str(k), format_number(step.x, digits), format_scientific(step.error)]
        for k, step in enumerate(root.iterations, start=1)
    ]
    return format_table(["k", "x_k", error], rows)


def _analysis(a: float, b: float) -> list[str]:
    rows = []
    for eps in PRECISIONS:
        simple, tangent = solve(a, b, eps)
        rows.append([f"{eps:.0e}", str(len(simple.iterations)), str(len(tangent.iterations))])
    return [
        "Iterations depending on the precision:",
        *format_table(["eps", "simple", "Newton"], rows),
    ]


def task(reader: InputReader) -> list[str]:
    a, b, eps = read(reader)
    simple, tangent = solve(a, b, eps)
    digits = decimals(eps)
    return [
        f"Simple iteration: x = {format_number(simple.value, digits)}, "
        f"{iterations_text(len(simple.iterations))}",
        f"q = max |phi'(x)| = {format_number(contraction_factor(phi_derivative, a, b))}",
        *_trace(simple, "q/(1-q)|x_k - x_(k-1)|", digits),
        "",
        f"Newton method: x = {format_number(tangent.value, digits)}, "
        f"{iterations_text(len(tangent.iterations))}",
        *_trace(tangent, "|x_k - x_(k-1)|", digits),
        "",
        *_analysis(a, b),
    ]


def figure(reader: InputReader) -> str:
    a, b, eps = read(reader)
    root = newton(f, f_derivative, f_second, a, b, eps).value
    xs = linspace(min(PLOT_RANGE[0], a), max(PLOT_RANGE[1], b), 161)
    return chart(
        "f(x) = lg(2x + 1) - x^3 + 1",
        [
            Series("f(x)", xs, [f(x) for x in xs]),
            Series("a, b", [a, b], [0.0, 0.0], markers=True),
            Series("root", [root], [0.0], markers=True),
        ],
    )


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:], figure))
