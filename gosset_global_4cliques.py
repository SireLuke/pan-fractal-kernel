"""Independent exact enumeration of Gosset global 4-cliques.

The local-star audit derives the expected count by incidence. This module
enumerates each global 4-clique directly from the 240-root adjacency graph
and independently counts its six edge incidences.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations

from e8_bounded_symmetry import ROOT_COUNT, _dot
from gosset_local_star import (
    FOUR_CLIQUES_PER_GLOBAL_EDGE,
    GLOBAL_FOUR_CLIQUE_COUNT,
    LOCAL_VERTEX_COUNT,
    _resolve_roots,
    build_vertex_star,
)

EXPECTED_GOSSET_EDGES = 6720
EXPECTED_FOUR_CLIQUES_PER_VERTEX = 4032
EXPECTED_FOUR_CLIQUE_EDGE_INCIDENCE = 216


def build_global_adjacency():
    """Return sorted root tuple and exact 56-regular adjacency sets."""
    roots = _resolve_roots()
    if len(roots) != ROOT_COUNT:
        raise ArithmeticError("canonical root orbit must contain 240 roots")
    adjacency = []
    for index, root in enumerate(roots):
        neighbors = {
            other_index
            for other_index, other in enumerate(roots)
            if other_index != index and _dot(root, other) == 4
        }
        if len(neighbors) != LOCAL_VERTEX_COUNT:
            raise ArithmeticError(
                f"root {index} has degree {len(neighbors)}; expected 56"
            )
        adjacency.append(neighbors)
    return roots, tuple(adjacency)


def enumerate_global_four_cliques():
    """Enumerate each K4 exactly once using ordered common-neighbor intersections."""
    roots, adjacency = build_global_adjacency()
    cliques = []
    edge_incidence = Counter()
    vertex_incidence = Counter()

    for a in range(ROOT_COUNT):
        for b in sorted(v for v in adjacency[a] if v > a):
            common_ab = adjacency[a].intersection(adjacency[b])
            for c in sorted(v for v in common_ab if v > b):
                common_abc = common_ab.intersection(adjacency[c])
                for d in sorted(v for v in common_abc if v > c):
                    clique = (a, b, c, d)
                    cliques.append(clique)
                    vertex_incidence.update(clique)
                    edge_incidence.update(combinations(clique, 2))

    return roots, tuple(cliques), edge_incidence, vertex_incidence


def audit_global_four_cliques() -> dict[str, object]:
    roots, cliques, edge_incidence, vertex_incidence = (
        enumerate_global_four_cliques()
    )
    if len(cliques) != GLOBAL_FOUR_CLIQUE_COUNT:
        raise ArithmeticError(
            f"direct enumeration found {len(cliques)} K4s; "
            f"expected {GLOBAL_FOUR_CLIQUE_COUNT}"
        )
    if len(edge_incidence) != EXPECTED_GOSSET_EDGES:
        raise ArithmeticError(
            f"K4s touched {len(edge_incidence)} edges; "
            f"expected {EXPECTED_GOSSET_EDGES}"
        )
    if set(edge_incidence.values()) != {EXPECTED_FOUR_CLIQUE_EDGE_INCIDENCE}:
        raise ArithmeticError("not every global edge has exactly 216 K4 incidences")
    if set(vertex_incidence.values()) != {EXPECTED_FOUR_CLIQUES_PER_VERTEX}:
        raise ArithmeticError("not every global vertex belongs to exactly 4,032 K4s")

    # Independent local-to-global comparison: each K4 containing v corresponds
    # to a triangle in the induced 56-vertex star at v.
    local_triangle_counts = set()
    for root in roots:
        star = build_vertex_star(root)
        local_triangle_counts.add(star.triangles)
    if local_triangle_counts != {EXPECTED_FOUR_CLIQUES_PER_VERTEX}:
        raise ArithmeticError("direct K4 vertex incidence disagrees with local stars")

    return {
        "status": "PASS",
        "enumeration": "direct ordered common-neighbor intersections",
        "global_vertices": ROOT_COUNT,
        "global_edges": EXPECTED_GOSSET_EDGES,
        "global_four_cliques": len(cliques),
        "edges_with_four_clique_incidence": len(edge_incidence),
        "four_cliques_per_global_edge": EXPECTED_FOUR_CLIQUE_EDGE_INCIDENCE,
        "four_cliques_per_global_vertex": EXPECTED_FOUR_CLIQUES_PER_VERTEX,
        "local_star_cross_check": "PASS for all 240 base vertices",
        "unique_cliques": True,
        "weyl_group_enumerated": False,
        "physical_validation_claimed": False,
    }


def audit_local_antipodes(base_index: int = 0) -> dict[str, object]:
    """Check the 28 matching pairs are antipodes in the projected vertex figure."""
    roots = _resolve_roots()
    if not 0 <= base_index < len(roots):
        raise ValueError("base_index must identify one of the 240 roots")
    base = roots[base_index]
    star = build_vertex_star(base)
    index_by_root = {root: i for i, root in enumerate(star.vertices)}
    partners = {}
    for index, vertex in enumerate(star.vertices):
        # In the hyperplane orthogonal to base, projection is vertex - base/2.
        # Its antipode is base - vertex, still a root adjacent to base.
        partner_root = tuple(x - y for x, y in zip(base, vertex))
        if partner_root not in index_by_root:
            raise ArithmeticError("projected antipode is not in the local star")
        partner = index_by_root[partner_root]
        if partner == index or index_by_root.get(
            tuple(x - y for x, y in zip(base, partner_root))
        ) != index:
            raise ArithmeticError("projected antipode map is not an involution")
        if star.common_neighbor_count(index, partner) != 0:
            raise ArithmeticError("antipodal pair unexpectedly has common neighbors")
        partners[index] = partner

    pairs = {tuple(sorted((i, j))) for i, j in partners.items()}
    if len(pairs) != 28 or any(partners[partners[i]] != i for i in partners):
        raise ArithmeticError("local antipodes do not form 28 disjoint pairs")
    if pairs != set(star.unique_zero_common_neighbor_pairs):
        raise ArithmeticError("zero-common-neighbor matching differs from antipodes")
    return {
        "status": "PASS",
        "base_root_index": base_index,
        "local_vertices": LOCAL_VERTEX_COUNT,
        "antipodal_pairs": len(pairs),
        "antipode_map_is_involution": True,
        "matches_zero_common_neighbor_pairs": True,
        "interpretation": (
            "The 56 projected vertex-figure points occur in 28 antipodal pairs."
        ),
    }
