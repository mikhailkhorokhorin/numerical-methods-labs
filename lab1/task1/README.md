# 1.1. LU Decomposition

Solves a linear system through the factorization $PA = LU$ and reuses the factors for the determinant and the inverse matrix.

## Task

Implement the LU decomposition of a matrix with the choice of the pivot element. Use it to solve a system of linear algebraic equations. For the matrix of the system compute the determinant and the inverse matrix.

Variant 28:

$$
\begin{cases}
x_1 + 4x_2 - 9x_3 + 7x_4 = -67 \\
2x_1 - 2x_2 - 2x_3 + 3x_4 = -57 \\
-x_1 + 3x_2 - 9x_3 - x_4 = -26 \\
-5x_1 + 2x_2 + 2x_3 + x_4 = 52
\end{cases}
$$

Answer: $x = (-5, 9, 7, -5)$, $\det A = 935$.

## Method

Gaussian elimination is stored as a product $PA = LU$: $L$ is lower triangular with ones on the diagonal (the elimination multipliers), $U$ is upper triangular, $P$ is the permutation of rows.

- **Pivoting.** At step $k$ the row with the largest $|u_{ik}|$, $i \ge k$, is swapped into position $k$. Every multiplier then satisfies $|l_{ik}| \le 1$, which keeps the rounding errors small. A pivot below $10^{-12}\lVert A \rVert_\infty$ means the matrix is singular.
- **Solving.** $Ly = Pb$ by forward substitution, then $Ux = y$ by back substitution.
- **Determinant.** $\det A = (-1)^s \prod_i u_{ii}$, where $s$ is the number of row swaps.
- **Inverse.** Column $j$ of $A^{-1}$ is the solution of $Ax = e_j$; the decomposition is reused for all $n$ columns.

The decomposition costs $O(n^3)$ once, every further solution costs only $O(n^2)$.

## Run

```bash
make run LAB=lab1 TASK=task1
make run LAB=lab1 TASK=task1 ARGS=my_input.txt
python3 -m lab1.task1.main [file]
```

Commands run from the repository root. Without an argument the program reads `input.txt` next to `main.py`.

## Input

Numbers separated by spaces or new lines: the size $n$, the matrix $A$ row by row, the right-hand side $b$.

```text
4
1 4 -9 7
2 -2 -2 3
-1 3 -9 -1
-5 2 2 1
-67 -57 -26 52
```

## Output

```text
P = (4, 1, 3, 2)
L =
   1.0000   0.0000   0.0000   0.0000
  -0.2000   1.0000   0.0000   0.0000
   0.2000   0.5909   1.0000   0.0000
  -0.4000  -0.2727   0.8211   1.0000
U =
  -5.0000   2.0000   2.0000   1.0000
   0.0000   4.4000  -8.6000   7.2000
   0.0000   0.0000  -4.3182  -5.4545
   0.0000   0.0000   0.0000   9.8421
x = (-5.0000, 9.0000, 7.0000, -5.0000)
det(A) = 935.0000
A^-1 =
   0.1027  -0.1979  -0.1112  -0.2364
   0.1786  -0.4171  -0.1102  -0.1091
   0.0396  -0.1283  -0.1262  -0.0182
   0.0770   0.1016  -0.0834   0.0727
```

$P$ is the permutation (row $i$ of $PA$ is row $P_i$ of $A$), then the factors $L$ and $U$, the solution $x$, the determinant and the inverse matrix.

## Files

| File | Contents |
| --- | --- |
| [main.py](main.py) | the variant: reads the input, prints the result |
| [lu.py](lu.py) | LU decomposition with partial pivoting, solving, determinant, inverse |
| [input.txt](input.txt) | data of the variant |
| [output.txt](output.txt) | expected output, checked by the tests |

Invalid input or a failed method prints `error: <message>` to stderr and exits with code 1.
