"""Golden-ratio scaling helpers with explicit reference units."""
from __future__ import annotations

import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0


def phi_power(exponent: int, *, reference_scale: float = 1.0) -> float:
    """Return reference_scale * phi**exponent for an integer shell index."""
    if isinstance(exponent, bool) or not isinstance(exponent, int):
        raise ValueError("exponent must be an integer")
    reference_scale = float(reference_scale)
    if not math.isfinite(reference_scale) or reference_scale <= 0.0:
        raise ValueError("reference_scale must be finite and positive")
    result = reference_scale * PHI ** exponent
    if not math.isfinite(result) or result <= 0.0:
        raise OverflowError("requested harmonic scale is outside finite positive range")
    return result


def log_phi_ratio(quantity: float, reference_quantity: float) -> float:
    """Return log_phi(quantity/reference_quantity); ratio is dimensionless."""
    quantity = float(quantity)
    reference_quantity = float(reference_quantity)
    if not all(math.isfinite(v) and v > 0.0 for v in (quantity, reference_quantity)):
        raise ValueError("quantity and reference_quantity must be finite and positive")
    return (math.log(quantity) - math.log(reference_quantity)) / math.log(PHI)
