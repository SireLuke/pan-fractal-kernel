"""Resolution-aware geometric comparisons for lemniscate candidates.

Each run matches one measure at a time; it does not assume unlike curves can
simultaneously match width, lobe area and arc length.
"""
from __future__ import annotations

import math
import numpy as np

from .curves import CurveSamples, curve_metrics, sample_bernoulli, sample_gerono


def _lobe_areas(points: np.ndarray) -> tuple[float, float]:
    radii = np.linalg.norm(points, axis=1)
    crossings = np.flatnonzero(radii <= 1e-10)
    if len(crossings) != 2:
        raise ValueError("curve must have exactly two sampled origin crossings")

    def polygon_area(segment: np.ndarray) -> float:
        x, y = segment[:, 0], segment[:, 1]
        return abs(float(0.5 * np.sum(x[:-1] * y[1:] - x[1:] * y[:-1])))

    first, second = crossings
    lobe_a = polygon_area(points[first:second + 1])
    wrapped = np.concatenate((points[second:], points[:first + 1]), axis=0)
    lobe_b = polygon_area(wrapped)
    return lobe_a, lobe_b


def _metrics(curve: CurveSamples) -> dict[str, float | int | str]:
    result = curve_metrics(curve)
    areas = _lobe_areas(curve.points)
    steps = np.diff(curve.points, axis=0)
    lengths = np.linalg.norm(steps, axis=1)
    norms = np.maximum(lengths, 1e-15)
    unit = steps / norms[:, None]
    turns = np.arccos(np.clip(np.sum(unit[:-1] * unit[1:], axis=1), -1.0, 1.0))
    curvature = turns / np.maximum((lengths[:-1] + lengths[1:]) / 2.0, 1e-15)
    result.update({
        "lobe_area_1": areas[0],
        "lobe_area_2": areas[1],
        "total_lobe_area": sum(areas),
        "lobe_area_asymmetry": abs(areas[0] - areas[1]),
        "max_discrete_curvature_proxy": float(np.max(curvature)),
    })
    return result


def _scaled(curve: CurveSamples, factor: float) -> CurveSamples:
    return CurveSamples(curve.name, curve.parameter.copy(), curve.points * factor)


def _match(curve: CurveSamples, target: float, measure: str) -> CurveSamples:
    current = float(_metrics(curve)[measure])
    if not math.isfinite(current) or current <= 0.0:
        raise ValueError(f"cannot normalize non-positive {measure}")
    factor = math.sqrt(target / current) if measure == "total_lobe_area" else target / current
    return _scaled(curve, factor)


def compare_lemniscates(*, n_samples: int = 801) -> dict:
    """Compare Gerono and Bernoulli candidates under three separate constraints."""
    candidates = {
        "gerono": sample_gerono(a=1.0, b=0.5, n_samples=n_samples),
        "bernoulli": sample_bernoulli(c=1.0, n_samples=n_samples),
    }
    raw = {name: _metrics(curve) for name, curve in candidates.items()}
    modes = {
        "same_bounding_width": "bounding_width",
        "same_total_lobe_area": "total_lobe_area",
        "same_polyline_length": "polyline_length",
    }
    comparisons = {}
    for mode, measure in modes.items():
        target = min(float(raw[name][measure]) for name in candidates)
        normalized = {name: _match(curve, target, measure)
                      for name, curve in candidates.items()}
        comparisons[mode] = {
            "matched_measure": measure,
            "target": target,
            "curves": {name: _metrics(curve) for name, curve in normalized.items()},
        }
    return {
        "experiment": "ABOM-V8-LEMNI-COMPARE-001",
        "resolution": n_samples,
        "raw": raw,
        "comparisons": comparisons,
        "interpretation": (
            "Each mode matches one scalar measure independently. Differences in "
            "the other measures are retained as results, not optimized away."
        ),
    }


def resolution_sweep(resolutions: tuple[int, ...] = (401, 801, 1601)) -> dict:
    """Measure discretization sensitivity at increasing sample resolutions."""
    if len(resolutions) < 2 or any(n < 5 or (n - 1) % 4 for n in resolutions):
        raise ValueError("use at least two valid resolutions with (n-1) divisible by four")
    runs = [compare_lemniscates(n_samples=n) for n in resolutions]
    convergence = {}
    for curve_name in ("gerono", "bernoulli"):
        convergence[curve_name] = {}
        for metric in ("bounding_width", "bounding_height", "polyline_length",
                       "total_lobe_area", "max_discrete_curvature_proxy"):
            convergence[curve_name][metric] = [
                run["raw"][curve_name][metric] for run in runs
            ]
    return {
        "experiment": "ABOM-V8-LEMNI-RESOLUTION-001",
        "resolutions": list(resolutions),
        "runs": runs,
        "convergence_check": convergence,
    }
