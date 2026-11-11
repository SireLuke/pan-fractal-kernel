"""Hydrogen eigenstates sampled on the 3D view of E8 / 5_21 Euclidean shells.

Scope
-----
Exact, numpy-only reference functions for hydrogen (atomic units, a0 = 1; n <= 3 plus
R_42 for the 12 a0 radial node) and real spherical / solid harmonics for l <= 2, plus
tools that sample them on the projection of an E8 Euclidean shell (``five21_neighborhood``)
through an orthonormal 3-frame (``view_ladder.seeded_3d_rows``).

What is exact here
------------------
The 240 / 2160 / 6720 vectors of shells n = 1, 2, 3 are spherical 7-designs on S^7. For a
3 x 8 frame P with orthonormal rows, a real solid harmonic S_lm(Px) is a *harmonic polynomial*
in x, so for l + l' <= 7 the shell mean of S_lm S_l'm' equals its S^7 average. That average is
diagonal: delta_{ll'} delta_{mm'} E[rho^{2l}] / (4 pi), where rho = |P u| for u uniform on S^7
and E[rho^{2k}] = B(k + 3/2, 5/2) / B(3/2, 5/2). ``solid_harmonic_gram`` and
``expected_solid_gram`` expose this; it holds to machine precision for every frame.

What is NOT claimed
-------------------
Hydrogen wavefunctions are not polynomials in x, so orthogonality of psi_nlm on the projected
cloud is only approximate; ``hydrogen_overlap_matrix`` measures it and callers must compare
against a stated null. A 3D view is a display transform, not a physical identification, and
nothing here maps V8 coordinates, UHFE/UDFE, or Janus Hydra onto hydrogen.
"""
from __future__ import annotations

import math
from typing import Sequence

import numpy as np

try:
    from . import five21_neighborhood as _f21
    from .view_ladder import seeded_3d_rows
except ImportError:
    import five21_neighborhood as _f21
    from view_ladder import seeded_3d_rows

SOLID_L_MAX = 2
_ORDERS = {0: (0,), 1: (-1, 0, 1), 2: (-2, -1, 0, 1, 2)}


# --------------------------------------------------------------------------- hydrogen (a0 = 1)
def hydrogen_radial(n: int, l: int, r) -> np.ndarray:
    """Normalised radial function R_nl(r), atomic units. Supported: n <= 3 all l, and (4, 2)."""
    r = np.asarray(r, dtype=float)
    s3, s6, s30, s5 = math.sqrt(3.0), math.sqrt(6.0), math.sqrt(30.0), math.sqrt(5.0)
    table = {
        (1, 0): lambda x: 2.0 * np.exp(-x),
        (2, 0): lambda x: (1 / math.sqrt(2)) * (1 - x / 2) * np.exp(-x / 2),
        (2, 1): lambda x: (1 / (2 * s6)) * x * np.exp(-x / 2),
        (3, 0): lambda x: (2 / (3 * s3)) * (1 - 2 * x / 3 + 2 * x**2 / 27) * np.exp(-x / 3),
        (3, 1): lambda x: (8 / (27 * s6)) * x * (1 - x / 6) * np.exp(-x / 3),
        (3, 2): lambda x: (4 / (81 * s30)) * x**2 * np.exp(-x / 3),
        (4, 2): lambda x: (1 / (64 * s5)) * x**2 * (1 - x / 12) * np.exp(-x / 4),
    }
    if (n, l) not in table:
        raise ValueError(f"unsupported hydrogen state (n={n}, l={l})")
    return table[(n, l)](r)


def radial_node_count(n: int, l: int) -> int:
    """Number of radial nodes (r > 0) of R_nl: n - l - 1."""
    if not (isinstance(n, int) and isinstance(l, int) and 0 <= l < n):
        raise ValueError("require integers 0 <= l < n")
    return n - l - 1


# --------------------------------------------------------------------------- harmonics (l <= 2)
def _unit_xyz(xyz) -> tuple:
    a = np.asarray(xyz, dtype=float)
    if a.ndim != 2 or a.shape[1] != 3:
        raise ValueError("xyz must have shape (N, 3)")
    return a[:, 0], a[:, 1], a[:, 2]


def solid_harmonic(l: int, m: int, xyz) -> np.ndarray:
    """Real solid harmonic S_lm = r^l Y_lm (Y_lm orthonormal on S^2), l <= 2, m in -l..l."""
    if l not in _ORDERS or m not in _ORDERS[l]:
        raise ValueError(f"unsupported (l={l}, m={m}); l must be 0..{SOLID_L_MAX}")
    x, y, z = _unit_xyz(xyz)
    pi = math.pi
    if l == 0:
        return np.full_like(x, 1.0 / (2.0 * math.sqrt(pi)))
    if l == 1:
        c = math.sqrt(3.0 / (4.0 * pi))
        return c * {-1: y, 0: z, 1: x}[m]
    r2 = x * x + y * y + z * z
    return {
        -2: 0.5 * math.sqrt(15.0 / pi) * x * y,
        -1: 0.5 * math.sqrt(15.0 / pi) * y * z,
        0: 0.25 * math.sqrt(5.0 / pi) * (3.0 * z * z - r2),
        1: 0.5 * math.sqrt(15.0 / pi) * x * z,
        2: 0.25 * math.sqrt(15.0 / pi) * (x * x - y * y),
    }[m]


def real_ylm(l: int, m: int, xyz) -> np.ndarray:
    """Real spherical harmonic Y_lm on directions of xyz (zero vectors give 0 for l >= 1)."""
    x, y, z = _unit_xyz(xyz)
    r = np.sqrt(x * x + y * y + z * z)
    s = solid_harmonic(l, m, xyz)
    if l == 0:
        return s
    with np.errstate(divide="ignore", invalid="ignore"):
        out = np.where(r > 0, s / np.where(r > 0, r, 1.0) ** l, 0.0)
    return out


def hydrogen_psi(n: int, l: int, m: int, xyz, length_scale: float = 1.0) -> np.ndarray:
    """psi_nlm at points; radius in a0 is length_scale * |xyz|. length_scale must be explicit/positive."""
    if not (math.isfinite(length_scale) and length_scale > 0):
        raise ValueError("length_scale must be finite and positive")
    x, y, z = _unit_xyz(xyz)
    r = length_scale * np.sqrt(x * x + y * y + z * z)
    return hydrogen_radial(n, l, r) * real_ylm(l, m, xyz)


def solid_basis_labels() -> tuple:
    return tuple((l, m) for l in range(SOLID_L_MAX + 1) for m in _ORDERS[l])


# --------------------------------------------------------------------------- shell sampling
def shell_unit_points(n: int) -> np.ndarray:
    """Shell n (norm^2 = 2n) as points on the unit sphere S^7 (exact lattice, then scaled)."""
    pts = np.asarray(_f21.shell(n), dtype=float) / 2.0
    return pts / math.sqrt(2.0 * n)


def project_points(points: np.ndarray, frame: np.ndarray) -> np.ndarray:
    frame = np.asarray(frame, dtype=float)
    if frame.shape != (3, points.shape[1]) or not np.allclose(frame @ frame.T, np.eye(3), atol=1e-10):
        raise ValueError("frame must be a 3 x N matrix with orthonormal rows")
    return points @ frame.T


def shell_view(n: int, seed: int = 421) -> np.ndarray:
    """Unit-sphere-normalised shell n viewed through the seeded 3D frame (matches View Ladder)."""
    return project_points(shell_unit_points(n), seeded_3d_rows(seed))


# --------------------------------------------------------------------------- exact moments
def _beta(a: float, b: float) -> float:
    return math.gamma(a) * math.gamma(b) / math.gamma(a + b)


def projected_radius_moment(k: int, ambient: int = 8, view: int = 3) -> float:
    """E[rho^{2k}], rho = |P u|, u uniform on S^{ambient-1}, P an orthonormal view-frame."""
    a, b = view / 2.0, (ambient - view) / 2.0
    return _beta(a + k, b) / _beta(a, b)


def expected_solid_gram() -> np.ndarray:
    """Isotropic expectation of S_lm S_l'm' for the S^7 -> R^3 projection (diagonal)."""
    labels = solid_basis_labels()
    return np.diag([projected_radius_moment(l) / (4.0 * math.pi) for l, _ in labels])


def solid_harmonic_gram(points3: np.ndarray) -> np.ndarray:
    """Mean over points of S_lm S_l'm' for all l, l' <= 2 (9 x 9)."""
    cols = np.stack([solid_harmonic(l, m, points3) for l, m in solid_basis_labels()], axis=1)
    return cols.T @ cols / len(points3)


def solid_gram_error(points3: np.ndarray) -> float:
    """Max-abs deviation of the point-set solid-harmonic Gram from the exact isotropic value."""
    return float(np.max(np.abs(solid_harmonic_gram(points3) - expected_solid_gram())))


def hydrogen_overlap_matrix(points3: np.ndarray, states: Sequence[tuple], length_scale: float = 1.0) -> np.ndarray:
    """Normalised overlaps <psi_a|psi_b> / sqrt(<a|a><b|b>) using equal point weights."""
    cols = np.stack([hydrogen_psi(n, l, m, points3, length_scale) for n, l, m in states], axis=1)
    g = cols.T @ cols
    d = np.sqrt(np.diag(g))
    if not np.all(d > 0):
        raise ValueError("a state vanishes on every sampled point")
    return g / np.outer(d, d)


def max_cross_lm_overlap(points3: np.ndarray, states: Sequence[tuple], length_scale: float = 1.0) -> float:
    """Largest |overlap| between states with DIFFERENT (l, m); angular orthogonality diagnostic."""
    ov = hydrogen_overlap_matrix(points3, states, length_scale)
    worst = 0.0
    for i, (_, li, mi) in enumerate(states):
        for j, (_, lj, mj) in enumerate(states):
            if (li, mi) != (lj, mj):
                worst = max(worst, abs(ov[i, j]))
    return float(worst)


def states_up_to(n_max: int) -> tuple:
    if not (1 <= n_max <= 3):
        raise ValueError("n_max must be 1..3")
    return tuple((n, l, m) for n in range(1, n_max + 1) for l in range(n) for m in _ORDERS[l])
