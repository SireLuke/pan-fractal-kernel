import math

import pytest

from gosset_421 import (
    E8_ROOTS,
    EDGE_COUNT,
    NEAREST_NEIGHBORS,
    ROOT_COUNT,
    antipode,
    edge_count,
    geometry_summary,
    inner_product_distribution,
    is_e8_root,
    neighbors,
    radial_boundary,
    reflection_preserves_root_system,
    squared_norm,
    support_value,
    weyl_reflection,
)


def test_e8_root_count_uniqueness_and_norm():
    assert len(E8_ROOTS) == ROOT_COUNT == 240
    assert len(set(E8_ROOTS)) == 240
    assert all(math.isclose(squared_norm(root), 2.0) for root in E8_ROOTS)


def test_root_families_have_expected_split():
    integral = [r for r in E8_ROOTS if all(x in (-1.0, 0.0, 1.0) for x in r)]
    half_integral = [r for r in E8_ROOTS if all(abs(x) == 0.5 for x in r)]
    assert len(integral) == 112
    assert len(half_integral) == 128
    assert all(sum(x < 0 for x in r) % 2 == 0 for r in half_integral)


def test_antipodal_pairing_is_exact():
    root_set = set(E8_ROOTS)
    assert all(tuple(-x for x in root) in root_set for root in E8_ROOTS)
    assert all(antipode(root) in root_set for root in E8_ROOTS)


def test_inner_products_have_e8_values_and_distribution():
    distribution = inner_product_distribution()
    assert set(distribution) == {-2.0, -1.0, 0.0, 1.0, 2.0}
    assert distribution[-2.0] == 1
    assert distribution[-1.0] == 56
    assert distribution[0.0] == 126
    assert distribution[1.0] == 56
    assert distribution[2.0] == 1


def test_gosset_vertex_degree_and_edge_count():
    assert len(neighbors(E8_ROOTS[0])) == NEAREST_NEIGHBORS == 56
    assert edge_count() == EDGE_COUNT == 6720


def test_weyl_reflections_preserve_root_set_and_norm():
    alpha = E8_ROOTS[0]
    assert reflection_preserves_root_system(alpha)
    for root in E8_ROOTS[::17]:
        reflected = weyl_reflection(root, alpha)
        assert is_e8_root(reflected)
        assert squared_norm(reflected) == pytest.approx(2.0)


def test_reflection_is_an_involution():
    alpha = E8_ROOTS[31]
    x = (0.1, -0.2, 0.3, -0.4, 0.5, -0.6, 0.7, -0.8)
    twice = weyl_reflection(weyl_reflection(x, alpha), alpha)
    assert twice == pytest.approx(x)


def test_support_function_is_positive_and_homogeneous():
    u = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    assert support_value(u) == pytest.approx(1.0)
    assert support_value(tuple(3.0 * x for x in u)) == pytest.approx(3.0)


def test_radial_boundary_lp_if_scipy_available():
    pytest.importorskip("scipy")
    # E8 roots have norm sqrt(2), and symmetry makes coordinate directions simple.
    axis = (1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0)
    diagonal = (1.0,) * 8
    assert radial_boundary(axis) == pytest.approx(1.0, abs=1e-8)
    assert radial_boundary(diagonal) == pytest.approx(math.sqrt(2.0), abs=1e-8)


def test_geometry_summary_contract():
    summary = geometry_summary()
    assert summary["name"] == "Gosset 4_21"
    assert summary["vertices"] == 240
    assert summary["nearest_neighbors_per_vertex"] == 56
    assert summary["edges"] == 6720
