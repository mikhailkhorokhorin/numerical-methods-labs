from itertools import pairwise

from lab1.common import InputReader, Vector, format_number


def evaluate(coefficients: Vector, x: float) -> float:
    result = 0.0
    for value in reversed(coefficients):
        result = result * x + value
    return result


def multiply_linear(coefficients: Vector, root: float) -> Vector:
    result = [0.0] * (len(coefficients) + 1)
    for power, value in enumerate(coefficients):
        result[power + 1] += value
        result[power] -= root * value
    return result


def format_polynomial(coefficients: Vector) -> str:
    terms: list[tuple[bool, str]] = []
    for power, value in enumerate(coefficients):
        magnitude = format_number(abs(value))
        if float(magnitude) == 0.0:
            continue
        monomial = "" if power == 0 else "x" if power == 1 else f"x^{power}"
        terms.append((value < 0.0, f"{magnitude}{monomial}"))
    if not terms:
        return format_number(0.0)
    negative, first = terms[0]
    text = f"-{first}" if negative else first
    for negative, term in terms[1:]:
        text += f" {'-' if negative else '+'} {term}"
    return text


def read_table(reader: InputReader, minimum: int) -> tuple[Vector, Vector]:
    n = reader.size(minimum)
    return reader.vector(n), reader.vector(n)


def check_increasing(xs: Vector) -> None:
    if any(right <= left for left, right in pairwise(xs)):
        raise ValueError("nodes must be strictly increasing")
