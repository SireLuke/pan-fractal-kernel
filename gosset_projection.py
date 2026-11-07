"""Loss-aware orthographic projections of the canonical Gosset 4_21 / E8 root set.

The source geometry remains in R^8. A projection is a view transform, not a
replacement geometry. Source coordinates and root indices are retained in
ProjectionResult so callers can preserve identity and E8 adjacency overlays.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations
from typing import Iterable, Sequence

import numpy as np

try:
    from .gosset_421 import DIMENSION, E8_ROOTS, ROOT_COUNT, dot
except ImportError:
    from gosset_421 import DIMENSION, E8_ROOTS, ROOT_COUNT, dot

DEFAULT_TOLERANCE = 1e-10
V8_CHANNELS = ("h", "R", "u", "d", "tau", "chi", "s", "f")


@dataclass(frozen=True)
class ProjectionFrame:
    """An orthonormal row-frame mapping R^input_dimension to R^output_dimension."""

    matrix: np.ndarray
    name: str = "orthographic"

    def __post_init__(self) -> None:
        matrix = np.asarray(self.matrix, dtype=float)
        if matrix.ndim != 2:
            raise ValueError("projection matrix must be two-dimensional")
        out_dim, in_dim = matrix.shape
        if not (1 <= out_dim <= in_dim):
            raise ValueError("projection dimensions must satisfy 1 <= output <= input")
        if not np.all(np.isfinite(matrix)):
            raise ValueError("projection matrix must contain only finite values")
        gram = matrix @ matrix.T
        if not np.allclose(gram, np.eye(out_dim), atol=DEFAULT_TOLERANCE, rtol=0.0):
            raise ValueError("projection frame rows must be orthonormal")
        matrix = np.array(matrix, copy=True)
        matrix.setflags(write=False)
        object.__setattr__(self, "matrix", matrix)

    @property
    def input_dimension(self) -> int:
        return int(self.matrix.shape[1])

    @property
    def output_dimension(self) -> int:
        return int(self.matrix.shape[0])


@dataclass(frozen=True)
class ProjectionResult:
    """A projected view plus enough provenance to audit/reconstruct its source."""

    frame: ProjectionFrame
    source_points: np.ndarray
    projected_points: np.ndarray
    reconstructed_points: np.ndarray
    residual_norms: np.ndarray
    exact_mask: np.ndarray
    source_indices: np.ndarray | None = None

    @property
    def is_lossless(self) -> bool:
        return bool(np.all(self.exact_mask))

    @property
    def maximum_reconstruction_error(self) -> float:
        return float(np.max(self.residual_norms, initial=0.0))


def coordinate_frame(input_dimension: int, output_dimension: int,
                     axes: Sequence[int] | None = None,
                     *, name: str | None = None) -> ProjectionFrame:
    """Create a transparent coordinate projection onto selected input axes.

    By default, the first output_dimension axes are retained. This is a
    convention for deterministic views, not a claim that those axes are
    uniquely privileged by E8 symmetry.
    """
    if not (1 <= output_dimension <= input_dimension):
        raise ValueError("require 1 <= output_dimension <= input_dimension")
    selected = tuple(range(output_dimension)) if axes is None else tuple(int(i) for i in axes)
    if len(selected) != output_dimension or len(set(selected)) != len(selected):
        raise ValueError("axes must contain output_dimension unique indices")
    if any(i < 0 or i >= input_dimension for i in selected):
        raise ValueError("axis index outside input dimension")
    matrix = np.zeros((output_dimension, input_dimension), dtype=float)
    matrix[np.arange(output_dimension), selected] = 1.0
    frame_name = name or f"coordinate_{input_dimension}d_to_{output_dimension}d"
    return ProjectionFrame(matrix, frame_name)


def project_points(points: Sequence[Sequence[float]] | np.ndarray,
                   frame: ProjectionFrame, *,
                   source_indices: Sequence[int] | np.ndarray | None = None,
                   tolerance: float = DEFAULT_TOLERANCE) -> ProjectionResult:
    """Project row-major points and report exactly what information was lost.

    For an orthonormal row-frame A, y=x A^T and the canonical least-squares
    lift is y A. A lift is exact only when x lies in the retained row-space.
    """
    source = np.asarray(points, dtype=float)
    if source.ndim == 1:
        source = source.reshape(1, -1)
    if source.ndim != 2 or source.shape[1] != frame.input_dimension:
        raise ValueError(f"points must have shape (N, {frame.input_dimension})")
    if not np.all(np.isfinite(source)):
        raise ValueError("points must contain only finite coordinates")
    if not np.isfinite(tolerance) or tolerance < 0:
        raise ValueError("tolerance must be finite and nonnegative")
    indices = None
    if source_indices is not None:
        indices = np.asarray(source_indices, dtype=np.int64)
        if indices.shape != (len(source),):
            raise ValueError("source_indices must contain one index per point")
        indices = np.array(indices, copy=True)
        indices.setflags(write=False)

    projected = source @ frame.matrix.T
    reconstructed = projected @ frame.matrix
    residuals = np.linalg.norm(source - reconstructed, axis=1)
    exact = residuals <= tolerance
    arrays = [np.array(value, copy=True) for value in
              (source, projected, reconstructed, residuals, exact)]
    for value in arrays:
        value.setflags(write=False)
    return ProjectionResult(frame, *arrays, source_indices=indices)


def project_gosset_roots(output_dimension: int, *,
                         axes: Sequence[int] | None = None,
                         name: str | None = None) -> ProjectionResult:
    """Project all 240 Gosset vertices while retaining canonical root indices."""
    frame = coordinate_frame(DIMENSION, output_dimension, axes, name=name)
    return project_points(np.asarray(E8_ROOTS), frame,
                          source_indices=np.arange(ROOT_COUNT, dtype=np.int64))


@lru_cache(maxsize=1)
def gosset_edge_indices() -> np.ndarray:
    """Return the 6,720 undirected E8/Gosset edges as pairs of root indices.

    Adjacency is defined in the canonical source space by alpha dot beta = 1.
    It is never recomputed from a lower-dimensional projection, where distinct
    vertices may overlap and apparent adjacency can be misleading.
    """
    index = {root: i for i, root in enumerate(E8_ROOTS)}
    edges = []
    for i, alpha in enumerate(E8_ROOTS):
        for beta in E8_ROOTS[i + 1:]:
            if abs(dot(alpha, beta) - 1.0) <= DEFAULT_TOLERANCE:
                edges.append((i, index[beta]))
    result = np.asarray(edges, dtype=np.int64)
    if result.shape != (6720, 2):
        raise RuntimeError(f"expected 6720 Gosset edges, found {len(result)}")
    result.setflags(write=False)
    return result


def project_gosset_chain(*, axes_8_to_4: Sequence[int] | None = None,
                         axes_4_to_3: Sequence[int] | None = None,
                         axes_3_to_2: Sequence[int] | None = None
                         ) -> dict[int, ProjectionResult]:
    """Build a deterministic 8D -> 4D -> 3D -> 2D view ladder.

    Each stage retains its own source coordinates and reconstruction error.
    The 3D and 2D stages are projections of the immediately preceding view;
    callers can always return to the canonical 8D roots via the 8D source
    identity retained by the 4D result.
    """
    roots = np.asarray(E8_ROOTS, dtype=float)
    p4 = project_points(roots, coordinate_frame(8, 4, axes_8_to_4),
                        source_indices=np.arange(ROOT_COUNT))
    p3 = project_points(p4.projected_points, coordinate_frame(4, 3, axes_4_to_3),
                        source_indices=np.arange(ROOT_COUNT))
    p2 = project_points(p3.projected_points, coordinate_frame(3, 2, axes_3_to_2),
                        source_indices=np.arange(ROOT_COUNT))
    return {8: ProjectionResult(
                coordinate_frame(8, 8, tuple(range(8)), name="identity_8d"),
                roots, roots.copy(), roots.copy(),
                np.zeros(ROOT_COUNT), np.ones(ROOT_COUNT, dtype=bool),
                np.arange(ROOT_COUNT, dtype=np.int64)),
            4: p4, 3: p3, 2: p2}


def v8_channel_metadata() -> tuple[str, ...]:
    """Return the canonical V8 channel order without modifying semantic records."""
    return V8_CHANNELS
