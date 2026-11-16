import sys

from lab1.common import run
from lab4.task1 import main as task1
from lab4.task2 import main as task2

TASKS = [
    ("4.1", "Euler, Runge-Kutta and Adams methods", task1),
    ("4.2", "Shooting and finite difference methods", task2),
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
