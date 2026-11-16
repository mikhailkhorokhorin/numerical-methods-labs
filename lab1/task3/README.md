# 1.3. Simple Iteration and Seidel Methods

[Lab 1](../README.md) / 1.3

Solves a linear system iteratively with a given precision and compares how many iterations the two methods need.

## Task

Implement the simple iteration method and the Seidel method, taking the matrix, the right-hand side and the precision as input. Use them to solve a system of linear equations. Analyse the number of iterations needed to reach the given precision.

Variant 28:

$$
\begin{cases}
10x_1 + 2x_3 + 4x_4 = 110 \\
2x_1 + 16x_2 - 3x_3 + 8x_4 = 128 \\
x_1 + 5x_2 + 11x_3 - 4x_4 = 102 \\
8x_1 + x_2 + 6x_3 - 17x_4 = 81
\end{cases}
\qquad \varepsilon = 10^{-4}
$$

Answer: $x = (9, 7, 6, 2)$.

## Method

Each equation is solved for its diagonal unknown, which gives the form $x = \beta + \alpha x$ with $\beta_i = b_i / a_{ii}$, $\alpha_{ij} = -a_{ij} / a_{ii}$, $\alpha_{ii} = 0$.

- **Simple iteration (Jacobi).** $x^{(k+1)} = \beta + \alpha x^{(k)}$. It converges when $\lVert \alpha \rVert_\infty < 1$, for example for a diagonally dominant matrix.
- **Seidel.** The same formula, but every new component is used at once: $x_i^{(k+1)} = \beta_i + \sum_{j < i} \alpha_{ij} x_j^{(k+1)} + \sum_{j > i} \alpha_{ij} x_j^{(k)}$.
- **Stopping rule.** The a posteriori estimate $\varepsilon^{(k)} = \frac{\lVert \alpha \rVert}{1 - \lVert \alpha \rVert} \lVert x^{(k)} - x^{(k-1)} \rVert_\infty \le \varepsilon$; for Seidel the numerator uses the upper triangle of $\alpha$.
- **A priori estimate.** $k + 1 \ge \frac{\lg \varepsilon - \lg \lVert \beta \rVert + \lg(1 - \lVert \alpha \rVert)}{\lg \lVert \alpha \rVert}$ iterations always suffice. Here $\lVert \alpha \rVert_\infty = 0.9091$ is close to 1, so the bound is far too pessimistic.

## Run

```bash
make run LAB=lab1 TASK=task3
make run LAB=lab1 TASK=task3 ARGS=my_input.txt
python3 -m lab1.task3.main [file]
```

Commands run from the repository root. Without an argument the program reads `input.txt` next to `main.py`.

## Input

Numbers separated by spaces or new lines: the size $n$, the matrix $A$ row by row, the right-hand side $b$, the precision $\varepsilon$.

```text
4
10 0 2 4
2 16 -3 8
1 5 11 -4
8 1 6 -17
110 128 102 81
0.0001
```

## Output

```text
||alpha|| = 0.9091
A priori estimate: 146 iterations
Simple iteration: 22 iterations
x = (9.0000, 7.0000, 6.0000, 2.0000)
Seidel: 12 iterations
x = (9.0000, 7.0000, 6.0000, 2.0000)

Iterations depending on the precision:
    eps  a priori   simple   Seidel
  1e-01        74       12        7
  1e-02        98       15        9
  1e-03       122       18       10
  1e-04       146       22       12
  1e-05       171       26       14
  1e-06       195       29       15
  1e-07       219       33       17
  1e-08       243       36       19
  1e-09       267       40       20
  1e-10       291       43       22
```

$\lVert \alpha \rVert_\infty$, the a priori estimate, the solution and the number of iterations of both methods, and a table of iterations for $\varepsilon = 10^{-1}, \ldots, 10^{-10}$. Seidel needs about half as many iterations as simple iteration, both grow linearly with the number of correct digits.

## Analysis

| $\varepsilon$ | a priori | simple iteration | Seidel |
| --- | --- | --- | --- |
| $10^{-2}$ | 98 | 15 | 9 |
| $10^{-4}$ | 146 | 22 | 12 |
| $10^{-6}$ | 195 | 29 | 15 |
| $10^{-8}$ | 243 | 36 | 19 |
| $10^{-10}$ | 291 | 43 | 22 |

- Both methods converge linearly: every new decimal digit costs a constant number of iterations, about 3.5 for simple iteration and 1.7 for Seidel.
- Seidel needs about half as many iterations, because every new component is used immediately.
- The a priori estimate is valid but 7 times too pessimistic: it only uses $\lVert \alpha \rVert_\infty = 0.9091$, while the real error falls much faster.

## Files

| File | Contents |
| --- | --- |
| [main.py](main.py) | the variant: reads the input, prints the result |
| [iterative.py](iterative.py) | reduction to the iteration form, both methods, the a priori estimate |
| [input.txt](input.txt) | data of the variant |
| [output.txt](output.txt) | expected output, checked by the tests |

Invalid input or a failed method prints `error: <message>` to stderr and exits with code 1.
