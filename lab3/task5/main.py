import math
import sys
from pathlib import Path

from lab1.common import InputReader, format_number, format_scientific, format_table, run
from lab3.task5.integration import METHODS, runge_romberg

INPUT = Path(__file__).with_name("input.txt")


def function(x: float) -> float:
    return x**3 * math.sqrt(4.0 + x**2)


def antiderivative(x: float) -> float:
    u = 4.0 + x**2
    return u * math.sqrt(u) * (u / 5.0 - 4.0 / 3.0)


def task(reader: InputReader) -> list[str]:
    a = reader.number()
    b = reader.number()
    coarse_step = reader.precision()
    fine_step = reader.precision()
    reader.finish()

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


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
