import pytest

from e8_bounded_symmetry import propagate_root_orbit
from gosset_local_star import (
    FOUR_CLIQUES_PER_GLOBAL_EDGE,
    GLOBAL_FOUR_CLIQUE_COUNT,
    LOCAL_DEGREE,
    LOCAL_DISTANCE_DISTRIBUTION,
    LOCAL_EDGE_COUNT,
    LOCAL_PAIR_CLASS_COUNTS,
    LOCAL_TRIANGLE_COUNT,
    LOCAL_VERTEX_COUNT,
    TRIANGLES_THROUGH_LOCAL_VERTEX,
    audit_all_vertex_stars,
    build_vertex_star,
)


def test_one_vertex_star_has_expected_local_graph_invariants():
    base = propagate_root_orbit().roots[0]
    star = build_vertex_star(base)
    assert len(star.vertices) == LOCAL_VERTEX_COUNT == 56
    assert len(star.edges) == LOCAL_EDGE_COUNT == 756
    assert set(star.degree_sequence) == {LOCAL_DEGREE}
    assert star.common_neighbor_classes == LOCAL_PAIR_CLASS_COUNTS
    assert star.triangles == LOCAL_TRIANGLE_COUNT == 4032
    assert set(star.triangles_through_each_vertex) == {
        TRIANGLES_THROUGH_LOCAL_VERTEX
    }
    assert all(row == LOCAL_DISTANCE_DISTRIBUTION
               for row in star.distance_distributions)


def test_exceptional_zero_common_neighbor_pairs_are_a_perfect_matching():
    star = build_vertex_star(propagate_root_orbit().roots[0])
    pairs = star.unique_zero_common_neighbor_pairs
    assert len(pairs) == 28
    partner_counts = [0] * LOCAL_VERTEX_COUNT
    for left, right in pairs:
        partner_counts[left] += 1
        partner_counts[right] += 1
        assert left < right
        assert right not in star.adjacency[left]
    assert partner_counts == [1] * LOCAL_VERTEX_COUNT


def test_invalid_base_root_is_rejected():
    with pytest.raises(ValueError, match="base_root"):
        build_vertex_star((0, 0, 0, 0, 0, 0, 0, 0))


def test_all_240_vertex_stars_and_global_incidence_balance():
    report = audit_all_vertex_stars()
    assert report["status"] == "PASS"
    assert report["base_vertices_checked"] == 240
    assert report["global_four_cliques_from_vertex_stars"] == (
        GLOBAL_FOUR_CLIQUE_COUNT
    )
    assert report["four_cliques_per_global_edge"] == (
        FOUR_CLIQUES_PER_GLOBAL_EDGE
    )
    assert report["global_edge_four_clique_incidence_balances"] is True
