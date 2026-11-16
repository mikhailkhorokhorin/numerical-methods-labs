# Lab 4. Numerical Methods for Ordinary Differential Equations

Initial and boundary value problems for second-order ordinary differential equations. The finite difference method reuses the Thomas algorithm from lab 1, the error estimates reuse the Runge-Romberg method from lab 3.

## Tasks

Variant 28. Every task lives in its own folder with its own README: the statement, the method, the input and the output.

| No. | Task | Method | Result |
| --- | --- | --- | --- |
| 4.1 | [Cauchy Problem](task1/) | Euler, Runge-Kutta and Adams methods of order 4 | solution of a Cauchy problem, Runge-Romberg and exact errors |
| 4.2 | [Boundary Value Problem](task2/) | shooting and finite difference methods | solution of a boundary value problem, Runge-Romberg and exact errors |

## Run

```bash
make run LAB=lab4
make run LAB=lab4 TASK=task1
make test LAB=lab4
```

The first command runs both tasks, the second one task, the third the tests of the lab. Without `make`: `python3 -m lab4.main` from the repository root.
