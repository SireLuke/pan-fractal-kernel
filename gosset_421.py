"""Canonical Gosset 4_21 / E8 root-polytope geometry.

Coordinates use the standard E8 root normalization ||alpha||^2 = 2:
  (±1, ±1, 0^6), all coordinate placements/signs (112 roots), and
  (±1/2)^8 with an even number of minus signs (128 roots).

The 240 roots are the vertices of the Gosset 4_21 polytope. This module
keeps that geometry distinct from the 16-vertex 8D cross-polytope.

The exact combinatorial routines use only the Python standard library.
The radial-boundary LP is optional and requires scipy.
"""
from __future__ import annotations

from itertools import combinations, product
from math import isfinite, sqrt
from typing import Iterable, Sequence

DIMENSION = 8
ROOT_COUNT = 240
ROOT_NORM_SQUARED = 2.0
NEAREST_NEIGHBORS = 56
EDGE_COUNT = 6720
TOLERANCE = 1e-10


def _build_roots() -> tuple[tuple[float, ...], ...]:
    roots: set[tuple[float, ...]] = set()

    # 112 roots: choose two nonzero coordinate positions and their signs.
    for i, j in combinations(range(DIMENSION), 2):
        for si, sj in product((-1.0, 1.0), repeat=2):
            v = [0.0] * DIMENSION
            v[i], v[j] = si, sj
            roots.add(tuple(v))

    # 128 roots: half-integral coordinates with even minus-sign parity.
    for signs in product((-1.0, 1.0), repeat=DIMENSION):
        minus_count = sum(sign < 0 for sign in signs)
        if minus_count % 2 == 0:
            roots.add(tuple(sign / 2.0 for sign in signs))

    result = tuple(sorted(roots))
    if len(result) != ROOT_COUNT:
        raise RuntimeError(f"E8 construction produced {len(result)} roots, expected 240")
    return result


E8_ROOTS = _build_roots()
_ROOT_SET = frozenset(E8_ROOTS)


def _vector(values: Sequence[float], *, name: str = "vector") -> tuple[float, ...]:
    if len(values) != DIMENSION:
        raise ValueError(f"{name} must contain exactly 8 coordinates")
    result = tuple(float(x) for x in values)
    if not all(isfinite(x) for x in result):
        raise ValueError(f"{name} coordinates must be finite")
    return result


def dot(a: Sequence[float], b: Sequence[float]) -> float:
    """Euclidean inner product for two 8-vectors."""
    x, y = _vector(a, name="a"), _vector(b, name="b")
    return sum(u * v for u, v in zip(x, y))


def squared_norm(v: Sequence[float]) -> float:
    x = _vector(v)
    return sum(value * value for value in x)


def is_e8_root(v: Sequence[float], *, atol: float = TOLERANCE) -> bool:
    """Return whether v matches one of the 240 roots within tolerance."""
    try:
        x = _vector(v)
    except (TypeError, ValueError):
        return False
    return any(max(abs(a - b) for a, b in zip(x, root)) <= atol for root in E8_ROOTS)


def antipode(root: Sequence[float]) -> tuple[float, ...]:
    """Return -root; input must be one of the canonical E8 roots."""
    x = _vector(root, name="root")
    if not is_e8_root(x):
        raise ValueError("root must be one of the canonical E8 roots")
    return tuple(-value for value in x)


def inner_product_distribution() -> dict[float, int]:
    """Count inner products with a fixed root against all 240 roots."""
    reference = E8_ROOTS[0]
    counts: dict[float, int] = {}
    for root in E8_ROOTS:
        value = round(dot(reference, root), 10)
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def neighbors(root: Sequence[float]) -> tuple[tuple[float, ...], ...]:
    """Return the 56 adjacent Gosset vertices; adjacency is alpha·beta = 1."""
    x = _vector(root, name="root")
    if not is_e8_root(x):
        raise ValueError("root must be one of the canonical E8 roots")
    return tuple(candidate for candidate in E8_ROOTS
                 if abs(dot(x, candidate) - 1.0) <= TOLERANCE)


def edge_count() -> int:
    """Count undirected edges in the 1-skeleton of Gosset 4_21."""
    directed_degrees = sum(len(neighbors(root)) for root in E8_ROOTS)
    if directed_degrees % 2:
        raise RuntimeError("Gosset adjacency degree sum must be even")
    return directed_degrees // 2


def weyl_reflection(vector: Sequence[float], root: Sequence[float]) -> tuple[float, ...]:
    """Reflect vector in the hyperplane perpendicular to root.

    For an E8 root alpha with alpha·alpha=2:
        s_alpha(x) = x - (x·alpha) alpha.
    """
    x, alpha = _vector(vector), _vector(root, name="root")
    if not is_e8_root(alpha):
        raise ValueError("reflection normal must be an E8 root")
    scale = dot(x, alpha)
    return tuple(value - scale * normal for value, normal in zip(x, alpha))


def reflection_preserves_root_system(root: Sequence[float]) -> bool:
    """Check that reflection in a canonical root permutes all 240 roots."""
    alpha = _vector(root, name="root")
    if not is_e8_root(alpha):
        raise ValueError("reflection normal must be an E8 root")
    reflected = {tuple(round(x, 10) for x in weyl_reflection(v, alpha))
                 for v in E8_ROOTS}
    expected = {tuple(round(x, 10) for x in v) for v in E8_ROOTS}
    return reflected == expected


def support_value(direction: Sequence[float]) -> float:
    """Support function h_P(u)=max_{v in vertices} u·v for P=conv(E8_ROOTS)."""
    u = _vector(direction, name="direction")
    if squared_norm(u) == 0.0:
        raise ValueError("direction must be nonzero")
    return max(dot(u, root) for root in E8_ROOTS)


def radial_boundary(direction: Sequence[float]) -> float:
    """Return rho_P(u) where rho_P(u)u_hat lies on conv(E8_ROOTS).

    This solves a small linear program over convex weights lambda:
      maximize t
      subject to sum(lambda_i)=1, sum(lambda_i * root_i)=t*u_hat,
                 lambda_i >= 0, t >= 0.
    scipy is imported lazily; the core root/adjacency routines do not need it.
    """
    u = _vector(direction, name="direction")
    norm = sqrt(squared_norm(u))
    if norm == 0.0:
        raise ValueError("direction must be nonzero")
    unit = tuple(value / norm for value in u)

    try:
        import numpy as np
        from scipy.optimize import linprog
    except ImportError as exc:
        raise ImportError("radial_boundary requires numpy and scipy") from exc

    roots = np.asarray(E8_ROOTS, dtype=float)
    # Variables are 240 convex weights followed by the radial scale t.
    a_eq = np.zeros((DIMENSION + 1, ROOT_COUNT + 1), dtype=float)
    a_eq[0, :ROOT_COUNT] = 1.0
    a_eq[1:, :ROOT_COUNT] = roots.T
    a_eq[1:, ROOT_COUNT] = -np.asarray(unit)
    b_eq = np.zeros(DIMENSION + 1, dtype=float)
    b_eq[0] = 1.0
    objective = np.zeros(ROOT_COUNT + 1, dtype=float)
    objective[-1] = -1.0
    result = linprog(
        objective,
        A_eq=a_eq,
        b_eq=b_eq,
        bounds=[(0.0, None)] * ROOT_COUNT + [(0.0, None)],
        method="highs",
    )
    if not result.success:
        raise RuntimeError(f"Gosset radial-boundary LP failed: {result.message}")
    return float(result.x[-1])


def geometry_summary() -> dict[str, object]:
    """Return invariant metadata useful for diagnostics and serialized reports."""
    degree = len(neighbors(E8_ROOTS[0]))
    return {
        "name": "Gosset 4_21",
        "dimension": DIMENSION,
        "vertices": len(E8_ROOTS),
        "root_norm_squared": ROOT_NORM_SQUARED,
        "nearest_neighbors_per_vertex": degree,
        "edges": edge_count(),
        "inner_product_distribution": inner_product_distribution(),
    }
