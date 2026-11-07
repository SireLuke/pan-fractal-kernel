"""Experimental V9 affine-E8 view family built on the canonical Gosset projector.

V9 adds a normalized traversal parameter xi to the view frame, not a ninth
Euclidean E8 root coordinate. The canonical E8 roots and V8 semantic state are
never mutated. Continuous frames are orthogonal display transforms; except at
special values, they are not E8 lattice automorphisms.
"""
from __future__ import annotations
import math
from typing import Sequence
import numpy as np
try:
    from .gosset_421 import E8_ROOTS, DIMENSION, ROOT_COUNT
    from .gosset_projection import ProjectionFrame, ProjectionResult, coordinate_frame, project_points
except ImportError:
    from gosset_421 import E8_ROOTS, DIMENSION, ROOT_COUNT
    from gosset_projection import ProjectionFrame, ProjectionResult, coordinate_frame, project_points

_ROTATION_PLANES = (
    (0, 1, 2.0 * math.pi),
    (2, 3, math.pi / math.sqrt(2.0)),
    (4, 5, -math.pi / math.sqrt(3.0)),
    (6, 7, math.pi / 2.0),
)

def _validate_xi(xi: float) -> float:
    value = float(xi)
    if not math.isfinite(value) or not 0.0 <= value <= 1.0:
        raise ValueError("xi must be finite and normalized to [0, 1]")
    return value

def orthogonal_xi_frame(xi: float) -> np.ndarray:
    """Return Q(xi) in SO(8), with Q(0)=I and deterministic reverse Q.T."""
    value = _validate_xi(xi)
    q = np.eye(DIMENSION, dtype=float)
    for i, j, rate in _ROTATION_PLANES:
        angle = value * rate
        c, s = math.cos(angle), math.sin(angle)
        q[i, i], q[i, j] = c, -s
        q[j, i], q[j, j] = s, c
    q.setflags(write=False)
    return q

def affine_e8_projection_frame(output_dimension: int, xi: float,
                               axes: Sequence[int] | None = None) -> ProjectionFrame:
    """Compose the canonical coordinate view with a continuous SO(8) frame."""
    q = orthogonal_xi_frame(xi)
    base = coordinate_frame(DIMENSION, output_dimension, axes)
    return ProjectionFrame(base.matrix @ q, f"affine_e8_xi_{_validate_xi(xi):.6f}_{output_dimension}d")

def project_gosset_roots_at_xi(output_dimension: int, xi: float,
                               axes: Sequence[int] | None = None) -> ProjectionResult:
    """Project canonical Gosset roots while retaining source roots and indices."""
    frame = affine_e8_projection_frame(output_dimension, xi, axes)
    return project_points(np.asarray(E8_ROOTS, dtype=float), frame,
                          source_indices=np.arange(ROOT_COUNT, dtype=np.int64))

def project_gosset_chain_at_xi(xi: float, *,
        axes_8_to_4: Sequence[int] | None = None,
        axes_4_to_3: Sequence[int] | None = None,
        axes_3_to_2: Sequence[int] | None = None) -> dict[int, ProjectionResult]:
    """Build an xi-oriented 8D->4D->3D->2D chain with root provenance."""
    p4 = project_gosset_roots_at_xi(4, xi, axes_8_to_4)
    p3 = project_points(p4.projected_points, coordinate_frame(4, 3, axes_4_to_3),
                        source_indices=np.arange(ROOT_COUNT, dtype=np.int64))
    p2 = project_points(p3.projected_points, coordinate_frame(3, 2, axes_3_to_2),
                        source_indices=np.arange(ROOT_COUNT, dtype=np.int64))
    identity = project_gosset_roots_at_xi(8, 0.0)
    return {8: identity, 4: p4, 3: p3, 2: p2}

def is_e8_lattice_point(vector: Sequence[float], *, atol: float = 1e-10) -> bool:
    """E8 lattice: integer or half-integer coordinates, with even coordinate sum."""
    x = np.asarray(vector, dtype=float)
    if x.shape != (DIMENSION,) or not np.all(np.isfinite(x)) or not math.isfinite(atol) or atol < 0:
        return False
    integer = np.rint(x)
    if np.all(np.abs(x - integer) <= atol):
        return int(round(float(np.sum(integer)))) % 2 == 0
    doubled = np.rint(2.0 * x)
    half_integral = np.all(np.abs(2.0 * x - doubled) <= 2.0 * atol)
    odd_coordinates = np.all(np.abs(np.abs(doubled % 2.0) - 1.0) <= 2.0 * atol)
    even_sum = abs(float(np.sum(x)) - round(float(np.sum(x)) / 2.0) * 2.0) <= 2.0 * atol
    return bool(half_integral and odd_coordinates and even_sum)

def translate_e8_lattice_points(points: Sequence[Sequence[float]] | np.ndarray,
                                lattice_vector: Sequence[float]) -> np.ndarray:
    """Translate E8 lattice points by a lattice vector, preserving membership.

    The translated finite 240-root subset is not asserted to remain the same
    root subset; it becomes another finite subset of the full E8 lattice.
    """
    cloud, shift = np.asarray(points, dtype=float), np.asarray(lattice_vector, dtype=float)
    if cloud.ndim != 2 or cloud.shape[1] != DIMENSION or not np.all(np.isfinite(cloud)):
        raise ValueError("points must be a finite (N, 8) array")
    if not is_e8_lattice_point(shift):
        raise ValueError("translation vector must belong to the E8 lattice")
    if not all(is_e8_lattice_point(point) for point in cloud):
        raise ValueError("every translated point must belong to the E8 lattice")
    translated = cloud + shift
    if not all(is_e8_lattice_point(point) for point in translated):
        raise ArithmeticError("E8 lattice translation failed membership invariant")
    return translated

def normalize_point_cloud(points: Sequence[Sequence[float]] | np.ndarray) -> np.ndarray:
    """Center and divide by RMS radius; a shape normalization, not a Weyl action."""
    cloud = np.asarray(points, dtype=float)
    if cloud.ndim != 2 or cloud.shape[0] == 0 or not np.all(np.isfinite(cloud)):
        raise ValueError("points must be a nonempty finite 2D array")
    centered = cloud - np.mean(cloud, axis=0)
    rms = math.sqrt(float(np.mean(np.sum(centered * centered, axis=1))))
    if not math.isfinite(rms) or rms <= 0.0:
        raise ValueError("cannot normalize a degenerate point cloud")
    return centered / rms

def reverse_xi_frame(xi: float) -> np.ndarray:
    """Return the exact orthogonal inverse Q(xi).T."""
    return orthogonal_xi_frame(xi).T.copy()
