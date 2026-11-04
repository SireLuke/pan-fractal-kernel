import math

import pytest

from naht_topology import compare_networks, triangle_network_lengths
from naht_su2 import SU2


def test_equilateral_triangle_has_120_degree_steiner_junction():
    points = ((0.0, 0.0), (2.0, 0.0), (1.0, math.sqrt(3.0)))
    result = triangle_network_lengths(points)
    assert result["steiner_regime"] == "steiner_120"
    assert result["y_length"] == pytest.approx(2.0 * math.sqrt(3.0))
    assert result["delta_length"] == pytest.approx(3.0)


def test_triangle_with_angle_over_120_uses_vertex_solution():
    points = ((0.0, 0.0), (2.0, 0.0), (0.2, 0.1))
    result = triangle_network_lengths(points)
    assert result["steiner_regime"] == "vertex"
    assert result["y_length"] == pytest.approx(
        math.dist(points[2], points[0]) + math.dist(points[2], points[1])
    )


def test_three_dimensional_triangle_supported():
    result = triangle_network_lengths(((0, 0, 0), (2, 0, 0), (1, 1, 0)))
    assert result["y_length"] > 0
    assert result["delta_length"] > 0


def test_invalid_triangle_inputs_rejected():
    with pytest.raises(ValueError):
        triangle_network_lengths(((0, 0), (1, 0)))
    with pytest.raises(ValueError):
        triangle_network_lengths(((0, 0), (1, 0, 0), (0, 1)))


def test_network_comparison_does_not_force_a_distance_threshold():
    result = compare_networks(((0, 0), (2, 0), (1, math.sqrt(3))))
    assert result["shorter_geometric_objective"] in ("Y", "Delta")
    assert result["steiner_regime"] == "steiner_120"


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
    assert a*d - b*c == pytest.approx(1.0 + 0j)


def test_su2_requires_unit_quaternion():
    with pytest.raises(ValueError):
        SU2(2, 0, 0, 0)
