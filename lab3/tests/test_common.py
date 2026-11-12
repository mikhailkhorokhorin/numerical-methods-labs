import pytest

from lab1.common import InputReader
from lab3.common import check_increasing, evaluate, format_polynomial, multiply_linear, read_table


def test_evaluates_and_multiplies_polynomials() -> None:
    assert evaluate([1.0, -2.0, 3.0], 2.0) == 9.0
    assert evaluate([], 5.0) == 0.0
    assert multiply_linear([1.0], 2.0) == [-2.0, 1.0]
    assert multiply_linear([-2.0, 1.0], -3.0) == [-6.0, 1.0, 1.0]


@pytest.mark.parametrize(
    ("coefficients", "text"),
    [
        ([0.3284, -0.53007], "0.3284 - 0.5301x"),
        ([0.0, 1.09807, -0.31518, -0.24434], "1.0981x - 0.3152x^2 - 0.2443x^3"),
        ([-1.0, 0.0, 2.0], "-1.0000 + 2.0000x^2"),
        ([1e-9, -1e-9], "0.0000"),
        ([], "0.0000"),
    ],
)
def test_formats_polynomials(coefficients: list[float], text: str) -> None:
    assert format_polynomial(coefficients) == text


def test_reads_tables() -> None:
    reader = InputReader("3\n0 1 2\n5 6 7\n")
    assert read_table(reader, 2) == ([0.0, 1.0, 2.0], [5.0, 6.0, 7.0])
    with pytest.raises(ValueError, match="expected a size from 3"):
        read_table(InputReader("2 0 1 0 1"), 3)


def test_checks_increasing_nodes() -> None:
    check_increasing([0.0, 1.0, 3.0])
    with pytest.raises(ValueError, match="strictly increasing"):
        check_increasing([0.0, 1.0, 1.0])
