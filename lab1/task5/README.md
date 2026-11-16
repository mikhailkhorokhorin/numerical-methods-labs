# 1.5. QR Algorithm

[Lab 1](../README.md) / 1.5

Finds all eigenvalues of an arbitrary matrix, including complex ones, by repeated QR decompositions.

## Task

Implement the QR decomposition of a matrix. Based on it, implement the QR algorithm for the full eigenvalue problem of an arbitrary matrix, taking the matrix and the precision as input. Use it to find the eigenvalues of the matrix.

Variant 28:

$$
A = \begin{pmatrix} -6 & -3 & 7 \\ 9 & 1 & -6 \\ 3 & -5 & 5 \end{pmatrix}, \qquad \varepsilon = 10^{-6}
$$

Answer: $\lambda \approx 7.4433,\ -7.3888,\ -0.0545$.

## Method

- **QR decomposition.** $A = QR$ with orthogonal $Q$ and upper triangular $R$. Column $k$ is cleared below the diagonal by the Householder reflection $H = E - 2\frac{vv^T}{v^Tv}$, where $v$ is built from the column so that $Hx$ is a multiple of $e_k$. Then $R = H_{n-1} \cdots H_1 A$ and $Q = H_1 \cdots H_{n-1}$.
- **QR algorithm.** $A^{(k)} = Q^{(k)}R^{(k)}$, $A^{(k+1)} = R^{(k)}Q^{(k)} = Q^{(k)T}A^{(k)}Q^{(k)}$. The matrices are similar, so the eigenvalues do not change, while the elements below the diagonal tend to zero.
- **Complex eigenvalues.** A pair of complex eigenvalues shows up as a $2 \times 2$ block on the diagonal that does not vanish; its eigenvalues are the roots of a quadratic equation. A block is accepted when its eigenvalues change by less than $\varepsilon$ between iterations.
- **Stopping rule.** Every subdiagonal column is either below $\varepsilon$ in norm or belongs to a converged $2 \times 2$ block.

## Run

```bash
make run LAB=lab1 TASK=task5
make run LAB=lab1 TASK=task5 ARGS=my_input.txt
python3 -m lab1.task5.main [file]
```

Commands run from the repository root. Without an argument the program reads `input.txt` next to `main.py`.

## Input

Numbers separated by spaces or new lines: the size $n$, the matrix $A$ row by row, the precision $\varepsilon$.

```text
3
-6 -3 7
9 1 -6
3 -5 5
0.000001
```

## Output

```text
Q =
  -0.5345  -0.4174  -0.7349
   0.8018   0.0246  -0.5971
   0.2673  -0.9084   0.3215
R =
  11.2250   1.0690  -7.2161
   0.0000   5.8187  -7.6109
   0.0000   0.0000   0.0459

Eigenvalues:
lambda_1 = 7.4433
lambda_2 = -7.3888
lambda_3 = -0.0545
Iterations: 5

Iterations depending on the precision:
    eps  iterations
  1e-01           2
  1e-02           3
  1e-03           3
  1e-04           4
  1e-05           4
  1e-06           5
  1e-07           5
  1e-08           6
  1e-09           6
  1e-10           7
```

The factors $Q$ and $R$ of the first decomposition, the eigenvalues, the number of iterations and a table of iterations for $\varepsilon = 10^{-1}, \ldots, 10^{-10}$.

## Analysis

| $\varepsilon$ | $10^{-2}$ | $10^{-4}$ | $10^{-6}$ | $10^{-8}$ | $10^{-10}$ |
| --- | --- | --- | --- | --- | --- |
| iterations | 3 | 4 | 5 | 6 | 7 |

The subdiagonal elements decrease geometrically, so every two additional digits cost about one more iteration.

## Files

| File | Contents |
| --- | --- |
| [main.py](main.py) | the variant: reads the input, prints the result |
| [qr.py](qr.py) | the QR decomposition with Householder reflections and the QR algorithm |
| [input.txt](input.txt) | data of the variant |
| [output.txt](output.txt) | expected output, checked by the tests |

Invalid input or a failed method prints `error: <message>` to stderr and exits with code 1.
