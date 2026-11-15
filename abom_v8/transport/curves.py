"""Parameterized lemniscate candidates for geometric transport experiments.

These functions construct curves only. A transport law, direction, speed and
occupancy update must be supplied independently.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


@dataclass(frozen=True, slots=True)
class CurveSamples:
    name: str
    parameter: FloatArray
    points: FloatArray

    def __post_init__(self) -> None:
        if self.points.ndim != 2 or self.points.shape[1] != 2:
            raise ValueError("curve points must have shape (n, 2)")
        if self.parameter.ndim != 1 or len(self.parameter) != len(self.points):
            raise ValueError("parameter and point sample counts must match")
        if len(self.parameter) < 3 or not np.all(np.isfinite(self.points)):
            raise ValueError("curve samples must be finite and contain at least three points")


def _validate_scale(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _parameter_grid(n_samples: int) -> FloatArray:
    if isinstance(n_samples, bool) or not isinstance(n_samples, int) or n_samples < 5:
        raise ValueError("n_samples must be an integer >= 5")
    # Four equal subintervals per half-turn ensure both origin crossings are sampled.
    intervals = n_samples - 1
    if intervals % 4:
        raise ValueError("n_samples - 1 must be divisible by 4 to sample origin crossings exactly")
    return np.linspace(0.0, 2.0 * math.pi, n_samples, endpoint=True, dtype=float)


def sample_gerono(*, a: float = 1.0, b: float = 0.5,
                   n_samples: int = 401) -> CurveSamples:
    """Sample x=a cos(t), y=b sin(2t); a and b independently set lobe width/height."""
    a = _validate_scale(a, "a")
    b = _validate_scale(b, "b")
    t = _parameter_grid(n_samples)
    points = np.column_stack((a * np.cos(t), b * np.sin(2.0 * t)))
    # Remove floating-point residue at the exact mathematical crossings.
    points[np.isclose(points, 0.0, atol=1e-14)] = 0.0
    return CurveSamples("gerono", t, points)


def sample_bernoulli(*, c: float = 1.0,
                      n_samples: int = 401) -> CurveSamples:
    """Sample the Bernoulli lemniscate r^2 = c^2 cos(2 theta).

    The parameterization is x=c cos(t)/(1+sin(t)^2),
    y=c cos(t) sin(t)/(1+sin(t)^2).
    """
    c = _validate_scale(c, "c")
    t = _parameter_grid(n_samples)
    denominator = 1.0 + np.sin(t) ** 2
    x = c * np.cos(t) / denominator
    y = c * np.cos(t) * np.sin(t) / denominator
    points = np.column_stack((x, y))
    points[np.isclose(points, 0.0, atol=1e-14)] = 0.0
    return CurveSamples("bernoulli", t, points)


def curve_metrics(curve: CurveSamples, *, origin_tolerance: float = 1e-9) -> dict[str, float | int | str]:
    """Return resolution-dependent polyline diagnostics for a sampled closed curve."""
    if not math.isfinite(origin_tolerance) or origin_tolerance < 0.0:
        raise ValueError("origin_tolerance must be finite and non-negative")
    steps = np.diff(curve.points, axis=0)
    arc_length = float(np.linalg.norm(steps, axis=1).sum())
    widths = np.ptp(curve.points, axis=0)
    crossings = np.linalg.norm(curve.points, axis=1) <= origin_tolerance
    return {
        "name": curve.name,
        "bounding_width": float(widths[0]),
        "bounding_height": float(widths[1]),
        "polyline_length": arc_length,
        "sampled_origin_crossings": int(crossings.sum()),
    }


def rescale_to_bounding_width(curve: CurveSamples, target_width: float) -> CurveSamples:
    """Uniformly rescale a sample set to a requested horizontal bounding-box width."""
    target_width = _validate_scale(target_width, "target_width")
    current_width = float(np.ptp(curve.points[:, 0]))
    if current_width <= 0.0:
        raise ValueError("curve has zero bounding width")
    points = curve.points * (target_width / current_width)
    return CurveSamples(curve.name, curve.parameter.copy(), points)
