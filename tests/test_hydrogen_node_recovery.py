import math

import numpy as np
import pytest

import hydrogen_node_recovery as N
import hydrogen_shell_modes as H


def test_angular_domain_counts():
    assert [N.angular_domain_count(l, 0) for l in (0, 1, 2)] == [1, 2, 3]
    assert N.angular_domain_count(1, 1) == 2 and N.angular_domain_count(1, -1) == 2   # p_x, p_y
    assert N.angular_domain_count(2, 2) == 4 and N.angular_domain_count(2, -2) == 4   # d_x2-y2, d_xy
    assert N.angular_domain_count(2, 1) == 4 and N.angular_domain_count(2, -1) == 4   # d_xz, d_yz
    with pytest.raises(ValueError):
        N.angular_domain_count(1, 2)


def test_expected_domains_and_ambiguous_band():
    assert N.expected_domains(1, 0, 0, 10.0) == 1
    assert N.expected_domains(2, 0, 0, 10.0) == 2          # node at 2 < 0.8 r_max
    assert N.expected_domains(2, 0, 0, 1.5) == 1           # node beyond the cloud
    assert N.expected_domains(2, 0, 0, 2.2) is None        # node at 0.91 r_max: ambiguous
    assert N.expected_domains(3, 0, 0, 30.0) == 3
    assert N.expected_domains(3, 2, 0, 30.0) == 3
    assert N.expected_domains(3, 1, 0, 30.0) == 4          # (1 radial node) x 2
    with pytest.raises(ValueError):
        N.expected_domains(2, 0, 0, 0.0)


def _ball(r_max, n=40_000, seed=1):
    rng = np.random.default_rng(seed)
    d = rng.normal(size=(n, 3))
    d /= np.linalg.norm(d, axis=1)[:, None]
    return d * (r_max * rng.random(n) ** (1 / 3))[:, None]


@pytest.mark.parametrize("state,r_max", [((1, 0, 0), 5.0), ((2, 0, 0), 10.0), ((2, 1, 0), 12.0),
                                          ((2, 1, 1), 12.0), ((3, 2, 0), 24.0), ((3, 2, 2), 24.0)])
def test_dense_ball_recovers_exact_domain_counts(state, r_max):
    """Radius chosen so the 5% amplitude region holds enough points (components below 0.5% N are dropped)."""
    pts = _ball(r_max)
    g = N.knn_graph(pts, 10)
    exp = N.expected_domains(*state, r_max=r_max)
    assert exp is not None
    assert N.count_domains(H.hydrogen_psi(*state, pts), g) == exp


def test_validation():
    pts = _ball(5.0, n=50)
    with pytest.raises(ValueError):
        N.knn_graph(pts, 0)
    with pytest.raises(ValueError):
        N.knn_graph(pts, 50)
    with pytest.raises(ValueError):
        N.count_domains(np.zeros(50), N.knn_graph(pts, 5))
    with pytest.raises(ValueError):
        N.radial_node_radii(5, 0)
    with pytest.raises(ValueError):
        N.evaluate_subsampled(2, "lattice_unit", n_sub=5, trials=1)


def test_recorded_primary_outcome_is_not_a_pass():
    """Regression pin: the pre-registered criterion is not met (E8 is not above the shuffled null)."""
    for rule, n in (("lattice_unit", 2), ("mean_radius", 3)):
        r = N.evaluate(n, rule, null_trials=10)
        assert r["passes"] is False
    assert N.evaluate(2, "lattice_unit", null_trials=5)["e8"]["recovery_rate"] == 1.0
