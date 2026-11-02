import sys
from pathlib import Path

from lab1.common import (
    InputReader,
    Matrix,
    Vector,
    format_number,
    format_vector,
    iterations_text,
    matrix_norm_inf,
    run,
)
from lab1.task3.iterative import (
    IterationResult,
    apriori_iterations,
    seidel,
    simple_iteration,
    to_iteration_form,
)

INPUT = Path(__file__).with_name("input.txt")
PRECISIONS = [10.0**-power for power in range(1, 11)]


def _result_lines(name: str, result: IterationResult) -> list[str]:
    if not result.converged:
        return [f"{name}: no convergence after {iterations_text(result.iterations)}"]
    return [
        f"{name}: {iterations_text(result.iterations)}",
        f"x = {format_vector(result.solution)}",
    ]


def _count(result: IterationResult) -> str:
    return str(result.iterations) if result.converged else "-"


def _analysis(matrix: Matrix, rhs: Vector) -> list[str]:
    lines = [
        "Iterations depending on the precision:",
        f"{'eps':>7}  {'a priori':>8}  {'simple':>7}  {'Seidel':>7}",
    ]
    for eps in PRECISIONS:
        estimate = apriori_iterations(matrix, rhs, eps)
        jacobi = _count(simple_iteration(matrix, rhs, eps))
        gauss_seidel = _count(seidel(matrix, rhs, eps))
        bound = "-" if estimate is None else str(estimate)
        lines.append(f"{eps:7.0e}  {bound:>8}  {jacobi:>7}  {gauss_seidel:>7}")
    return lines


def task(reader: InputReader) -> list[str]:
    n = reader.size()
    matrix = reader.matrix(n)
    rhs = reader.vector(n)
    eps = reader.precision()
    reader.finish()

    form = to_iteration_form(matrix, rhs)
    jacobi = simple_iteration(matrix, rhs, eps)
    gauss_seidel = seidel(matrix, rhs, eps)
    estimate = apriori_iterations(matrix, rhs, eps)
    if not jacobi.converged and not gauss_seidel.converged:
        raise RuntimeError("neither method converged")

    return [
        f"||alpha|| = {format_number(matrix_norm_inf(form.alpha))}",
        f"A priori estimate: {'none' if estimate is None else iterations_text(estimate)}",
        *_result_lines("Simple iteration", jacobi),
        *_result_lines("Seidel", gauss_seidel),
        "",
        *_analysis(matrix, rhs),
    ]


if __name__ == "__main__":
    sys.exit(run(task, INPUT, sys.argv[1:]))
