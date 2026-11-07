import math

import pytest

from naht_topology import compare_networks, triangle_network_lengths
from naht_su2 import SU2


def test_equilateral_triangle_has_120_degree_steiner_junction():
    points = ((0.0, 0.0), (2.0, 0.0), (1.0, math.sqrt(3.0)))
    result = triangle_network_lengths(points)
    assert result["steiner_regime"] == "steiner_120"
    assert result["y_length"] == pytest.approx(2.0 * math.sqrt(3.0))
    assert result["delta_half_perimeter"] == pytest.approx(3.0)


def test_triangle_with_angle_over_120_uses_vertex_solution():
    points = ((0.0, 0.0), (2.0, 0.0), (0.2, 0.1))
    result = triangle_network_lengths(points)
    assert result["steiner_regime"] == "vertex"
    assert result["y_length"] == pytest.approx(
        math.dist(points[2], points[0]) + math.dist(points[2], points[1])
    )


def test_coincident_pair_uses_single_segment():
    result = triangle_network_lengths(((0, 0), (0, 0), (2, 0)))
    assert result["steiner_regime"] == "coincident_pair"
    assert result["y_length"] == pytest.approx(2.0)
    assert result["delta_half_perimeter"] == pytest.approx(2.0)


def test_three_dimensional_triangle_supported():
    result = triangle_network_lengths(((0, 0, 0), (2, 0, 0), (1, 1, 0)))
    assert result["y_length"] > 0
    assert result["delta_half_perimeter"] > 0


def test_invalid_triangle_inputs_rejected():
    with pytest.raises(ValueError):
        triangle_network_lengths(((0, 0), (1, 0)))
    with pytest.raises(ValueError):
        triangle_network_lengths(((0, 0), (1, 0, 0), (0, 1)))


def test_network_comparison_returns_geometry_without_physical_winner():
    result = compare_networks(((0, 0), (2, 0), (1, math.sqrt(3))))
    assert "y_length" in result and "delta_half_perimeter" in result
    assert "shorter_geometric_objective" not in result


def test_su2_identity_and_inverse():
    u = SU2.from_axis_angle((0, 0, 1), 0.7)
    identity = u @ u.inverse()
    assert identity.w == pytest.approx(1.0)
    assert (identity.x, identity.y, identity.z) == pytest.approx((0, 0, 0))
    assert SU2.identity().trace() == pytest.approx(2.0)


def test_su2_path_order_is_noncommutative():
    x = SU2.from_axis_angle((1, 0, 0), 0.8)
    z = SU2.from_axis_angle((0, 0, 1), 1.1)
    x_then_z = x @ z
    z_then_x = z @ x
    assert (x_then_z.x, x_then_z.y, x_then_z.z) != pytest.approx(
        (z_then_x.x, z_then_x.y, z_then_x.z)
    )


def test_su2_matrix_is_unitary_and_determinant_one():
    u = SU2.from_axis_angle((1, 2, 3), 0.9)
    m = u.to_matrix()
    a, b = m[0]
    c, d = m[1]
    assert a.conjugate()*a + c.conjugate()*c == pytest.approx(1.0)
    assert b.conjugate()*b + d.conjugate()*d == pytest.approx(1.0)
    assert a.conjugate()*b + c.conjugate()*d == pytest.approx(0j)
    assert a*d - b*c == pytest.approx(1.0 + 0j)


def test_su2_requires_unit_quaternion():
    with pytest.raises(ValueError):
        SU2(2, 0, 0, 0)



def test_su2_matrix_representation_respects_ordered_composition():
    x = SU2.from_axis_angle((1, 0, 0), 0.8).to_matrix()
    z = SU2.from_axis_angle((0, 0, 1), 1.1).to_matrix()
    composed = (SU2.from_axis_angle((1, 0, 0), 0.8)
                @ SU2.from_axis_angle((0, 0, 1), 1.1)).to_matrix()
    product = tuple(
        tuple(sum(x[i][k] * z[k][j] for k in range(2)) for j in range(2))
        for i in range(2)
    )
    for i in range(2):
        for j in range(2):
            assert composed[i][j] == pytest.approx(product[i][j])
