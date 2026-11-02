from pathlib import Path

import pytest

from lab1.common import (
    InputReader,
    column,
    copy_matrix,
    distance_inf,
    format_complex,
    format_matrix,
    format_number,
    format_scientific,
    format_vector,
    identity,
    is_square,
    is_symmetric,
    matmul,
    matrix_norm_inf,
    matvec,
    norm_inf,
    run,
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
    with pytest.raises(ValueError, match="expected a matrix size"):
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
