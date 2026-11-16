# 1.4. Jacobi Rotation Method

Finds all eigenvalues and eigenvectors of a symmetric matrix by zeroing off-diagonal elements with plane rotations.

## Task

Implement the rotation method, taking the matrix and the precision as input. Use it to find the eigenvalues and eigenvectors of a symmetric matrix. Analyse how the error depends on the number of iterations.

Variant 28:

$$
A = \begin{pmatrix} 3 & 2 & 6 \\ 2 & -3 & -7 \\ 6 & -7 & 3 \end{pmatrix}, \qquad \varepsilon = 10^{-6}
$$

Answer: $\lambda \approx 2.4775,\ -9.7068,\ 10.2293$.

## Method

A symmetric matrix is turned into a diagonal one by a sequence of plane rotations.

- **Step.** Take the off-diagonal element $a_{ij}$ with the largest absolute value and the rotation $U$ in the plane $(i, j)$ with the angle $\varphi = \frac{1}{2}\arctan\frac{2a_{ij}}{a_{ii} - a_{jj}}$ ($\varphi = \pi/4$ when $a_{ii} = a_{jj}$). Then $A^{(k+1)} = U^T A^{(k)} U$ has a zero in place of $a_{ij}$.
- **Stopping rule.** $t(A) = \sqrt{\sum_{i < j} a_{ij}^2} \le \varepsilon$.
- **Result.** The diagonal of the last matrix holds the eigenvalues, the columns of $U_1 U_2 \cdots U_k$ hold the eigenvectors. They are orthonormal because every rotation is orthogonal.

Every rotation zeroes one element but may spoil others; still $t(A)$ decreases at every step, and near the end it falls quadratically.

## Run

```bash
make run LAB=lab1 TASK=task4
make run LAB=lab1 TASK=task4 ARGS=my_input.txt
python3 -m lab1.task4.main [file]
```

Commands run from the repository root. Without an argument the program reads `input.txt` next to `main.py`.

## Input

Numbers separated by spaces or new lines: the size $n$, the symmetric matrix $A$ row by row, the precision $\varepsilon$.

```text
3
3 2 6
2 -3 -7
6 -7 3
0.000001
```

## Output

```text
Eigenvalues and eigenvectors:
lambda_1 = 2.4775, x_1 = (0.7410, 0.6150, -0.2695)
lambda_2 = -9.7068, x_2 = (-0.3862, 0.7187, 0.5783)
lambda_3 = 10.2293, x_3 = (0.5494, -0.3244, 0.7700)

Rotations: 8
Error after every rotation:
  k  off(A)
  0  9.4340e+00
  1  6.3246e+00
  2  3.9081e+00
  3  1.4365e+00
  4  8.2361e-01
  5  4.8846e-02
  6  3.3034e-03
  7  2.0768e-05
  8  3.4412e-09
```

Every eigenvalue with its eigenvector, the number of rotations and the error $t(A)$ after every rotation: it falls from $9.4$ to $3.4 \cdot 10^{-9}$ in 8 rotations.

## Analysis

- The error $t(A)$ decreases after every rotation, even though a rotation can make a zeroed element nonzero again.
- At first it falls slowly ($9.43 \to 6.32 \to 3.91$), near the end quadratically ($2.1 \cdot 10^{-5} \to 3.4 \cdot 10^{-9}$).
- Eight rotations are enough for $\varepsilon = 10^{-6}$; the product of the rotations gives orthonormal eigenvectors.

## Files

| File | Contents |
| --- | --- |
| [main.py](main.py) | the variant: reads the input, prints the result |
| [rotation.py](rotation.py) | the Jacobi rotation method |
| [input.txt](input.txt) | data of the variant |
| [output.txt](output.txt) | expected output, checked by the tests |

Invalid input or a failed method prints `error: <message>` to stderr and exits with code 1.
