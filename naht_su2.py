"""SU(2) path transport represented by unit quaternions.

A unit quaternion is an element of SU(2) in its fundamental doublet
representation. Quaternion multiplication composes ordered path segments.
This is an optional two-state transport primitive, not a replacement for
the three-channel NAHT state or the SU(3) adapter.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import acos, cos, isfinite, sin, sqrt
from typing import Iterable


@dataclass(frozen=True)
class SU2:
    """Unit quaternion (w, x, y, z) with a fixed SU(2) matrix convention."""
    w: float
    x: float
    y: float
    z: float

    def __post_init__(self) -> None:
        values = tuple(float(v) for v in (self.w, self.x, self.y, self.z))
        if not all(isfinite(v) for v in values):
            raise ValueError("SU(2) components must be finite")
        norm = sqrt(sum(v*v for v in values))
        if abs(norm - 1.0) > 1e-10:
            raise ValueError("SU(2) quaternion must have unit norm")
        for name, value in zip(("w", "x", "y", "z"), values):
            object.__setattr__(self, name, value)

    @classmethod
    def identity(cls) -> "SU2":
        return cls(1.0, 0.0, 0.0, 0.0)

    @classmethod
    def from_axis_angle(cls, axis: Iterable[float], angle: float) -> "SU2":
        """Build exp(-i angle n.sigma/2) using the matrix convention below."""
        vector = tuple(float(v) for v in axis)
        if len(vector) != 3 or not all(isfinite(v) for v in vector):
            raise ValueError("axis must contain three finite values")
        norm = sqrt(sum(v*v for v in vector))
        if norm == 0.0 or not isfinite(angle):
            raise ValueError("axis must be nonzero and angle finite")
        half = 0.5 * float(angle)
        scale = sin(half) / norm
        return cls(cos(half), vector[0]*scale,
                   vector[1]*scale, vector[2]*scale)

    def __matmul__(self, other: "SU2") -> "SU2":
        """Ordered composition: self @ other is quaternion product self*other."""
        if not isinstance(other, SU2):
            return NotImplemented
        a, b, c, d = self.w, self.x, self.y, self.z
        e, f, g, h = other.w, other.x, other.y, other.z
        return SU2(
            a*e - b*f - c*g - d*h,
            a*f + b*e + c*h - d*g,
            a*g - b*h + c*e + d*f,
            a*h + b*g - c*f + d*e,
        )

    def inverse(self) -> "SU2":
        return SU2(self.w, -self.x, -self.y, -self.z)

    def trace(self) -> float:
        """Trace in the 2x2 fundamental representation."""
        return 2.0 * self.w

    def rotation_angle(self) -> float:
        """Return associated SO(3) rotation angle in [0, pi]."""
        return 2.0 * acos(max(-1.0, min(1.0, abs(self.w))))

    def to_matrix(self) -> tuple[tuple[complex, complex],
                                 tuple[complex, complex]]:
        """Return the equivalent 2x2 special-unitary matrix."""
        return (
            (complex(self.w, self.z), complex(self.y, self.x)),
            (complex(-self.y, self.x), complex(self.w, -self.z)),
        )
