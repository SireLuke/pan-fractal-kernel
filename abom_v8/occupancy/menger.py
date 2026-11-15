"""Menger mu-cube volume and flux helpers (exact identities, no physical claim).

Everything here is arithmetic on the finite Menger construction already owned
by ``menger_sponge`` plus the Fermi occupancy ``N``:

* ``menger_volume_fraction(level, d)``  = (cells_per_level(d) / 3**d) ** level
  (20/27 per level for d = 3, 8/9 for the d = 2 Sierpinski carpet).
* ``menger_hausdorff_dimension(d)``  = ln(cells_per_level(d)) / ln(3)
  (ln 20 / ln 3 ~ 2.7268 for d = 3; the *similarity* dimension of the
  self-similar limit, which equals its Hausdorff dimension for this
  construction).
* ``mu_cube_volume(n, level, d)``  = n * menger_volume_fraction(level, d):
  an occupancy-weighted volume *definition* used for visualization.
* ``lemniscate_flux(n)``  = n (1 - n) = (1 - delta**2) / 4 with
  delta = 2 n - 1; it peaks at 1/4 when n = 1/2.

The flux is the Bernoulli variance of a two-state occupancy. It is a
bookkeeping quantity, not a measured flow and not a gravitational
self-energy.
"""
from __future__ import annotations

import math

FLUX_MAXIMUM = 0.25


def _check_occupancy(n: float) -> float:
    n = float(n)
    if not math.isfinite(n) or not 0.0 <= n <= 1.0:
        raise ValueError("occupancy must be finite and in [0, 1]")
    return n


def _check_level(level: int) -> int:
    if isinstance(level, bool) or not isinstance(level, int) or level < 0:
        raise ValueError("level must be a non-negative integer")
    return level


def menger_cells_per_level(d: int = 3) -> int:
    """Kept sub-cells per subdivision step: 2**d + d * 2**(d-1)."""
    # Lazy import keeps this module optional for consumers without numpy/scipy.
    from menger_sponge import cells_per_level

    return cells_per_level(d)


def menger_volume_fraction(level: int, d: int = 3) -> float:
    """Volume fraction kept by a level-``level`` d-dimensional Menger sponge."""
    level = _check_level(level)
    return (menger_cells_per_level(d) / 3.0**d) ** level


def menger_hausdorff_dimension(d: int = 3) -> float:
    """Similarity (= Hausdorff) dimension ln(N_d) / ln(3); ~2.7268 for d = 3."""
    from menger_sponge import similarity_dimension

    return similarity_dimension(d)


def mu_cube_volume(n: float, level: int = 2, d: int = 3) -> float:
    """Occupancy-weighted level-``level`` Menger volume, n * (N_d / 3**d)**level."""
    return _check_occupancy(n) * menger_volume_fraction(level, d)


def lemniscate_flux(n: float) -> float:
    """Two-state flux n (1 - n); equals (1 - delta**2) / 4 with delta = 2n - 1."""
    n = _check_occupancy(n)
    return n * (1.0 - n)


def flux_from_asymmetry(delta: float) -> float:
    """Flux (1 - delta**2) / 4 from the boundary asymmetry delta in [-1, 1]."""
    delta = float(delta)
    if not math.isfinite(delta) or not -1.0 <= delta <= 1.0:
        raise ValueError("delta must be finite and in [-1, 1]")
    return (1.0 - delta * delta) / 4.0
