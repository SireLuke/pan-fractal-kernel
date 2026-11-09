"""Geometry adapters for JOBF radial-boundary evaluation.

Gosset 4_21 is the primary domain. The 8D cross-polytope remains an explicit
legacy/comparison geometry. Both adapters consume rows of 8D directions and
return radii along normalized rays from the shared origin.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Protocol
import hashlib
import os
import tempfile
import zipfile
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


def _e8_root_fingerprint() -> str:
    try:
        from .gosset_421 import E8_ROOTS
    except ImportError:
        from gosset_421 import E8_ROOTS
    roots = np.asarray(E8_ROOTS, dtype="<f8")
    return hashlib.sha256(roots.tobytes(order="C")).hexdigest()


def _default_halfspace_cache_path() -> Path:
    cache_dir = os.environ.get("PAN_FRACTAL_CACHE_DIR")
    root = Path(cache_dir) if cache_dir else Path(tempfile.gettempdir()) / "pan-fractal-kernel"
    fingerprint = _e8_root_fingerprint()
    return root / f"gosset_4_21_halfspaces_v1_{fingerprint[:16]}.npz"


def _validated_halfspaces(normals: np.ndarray, offsets: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    normals = np.asarray(normals, dtype=float)
    offsets = np.asarray(offsets, dtype=float)
    if (normals.ndim != 2 or normals.shape[1] != DIMENSION or normals.shape[0] == 0
            or offsets.shape != (normals.shape[0],)):
        raise ValueError("cached Gosset halfspaces have invalid shapes")
    if (not np.all(np.isfinite(normals)) or not np.all(np.isfinite(offsets))
            or np.any(np.linalg.norm(normals, axis=1) <= 0.0)
            or np.any(offsets >= 0.0)):
        raise ValueError("cached Gosset halfspaces failed finite/origin checks")
    normals = np.array(normals, copy=True)
    offsets = np.array(offsets, copy=True)
    normals.setflags(write=False)
    offsets.setflags(write=False)
    return normals, offsets


def _load_halfspace_cache(path: Path, fingerprint: str) -> tuple[np.ndarray, np.ndarray] | None:
    if not path.is_file():
        return None
    try:
        with np.load(path, allow_pickle=False) as cached:
            version = int(np.asarray(cached["version"]).item())
            saved_fingerprint = str(np.asarray(cached["root_sha256"]).item())
            normals = np.asarray(cached["normals"], dtype=float)
            offsets = np.asarray(cached["offsets"], dtype=float)
        if version != 1 or saved_fingerprint != fingerprint:
            return None
        return _validated_halfspaces(normals, offsets)
    except (OSError, ValueError, KeyError, EOFError, zipfile.BadZipFile):
        return None


def _write_halfspace_cache(
    path: Path,
    fingerprint: str,
    normals: np.ndarray,
    offsets: np.ndarray,
) -> None:
    temporary = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        with tempfile.NamedTemporaryFile(mode="w+b", suffix=".npz", dir=path.parent, delete=False) as stream:
            temporary = Path(stream.name)
            np.savez_compressed(
                stream,
                version=np.asarray(1, dtype=np.int64),
                root_sha256=np.asarray(fingerprint),
                normals=normals,
                offsets=offsets,
            )
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, path)
    except OSError:
        # Disk caching is an optimization; a read-only temp/cache directory
        # must not prevent correct in-memory geometry evaluation.
        if temporary is not None:
            try:
                temporary.unlink(missing_ok=True)
            except OSError:
                pass


@lru_cache(maxsize=8)
def _gosset_halfspaces(cache_path: str | None = None) -> tuple[np.ndarray, np.ndarray]:
    """Load or build facet inequalities for conv(E8 roots).

    A validated NPZ cache keeps the expensive 8D Qhull construction from
    repeating in every Python process. Set PAN_FRACTAL_CACHE_DIR to override
    the default per-user temporary cache directory.
    """
    try:
        from .gosset_421 import E8_ROOTS
    except ImportError:
        from gosset_421 import E8_ROOTS

    fingerprint = _e8_root_fingerprint()
    path = Path(cache_path) if cache_path else _default_halfspace_cache_path()
    cached = _load_halfspace_cache(path, fingerprint)
    if cached is not None:
        return cached

    from scipy.spatial import ConvexHull, QhullError
    try:
        hull = ConvexHull(np.asarray(E8_ROOTS, dtype=float))
    except QhullError as exc:
        raise RuntimeError(f"Could not construct Gosset 4_21 facets: {exc}") from exc
    equations = np.asarray(hull.equations, dtype=float)
    if equations.ndim != 2 or equations.shape[1] != DIMENSION + 1:
        raise RuntimeError("Gosset hull returned an invalid halfspace matrix")
    normals, offsets = _validated_halfspaces(equations[:, :DIMENSION], equations[:, DIMENSION])
    _write_halfspace_cache(path, fingerprint, normals, offsets)
    return normals, offsets

class Gosset421Adapter:
    """Primary radial geometry: convex hull of the 240 E8 roots.

    Facets are loaded from a validated cross-process disk cache when available.
    On a cache miss, scipy.spatial.ConvexHull builds them once and the result
    is saved atomically. Each batch then uses vectorized ray/facet intersections.
    """

    name = "gosset_4_21_e8_root_polytope"

    def __init__(self, chunk_size: int = 256, cache_path: str | Path | None = None):
        if chunk_size < 1:
            raise ValueError("chunk_size must be positive")
        self.chunk_size = int(chunk_size)
        self.cache_path = str(Path(cache_path)) if cache_path is not None else None

    def radial_boundary_many(self, directions: np.ndarray) -> np.ndarray:
        unit = _unit_rows(directions)
        normals, offsets = _gosset_halfspaces(self.cache_path)
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
