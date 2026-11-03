"""Geometry adapters for JOBF radial-boundary evaluation.

Gosset 4_21 is the primary domain. The 8D cross-polytope remains an explicit
legacy/comparison geometry. Both adapters consume rows of 8D directions and
return radii along normalized rays from the shared origin.
"""
from __future__ import annotations

from functools import lru_cache
from typing import Protocol
import numpy as np

DIMENSION = 8


class RadialGeometry(Protocol):
    name: str

    def radial_boundary_many(self, directions: np.ndarray) -> np.ndarray:
        """Return one positive radial boundary per nonzero direction row."""


def _unit_rows(directions: np.ndarray) -> np.ndarray:
    values = np.asarray(directions, dtype=float)
    if values.ndim != 2 or values.shape[1] != DIMENSION:
        raise ValueError("directions must have shape (N, 8)")
    if not np.all(np.isfinite(values)):
        raise ValueError("directions must contain only finite values")
    norms = np.linalg.norm(values, axis=1)
    if np.any(norms <= 0.0):
        raise ValueError("directions must be nonzero")
    return values / norms[:, None]


class CrossPolytopeAdapter:
    """Legacy H8={x: sum(abs(x_i)) <= 1}; retained for comparison."""

    name = "cross_polytope_h8"

    def radial_boundary_many(self, directions: np.ndarray) -> np.ndarray:
        unit = _unit_rows(directions)
        return 1.0 / np.maximum(np.abs(unit).sum(axis=1), 1e-15)


@lru_cache(maxsize=1)
def _gosset_halfspaces() -> tuple[np.ndarray, np.ndarray]:
    """Build and cache ConvexHull inequalities for conv(E8 roots)."""
    from scipy.spatial import ConvexHull, QhullError
    try:
        from .gosset_421 import E8_ROOTS
    except ImportError:
        from gosset_421 import E8_ROOTS

    try:
        hull = ConvexHull(np.asarray(E8_ROOTS, dtype=float))
    except QhullError as exc:
        raise RuntimeError(f"Could not construct Gosset 4_21 facets: {exc}") from exc
    equations = np.asarray(hull.equations, dtype=float)
    normals = equations[:, :DIMENSION]
    offsets = equations[:, DIMENSION]
    if not np.all(np.isfinite(equations)) or np.any(offsets >= 0.0):
        raise RuntimeError("Gosset hull facets failed finite/origin-interior checks")
    normals.setflags(write=False)
    offsets.setflags(write=False)
    return normals, offsets


class Gosset421Adapter:
    """Primary radial geometry: convex hull of the 240 E8 roots.

    Facets are generated once through scipy.spatial.ConvexHull and cached.
    Each batch then uses vectorized ray/facet intersections; no per-direction
    linear program is solved in the JOBF hot loop.
    """

    name = "gosset_4_21_e8_root_polytope"

    def __init__(self, chunk_size: int = 256):
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        self.chunk_size = int(chunk_size)

    def radial_boundary_many(self, directions: np.ndarray) -> np.ndarray:
        unit = _unit_rows(directions)
        normals, offsets = _gosset_halfspaces()
        radii = np.full(unit.shape[0], np.inf, dtype=float)
        for start in range(0, len(unit), self.chunk_size):
            stop = min(start + self.chunk_size, len(unit))
            # For facet n.x + b <= 0 and ray x=r*u, intersection is
            # r=-b/(n.u), considering only facets facing the ray.
            projections = unit[start:stop] @ normals.T
            valid = projections > 1e-12
            candidates = np.full(projections.shape, np.inf, dtype=float)
            np.divide(-offsets[None, :], projections, out=candidates, where=valid)
            radii[start:stop] = candidates.min(axis=1)
        if not np.all(np.isfinite(radii)) or np.any(radii <= 0.0):
            raise RuntimeError("Gosset radial intersection failed for one or more directions")
        return radii


def get_geometry(name: str = "gosset") -> RadialGeometry:
    """Resolve explicit geometry names; no silent geometry substitution."""
    key = str(name).strip().lower()
    if key in {"gosset", "gosset_4_21", "e8"}:
        return Gosset421Adapter()
    if key in {"cross_polytope", "cross_polytope_h8", "h8", "legacy"}:
        return CrossPolytopeAdapter()
    raise ValueError(f"Unknown radial geometry: {name!r}")
