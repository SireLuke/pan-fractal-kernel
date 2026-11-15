"""Fermi-occupancy yin-yang (UH/UDFE conjoined) geometry. Stdlib only.

A deterministic *geometric encoding* of one scalar: the Fermi-Dirac occupancy
N = 1 / (exp((E - mu) / T) + 1). It is a display/semantic mapping, not a field
solver and not a physical identity.

Construction (unit disk, area pi):
  delta = 2N - 1 = -tanh((E - mu) / (2T))
  The S-curve boundary is two semicircles on the horizontal diameter with
  diameters d1 = 1 - delta (black head, upper side) and d2 = 1 + delta (white
  head, lower side); d1 + d2 = 2.
  White area = pi/2 - pi*d1^2/8 + pi*d2^2/8 = pi*(1 + delta)/2 = pi*N   (exact)
  Black area = pi*(1 - N). UHFE side (white) = N, UDFE side (black) = 1 - N.
Limits: N -> 1 (E -> -inf) and N -> 0 (E -> +inf) are the two infinities; the
disk is then wholly white or wholly black. Each head carries an "eye" of the
opposite colour (a lemniscate); eyes are excluded from the area statement.
"""
from __future__ import annotations

import math

PHI = (1.0 + math.sqrt(5.0)) / 2.0
GOLDEN_ANGLE_RAD = 2.0 * math.pi / (PHI * PHI)           # 360 / phi^2 degrees
GOLDEN_ANGLE_DEG = 360.0 / (PHI * PHI)                    # 137.50776...
INVERSE_GOLDEN_ANGLE_DEG = 360.0 / PHI                    # 222.49223... = 360 - 360/phi^2


def occupancy(energy: float, mu: float, temperature: float) -> float:
    """Fermi-Dirac occupancy in [0, 1]; temperature 0 gives the step function (1/2 at E = mu)."""
    if temperature < 0 or not all(math.isfinite(v) for v in (energy, mu, temperature)):
        raise ValueError("energy, mu finite and temperature finite and >= 0")
    if temperature == 0:
        return 1.0 if energy < mu else 0.5 if energy == mu else 0.0
    x = (energy - mu) / temperature
    if x > 700:
        return 0.0
    if x < -700:
        return 1.0
    return 1.0 / (math.exp(x) + 1.0)


def delta(n: float) -> float:
    if not 0.0 <= n <= 1.0:
        raise ValueError("N must be in [0, 1]")
    return 2.0 * n - 1.0


def head_diameters(n: float) -> tuple[float, float]:
    """(black head diameter, white head diameter); they sum to 2 (the disk diameter)."""
    d = delta(n)
    return 1.0 - d, 1.0 + d


def lobe_area_fractions(n: float) -> tuple[float, float]:
    """(white/UHFE, black/UDFE) area fractions of the disk, from the closed form."""
    d1, d2 = head_diameters(n)
    white = (math.pi / 2 - math.pi * d1 * d1 / 8 + math.pi * d2 * d2 / 8) / math.pi
    return white, 1.0 - white


def head_centres(n: float) -> tuple[float, float]:
    """x-centres of (black head, white head) circles on the horizontal diameter."""
    d1, d2 = head_diameters(n)
    return -1.0 + d1 / 2.0, -1.0 + d1 + d2 / 2.0


def is_white(x: float, y: float, n: float) -> bool:
    """Point membership in the white lobe (eyes ignored); points outside the disk are not white."""
    if x * x + y * y > 1.0:
        return False
    d1, d2 = head_diameters(n)
    c1, c2 = head_centres(n)
    if y > 0:
        return (x - c1) ** 2 + y * y > (d1 / 2) ** 2
    return (x - c2) ** 2 + y * y <= (d2 / 2) ** 2


def eye_radius_parameter(n: float) -> tuple[float, float]:
    """Lemniscate scale a = d/4 for (black head eye (white ink), white head eye (black ink)); 0 when a head vanishes."""
    d1, d2 = head_diameters(n)
    return d1 / 4.0, d2 / 4.0
