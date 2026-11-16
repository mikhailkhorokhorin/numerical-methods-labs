# Lab 3. Approximation, Numerical Differentiation and Integration

Interpolation, splines, least squares, numerical differentiation and integration of functions given by a formula or a table. The spline and the normal equations reuse the Thomas algorithm and the LU decomposition from lab 1.

## Tasks

Variant 28. Every task lives in its own folder with its own README: the statement, the method, the input and the output.

| No. | Task | Method | Result |
| --- | --- | --- | --- |
| 3.1 | [Lagrange and Newton Interpolation](task1/) | Lagrange and Newton interpolation polynomials | polynomials for two sets of nodes, interpolation error at $X^*$ |
| 3.2 | [Cubic Spline](task2/) | natural cubic spline | spline coefficients, value at $X^*$ |
| 3.3 | [Least Squares](task3/) | least squares | polynomials of degree 1 and 2, sums of squared errors, graphs |
| 3.4 | [Numerical Differentiation](task4/) | numerical differentiation | first and second derivatives at $X^*$ |
| 3.5 | [Numerical Integration](task5/) | rectangle, trapezoid and Simpson rules | integral for two steps, Runge-Romberg error estimate |

## Run

```bash
make run LAB=lab3
make run LAB=lab3 TASK=task1
make test LAB=lab3
```

The first command runs all five tasks, the second one task, the third the tests of the lab. Without `make`: `python3 -m lab3.main` from the repository root.
