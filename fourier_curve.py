"""Finite Fourier reconstruction for sampled, parameterized closed curves.

Project attribution: Lucas Thouvenell (@SireLuke).

The coefficients describe the supplied parameterization, not only the
geometric locus. Errors reported here are synchronized parametric errors;
they are not Hausdorff distances between unparameterized shapes.
"""
from __future__ import annotations

from dataclasses import dataclass
import cmath
import math
from typing import Iterable, Sequence


@dataclass(frozen=True)
class FourierCurve:
    """Truncated complex Fourier representation of a periodic planar curve."""

    coefficients: tuple[complex, ...]
    minimum_mode: int
    maximum_mode: int
    sample_count: int

    @classmethod
    def fit(
        cls, samples: Iterable[complex | Sequence[float]], harmonics: int
    ) -> "FourierCurve":
        """Fit modes -harmonics..+harmonics to equally spaced periodic samples.

        The samples must cover one period without duplicating the endpoint.
        """
        if isinstance(harmonics, bool) or not isinstance(harmonics, int) or harmonics < 0:
            raise ValueError("harmonics must be a non-negative integer")
        points = tuple(_as_complex(point) for point in samples)
        count = len(points)
        if count < 3:
            raise ValueError("at least three periodic samples are required")
        if 2 * harmonics + 1 > count:
            raise ValueError("sample_count must be at least 2 * harmonics + 1")
        if any(not (math.isfinite(p.real) and math.isfinite(p.imag)) for p in points):
            raise ValueError("all samples must be finite")

        modes = range(-harmonics, harmonics + 1)
        coefficients = tuple(
            sum(
                point * cmath.exp(-2j * math.pi * mode * index / count)
                for index, point in enumerate(points)
            ) / count
            for mode in modes
        )
        return cls(coefficients, -harmonics, harmonics, count)

    @property
    def harmonics(self) -> int:
        return self.maximum_mode

    def evaluate(self, t: float) -> complex:
        """Evaluate the truncated series at normalized periodic parameter t."""
        t = float(t)
        if not math.isfinite(t):
            raise ValueError("t must be finite")
        return sum(
            coefficient * cmath.exp(2j * math.pi * mode * t)
            for mode, coefficient in zip(
                range(self.minimum_mode, self.maximum_mode + 1),
                self.coefficients,
            )
        )

    def reconstruct_samples(self) -> tuple[complex, ...]:
        """Reconstruct at the original uniform sample parameters."""
        return tuple(self.evaluate(index / self.sample_count) for index in range(self.sample_count))

    def error_report(self, samples: Iterable[complex | Sequence[float]]) -> dict[str, float]:
        """Return synchronized pointwise errors and errors normalized by outline height."""
        points = tuple(_as_complex(point) for point in samples)
        if len(points) != self.sample_count:
            raise ValueError("samples length must match the fitted sample_count")
        if any(not (math.isfinite(p.real) and math.isfinite(p.imag)) for p in points):
            raise ValueError("all samples must be finite")
        errors = tuple(abs(self.evaluate(i / self.sample_count) - point)
                       for i, point in enumerate(points))
        height = max(p.imag for p in points) - min(p.imag for p in points)
        if height <= 0.0:
            raise ValueError("outline height must be positive for normalized error")
        maximum = max(errors)
        rms = math.sqrt(sum(error * error for error in errors) / len(errors))
        return {
            "max_error": maximum,
            "rms_error": rms,
            "outline_height": height,
            "max_error_fraction_of_height": maximum / height,
            "rms_error_fraction_of_height": rms / height,
        }


def _as_complex(point: complex | Sequence[float]) -> complex:
    if isinstance(point, complex):
        return point
    if len(point) != 2:
        raise ValueError("each planar sample must contain exactly x and y")
    return complex(float(point[0]), float(point[1]))
