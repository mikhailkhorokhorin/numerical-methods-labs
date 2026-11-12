import sys
from pathlib import Path

from lab1.common import InputReader, format_number, run
from lab3.common import read_table
from lab3.task4.derivative import derivatives

INPUT = Path(__file__).with_name("input.txt")


def task(reader: InputReader) -> list[str]:
    xs, ys = read_table(reader, 3)
    point = reader.number()
    reader.finish()

    result = derivatives(xs, ys, point)
    at = format_number(point)

    return [
        f"Left difference:   y'({at}) = {format_number(result.left)}",
        f"Right difference:  y'({at}) = {format_number(result.right)}",
        f"Second order:      y'({at}) = {format_number(result.first)}",
        f"Second derivative: y''({at}) = {format_number(result.second)}",
    ]


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
