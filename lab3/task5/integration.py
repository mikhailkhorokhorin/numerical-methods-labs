from collections.abc import Callable

from lab1.common import step_count

Function = Callable[[float], float]
Rule = Callable[[Function, float, float, float], float]


def rectangles(f: Function, a: float, b: float, h: float) -> float:
    n = step_count(a, b, h)
    step = (b - a) / n
    return step * sum(f(a + (i + 0.5) * step) for i in range(n))


def trapezoids(f: Function, a: float, b: float, h: float) -> float:
    n = step_count(a, b, h)
    step = (b - a) / n
    return step * ((f(a) + f(b)) / 2.0 + sum(f(a + i * step) for i in range(1, n)))


def simpson(f: Function, a: float, b: float, h: float) -> float:
    n = step_count(a, b, h)
    if n % 2 != 0:
        raise ValueError("Simpson's method needs an even number of steps")
    step = (b - a) / n
    inner = sum((4.0 if i % 2 else 2.0) * f(a + i * step) for i in range(1, n))
    return step / 3.0 * (f(a) + f(b) + inner)


METHODS: list[tuple[str, Rule, int]] = [
    ("Rectangles", rectangles, 2),
    ("Trapezoids", trapezoids, 2),
    ("Simpson", simpson, 4),
]


def runge_romberg(coarse: float, fine: float, ratio: float, order: int) -> float:
    if ratio <= 1.0:
        raise ValueError("Runge-Romberg needs a coarse step larger than the fine one")
    return (fine - coarse) / (ratio**order - 1.0)
