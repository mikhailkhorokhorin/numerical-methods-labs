# Lab 1. Numerical Methods of Linear Algebra

Direct and iterative methods for systems of linear equations and methods for the eigenvalue problem. All methods are written from scratch in pure Python.

## Tasks

Variant 28. Every task lives in its own folder with its own README: the statement, the method, the input and the output.

| No. | Task | Method | Result |
| --- | --- | --- | --- |
| 1.1 | [LU Decomposition](task1/) | LU decomposition with partial pivoting | solution of $Ax = b$, $\det A$, $A^{-1}$ |
| 1.2 | [Thomas Algorithm](task2/) | Thomas algorithm | solution of a tridiagonal system |
| 1.3 | [Simple Iteration and Seidel Methods](task3/) | simple iteration and Seidel methods | solution with precision $\varepsilon$, iterations depending on $\varepsilon$ |
| 1.4 | [Jacobi Rotation Method](task4/) | Jacobi rotation method | eigenvalues and eigenvectors of a symmetric matrix, error after every rotation |
| 1.5 | [QR Algorithm](task5/) | QR algorithm with Householder reflections | eigenvalues of an arbitrary matrix, iterations depending on $\varepsilon$ |

## Run

```bash
make run LAB=lab1
make run LAB=lab1 TASK=task1
make test LAB=lab1
```

The first command runs all five tasks, the second one task, the third the tests of the lab. Without `make`: `python3 -m lab1.main` from the repository root.
