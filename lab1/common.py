import ast
import math
import operator
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass, replace
from html import escape
from pathlib import Path

Vector = list[float]
Matrix = list[list[float]]

PRECISION = 4
ZERO_THRESHOLD = 5e-5
MAX_SIZE = 1000
CONSTANTS = {"pi": math.pi, "e": math.e}
OPERATORS: dict[type[ast.operator], Callable[[float, float], float]] = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.Pow: operator.pow,
}


def zeros(rows: int, cols: int) -> Matrix:
    return [[0.0] * cols for _ in range(rows)]


def identity(size: int) -> Matrix:
    result = zeros(size, size)
    for i in range(size):
        result[i][i] = 1.0
    return result


def copy_matrix(matrix: Matrix) -> Matrix:
    return [row[:] for row in matrix]


def is_square(matrix: Matrix) -> bool:
    return all(len(row) == len(matrix) for row in matrix)


def column(matrix: Matrix, col: int) -> Vector:
    return [row[col] for row in matrix]


def transposed(matrix: Matrix) -> Matrix:
    cols = len(matrix[0]) if matrix else 0
    return [[row[j] for row in matrix] for j in range(cols)]


def matmul(lhs: Matrix, rhs: Matrix) -> Matrix:
    if any(len(row) != len(rhs) for row in lhs):
        raise ValueError("matrix sizes do not match")
    cols = len(rhs[0]) if rhs else 0
    result = zeros(len(lhs), cols)
    for row, out in zip(lhs, result, strict=True):
        for value, other in zip(row, rhs, strict=True):
            for j in range(cols):
                out[j] += value * other[j]
    return result


def matvec(matrix: Matrix, vector: Vector) -> Vector:
    if any(len(row) != len(vector) for row in matrix):
        raise ValueError("matrix and vector sizes do not match")
    result = [0.0] * len(matrix)
    for i, row in enumerate(matrix):
        for value, component in zip(row, vector, strict=True):
            result[i] += value * component
    return result


def norm_inf(vector: Vector) -> float:
    result = 0.0
    for value in vector:
        result = max(result, abs(value))
    return result


def matrix_norm_inf(matrix: Matrix) -> float:
    result = 0.0
    for row in matrix:
        row_sum = 0.0
        for value in row:
            row_sum += abs(value)
        result = max(result, row_sum)
    return result


def distance_inf(lhs: Vector, rhs: Vector) -> float:
    if len(lhs) != len(rhs):
        raise ValueError("vector sizes do not match")
    result = 0.0
    for left, right in zip(lhs, rhs, strict=True):
        result = max(result, abs(left - right))
    return result


def is_symmetric(matrix: Matrix, tolerance: float = 0.0) -> bool:
    if not is_square(matrix):
        return False
    n = len(matrix)
    return all(
        abs(matrix[i][j] - matrix[j][i]) <= tolerance for i in range(n) for j in range(i + 1, n)
    )


def linspace(start: float, stop: float, count: int) -> Vector:
    if count < 2:
        raise ValueError("linspace needs at least two points")
    return [start + (stop - start) * i / (count - 1) for i in range(count)]


def step_count(start: float, stop: float, step: float) -> int:
    length = abs(stop - start)
    if step <= 0.0 or length == 0.0:
        raise ValueError("the step and the segment length must be positive")
    count = round(length / step)
    if count < 1 or abs(count * step - length) > 1e-9 * length:
        raise ValueError(f"the step {step:g} does not divide the segment [{start:g}, {stop:g}]")
    return count


def _evaluate(node: ast.expr) -> float:
    match node:
        case ast.Constant(value=int() | float() as value) if not isinstance(value, bool):
            return float(value)
        case ast.Name(id=name) if name in CONSTANTS:
            return CONSTANTS[name]
        case ast.UnaryOp(op=ast.USub(), operand=operand):
            return -_evaluate(operand)
        case ast.UnaryOp(op=ast.UAdd(), operand=operand):
            return _evaluate(operand)
        case ast.BinOp(left=left, op=op, right=right) if type(op) in OPERATORS:
            value = OPERATORS[type(op)](_evaluate(left), _evaluate(right))
            if isinstance(value, float):
                return value
    raise ValueError("unsupported expression")


def parse_number(token: str) -> float:
    try:
        return float(token)
    except ValueError:
        pass
    try:
        return _evaluate(ast.parse(token.replace("^", "**"), mode="eval").body)
    except (SyntaxError, ValueError, ArithmeticError, RecursionError):
        raise ValueError(f"expected a number, got '{token}'") from None


class InputReader:
    def __init__(self, text: str) -> None:
        self._tokens = text.split()
        self._position = 0

    def _next(self) -> str:
        if self._position == len(self._tokens):
            raise ValueError("unexpected end of input")
        token = self._tokens[self._position]
        self._position += 1
        return token

    def size(self, minimum: int = 1) -> int:
        token = self._next()
        if not token.isdigit() or not minimum <= int(token) <= MAX_SIZE:
            raise ValueError(f"expected a size from {minimum} to {MAX_SIZE}, got '{token}'")
        return int(token)

    def number(self) -> float:
        token = self._next()
        value = parse_number(token)
        if not math.isfinite(value) or abs(value) > 1e100:
            raise ValueError(f"numbers must lie in [-1e100, 1e100], got '{token}'")
        return value

    def precision(self) -> float:
        value = self.number()
        if value <= 0.0:
            raise ValueError("precision must be positive")
        return value

    def vector(self, size: int) -> Vector:
        return [self.number() for _ in range(size)]

    def matrix(self, size: int) -> Matrix:
        return [self.vector(size) for _ in range(size)]

    def finish(self) -> None:
        if self._position < len(self._tokens):
            raise ValueError(f"unexpected trailing input '{self._tokens[self._position]}'")


def format_number(value: float, digits: int = PRECISION) -> str:
    return f"{0.0 if abs(value) < 0.5 * 10.0**-digits else value:.{digits}f}"


def format_scientific(value: float) -> str:
    return f"{value:.{PRECISION}e}"


def format_complex(value: complex) -> str:
    if abs(value.imag) < ZERO_THRESHOLD:
        return format_number(value.real)
    sign = " - " if value.imag < 0.0 else " + "
    return f"{format_number(value.real)}{sign}{format_number(abs(value.imag))}i"


def format_vector(vector: Vector, digits: int = PRECISION) -> str:
    return "(" + ", ".join(format_number(value, digits) for value in vector) + ")"


def format_matrix(matrix: Matrix) -> list[str]:
    cells = [[format_number(value) for value in row] for row in matrix]
    width = max((len(cell) for row in cells for cell in row), default=0)
    return ["".join(f"  {cell:>{width}}" for cell in row) for row in cells]


def format_table(header: list[str], rows: list[list[str]]) -> list[str]:
    table = [header, *rows]
    widths = [max(len(row[i]) for row in table) for i in range(len(header))]
    return [
        "".join(f"  {cell:>{width}}" for cell, width in zip(row, widths, strict=True))
        for row in table
    ]


@dataclass(frozen=True, slots=True)
class Series:
    label: str
    xs: Vector
    ys: Vector
    markers: bool = False
    filled: bool = False
    band: bool = False


CHART_WIDTH = 880
CHART_HEIGHT = 480
LEFT = 70.0
RIGHT = 660.0
TOP = 50.0
BOTTOM = 430.0
MAX_RADIUS = 6.0
MIN_RADIUS = 3.0
LEGEND_CHAR_WIDTH = 7.0
FILL_OPACITY = 0.15
COLORS = ("#2563eb", "#dc2626", "#16a34a", "#9333ea", "#ea580c", "#0891b2")


def _ticks(low: float, high: float) -> Vector:
    if high - low <= 1e-12 * max(1.0, abs(low), abs(high)):
        low, high = low - 1.0, high + 1.0
    raw = (high - low) / 8.0
    magnitude = 10.0 ** math.floor(math.log10(raw))
    step = next(m * magnitude for m in (1.0, 2.0, 5.0, 10.0) if m * magnitude >= raw * (1 - 1e-9))
    first = math.floor(low / step + 1e-9)
    last = math.ceil(high / step - 1e-9)
    return [k * step for k in range(first, last + 1)]


def _tick_label(value: float, ticks: Vector) -> str:
    step = ticks[1] - ticks[0]
    decimals = max(0, -math.floor(math.log10(step) + 1e-9))
    return f"{0.0 if abs(value) < step / 2.0 else value:.{decimals}f}"


def _segments(series: Series) -> list[list[tuple[float, float]]]:
    segments: list[list[tuple[float, float]]] = [[]]
    for x, y in zip(series.xs, series.ys, strict=True):
        if math.isfinite(x) and math.isfinite(y):
            segments[-1].append((x, y))
        elif segments[-1]:
            segments.append([])
    return [segment for segment in segments if segment]


@dataclass(frozen=True, slots=True)
class _Frame:
    x_ticks: Vector
    y_ticks: Vector
    log_y: bool = False

    def x(self, value: float) -> float:
        low, high = self.x_ticks[0], self.x_ticks[-1]
        return LEFT + (value - low) / (high - low) * (RIGHT - LEFT)

    def y(self, value: float) -> float:
        low, high = self.y_ticks[0], self.y_ticks[-1]
        return BOTTOM - (value - low) / (high - low) * (BOTTOM - TOP)


def _line(x1: float, y1: float, x2: float, y2: float, color: str, width: int = 1) -> str:
    return (
        f'<line x1="{x1:.2f}" y1="{y1:.2f}" x2="{x2:.2f}" y2="{y2:.2f}" '
        f'stroke="{color}" stroke-width="{width}"/>'
    )


def _text(x: float, y: float, content: str, anchor: str = "start", size: int = 13) -> str:
    return (
        f'<text x="{x:.2f}" y="{y:.2f}" text-anchor="{anchor}" font-size="{size}">'
        f"{escape(content)}</text>"
    )


def _circle(x: float, y: float, color: str, radius: float) -> str:
    return f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{radius:g}" fill="{color}" stroke="#ffffff"/>'


def _grid_color(tick: float) -> str:
    return "#9ca3af" if abs(tick) < 1e-12 else "#e5e7eb"


def _axes(frame: _Frame) -> list[str]:
    parts: list[str] = []
    for tick in frame.x_ticks:
        x = frame.x(tick)
        parts.append(_line(x, TOP, x, BOTTOM, _grid_color(tick)))
        parts.append(_text(x, BOTTOM + 20, _tick_label(tick, frame.x_ticks), "middle"))
    for tick in frame.y_ticks:
        y = frame.y(tick)
        color = "#e5e7eb" if frame.log_y else _grid_color(tick)
        label = f"1e{tick:+03.0f}" if frame.log_y else _tick_label(tick, frame.y_ticks)
        parts.append(_line(LEFT, y, RIGHT, y, color))
        parts.append(_text(LEFT - 8, y + 4, label, "end"))
    return parts


def _log_ticks(low: float, high: float) -> Vector:
    step = max(1, math.ceil((high - low) / 8))
    first = math.floor(low / step)
    last = math.ceil(high / step)
    if first == last:
        first, last = first - 1, last + 1
    return [float(k * step) for k in range(first, last + 1)]


def _log10(value: float) -> float:
    return math.log10(value) if value > 0.0 else math.nan


def _axis_labels(x_label: str, y_label: str) -> list[str]:
    parts = []
    if x_label:
        parts.append(_text((LEFT + RIGHT) / 2, BOTTOM + 42, x_label, "middle"))
    if y_label:
        parts.append(
            f'<text x="18" y="{(TOP + BOTTOM) / 2:.2f}" text-anchor="middle" font-size="13" '
            f'transform="rotate(-90 18 {(TOP + BOTTOM) / 2:.2f})">{escape(y_label)}</text>'
        )
    return parts


def _series(index: int, series: Series, frame: _Frame, radius: float) -> list[str]:
    color = COLORS[index % len(COLORS)]
    parts: list[str] = []
    if series.band:
        left, right = frame.x(min(series.xs)), frame.x(max(series.xs))
        parts.append(
            f'<rect x="{left:.2f}" y="{TOP:.2f}" width="{right - left:.2f}" '
            f'height="{BOTTOM - TOP:.2f}" fill="{color}" fill-opacity="{FILL_OPACITY:g}"/>'
        )
        parts.extend(_line(x, TOP, x, BOTTOM, color, 2) for x in (left, right))
    for segment in [] if series.band else _segments(series):
        points = [(frame.x(x), frame.y(y)) for x, y in segment]
        path = " ".join(f"{x:.2f},{y:.2f}" for x, y in points)
        if series.markers:
            parts.extend(_circle(x, y, color, radius) for x, y in points)
        elif series.filled:
            parts.append(
                f'<polygon points="{path}" fill="{color}" fill-opacity="{FILL_OPACITY:g}" '
                f'stroke="{color}" stroke-width="1.5"/>'
            )
        else:
            parts.append(
                f'<polyline points="{path}" fill="none" stroke="{color}" stroke-width="2" '
                'stroke-linejoin="round"/>'
            )
    legend = TOP + 12 + 24 * index
    if series.markers:
        parts.append(_circle(RIGHT + 34, legend, color, radius))
    elif series.filled or series.band:
        parts.append(
            f'<rect x="{RIGHT + 22:.2f}" y="{legend - 6:.2f}" width="24" height="12" '
            f'fill="{color}" fill-opacity="{FILL_OPACITY:g}" stroke="{color}"/>'
        )
    else:
        parts.append(_line(RIGHT + 22, legend, RIGHT + 46, legend, color, 2))
    parts.append(_text(RIGHT + 54, legend + 4, series.label))
    return parts


def chart(
    title: str, series: list[Series], x_label: str = "", y_label: str = "", log_y: bool = False
) -> str:
    if log_y:
        series = [replace(item, ys=[_log10(y) for y in item.ys]) for item in series]
    points = [
        point
        for item in series
        if not item.band
        for segment in _segments(item)
        for point in segment
    ]
    if not points:
        raise ValueError("nothing to plot")
    xs = [x for x, _ in points] + [x for item in series if item.band for x in item.xs]
    ys = [y for _, y in points]
    margin = 0.05 * (max(ys) - min(ys))
    y_ticks = _log_ticks(min(ys), max(ys)) if log_y else _ticks(min(ys) - margin, max(ys) + margin)
    frame = _Frame(_ticks(min(xs), max(xs)), y_ticks, log_y)
    label = max(len(item.label) for item in series)
    width = max(CHART_WIDTH, math.ceil(RIGHT + 70 + LEGEND_CHAR_WIDTH * label))
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{CHART_HEIGHT}" '
        f'viewBox="0 0 {width} {CHART_HEIGHT}" font-family="Helvetica, Arial, sans-serif" '
        'fill="#1f2937">',
        f'<rect width="{width}" height="{CHART_HEIGHT}" fill="#ffffff"/>',
        _text((LEFT + RIGHT) / 2, 30, title, "middle", 16),
        *_axes(frame),
        *_axis_labels(x_label, y_label),
        f'<rect x="{LEFT:.2f}" y="{TOP:.2f}" width="{RIGHT - LEFT:.2f}" '
        f'height="{BOTTOM - TOP:.2f}" fill="none" stroke="#6b7280"/>',
    ]
    markers = 0
    layers: tuple[list[str], list[str]] = ([], [])
    for index, item in enumerate(series):
        drawn = _series(index, item, frame, max(MIN_RADIUS, MAX_RADIUS - 1.5 * markers))
        layers[0 if item.band else 1].extend(drawn)
        if item.markers:
            markers += 1
    parts.extend([*layers[0], *layers[1], "</svg>"])
    return "\n".join(parts) + "\n"


Task = Callable[[InputReader], list[str]]
Figure = Callable[[InputReader], str]
PLOT_NAME = "plot.svg"


def iterations_text(count: int) -> str:
    return f"{count} iteration" if count == 1 else f"{count} iterations"


def solve_file(task: Task, path: Path) -> list[str]:
    return task(InputReader(path.read_text(encoding="utf-8")))


def save_figure(figure: Figure, path: Path, name: str = PLOT_NAME) -> Path:
    target = path.with_name(name)
    svg = figure(InputReader(path.read_text(encoding="utf-8")))
    try:
        target.write_text(svg, encoding="utf-8", newline="\n")
    except OSError as error:
        raise RuntimeError(f"cannot write {target}: {error.strerror}") from None
    return target


def run(
    task: Task, default_input: Path, args: list[str], figures: Mapping[str, Figure] | None = None
) -> int:
    path = Path(args[0]) if args else default_input
    try:
        lines = solve_file(task, path)
        for name, figure in (figures or {}).items():
            save_figure(figure, path, name)
    except FileNotFoundError:
        message = f"file not found: {path}"
    except OSError as error:
        message = f"cannot read {path}: {error.strerror}"
    except ArithmeticError:
        message = "arithmetic error (division by zero or overflow)"
    except (ValueError, RuntimeError) as error:
        message = str(error)
    else:
        print("\n".join(lines))
        return 0
    print(f"error: {message}", file=sys.stderr)
    return 1
