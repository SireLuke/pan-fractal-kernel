"""Experimental PAN V8 dynamic phase-locking primitives.

This module is a numerical scaffold, not a physical law or a general-relativistic
Cauchy-problem solver. Timestamps are supplied by the caller (e.g. an atomic-clock
adapter); this code does not read hardware clocks.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import cos, exp, isfinite, pi, sin, sqrt
from typing import Sequence

V8_NAMES = ("h", "R", "u", "d", "tau", "chi", "s", "f")
PHI = (1.0 + sqrt(5.0)) / 2.0


def wrap_phase(angle: float) -> float:
    """Wrap an angle to (-pi, pi], with finite input required."""
    if not isfinite(angle):
        raise ValueError("angle must be finite")
    wrapped = (angle + pi) % (2.0 * pi) - pi
    return pi if wrapped == -pi else wrapped


@dataclass(frozen=True)
class V8State:
    """One eight-coordinate PAN state in canonical order."""
    h: float
    R: float
    u: float
    d: float
    tau: float
    chi: float
    s: float
    f: float

    def as_tuple(self) -> tuple[float, ...]:
        values = (self.h, self.R, self.u, self.d, self.tau, self.chi, self.s, self.f)
        if not all(isfinite(x) for x in values):
            raise ValueError("all V8 coordinates must be finite")
        return values


@dataclass(frozen=True)
class PhaseLockState:
    """Eight phase channels evaluated against one geometric reference phase."""
    timestamp: float
    phases: tuple[float, ...]
    angular_frequencies: tuple[float, ...]
    offsets: tuple[float, ...]

    def __post_init__(self) -> None:
        if not isfinite(self.timestamp):
            raise ValueError("timestamp must be finite")
        if not (len(self.phases) == len(self.angular_frequencies) == len(self.offsets) == 8):
            raise ValueError("phases, angular_frequencies and offsets must each have 8 values")
        if not all(isfinite(x) for x in self.phases + self.angular_frequencies + self.offsets):
            raise ValueError("phase parameters must be finite")

    def advance(self, timestamp: float) -> "PhaseLockState":
        """Advance phases using elapsed externally supplied time."""
        if not isfinite(timestamp) or timestamp < self.timestamp:
            raise ValueError("timestamp must be finite and monotonic")
        dt = timestamp - self.timestamp
        next_phases = tuple(
            wrap_phase(phase + omega * dt)
            for phase, omega in zip(self.phases, self.angular_frequencies)
        )
        return PhaseLockState(timestamp, next_phases, self.angular_frequencies, self.offsets)

    def phase_errors(self, geometric_reference_phase: float) -> tuple[float, ...]:
        """Return eight wrapped errors relative to geometry phase plus each offset."""
        if not isfinite(geometric_reference_phase):
            raise ValueError("geometric reference phase must be finite")
        return tuple(
            wrap_phase(phase - geometric_reference_phase - offset)
            for phase, offset in zip(self.phases, self.offsets)
        )


def rotate_8d_plane(
    vector: Sequence[float], i: int, j: int, angle: float
) -> tuple[float, ...]:
    """Rotate an 8D vector in the selected coordinate plane (i,j)."""
    if len(vector) != 8:
        raise ValueError("vector must contain exactly 8 coordinates")
    if i == j or not (0 <= i < 8 and 0 <= j < 8):
        raise ValueError("i and j must be distinct indices in [0, 7]")
    if not isfinite(angle) or not all(isfinite(x) for x in vector):
        raise ValueError("vector and angle must be finite")
    result = list(vector)
    c, s = cos(angle), sin(angle)
    x, y = result[i], result[j]
    result[i] = c * x - s * y
    result[j] = s * x + c * y
    return tuple(result)


def hyperoctahedron_vertices() -> tuple[tuple[float, ...], ...]:
    """Return the 16 unit vertices ±e_i of the 8D cross-polytope."""
    vertices = []
    for i in range(8):
        for sign in (-1.0, 1.0):
            vertex = [0.0] * 8
            vertex[i] = sign
            vertices.append(tuple(vertex))
    return tuple(vertices)


def golden_hallways(value: float) -> tuple[float, float]:
    """Return the proposed +phi and -1/phi scalar branches."""
    if not isfinite(value):
        raise ValueError("value must be finite")
    return PHI * value, -(value / PHI)


def fermi_occupancy(
    energy: float, chemical_potential: float, temperature: float
) -> float:
    """Fermi-Dirac occupation with k_B=1; temperature is in energy units."""
    if not all(isfinite(x) for x in (energy, chemical_potential, temperature)):
        raise ValueError("energy, chemical potential and temperature must be finite")
    if temperature < 0:
        raise ValueError("temperature must be non-negative")
    delta = energy - chemical_potential
    if temperature == 0:
        return 1.0 if delta < 0 else (0.5 if delta == 0 else 0.0)
    z = delta / temperature
    # Stable logistic evaluation avoids overflow for large |z|.
    if z >= 0:
        e = exp(-z)
        return e / (1.0 + e)
    e = exp(z)
    return 1.0 / (1.0 + e)


def fermi_hole_occupancy(
    energy: float, chemical_potential: float, temperature: float
) -> float:
    """Complementary vacancy probability 1 - Fermi occupation."""
    return 1.0 - fermi_occupancy(energy, chemical_potential, temperature)


@dataclass(frozen=True)
class AcousticFeatures:
    """Optional measured features from a recorded glyph pronunciation."""
    fundamental_hz: float | None = None
    duration_seconds: float | None = None
    rms_amplitude: float | None = None

    def __post_init__(self) -> None:
        for name, value in (
            ("fundamental_hz", self.fundamental_hz),
            ("duration_seconds", self.duration_seconds),
            ("rms_amplitude", self.rms_amplitude),
        ):
            if value is not None and (not isfinite(value) or value < 0):
                raise ValueError(f"{name} must be finite and non-negative")


@dataclass(frozen=True)
class AbazithGlyph:
    """Metadata interface; it does not assume glyphs have inherent frequencies."""
    element_id: str
    register: int
    glyph_id: str
    pronunciation: str | None = None
    documented_meaning: str | None = None
    acoustic_features: AcousticFeatures | None = None

    def __post_init__(self) -> None:
        if not self.element_id.strip() or not self.glyph_id.strip():
            raise ValueError("element_id and glyph_id must be non-empty")
        if not 1 <= self.register <= 5:
            raise ValueError("register must be an integer from 1 to 5")
