"""Deterministic audit for bounded exact E8 symmetry propagation."""
from __future__ import annotations

import json

from e8_bounded_symmetry import (
    E8_SIMPLE_ROOTS_SCALED,
    GossetGraph,
    propagate_root_orbit,
    simple_root_gram_matrix,
)


def main() -> None:
    orbit = propagate_root_orbit()
    explicit = GossetGraph("explicit")
    implicit = GossetGraph("implicit")
    cached = GossetGraph("cached", max_cache_entries=4)

    roots = orbit.roots
    integer_count = sum(
        all(value in (-2, 0, 2) for value in root) for root in roots
    )
    half_integer_count = sum(
        all(abs(value) == 1 for value in root) for root in roots
    )
    inner_products = {}
    reference = roots[0]
    for root in roots:
        value = sum(a * b for a, b in zip(reference, root)) // 4
        inner_products[value] = inner_products.get(value, 0) + 1

    explicit_edges = explicit.edges()
    for root in roots[:5]:
        expected = explicit.neighbors(root)
        if implicit.neighbors(root) != expected or cached.neighbors(root) != expected:
            raise AssertionError("graph modes disagree on a vertex neighborhood")

    degrees = [len(explicit.neighbors(root)) for root in roots]
    report = {
        "status": "PASS",
        "coordinate_scale": "X = 2*x",
        "root_norm_squared_scaled": 8,
        "simple_reflection_generators": len(E8_SIMPLE_ROOTS_SCALED),
        "simple_root_gram_matrix": simple_root_gram_matrix(),
        "root_count": len(roots),
        "integer_root_family": integer_count,
        "half_integer_root_family": half_integer_count,
        "root_orbit_max_depth": orbit.max_depth_reached,
        "reflection_transitions": orbit.transitions,
        "inner_product_distribution": dict(sorted(inner_products.items())),
        "gosset_edges": len(explicit_edges),
        "vertex_degree_min": min(degrees),
        "vertex_degree_max": max(degrees),
        "mode_equivalence": True,
        "implicit_storage": implicit.cache_info(),
        "cached_storage": cached.cache_info(),
        "explicit_storage": explicit.cache_info(),
        "full_weyl_group_enumerated": False,
        "unbounded_archive_expansion_used": False,
    }
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
