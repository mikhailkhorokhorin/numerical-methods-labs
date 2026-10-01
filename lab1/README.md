# Lab 1. Numerical Methods of Linear Algebra

## Task

Five programs for variant 28 built on one shared matrix library:

| App | Method | Result |
| --- | --- | --- |
| `lu` | LU decomposition with partial pivoting | solution of $Ax = b$, $\det A$, $A^{-1}$ |
| `tridiagonal` | Thomas algorithm | solution of a tridiagonal system |
| `iterative` | simple iteration and Seidel methods | solution with precision $\varepsilon$, iteration counts |
| `rotation` | Jacobi rotation method | eigenvalues and eigenvectors of a symmetric matrix, error per rotation |
| `qr` | QR algorithm with Householder reflections | real and complex eigenvalues of an arbitrary matrix |

The statement of the variant, the theory and the analysis are in [report/report.pdf](report/report.pdf) (LaTeX sources in [report/](report/), rebuilt with `make report LAB=lab1`).

## Build and run

```bash
make run LAB=lab1 APP=lu < lab1/tests/data/lu/01.in
make run LAB=lab1 APP=tridiagonal < lab1/tests/data/tridiagonal/01.in
make run LAB=lab1 APP=iterative < lab1/tests/data/iterative/01.in
make run LAB=lab1 APP=rotation < lab1/tests/data/rotation/01.in
make run LAB=lab1 APP=qr < lab1/tests/data/qr/01.in
```

## Example

Input of `iterative`: the size $n$, the matrix $A$, the vector $b$ and the precision $\varepsilon$.

```text
4
10 0 2 4
2 16 -3 8
1 5 11 -4
8 1 6 -17
110 128 102 81
0.0001
```

Output:

```text
||alpha|| = 0.9091
A priori estimate: 146 iterations
Simple iteration: 22 iterations
x = (9.0000, 7.0000, 6.0000, 2.0000)
Seidel: 12 iterations
x = (9.0000, 7.0000, 6.0000, 2.0000)
```

## Notes

- Input is whitespace-separated. `lu`: $n$, $A$, $b$. `tridiagonal`: $n$, the sub-diagonal ($n - 1$), the diagonal ($n$), the super-diagonal ($n - 1$), the right-hand side ($n$). `rotation` and `qr`: $n$, $A$, $\varepsilon$.
- Numbers must lie in $[-10^{100}, 10^{100}]$. Invalid input, a matrix that is singular to working precision (pivot below $10^{-12} \|A\|_\infty$), a non-symmetric matrix for `rotation` or a non-convergent method print `error: <message>` to stderr and exit with code 1. `iterative` fails only if neither method converges; otherwise it reports the failed method as `no convergence after N iterations`.
- `qr` reports a pair of complex eigenvalues once the $2 \times 2$ diagonal block is isolated and its eigenvalues change by at most $\varepsilon$ between iterations.
