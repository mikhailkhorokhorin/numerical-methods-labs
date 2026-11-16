# Lab 2. Numerical Methods for Nonlinear Equations

Simple iteration and Newton methods for a single nonlinear equation and for a system of nonlinear equations. Linear systems inside Newton's method are solved with the LU decomposition from lab 1.

## Tasks

Variant 28. Every task lives in its own folder with its own README: the statement, the method, the input and the output.

| No. | Task | Method | Result |
| --- | --- | --- | --- |
| 2.1 | [Simple Iteration and Newton Methods for an Equation](task1/) | simple iteration and Newton methods | positive root of a nonlinear equation, error depending on the iteration |
| 2.2 | [Simple Iteration and Newton Methods for a System](task2/) | simple iteration and Newton methods for systems | positive solution of a nonlinear system, error depending on the iteration |

## Run

```bash
make run LAB=lab2
make run LAB=lab2 TASK=task1
make test LAB=lab2
```

The first command runs both tasks, the second one task, the third the tests of the lab. Without `make`: `python3 -m lab2.main` from the repository root.
