"""View-ladder schema: a nested chain of orthonormal views of a point set in R^N.

One schema serves the Gosset 4_21 roots (finite) and finite patches of the 5_21
honeycomb (affine E8 / "E9" lattice). Every stage is an orthonormal frame taken
directly from the SOURCE space, so reconstruction error is always measured against
the original 8D points (not against the previous stage). Source coordinates and ids
are never mutated; a ladder is a set of views, not a new geometry.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass
from typing import Sequence

import numpy as np

try:
    from .gosset_421 import E8_ROOTS, DIMENSION, ROOT_COUNT
    from .gosset_projection import (ProjectionFrame, ProjectionResult,
                                    coordinate_frame, project_points)
except ImportError:
    from gosset_421 import E8_ROOTS, DIMENSION, ROOT_COUNT
    from gosset_projection import (ProjectionFrame, ProjectionResult,
                                   coordinate_frame, project_points)

SCHEMA_VERSION = "view-ladder-v1"
NEST_TOL = 1e-9


class LadderError(ValueError):
    """Invalid ladder construction or schema."""


@dataclass(frozen=True)
class LadderStage:
    dimension: int
    frame: ProjectionFrame          # k x N, from the source space
    result: ProjectionResult        # projection of the source points
    nested_in_previous: bool        # row space contained in the previous (higher) stage


@dataclass(frozen=True)
class ViewLadder:
    name: str
    geometry: str
    notes: str
    ids: tuple                      # one JSON-serializable id per source point
    id_kind: str
    stages: tuple                   # ordered by strictly decreasing dimension

    def stage(self, dimension: int) -> LadderStage:
        for s in self.stages:
            if s.dimension == dimension:
                return s
        raise LadderError(f"no {dimension}D stage in ladder {self.name!r}")

    @property
    def dimensions(self) -> tuple:
        return tuple(s.dimension for s in self.stages)

    def to_schema(self) -> dict:
        src = self.stages[0].result.source_points
        total = float(np.sum(src * src))
        stages = []
        for s in self.stages:
            r = s.result
            retained = float(np.sum(r.projected_points ** 2)) / total if total > 0 else None
            stages.append({
                "dimension": s.dimension,
                "frame_name": s.frame.name,
                "frame_matrix": s.frame.matrix.tolist(),
                "nested_in_previous": s.nested_in_previous,
                "max_residual_vs_source": r.maximum_reconstruction_error,
                "rms_residual_vs_source": float(np.sqrt(np.mean(r.residual_norms ** 2))),
                "energy_retained_fraction": retained,
                "lossless": r.is_lossless,
            })
        body = {
            "schema": SCHEMA_VERSION,
            "name": self.name,
            "source": {
                "geometry": self.geometry,
                "ambient_dimension": int(src.shape[1]),
                "point_count": int(src.shape[0]),
                "id_kind": self.id_kind,
                "ids_sha256": hashlib.sha256(
                    json.dumps(self.ids, separators=(",", ":")).encode()).hexdigest(),
                "notes": self.notes,
            },
            "stages": stages,
        }
        body["schema_sha256"] = hashlib.sha256(
            json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        return body


def validate_schema(d: dict) -> None:
    """Raise LadderError unless d is a self-consistent view-ladder-v1 document."""
    try:
        if d["schema"] != SCHEMA_VERSION:
            raise LadderError(f"unknown schema {d['schema']!r}")
        body = {k: v for k, v in d.items() if k != "schema_sha256"}
        digest = hashlib.sha256(json.dumps(body, sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        if digest != d["schema_sha256"]:
            raise LadderError("schema_sha256 does not match content")
        n = d["source"]["ambient_dimension"]
        dims = [s["dimension"] for s in d["stages"]]
        if not dims or any(a <= b for a, b in zip(dims, dims[1:])) or dims[0] > n:
            raise LadderError("stage dimensions must be strictly decreasing and <= ambient")
        for s in d["stages"]:
            m = np.asarray(s["frame_matrix"], dtype=float)
            if m.shape != (s["dimension"], n) or not np.allclose(m @ m.T, np.eye(s["dimension"]), atol=1e-9):
                raise LadderError(f"stage {s['dimension']}: frame is not orthonormal k x N")
    except KeyError as e:
        raise LadderError(f"missing schema field {e}") from None


def build_ladder(name: str, geometry: str, source_points, ids: Sequence, id_kind: str,
                 frames: Sequence[ProjectionFrame], notes: str = "") -> ViewLadder:
    pts = np.asarray(source_points, dtype=float)
    if pts.ndim != 2 or len(pts) == 0 or not np.all(np.isfinite(pts)):
        raise LadderError("source_points must be a nonempty finite (M, N) array")
    if len(ids) != len(pts):
        raise LadderError("one id per source point is required")
    if not frames:
        raise LadderError("at least one frame is required")
    dims = [f.output_dimension for f in frames]
    if any(a <= b for a, b in zip(dims, dims[1:])):
        raise LadderError("frames must have strictly decreasing output dimension")
    if any(f.input_dimension != pts.shape[1] for f in frames):
        raise LadderError("every frame must act on the source space")
    stages, prev = [], None
    idx = np.arange(len(pts), dtype=np.int64)
    for f in frames:
        nested = True
        if prev is not None:
            a, b = f.matrix, prev.matrix          # a rows must lie in rowspace(b)
            nested = bool(np.allclose(a @ b.T @ b, a, atol=NEST_TOL))
        stages.append(LadderStage(f.output_dimension, f,
                                  project_points(pts, f, source_indices=idx), nested))
        prev = f
    return ViewLadder(name, geometry, notes, tuple(ids), id_kind, tuple(stages))


def seeded_3d_rows(seed: int = 421, n: int = DIMENSION) -> np.ndarray:
    """The 3 x N seeded viewing frame (identical RNG recipe to gosset_3d_simulation.seeded_view)."""
    rng = np.random.default_rng(seed)
    q, _ = np.linalg.qr(rng.normal(size=(n, 3)))
    return q.T


def extend_orthonormal(rows: np.ndarray, total: int, seed: int) -> np.ndarray:
    """Extend orthonormal rows to `total` rows by seeded Gram-Schmidt; leading rows are unchanged."""
    out = [r for r in np.asarray(rows, dtype=float)]
    n = len(out[0])
    rng = np.random.default_rng([seed, total])
    while len(out) < total:
        v = rng.normal(size=n)
        for _ in range(2):                       # re-orthogonalise for stability
            for r in out:
                v = v - (v @ r) * r
        norm = np.linalg.norm(v)
        if norm > 1e-8:
            out.append(v / norm)
    return np.array(out)


def nested_frames(rows3: np.ndarray, seed: int, dims: Sequence[int] = (8, 4, 3, 2)) -> list:
    """Nested frames whose 3D stage is rows3, 2D is its first 2 rows, 4D/8D extend it."""
    r3 = np.asarray(rows3, dtype=float)
    full = extend_orthonormal(r3, 8, seed)
    table = {8: full, 4: full[:4], 3: r3, 2: r3[:2]}
    return [ProjectionFrame(table[d], f"seeded_nested_{d}d_seed{seed}") for d in dims]


# ---------------------------------------------------------------- Gosset 4_21

_GOSSET_NOTE = ("240 canonical E8 roots; ids are canonical root indices. Views are lossy "
                "orthographic frames, not claimed to be privileged by E8 symmetry.")


def gosset_coordinate_ladder() -> ViewLadder:
    """8D -> 4D -> 3D -> 2D by retaining leading coordinates (same views as project_gosset_chain)."""
    frames = [ProjectionFrame(np.eye(DIMENSION), "identity_8d")] + [
        ProjectionFrame(coordinate_frame(DIMENSION, d).matrix, f"coordinate_8d_to_{d}d") for d in (4, 3, 2)]
    return build_ladder("gosset_421_coordinate", "Gosset 4_21 (240 E8 roots)", np.asarray(E8_ROOTS),
                        list(range(ROOT_COUNT)), "canonical_root_index", frames, _GOSSET_NOTE)


def gosset_seeded_ladder(seed: int = 421) -> ViewLadder:
    """Ladder whose 3D stage is the seeded 3D view used by gosset_3d_simulation."""
    frames = nested_frames(seeded_3d_rows(seed), seed)
    return build_ladder(f"gosset_421_seeded_{seed}", "Gosset 4_21 (240 E8 roots)", np.asarray(E8_ROOTS),
                        list(range(ROOT_COUNT)), "canonical_root_index", frames, _GOSSET_NOTE)
