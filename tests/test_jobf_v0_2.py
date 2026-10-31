import numpy as np
import pytest

from janus_hydra import (
    V8State, complement, formation_heads, inverse_heads,
    cross_polytope_radius, octadial_weights, golden_angle_phases,
)
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions, base_radius, aggregate_heads


def sample_state():
    return V8State(.8, .7, .75, .25, .65, .6, .72, .55)


def test_v8_state_rejects_out_of_range_and_nonfinite_values():
    with pytest.raises(ValueError):
        V8State(1.1, .7, .75, .25, .65, .6, .72, .55).validate()
    with pytest.raises(ValueError):
        V8State(.8, .7, .75, float("nan"), .65, .6, .72, .55).validate()


def test_complement_is_involution():
    for x in (0.0, .125, .25, .5, .75, .875, 1.0):
        assert complement(complement(x)) == pytest.approx(x)


def test_head_projections_are_finite_and_bounded():
    state = sample_state()
    for scores in (formation_heads(state), inverse_heads(state)):
        assert len(scores) == 5
        assert all(np.isfinite(x) and 0 <= x <= 1 for x in scores.values())


def test_cross_polytope_axis_and_diagonal_radii():
    assert cross_polytope_radius((1, 0, 0, 0, 0, 0, 0, 0)) == pytest.approx(1.0)
    assert cross_polytope_radius((1, 1, 1, 1, 1, 1, 1, 1)) == pytest.approx(1 / np.sqrt(8))


def test_direction_weights_sum_to_one_and_are_sign_symmetric():
    direction = (1., -2., 3., -4., 5., -6., 7., -8.)
    weights = octadial_weights(direction)
    flipped = octadial_weights(tuple(-x for x in direction))
    assert sum(weights) == pytest.approx(1.0)
    assert weights == pytest.approx(flipped)


def test_golden_angle_schedule_has_eight_phases():
    phases = golden_angle_phases()
    assert len(phases) == 8
    assert phases[0] == pytest.approx(0.0)
    assert all(np.isfinite(x) for x in phases)


def test_base_radius_matches_cross_polytope_formula():
    dirs = sphere_directions(128, seed=19)
    assert dirs.shape == (128, 8)
    assert np.allclose(np.linalg.norm(dirs, axis=1), 1.0)
    assert np.allclose(base_radius(dirs), 1.0 / np.abs(dirs).sum(axis=1))


def test_jobf_boundary_is_finite_positive_and_origin_domain_is_not_split():
    model = JanusOctadialBreathingField(dt=.01)
    dirs = sphere_directions(256, seed=23)
    for t in (0.0, .1, .7, 1.3):
        rho, rho0, exponent, diag = model.boundary(dirs, t)
        assert rho.shape == rho0.shape == exponent.shape == (256,)
        assert np.all(np.isfinite(rho))
        assert np.all(rho > 0)
        assert np.all(rho0 > 0)
        assert set(diag["uhfe_heads"]) == set(diag["udfe_heads"])
        assert diag["uhfe_channels"].shape == (8,)
        assert diag["udfe_channels"].shape == (8,)


def test_boundary_rejects_wrong_direction_shape():
    model = JanusOctadialBreathingField()
    with pytest.raises(ValueError):
        model.boundary(np.ones((4, 7)), 0.0)


def test_invalid_timestep_is_rejected():
    for dt in (0, -1, float("nan"), float("inf")):
        with pytest.raises(ValueError):
            JanusOctadialBreathingField(dt=dt)


def test_optional_shape_bias_keeps_boundary_positive():
    model = JanusOctadialBreathingField(shape_bias=0.5)
    rho, *_ = model.boundary(sphere_directions(128), 0.25)
    assert np.all(np.isfinite(rho))
    assert np.all(rho > 0)


def test_aggregate_heads_returns_eight_channels():
    state = sample_state()
    channels = aggregate_heads(formation_heads(state))
    assert channels.shape == (8,)
    assert np.all(np.isfinite(channels))
