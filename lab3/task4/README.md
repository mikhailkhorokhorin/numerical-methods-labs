# 3.4. Numerical Differentiation

Computes the first and second derivatives of a tabulated function with formulas of the first and second order.

## Task

Compute the first and the second derivatives of the function given by a table at the point $X^*$.

Variant 28:

| $x_i$ | 0.0 | 0.2 | 0.4 | 0.6 | 0.8 |
| --- | --- | --- | --- | --- | --- |
| $y_i$ | 0.0 | 0.048856 | 0.23869 | 0.65596 | 1.4243 |

$X^* = 0.4$. Answer: $y'(0.4) \approx 1.5178$, $y''(0.4) \approx 5.6859$.

## Method

The derivatives are the derivatives of the interpolation polynomial through neighbouring nodes. With $X^* = x_2$ and step $h = 0.2$:

- **left difference** (first order): $y' \approx \frac{y_2 - y_1}{x_2 - x_1} = 0.9492$;
- **right difference** (first order): $y' \approx \frac{y_3 - y_2}{x_3 - x_2} = 2.0864$;
- **second order** (the parabola through $x_1, x_2, x_3$):
  $$y' \approx \frac{y_2 - y_1}{x_2 - x_1} + \frac{\frac{y_3 - y_2}{x_3 - x_2} - \frac{y_2 - y_1}{x_2 - x_1}}{x_3 - x_1}(2X^* - x_1 - x_2) = 1.5178;$$
- **second derivative:** $y'' \approx 2\frac{\frac{y_3 - y_2}{x_3 - x_2} - \frac{y_2 - y_1}{x_2 - x_1}}{x_3 - x_1} = 5.6859$.

The table is $y = x^2 e^x$ rounded to five digits, with $y'(0.4) = 1.4322$ and $y''(0.4) = 5.6093$: the second-order formula is much closer than the one-sided ones. The formulas also work for unequally spaced nodes and for points between nodes.

## Run

```bash
make run LAB=lab3 TASK=task4
make run LAB=lab3 TASK=task4 ARGS=my_input.txt
python3 -m lab3.task4.main [file]
```

Commands run from the repository root. Without an argument the program reads `input.txt` next to `main.py`.

## Input

Numbers separated by spaces or new lines: the number of nodes $n$, the nodes $x_i$, the values $y_i$, the point $X^*$.

```text
5
0.0 0.2 0.4 0.6 0.8
0.0 0.048856 0.23869 0.65596 1.4243
0.4
```

## Output

```text
Left difference:   y'(0.4000) = 0.9492
Right difference:  y'(0.4000) = 2.0864
Second order:      y'(0.4000) = 1.5178
Second derivative: y''(0.4000) = 5.6859
```

The left and right differences, the second-order first derivative and the second derivative.

## Files

| File | Contents |
| --- | --- |
| [main.py](main.py) | the variant: reads the input, prints the result |
| [derivative.py](derivative.py) | one-sided, second-order and second-derivative formulas |
| [input.txt](input.txt) | data of the variant |
| [output.txt](output.txt) | expected output, checked by the tests |

Invalid input or a failed method prints `error: <message>` to stderr and exits with code 1.
