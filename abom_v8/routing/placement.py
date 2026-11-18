"""Benchmark results -> capability coordinates (deterministic, evidence-tracked).

The caller supplies the calibration (which benchmark informs which axis and the
score range that maps to 0 and 1).  This module ships no default calibration:
mapping a public benchmark to a capability axis is a measurement claim that has
to be declared, versioned and validated, not assumed.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
import math

from .capability import AXES, CapabilityVector

DEFAULT_CALIBRATION = "uncalibrated-0"


class PlacementError(ValueError):
    """Raised when benchmark evidence does not cover every capability axis."""


@dataclass(frozen=True, slots=True)
class BenchmarkMap:
    """One benchmark's contribution to one axis.

    A score `lo` maps to 0 and `hi` to 1 (linearly, then clipped).  hi < lo
    declares a lower-is-better benchmark.
    """

    benchmark: str
    axis: str
    lo: float
    hi: float
    weight: float = 1.0

    def __post_init__(self) -> None:
        if not self.benchmark.strip():
            raise ValueError("benchmark name must be non-empty")
        if self.axis not in AXES:
            raise ValueError(f"unknown capability axis: {self.axis!r}")
        for name in ("lo", "hi", "weight"):
            if not math.isfinite(float(getattr(self, name))):
                raise ValueError(f"{name} must be finite")
        if self.lo == self.hi:
            raise ValueError("lo and hi must differ")
        if self.weight <= 0.0:
            raise ValueError("weight must be positive")

    def normalise(self, score: float) -> tuple[float, bool]:
        raw = (score - self.lo) / (self.hi - self.lo)
        return min(1.0, max(0.0, raw)), not 0.0 <= raw <= 1.0


@dataclass(frozen=True, slots=True)
class Placement:
    vector: CapabilityVector | None
    missing_axes: tuple[str, ...]
    clipped: tuple[str, ...]
    evidence: Mapping[str, tuple[str, ...]] = field(default_factory=dict)
    calibration_version: str = DEFAULT_CALIBRATION

    def require_vector(self) -> CapabilityVector:
        if self.vector is None:
            raise PlacementError(
                "no benchmark evidence for axes: " + ", ".join(self.missing_axes)
            )
        return self.vector


def place(results: Mapping[str, float], calibration: Sequence[BenchmarkMap], *,
          calibration_version: str = DEFAULT_CALIBRATION) -> Placement:
    """Weighted mean of normalised scores per axis.

    Benchmarks absent from `results` are skipped.  An axis with no evidence is
    reported in `missing_axes` and no vector is produced: a missing axis is never
    filled with a default.
    """
    sums = {axis: 0.0 for axis in AXES}
    weights = {axis: 0.0 for axis in AXES}
    used: dict[str, list[str]] = {axis: [] for axis in AXES}
    clipped: list[str] = []
    for entry in calibration:
        if entry.benchmark not in results:
            continue
        score = results[entry.benchmark]
        if isinstance(score, bool) or not math.isfinite(float(score)):
            raise ValueError(f"score for {entry.benchmark!r} must be a finite number")
        value, was_clipped = entry.normalise(float(score))
        sums[entry.axis] += entry.weight * value
        weights[entry.axis] += entry.weight
        used[entry.axis].append(entry.benchmark)
        if was_clipped and entry.benchmark not in clipped:
            clipped.append(entry.benchmark)
    missing = tuple(axis for axis in AXES if weights[axis] == 0.0)
    vector = None
    if not missing:
        vector = CapabilityVector(tuple(sums[a] / weights[a] for a in AXES))
    return Placement(
        vector=vector,
        missing_axes=missing,
        clipped=tuple(clipped),
        evidence={axis: tuple(names) for axis, names in used.items() if names},
        calibration_version=calibration_version,
    )
