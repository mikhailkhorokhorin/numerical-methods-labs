import sys

from lab1.common import run
from lab2.task1 import main as task1
from lab2.task2 import main as task2

TASKS = [
    ("2.1", "Simple iteration and Newton methods for an equation", task1),
    ("2.2", "Simple iteration and Newton methods for a system", task2),
]


def main() -> int:
    status = 0
    for index, (number, title, module) in enumerate(TASKS):
        if index > 0:
            print()
        print(f"Task {number}. {title}")
        figure = getattr(module, "figure", None)
        status = max(status, run(module.task, module.INPUT, [], figure))
    return status


if __name__ == "__main__":
    sys.exit(main())
