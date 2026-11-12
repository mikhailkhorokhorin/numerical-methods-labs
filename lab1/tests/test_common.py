import math
from pathlib import Path

import pytest

from lab1.common import (
    PLOT_NAME,
    InputReader,
    Series,
    chart,
    column,
    copy_matrix,
    distance_inf,
    format_complex,
    format_matrix,
    format_number,
    format_scientific,
    format_table,
    format_vector,
    identity,
    is_square,
    is_symmetric,
    linspace,
    matmul,
    matrix_norm_inf,
    matvec,
    norm_inf,
    parse_number,
    run,
    save_figure,
    step_count,
    transposed,
    zeros,
)


def test_builds_zeros_and_identity() -> None:
    assert zeros(2, 3) == [[0.0, 0.0, 0.0], [0.0, 0.0, 0.0]]
    assert identity(2) == [[1.0, 0.0], [0.0, 1.0]]
    assert is_square([])
    assert not is_square(zeros(2, 3))


def test_copies_extracts_columns_and_transposes() -> None:
    matrix = [[1.0, 2.0], [3.0, 4.0], [5.0, 6.0]]
    copy = copy_matrix(matrix)
    copy[0][0] = 9.0
    assert matrix[0][0] == 1.0
    assert column(matrix, 1) == [2.0, 4.0, 6.0]
    assert transposed(matrix) == [[1.0, 3.0, 5.0], [2.0, 4.0, 6.0]]
    assert transposed([]) == []


def test_multiplies() -> None:
    lhs = [[1.0, 2.0], [3.0, 4.0]]
    assert matmul(lhs, [[0.0, 1.0], [1.0, 0.0]]) == [[2.0, 1.0], [4.0, 3.0]]
    assert matvec(lhs, [1.0, -1.0]) == [-1.0, -1.0]
    with pytest.raises(ValueError, match="matrix sizes do not match"):
        matmul(lhs, zeros(3, 1))
    with pytest.raises(ValueError, match="matrix and vector sizes do not match"):
        matvec(lhs, [0.0, 0.0, 0.0])


def test_computes_infinity_norms() -> None:
    assert norm_inf([1.0, -7.0, 3.0]) == 7.0
    assert matrix_norm_inf([[1.0, -2.0], [-3.0, 0.5]]) == 3.5
    assert distance_inf([1.0, 2.0], [1.5, -1.0]) == 3.0
    with pytest.raises(ValueError, match="vector sizes do not match"):
        distance_inf([1.0], [1.0, 2.0])


def test_checks_symmetry() -> None:
    assert is_symmetric([[1.0, 2.0], [2.0, 3.0]])
    assert not is_symmetric([[1.0, 2.0], [2.1, 3.0]])
    assert is_symmetric([[1.0, 2.0], [2.1, 3.0]], 0.2)
    assert not is_symmetric(zeros(2, 3))


def test_reads_sizes_matrices_vectors_and_precision() -> None:
    reader = InputReader("2\n1 -2.5\n3e-1 4\n+1 .5\n0.001\n")
    n = reader.size()
    assert reader.matrix(n) == [[1.0, -2.5], [0.3, 4.0]]
    assert reader.vector(n) == [1.0, 0.5]
    assert reader.precision() == 0.001
    reader.finish()


@pytest.mark.parametrize("text", ["0", "1001", "-1", "2.5", "x", "+2"])
def test_rejects_invalid_sizes(text: str) -> None:
    with pytest.raises(ValueError, match="expected a size from 1 to 1000"):
        InputReader(text).size()


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("x", "expected a number, got 'x'"),
        ("nan", r"numbers must lie in \[-1e100, 1e100\]"),
        ("1e101", "numbers must lie"),
        ("", "unexpected end of input"),
    ],
)
def test_rejects_invalid_numbers(text: str, message: str) -> None:
    with pytest.raises(ValueError, match=message):
        InputReader(text).number()


def test_rejects_non_positive_precision_and_trailing_input() -> None:
    with pytest.raises(ValueError, match="precision must be positive"):
        InputReader("0").precision()
    reader = InputReader("1 2")
    reader.number()
    with pytest.raises(ValueError, match="unexpected trailing input '2'"):
        reader.finish()


def test_formats_numbers_vectors_and_matrices() -> None:
    assert format_number(1.23456) == "1.2346"
    assert format_number(-0.00001) == "0.0000"
    assert format_scientific(0.000123) == "1.2300e-04"
    assert format_vector([1.0, -0.5]) == "(1.0000, -0.5000)"
    assert format_matrix([[1.0, -10.0], [100.0, 0.0]]) == [
        "    1.0000  -10.0000",
        "  100.0000    0.0000",
    ]


def test_formats_complex_numbers() -> None:
    assert format_complex(complex(1.5, 1e-9)) == "1.5000"
    assert format_complex(complex(1.0, 2.0)) == "1.0000 + 2.0000i"
    assert format_complex(complex(-1.0, -2.0)) == "-1.0000 - 2.0000i"


def double(reader: InputReader) -> list[str]:
    value = reader.number()
    reader.finish()
    return [f"2x = {2 * value}", "done"]


def test_run_prints_the_result(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "input.txt"
    path.write_text("2.5\n", encoding="utf-8")
    assert run(double, path, []) == 0
    assert capsys.readouterr() == ("2x = 5.0\ndone\n", "")


def test_run_takes_the_input_file_from_arguments(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    other = tmp_path / "other.txt"
    other.write_text("1\n", encoding="utf-8")
    assert run(double, tmp_path / "missing.txt", [str(other)]) == 0
    assert capsys.readouterr().out == "2x = 2.0\ndone\n"


def test_run_reports_errors(tmp_path: Path, capsys: pytest.CaptureFixture[str]) -> None:
    path = tmp_path / "input.txt"
    path.write_text("x\n", encoding="utf-8")
    assert run(double, path, []) == 1
    assert capsys.readouterr() == ("", "error: expected a number, got 'x'\n")
    assert run(double, tmp_path / "missing.txt", []) == 1
    assert "error: file not found" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("token", "value"),
    [
        ("pi/6", math.pi / 6.0),
        ("5*pi/12", 5.0 * math.pi / 12.0),
        ("-pi", -math.pi),
        ("+pi/2", math.pi / 2.0),
        ("e^2", math.e**2),
        ("2**0.5", math.sqrt(2.0)),
        ("(1+2)*3-4", 5.0),
        ("1.5e-3", 0.0015),
    ],
)
def test_parses_numbers_and_expressions(token: str, value: float) -> None:
    assert parse_number(token) == pytest.approx(value, rel=1e-15)
    assert InputReader(token).number() == pytest.approx(value, rel=1e-15)


@pytest.mark.parametrize(
    "token", ["pi/0", "(-8)^(1/3)", "x", "True", "pi(1)", "2^", "abs(1)", "9^9^9", "1//2"]
)
def test_rejects_invalid_expressions(token: str) -> None:
    with pytest.raises(ValueError, match="expected a number"):
        parse_number(token)


def test_reads_sizes_with_a_minimum() -> None:
    assert InputReader("3").size(3) == 3
    with pytest.raises(ValueError, match="expected a size from 3 to 1000, got '2'"):
        InputReader("2").size(3)


def test_builds_grids_and_counts_steps() -> None:
    assert linspace(0.0, 1.0, 5) == [0.0, 0.25, 0.5, 0.75, 1.0]
    with pytest.raises(ValueError, match="at least two points"):
        linspace(0.0, 1.0, 1)
    assert step_count(1.0, 2.0, 0.1) == 10
    assert step_count(1.0, 0.0, 0.25) == 4
    with pytest.raises(ValueError, match="does not divide"):
        step_count(0.0, 1.0, 0.3)
    with pytest.raises(ValueError, match="must be positive"):
        step_count(0.0, 1.0, 0.0)
    with pytest.raises(ValueError, match="must be positive"):
        step_count(1.0, 1.0, 0.1)


def test_formats_numbers_with_digits_and_tables() -> None:
    assert format_number(1.23456789, 6) == "1.234568"
    assert format_number(-1e-7, 6) == "0.000000"
    assert format_vector([1.0, 2.5], 2) == "(1.00, 2.50)"
    assert format_table(["k", "value"], [["1", "10.5"], ["10", "2"]]) == [
        "   k  value",
        "   1   10.5",
        "  10      2",
    ]


def test_draws_charts() -> None:
    svg = chart(
        "f & g",
        [
            Series("f", [0.0, 1.0, 2.0, 3.0], [0.0, 1.0, math.nan, 9.0]),
            Series("points", [1.0, 2.0], [1.0, 4.0], markers=True),
            Series("more points", [1.0], [1.0], markers=True),
        ],
    )
    assert svg.startswith("<svg ")
    assert svg.endswith("</svg>\n")
    assert "f &amp; g" in svg
    assert svg.count("<polyline") == 2
    assert svg.count("<circle") == 5
    assert svg.count('r="6"') == 3
    assert svg.count('r="4.5"') == 2
    assert chart("flat", [Series("c", [0.0, 1.0], [2.0, 2.0])]).count("<text") > 4


def test_rejects_empty_charts() -> None:
    with pytest.raises(ValueError, match="nothing to plot"):
        chart("empty", [Series("nan", [0.0], [math.nan])])


def plot(reader: InputReader) -> str:
    return f"<svg>{reader.number()}</svg>\n"


def test_run_saves_the_figure_next_to_the_input(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "input.txt"
    path.write_text("2.5\n", encoding="utf-8")
    assert run(double, path, [], plot) == 0
    assert capsys.readouterr().out == "2x = 5.0\ndone\n"
    assert (tmp_path / PLOT_NAME).read_text(encoding="utf-8") == "<svg>2.5</svg>\n"
    assert save_figure(plot, path) == tmp_path / PLOT_NAME


def test_run_reports_figures_it_cannot_write(
    tmp_path: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    path = tmp_path / "input.txt"
    path.write_text("1\n", encoding="utf-8")
    (tmp_path / PLOT_NAME).mkdir()
    assert run(double, path, [], plot) == 1
    assert capsys.readouterr().err.startswith(f"error: cannot write {tmp_path / PLOT_NAME}")
