import sys

from lab1.common import run
from lab1.task1 import main as task1
from lab1.task2 import main as task2
from lab1.task3 import main as task3
from lab1.task4 import main as task4
from lab1.task5 import main as task5

TASKS = [
    ("1.1", "LU decomposition", task1),
    ("1.2", "Thomas algorithm", task2),
    ("1.3", "Simple iteration and Seidel methods", task3),
    ("1.4", "Jacobi rotation method", task4),
    ("1.5", "QR algorithm", task5),
]


def main() -> int:
    status = 0
    for index, (number, title, module) in enumerate(TASKS):
        if index > 0:
            print()
        print(f"Task {number}. {title}")
        status = max(status, run(module.task, module.INPUT, []))
    return status


if __name__ == "__main__":
    sys.exit(main())
