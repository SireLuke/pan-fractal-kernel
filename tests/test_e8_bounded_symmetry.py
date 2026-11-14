import pytest

from gosset_421 import E8_ROOTS
from e8_bounded_symmetry import (
    DEFAULT_SEED, E8_SIMPLE_ROOTS_SCALED, EDGE_COUNT, MAX_TRANSITIONS,
    ROOT_COUNT, GossetGraph, TraversalBudget, TraversalBudgetExceeded,
    build_gosset_edges, is_scaled_e8_root, propagate_root_orbit,
    reflect_scaled_root, simple_root_gram_matrix, validate_simple_root_system,
)


def _scaled_existing_roots():
    return tuple(sorted(tuple(int(2 * value) for value in root) for root in E8_ROOTS))


def test_simple_generators_are_exact_e8_roots_with_e8_gram():
    assert len(E8_SIMPLE_ROOTS_SCALED) == 8
    assert validate_simple_root_system()
    gram = simple_root_gram_matrix()
    assert all(gram[i][i] == 8 for i in range(8))
    assert all(gram[i][j] in (0, -4) for i in range(8) for j in range(8) if i != j)
    assert sum(gram[i][j] == -4 for i in range(8) for j in range(i + 1, 8)) == 7


def test_exact_simple_reflection_is_an_involution_and_preserves_roots():
    for generator in E8_SIMPLE_ROOTS_SCALED:
        for root in (DEFAULT_SEED, E8_SIMPLE_ROOTS_SCALED[3], E8_SIMPLE_ROOTS_SCALED[7]):
            reflected = reflect_scaled_root(root, generator)
            assert is_scaled_e8_root(reflected)
            assert reflect_scaled_root(reflected, generator) == root


def test_bounded_orbit_recovers_existing_240_root_set_exactly():
    orbit = propagate_root_orbit()
    assert len(orbit.roots) == ROOT_COUNT == 240
    assert set(orbit.roots) == set(_scaled_existing_roots())
    assert orbit.transitions == MAX_TRANSITIONS == 1920
    assert orbit.max_depth_reached <= 64
    assert len(set(orbit.roots)) == 240


def test_orbit_is_transitive_from_other_seed_roots():
    existing = _scaled_existing_roots()
    for seed in (existing[0], existing[83], existing[-1]):
        assert set(propagate_root_orbit(seed).roots) == set(existing)


def test_every_one_of_240_seeds_generates_the_same_root_orbit():
    reference = set(_scaled_existing_roots())
    depths = []
    total_transitions = 0
    for seed in sorted(reference):
        orbit = propagate_root_orbit(seed)
        assert set(orbit.roots) == reference
        assert orbit.seed == seed
        assert orbit.transitions == MAX_TRANSITIONS
        depths.append(orbit.max_depth_reached)
        total_transitions += orbit.transitions
    assert len(depths) == ROOT_COUNT
    assert total_transitions == ROOT_COUNT * MAX_TRANSITIONS
    assert max(depths) <= 64


def test_root_families_and_exact_norm():
    roots = propagate_root_orbit().roots
    integer_roots = [root for root in roots if all(value in (-2, 0, 2) for value in root)]
    half_integer_roots = [root for root in roots if all(abs(value) == 1 for value in root)]
    assert len(integer_roots) == 112
    assert len(half_integer_roots) == 128
    assert all(sum(value * value for value in root) == 8 for root in roots)
    assert all(sum(value < 0 for value in root) % 2 == 0 for root in half_integer_roots)


def test_gosset_graph_has_6720_edges_and_degree_56():
    orbit = propagate_root_orbit()
    edges = build_gosset_edges(orbit.roots)
    assert len(edges) == EDGE_COUNT == 6720
    degrees = [0] * ROOT_COUNT
    for left, right in edges:
        degrees[left] += 1
        degrees[right] += 1
        assert sum(a * b for a, b in zip(orbit.roots[left], orbit.roots[right])) == 4
    assert set(degrees) == {56}


def test_explicit_implicit_and_cached_modes_agree():
    roots = propagate_root_orbit().roots
    explicit, implicit = GossetGraph("explicit"), GossetGraph("implicit")
    cached = GossetGraph("cached", max_cache_entries=2)
    assert explicit.roots() == implicit.roots() == cached.roots() == roots
    assert explicit.edges() == implicit.edges() == cached.edges()
    for root in roots[:3]:
        expected = explicit.neighbors(root)
        assert implicit.neighbors(root) == expected
        assert cached.neighbors(root) == expected
    assert implicit.cache_info()["retained_root_orbit"] is False
    assert implicit.cache_info()["retained_edge_list"] is False
    assert cached.cache_info()["cached_neighbor_entries"] == 2
    assert explicit.cache_info()["retained_edge_list"] is True


def test_traversal_budgets_reject_expansion_before_exceeding_limits():
    with pytest.raises(TraversalBudgetExceeded, match="node budget"):
        propagate_root_orbit(budget=TraversalBudget(max_nodes=239))
    with pytest.raises(TraversalBudgetExceeded, match="depth budget"):
        propagate_root_orbit(budget=TraversalBudget(max_depth=1))
    with pytest.raises(TraversalBudgetExceeded, match="transition budget"):
        propagate_root_orbit(budget=TraversalBudget(max_transitions=100))


def test_edge_and_cache_budgets_are_enforced():
    orbit = propagate_root_orbit()
    with pytest.raises(TraversalBudgetExceeded, match="edge budget"):
        build_gosset_edges(orbit.roots, max_edges=100)
    with pytest.raises(ValueError, match="max_cache_entries"):
        GossetGraph("cached", max_cache_entries=ROOT_COUNT + 1)


def test_invalid_roots_are_rejected():
    with pytest.raises(ValueError, match="seed"):
        propagate_root_orbit((0, 0, 0, 0, 0, 0, 0, 0))
    with pytest.raises(ValueError, match="240 scaled E8 roots"):
        reflect_scaled_root((0, 0, 0, 0, 0, 0, 0, 0), DEFAULT_SEED)
    assert not is_scaled_e8_root((1, 1, 1, 1, 1, 1, 1, -1))
