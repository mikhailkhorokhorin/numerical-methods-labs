import math

from lab1.common import PRECISION

PRECISIONS = [10.0**-power for power in range(1, 11)]


def decimals(eps: float) -> int:
    return max(PRECISION, math.ceil(-math.log10(eps) - 1e-9))
