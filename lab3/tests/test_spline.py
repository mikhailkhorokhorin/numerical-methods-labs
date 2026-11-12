import pytest

from lab1.tests.support import assert_expected_output, assert_expected_plot, assert_task_error
from lab3.task2.main import INPUT, figure, task
from lab3.task2.spline import Spline, natural_spline

XS = [0.0, 1.0, 2.0, 3.0, 5.0]
YS = [0.0, 0.45345, 0.52360, 0.0, -2.2672]


def derivatives(spline: Spline, i: int, t: float) -> tuple[float, float, float]:
    value = spline.a[i] + spline.b[i] * t + spline.c[i] * t**2 + spline.d[i] * t**3
    first = spline.b[i] + 2.0 * spline.c[i] * t + 3.0 * spline.d[i] * t**2
    second = 2.0 * spline.c[i] + 6.0 * spline.d[i] * t
    return value, first, second


def test_spline_interpolates_and_is_smooth() -> None:
    spline = natural_spline(XS, YS)
    for x, y in zip(XS, YS, strict=True):
        assert spline(x) == pytest.approx(y, abs=1e-12)
    for i in range(len(XS) - 2):
        left = derivatives(spline, i, XS[i + 1] - XS[i])
        right = derivatives(spline, i + 1, 0.0)
        assert left == pytest.approx(right, abs=1e-12)


def test_spline_has_zero_curvature_at_the_ends() -> None:
    spline = natural_spline(XS, YS)
    assert derivatives(spline, 0, 0.0)[2] == 0.0
    assert derivatives(spline, len(XS) - 2, XS[-1] - XS[-2])[2] == pytest.approx(0.0, abs=1e-12)


def test_variant_value() -> None:
    assert natural_spline(XS, YS)(1.5) == pytest.approx(0.5556, abs=5e-5)


def test_linear_data_gives_a_linear_spline() -> None:
    spline = natural_spline([0.0, 1.0, 3.0, 4.0], [1.0, 3.0, 7.0, 9.0])
    assert spline.c == pytest.approx([0.0, 0.0, 0.0], abs=1e-12)
    assert spline(2.5) == pytest.approx(6.0)


def test_two_nodes_give_a_segment() -> None:
    spline = natural_spline([0.0, 2.0], [1.0, 5.0])
    assert spline(1.0) == pytest.approx(3.0)
    assert spline.d == [0.0]


def test_rejects_invalid_tables_and_points() -> None:
    with pytest.raises(ValueError, match="at least two nodes"):
        natural_spline([0.0], [1.0])
    with pytest.raises(ValueError, match="at least two nodes"):
        natural_spline([0.0, 1.0], [1.0])
    with pytest.raises(ValueError, match="strictly increasing"):
        natural_spline([0.0, 2.0, 1.0], [1.0, 2.0, 3.0])
    with pytest.raises(ValueError, match="outside the spline nodes"):
        natural_spline(XS, YS)(6.0)


def test_task_prints_the_expected_output_and_plot() -> None:
    assert_expected_output(task, INPUT)
    assert_expected_plot(figure, INPUT)


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("1 0 1", "expected a size from 2"),
        ("2 0 1 0 1", "unexpected end of input"),
        ("2 0 1 0 1 2", "outside the spline nodes"),
    ],
)
def test_task_reports_invalid_input(text: str, message: str) -> None:
    assert_task_error(task, text, message)
