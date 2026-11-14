"""Exact local vertex-star and incidence audit for Gosset 4_21.

All calculations use doubled integer E8 coordinates. No floating point,
SciPy, or full Weyl-group enumeration is involved.
"""
from __future__ import annotations

from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations
from typing import Sequence

from e8_bounded_symmetry import (
    ROOT_COUNT,
    ScaledRoot,
    _dot,
    is_scaled_e8_root,
    propagate_root_orbit,
)

LOCAL_VERTEX_COUNT = 56
LOCAL_EDGE_COUNT = 756
LOCAL_DEGREE = 27
LOCAL_TRIANGLE_COUNT = 4032
TRIANGLES_THROUGH_LOCAL_VERTEX = 216
LOCAL_DISTANCE_DISTRIBUTION = {0: 1, 1: 27, 2: 27, 3: 1}
LOCAL_PAIR_CLASS_COUNTS = {
    "adjacent_common_16": 756,
    "nonadjacent_common_10": 756,
    "nonadjacent_common_0": 28,
}
GLOBAL_FOUR_CLIQUE_COUNT = 241_920
FOUR_CLIQUES_PER_GLOBAL_EDGE = 216


@dataclass(frozen=True)
class VertexStar:
    """Induced graph on the 56 Gosset vertices adjacent to one base vertex."""

    base_root: ScaledRoot
    vertices: tuple[ScaledRoot, ...]
    edges: tuple[tuple[int, int], ...]
    adjacency: tuple[tuple[int, ...], ...]
    degree_sequence: tuple[int, ...]
    common_neighbor_classes: dict[str, int]
    triangles: int
    triangles_through_each_vertex: tuple[int, ...]
    distance_distributions: tuple[dict[int, int], ...]

    @property
    def unique_zero_common_neighbor_pairs(self) -> tuple[tuple[int, int], ...]:
        return tuple(
            (i, j)
            for i, j in combinations(range(len(self.vertices)), 2)
            if self.common_neighbor_count(i, j) == 0
        )

    def common_neighbor_count(self, left: int, right: int) -> int:
        return len(set(self.adjacency[left]).intersection(self.adjacency[right]))


def _resolve_roots() -> tuple[ScaledRoot, ...]:
    return propagate_root_orbit().roots


def build_vertex_star(base_root: Sequence[int]) -> VertexStar:
    """Build the induced 56-vertex graph around a canonical E8 root."""
    base = tuple(base_root)
    if not is_scaled_e8_root(base):
        raise ValueError("base_root must be one of the 240 scaled E8 roots")

    roots = _resolve_roots()
    if base not in roots:
        raise ValueError("base_root is not present in the canonical E8 orbit")

    vertices = tuple(root for root in roots if _dot(base, root) == 4)
    if len(vertices) != LOCAL_VERTEX_COUNT:
        raise ArithmeticError(
            f"vertex star has {len(vertices)} vertices; expected {LOCAL_VERTEX_COUNT}"
        )

    adjacency_sets = [set() for _ in vertices]
    edges = []
    for left, right in combinations(range(len(vertices)), 2):
        if _dot(vertices[left], vertices[right]) == 4:
            edges.append((left, right))
            adjacency_sets[left].add(right)
            adjacency_sets[right].add(left)

    adjacency = tuple(tuple(sorted(row)) for row in adjacency_sets)
    degrees = tuple(len(row) for row in adjacency)
    if len(edges) != LOCAL_EDGE_COUNT:
        raise ArithmeticError(
            f"vertex-star graph has {len(edges)} edges; expected {LOCAL_EDGE_COUNT}"
        )
    if set(degrees) != {LOCAL_DEGREE}:
        raise ArithmeticError("vertex-star graph does not have constant degree 27")

    pair_classes: Counter[str] = Counter()
    for left, right in combinations(range(len(vertices)), 2):
        common = len(adjacency_sets[left].intersection(adjacency_sets[right]))
        adjacent = right in adjacency_sets[left]
        if adjacent and common == 16:
            pair_classes["adjacent_common_16"] += 1
        elif not adjacent and common == 10:
            pair_classes["nonadjacent_common_10"] += 1
        elif not adjacent and common == 0:
            pair_classes["nonadjacent_common_0"] += 1
        else:
            raise ArithmeticError(
                f"unexpected local pair type: adjacent={adjacent}, common={common}"
            )

    triangles_through = tuple(
        sum(
            1
            for left, right in combinations(adjacency_sets[vertex], 2)
            if right in adjacency_sets[left]
        )
        for vertex in range(len(vertices))
    )
    triangles = sum(triangles_through) // 3
    if sum(triangles_through) % 3:
        raise ArithmeticError("local triangle incidence is not divisible by 3")

    distances = tuple(_distance_distribution(adjacency, start)
                      for start in range(len(vertices)))
    return VertexStar(
        base_root=base,
        vertices=vertices,
        edges=tuple(edges),
        adjacency=adjacency,
        degree_sequence=degrees,
        common_neighbor_classes=dict(sorted(pair_classes.items())),
        triangles=triangles,
        triangles_through_each_vertex=triangles_through,
        distance_distributions=distances,
    )


def _distance_distribution(
    adjacency: tuple[tuple[int, ...], ...], start: int
) -> dict[int, int]:
    distances = {start: 0}
    pending = deque([start])
    while pending:
        current = pending.popleft()
        for neighbor in adjacency[current]:
            if neighbor not in distances:
                distances[neighbor] = distances[current] + 1
                pending.append(neighbor)
    if len(distances) != len(adjacency):
        raise ArithmeticError("local vertex-star graph is disconnected")
    return dict(sorted(Counter(distances.values()).items()))


def audit_all_vertex_stars() -> dict[str, object]:
    """Verify the local graph invariants at all 240 possible base vertices."""
    roots = _resolve_roots()
    if len(roots) != ROOT_COUNT:
        raise ArithmeticError("canonical E8 orbit does not contain 240 roots")

    for index, base in enumerate(roots):
        star = build_vertex_star(base)
        if star.common_neighbor_classes != LOCAL_PAIR_CLASS_COUNTS:
            raise ArithmeticError(f"local pair classes differ at base vertex {index}")
        if star.triangles != LOCAL_TRIANGLE_COUNT:
            raise ArithmeticError(f"local triangle count differs at base vertex {index}")
        if set(star.triangles_through_each_vertex) != {
            TRIANGLES_THROUGH_LOCAL_VERTEX
        }:
            raise ArithmeticError(
                f"triangle incidence differs at base vertex {index}"
            )
        if any(row != LOCAL_DISTANCE_DISTRIBUTION
               for row in star.distance_distributions):
            raise ArithmeticError(
                f"local distance distribution differs at base vertex {index}"
            )
        if len(star.unique_zero_common_neighbor_pairs) != 28:
            raise ArithmeticError(
                f"unique-partner relation differs at base vertex {index}"
            )
        partner_counts = [0] * LOCAL_VERTEX_COUNT
        for left, right in star.unique_zero_common_neighbor_pairs:
            partner_counts[left] += 1
            partner_counts[right] += 1
        if set(partner_counts) != {1}:
            raise ArithmeticError(
                f"zero-common-neighbor pairs are not a perfect matching at base {index}"
            )

    total_local_triangles = ROOT_COUNT * LOCAL_TRIANGLE_COUNT
    global_four_cliques = total_local_triangles // 4
    if total_local_triangles % 4:
        raise ArithmeticError("local-to-global four-clique incidence is not integral")
    if global_four_cliques != GLOBAL_FOUR_CLIQUE_COUNT:
        raise ArithmeticError("global four-clique count differs from expected incidence")
    if global_four_cliques * 6 != 6720 * FOUR_CLIQUES_PER_GLOBAL_EDGE:
        raise ArithmeticError("edge-to-four-clique incidence does not balance")

    return {
        "status": "PASS",
        "base_vertices_checked": ROOT_COUNT,
        "local_vertices_per_star": LOCAL_VERTEX_COUNT,
        "local_edges_per_star": LOCAL_EDGE_COUNT,
        "local_degree_sequence": [LOCAL_DEGREE] * LOCAL_VERTEX_COUNT,
        "local_pair_class_counts": LOCAL_PAIR_CLASS_COUNTS,
        "zero_common_neighbor_pairs_form_perfect_matching": True,
        "local_distance_distribution_from_each_vertex": LOCAL_DISTANCE_DISTRIBUTION,
        "local_triangles_per_star": LOCAL_TRIANGLE_COUNT,
        "triangles_through_each_local_vertex": TRIANGLES_THROUGH_LOCAL_VERTEX,
        "global_four_cliques_from_vertex_stars": global_four_cliques,
        "four_cliques_per_global_edge": FOUR_CLIQUES_PER_GLOBAL_EDGE,
        "global_edge_four_clique_incidence_balances": True,
        "weyl_group_enumerated": False,
        "physical_validation_claimed": False,
    }
