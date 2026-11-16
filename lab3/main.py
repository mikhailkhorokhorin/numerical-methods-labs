import sys

from lab1.common import run
from lab3.task1 import main as task1
from lab3.task2 import main as task2
from lab3.task3 import main as task3
from lab3.task4 import main as task4
from lab3.task5 import main as task5

TASKS = [
    ("3.1", "Lagrange and Newton interpolation", task1),
    ("3.2", "Cubic spline", task2),
    ("3.3", "Least squares", task3),
    ("3.4", "Numerical differentiation", task4),
    ("3.5", "Numerical integration", task5),
]


def main() -> int:
    status = 0
    for index, (number, title, module) in enumerate(TASKS):
        if index > 0:
            print()
        print(f"Task {number}. {title}")
        figures = getattr(module, "FIGURES", None)
        status = max(status, run(module.task, module.INPUT, [], figures))
    return status


if __name__ == "__main__":
    sys.exit(main())
