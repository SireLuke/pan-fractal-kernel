"""Deterministic graph-depth exploration of the infinite E8 / 5_21 lattice.

Graph depth counts nearest-root transitions. It is separate from Euclidean
norm shells and from View Ladder projection depth. Coordinates are doubled
integers, so E8 lattice arithmetic is exact.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from typing import Optional

try:
    from .five21_neighborhood import ROOTS2, is_e8_doubled
except ImportError:
    from five21_neighborhood import ROOTS2, is_e8_doubled

ORIGIN = (0,) * 8

@dataclass(frozen=True)
class DepthShell:
    depth: int
    new_vertices: int
    cumulative_vertices: int
    euclidean_norm_squared_counts: tuple[tuple[int, int], ...]
    sha256: str

@dataclass(frozen=True)
class DepthRun:
    origin: tuple[int, ...]
    max_depth_requested: int
    reached_depth: int
    visited_vertices: int
    shells: tuple[DepthShell, ...]
    truncated: bool
    stop_reason: str
    parent_edges: Optional[dict]

    def shell_counts(self) -> tuple[int, ...]:
        return tuple(shell.new_vertices for shell in self.shells)

    def path_to(self, vertex: tuple[int, ...]) -> tuple[int, ...]:
        """Return root indices for a shortest path from origin to vertex."""
        if self.parent_edges is None:
            raise ValueError("run with track_paths=True to retain parent edges")
        point = _point(vertex, name="vertex")
        if point == self.origin:
            return ()
        if point not in self.parent_edges:
            raise KeyError("vertex is not in the completed traversal")
        path = []
        cursor = point
        while cursor != self.origin:
            parent, root_index = self.parent_edges[cursor]
            path.append(root_index)
            cursor = parent
        path.reverse()
        return tuple(path)

def _point(values, *, name="point") -> tuple[int, ...]:
    try:
        point = tuple(values)
    except TypeError:
        raise ValueError(f"{name} must be an 8-coordinate iterable") from None
    if len(point) != 8 or any(type(x) is not int for x in point):
        raise ValueError(f"{name} must contain exactly 8 integer doubled-coordinates")
    if not is_e8_doubled(point):
        raise ValueError(f"{name} is not an E8 lattice point in doubled coordinates")
    return point

def _shell_record(depth: int, points: set[tuple[int, ...]], cumulative: int) -> DepthShell:
    ordered = sorted(points)
    norm_counts: dict[int, int] = {}
    for point in ordered:
        numerator = sum(x * x for x in point)
        if numerator % 4:
            raise ArithmeticError("E8 norm is not integral in doubled coordinates")
        norm2 = numerator // 4
        norm_counts[norm2] = norm_counts.get(norm2, 0) + 1
    payload = json.dumps(ordered, separators=(",", ":")).encode("ascii")
    return DepthShell(depth, len(ordered), cumulative, tuple(sorted(norm_counts.items())),
                      hashlib.sha256(payload).hexdigest())

def explore(max_depth: int, *, origin: tuple[int, ...] = ORIGIN,
            max_vertices: int | None = 1_000_000,
            track_paths: bool = False) -> DepthRun:
    """Explore complete nearest-root BFS shells from an E8 lattice point.

    If max_vertices would be exceeded, the incomplete next shell is discarded.
    Thus every reported shell and count is complete and exact.
    """
    if type(max_depth) is not int or max_depth < 0:
        raise ValueError("max_depth must be a nonnegative integer")
    if max_vertices is not None and (type(max_vertices) is not int or max_vertices < 1):
        raise ValueError("max_vertices must be a positive integer or None")
    start = _point(origin, name="origin")
    seen = {start}
    frontier = {start}
    records = [_shell_record(0, frontier, 1)]
    parents = {} if track_paths else None
    reached, truncated, stop_reason = 0, False, "max_depth"

    while reached < max_depth:
        following: set[tuple[int, ...]] = set()
        next_parents = {}
        limit_hit = False
        for point in sorted(frontier):
            for root_index, root in enumerate(ROOTS2):
                candidate = tuple(a + b for a, b in zip(point, root))
                if candidate in seen or candidate in following:
                    continue
                if max_vertices is not None and len(seen) + len(following) + 1 > max_vertices:
                    limit_hit = True
                    break
                following.add(candidate)
                if track_paths:
                    next_parents[candidate] = (point, root_index)
            if limit_hit:
                break
        if limit_hit:
            truncated, stop_reason = True, "max_vertices"
            break
        if not following:
            stop_reason = "exhausted_component"
            break
        seen.update(following)
        if track_paths:
            parents.update(next_parents)
        reached += 1
        records.append(_shell_record(reached, following, len(seen)))
        frontier = following

    return DepthRun(start, max_depth, reached, len(seen), tuple(records),
                    truncated, stop_reason, parents)

def run_to_dict(run: DepthRun) -> dict:
    """JSON-ready stable report; parent maps are intentionally excluded."""
    return {
        "schema": "pan-geometric-depth-v1",
        "geometry": "E8 lattice vertex graph of the 5_21 honeycomb",
        "origin_doubled": list(run.origin),
        "depth_metric": "shortest-path count using 240 norm-2 roots",
        "euclidean_norm_metric": "squared Euclidean norm, reported independently",
        "max_depth_requested": run.max_depth_requested,
        "reached_depth": run.reached_depth,
        "visited_vertices": run.visited_vertices,
        "truncated": run.truncated,
        "stop_reason": run.stop_reason,
        "shells": [{
            "depth": s.depth, "new_vertices": s.new_vertices,
            "cumulative_vertices": s.cumulative_vertices,
            "euclidean_norm_squared_counts": [
                {"norm_squared": norm2, "count": count}
                for norm2, count in s.euclidean_norm_squared_counts],
            "sha256": s.sha256,
        } for s in run.shells],
    }
