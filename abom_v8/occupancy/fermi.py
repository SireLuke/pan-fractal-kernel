"""Fermi-Dirac occupancy helpers and explicitly configurable visual measures.

The occupancy and yin-yang area construction reuse the kernel's existing
fermi_yinyang implementation rather than duplicating its boundary geometry.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

from fermi_yinyang import occupancy as fermi_dirac_occupancy
from fermi_yinyang import lobe_area_fractions


@dataclass(frozen=True, slots=True)
class OccupancyProfile:
    energy: float
    chemical_potential: float
    temperature: float
    occupied: float
    unoccupied: float
    asymmetry: float
    entropy_bits: float


def binary_entropy_bits(n: float) -> float:
    """Binary Shannon entropy H2(n), with exact zero limits at n=0 and n=1."""
    n = float(n)
    if not math.isfinite(n) or not 0.0 <= n <= 1.0:
        raise ValueError("occupancy must be finite and in [0, 1]")
    if n in (0.0, 1.0):
        return 0.0
    return -(n * math.log2(n) + (1.0 - n) * math.log2(1.0 - n))


def occupancy_profile(energy: float, chemical_potential: float,
                      temperature: float) -> OccupancyProfile:
    """Evaluate Fermi occupancy, complement, asymmetry and binary entropy."""
    n = fermi_dirac_occupancy(energy, chemical_potential, temperature)
    return OccupancyProfile(
        energy=float(energy),
        chemical_potential=float(chemical_potential),
        temperature=float(temperature),
        occupied=n,
        unoccupied=1.0 - n,
        asymmetry=2.0 * n - 1.0,
        entropy_bits=binary_entropy_bits(n),
    )


def focal_radii(n: float, *, disk_radius: float = 1.0) -> tuple[float, float]:
    """Return (UHFE, UDFE) focal-radius candidates from the supplied plot.

    The plot's candidate law is c+ = N R/sqrt(2), c- = (1-N) R/sqrt(2).
    This is a visualization parameterization, not a general theorem about
    Fermi-Dirac systems or all lemniscates.
    """
    n = float(n)
    disk_radius = float(disk_radius)
    if not math.isfinite(n) or not 0.0 <= n <= 1.0:
        raise ValueError("occupancy must be finite and in [0, 1]")
    if not math.isfinite(disk_radius) or disk_radius <= 0.0:
        raise ValueError("disk_radius must be finite and positive")
    factor = disk_radius / math.sqrt(2.0)
    return factor * n, factor * (1.0 - n)


def lemniscate_area_values(n: float) -> tuple[float, float]:
    """Return plotted eye-area candidates (N^2, (1-N)^2), eyes excluded elsewhere."""
    n = float(n)
    if not math.isfinite(n) or not 0.0 <= n <= 1.0:
        raise ValueError("occupancy must be finite and in [0, 1]")
    return n * n, (1.0 - n) ** 2


def yin_yang_area_fractions(n: float) -> tuple[float, float]:
    """Return exact (UHFE white, UDFE black) unit-disk lobe area fractions."""
    white, black = lobe_area_fractions(n)
    return float(white), float(black)
