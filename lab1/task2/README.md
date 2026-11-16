# 1.2. Thomas Algorithm

Solves a linear system with a tridiagonal matrix in $O(n)$ operations, storing only the three diagonals.

## Task

Implement the Thomas algorithm (tridiagonal matrix algorithm), taking the nonzero elements of the matrix and the right-hand side as input. Use it to solve a system of linear equations with a tridiagonal matrix.

Variant 28:

$$
\begin{cases}
16x_1 - 9x_2 = -27 \\
8x_1 - 13x_2 - 5x_3 = -84 \\
-3x_2 - 21x_3 + 9x_4 = -225 \\
-9x_3 + 16x_4 - 5x_5 = -89 \\
x_4 - 9x_5 = 69
\end{cases}
$$

Answer: $x = (0, 3, 9, -3, -8)$.

## Method

Every equation links only neighbouring unknowns: $a_i x_{i-1} + b_i x_i + c_i x_{i+1} = d_i$, $a_1 = c_n = 0$. Only the three diagonals are stored.

- **Forward sweep.** The solution is searched as $x_i = P_i x_{i+1} + Q_i$:
  $$P_i = \frac{-c_i}{b_i + a_i P_{i-1}}, \qquad Q_i = \frac{d_i - a_i Q_{i-1}}{b_i + a_i P_{i-1}}, \qquad P_0 = Q_0 = 0.$$
- **Back substitution.** $x_n = Q_n$, then $x_i = P_i x_{i+1} + Q_i$ for $i = n - 1, \ldots, 1$.
- **Stability.** The algorithm is stable when $|b_i| \ge |a_i| + |c_i|$ for every row with strict inequality in at least one row and $a_i, c_i \ne 0$. The program reports whether the condition holds.

The method costs $O(n)$ operations instead of $O(n^3)$ for Gaussian elimination.

## Run

```bash
make run LAB=lab1 TASK=task2
make run LAB=lab1 TASK=task2 ARGS=my_input.txt
python3 -m lab1.task2.main [file]
```

Commands run from the repository root. Without an argument the program reads `input.txt` next to `main.py`.

## Input

Numbers separated by spaces or new lines: the size $n$, the sub-diagonal $a_2, \ldots, a_n$, the diagonal $b_1, \ldots, b_n$, the super-diagonal $c_1, \ldots, c_{n-1}$, the right-hand side $d$.

```text
5
8 -3 -9 1
16 -13 -21 16 -9
-9 -5 9 -5
-27 -84 -225 -89 69
```

## Output

```text
x = (0.0000, 3.0000, 9.0000, -3.0000, -8.0000)
Stability condition: yes
```

The solution $x$ and whether the sufficient stability condition holds.

## Files

| File | Contents |
| --- | --- |
| [main.py](main.py) | the variant: reads the input, prints the result |
| [tridiagonal.py](tridiagonal.py) | the Thomas algorithm and the stability check |
| [input.txt](input.txt) | data of the variant |
| [output.txt](output.txt) | expected output, checked by the tests |

Invalid input or a failed method prints `error: <message>` to stderr and exits with code 1.
