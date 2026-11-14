from gosset_global_4cliques import (
    EXPECTED_FOUR_CLIQUES_PER_VERTEX,
    EXPECTED_FOUR_CLIQUE_EDGE_INCIDENCE,
    audit_global_four_cliques,
    audit_local_antipodes,
    enumerate_global_four_cliques,
)


def test_direct_global_four_clique_enumeration_and_edge_incidence():
    report = audit_global_four_cliques()
    assert report["status"] == "PASS"
    assert report["global_four_cliques"] == 241_920
    assert report["edges_with_four_clique_incidence"] == 6_720
    assert report["four_cliques_per_global_edge"] == (
        EXPECTED_FOUR_CLIQUE_EDGE_INCIDENCE
    )
    assert report["four_cliques_per_global_vertex"] == (
        EXPECTED_FOUR_CLIQUES_PER_VERTEX
    )


def test_global_four_cliques_are_unique_sorted_and_mutually_adjacent():
    roots, cliques, edge_incidence, vertex_incidence = (
        enumerate_global_four_cliques()
    )
    assert len(cliques) == len(set(cliques)) == 241_920
    assert all(tuple(sorted(clique)) == clique for clique in cliques)
    assert all(
        len(clique) == 4
        and all(
            sum(x * y for x, y in zip(roots[a], roots[b])) == 4
            for a, b in __import__("itertools").combinations(clique, 2)
        )
        for clique in cliques
    )
    assert set(edge_incidence.values()) == {216}
    assert set(vertex_incidence.values()) == {4032}


def test_exceptional_matching_is_exactly_projected_antipodes():
    report = audit_local_antipodes()
    assert report["status"] == "PASS"
    assert report["antipodal_pairs"] == 28
    assert report["antipode_map_is_involution"] is True
    assert report["matches_zero_common_neighbor_pairs"] is True
