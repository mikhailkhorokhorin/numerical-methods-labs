# Lab 1. Numerical Methods of Linear Algebra

## Task

Variant 28. Every task lives in its own folder:

| No. | Folder | Method | Result |
| --- | --- | --- | --- |
| 1.1 | [task1](task1/) | LU decomposition with partial pivoting | solution of $Ax = b$, $\det A$, $A^{-1}$ |
| 1.2 | [task2](task2/) | Thomas algorithm | solution of a tridiagonal system |
| 1.3 | [task3](task3/) | simple iteration and Seidel methods | solution with precision $\varepsilon$, iterations depending on $\varepsilon$ |
| 1.4 | [task4](task4/) | Jacobi rotation method | eigenvalues and eigenvectors of a symmetric matrix, error after every rotation |
| 1.5 | [task5](task5/) | QR algorithm with Householder reflections | eigenvalues of an arbitrary matrix, iterations depending on $\varepsilon$ |

The theory and the analysis are in [report/report.pdf](report/report.pdf) (sources in [report/](report/), rebuilt with `make report LAB=lab1`).

## Build and run

```bash
make run LAB=lab1
make run LAB=lab1 TASK=task3
make run LAB=lab1 TASK=task3 ARGS=my_input.txt
make test LAB=lab1
```

The first command runs all five tasks, the second one task on its `input.txt`, the third one task on another file. Without `make`: `python3 -m lab1.main` and `python3 -m lab1.task3.main [file]` from the repository root.

## Example

Variant 28: every task reads its data from `input.txt`, the expected output is in `output.txt`.

1.1:

$$
\begin{cases}
x_1 + 4x_2 - 9x_3 + 7x_4 = -67 \\
2x_1 - 2x_2 - 2x_3 + 3x_4 = -57 \\
-x_1 + 3x_2 - 9x_3 - x_4 = -26 \\
-5x_1 + 2x_2 + 2x_3 + x_4 = 52
\end{cases}
\qquad x = (-5, 9, 7, -5), \quad \det A = 935
$$

1.2:

$$
\begin{cases}
16x_1 - 9x_2 = -27 \\
8x_1 - 13x_2 - 5x_3 = -84 \\
-3x_2 - 21x_3 + 9x_4 = -225 \\
-9x_3 + 16x_4 - 5x_5 = -89 \\
x_4 - 9x_5 = 69
\end{cases}
\qquad x = (0, 3, 9, -3, -8)
$$

1.3, $\varepsilon = 10^{-4}$:

$$
\begin{cases}
10x_1 + 2x_3 + 4x_4 = 110 \\
2x_1 + 16x_2 - 3x_3 + 8x_4 = 128 \\
x_1 + 5x_2 + 11x_3 - 4x_4 = 102 \\
8x_1 + x_2 + 6x_3 - 17x_4 = 81
\end{cases}
\qquad x = (9, 7, 6, 2)
$$

1.4 and 1.5, $\varepsilon = 10^{-6}$:

$$
A_{1.4} = \begin{pmatrix} 3 & 2 & 6 \\ 2 & -3 & -7 \\ 6 & -7 & 3 \end{pmatrix}, \quad
\lambda \approx -9.7068,\ 2.4775,\ 10.2293
\qquad
A_{1.5} = \begin{pmatrix} -6 & -3 & 7 \\ 9 & 1 & -6 \\ 3 & -5 & 5 \end{pmatrix}, \quad
\lambda \approx -7.3888,\ -0.0545,\ 7.4433
$$

## Notes

Input: numbers separated by spaces or new lines.

| Task | Input |
| --- | --- |
| task1 | $n$, matrix $A$, vector $b$ |
| task2 | $n$, sub-diagonal $a_2, \ldots, a_n$, diagonal $b_1, \ldots, b_n$, super-diagonal $c_1, \ldots, c_{n-1}$, right-hand side $d$ |
| task3 | $n$, matrix $A$, vector $b$, precision $\varepsilon$ |
| task4 | $n$, symmetric matrix $A$, precision $\varepsilon$ |
| task5 | $n$, matrix $A$, precision $\varepsilon$ |

Invalid input or a failed method prints `error: <message>` and exits with code 1.

Layout:

```text
lab1/
  README.md
  main.py        runs all five tasks
  common.py      input reading, matrix operations, output formatting
  task1/
    main.py      reads input.txt (or the given file), solves the task, prints the result
    lu.py        the method
    input.txt    data of the variant
    output.txt   expected output, checked by the tests
  task2/ ... task5/   the same layout
  tests/         tests of every method, of common.py and of all programs
  report/        LaTeX report
```
