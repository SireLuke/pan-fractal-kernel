import numpy as np
import pytest

from janus_hydra import (
    V8State, complement, formation_heads, inverse_heads, paired_heads,
    cross_polytope_radius, octadial_weights, golden_angle_phases,
)
from hydra_semantic_reader import read_semantics, coerce_v8_state, project_heads, INVERSE_NAMES, HEAD_SUPPORT
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions, base_radius, aggregate_heads
from geometry_adapter import Gosset421Adapter, CrossPolytopeAdapter


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


def test_janus_head_pairs_preserve_distinct_semantic_names():
    state = sample_state()
    forward, inverse, pairs = formation_heads(state), inverse_heads(state), paired_heads(state)
    assert set(forward) == set(pairs)
    assert len(inverse) == len(pairs) == 5
    for formation_name, inverse_name in INVERSE_NAMES.items():
        assert pairs[formation_name]["formation"] == pytest.approx(forward[formation_name])
        assert pairs[formation_name]["inverse"] == pytest.approx(inverse[inverse_name])
        assert inverse_name != formation_name


def test_semantic_reader_is_the_canonical_v8_gateway():
    state = sample_state()
    frame = read_semantics(state)
    mapping = {key: getattr(state, key) for key in ("h", "R", "u", "d", "tau", "chi", "s", "f")}
    assert read_semantics(mapping).state == state
    assert read_semantics(tuple(mapping.values())).state == state
    assert frame.coordinate_order == ("h", "R", "u", "d", "tau", "chi", "s", "f")
    assert frame.reader == "janus_hydra_semantic_reader"
    assert frame.uhfe_channels.shape == frame.udfe_channels.shape == (8,)
    assert np.all(np.isfinite(frame.uhfe_channels))
    assert np.all(np.isfinite(frame.udfe_channels))


def test_semantic_reader_accepts_provisional_t_alias_only_when_tau_absent():
    mapping = {key: getattr(sample_state(), key) for key in ("h", "R", "u", "d", "tau", "chi", "s", "f")}
    mapping["T"] = mapping.pop("tau")
    assert read_semantics(mapping).state.tau == pytest.approx(.65)
    mapping["tau"] = .65
    with pytest.raises(ValueError):
        read_semantics(mapping)


def test_semantic_reader_rejects_incomplete_or_out_of_range_inputs():
    with pytest.raises(ValueError):
        read_semantics({"h": .5})
    with pytest.raises(ValueError):
        coerce_v8_state((.5, .5, .5, .5, .5, .5, .5, 1.2))


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
        assert len(diag["uhfe_heads"]) == len(diag["udfe_heads"]) == 5
        assert set(diag["uhfe_heads"]) == set(HEAD_SUPPORT)
        assert set(diag["udfe_heads"]) == set(INVERSE_NAMES.values())
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
    channels = aggregate_heads(formation_heads(sample_state()))
    assert channels.shape == (8,)
    assert np.all(np.isfinite(channels))


def test_gosset_adapter_matches_symmetric_reference_radii():
    adapter = Gosset421Adapter()
    axis = np.array([[1., 0., 0., 0., 0., 0., 0., 0.]])
    diagonal = np.ones((1, 8))
    assert adapter.radial_boundary_many(axis)[0] == pytest.approx(1.0, abs=1e-7)
    assert adapter.radial_boundary_many(diagonal)[0] == pytest.approx(np.sqrt(2.0), abs=1e-7)


def test_gosset_adapter_is_scale_and_sign_invariant():
    adapter = Gosset421Adapter()
    dirs = sphere_directions(12, seed=41)
    r1 = adapter.radial_boundary_many(dirs)
    r2 = adapter.radial_boundary_many(-3.0 * dirs)
    assert r1 == pytest.approx(r2, abs=1e-8)


def test_legacy_cross_polytope_adapter_is_explicit_and_unchanged():
    adapter = CrossPolytopeAdapter()
    dirs = sphere_directions(24, seed=7)
    assert adapter.name == "cross_polytope_h8"
    assert adapter.radial_boundary_many(dirs) == pytest.approx(1.0 / np.abs(dirs).sum(axis=1))


def test_jobf_is_locked_to_gosset_as_its_production_boundary():
    model = JanusOctadialBreathingField()
    assert isinstance(model.geometry, Gosset421Adapter)
    assert model.geometry.name == "gosset_4_21_e8_root_polytope"
    dirs = sphere_directions(16, seed=11)
    _, _, _, diag = model.boundary(dirs, .2)
    assert diag["geometry"] == "gosset_4_21_e8_root_polytope"

    # H8 remains a standalone comparison adapter, not a JOBF boundary option.
    assert CrossPolytopeAdapter().name == "cross_polytope_h8"
    with pytest.raises(TypeError):
        JanusOctadialBreathingField(geometry="cross_polytope")



def test_gosset_facet_radial_matches_reference_linear_program():
    from gosset_421 import radial_boundary
    pytest.importorskip("scipy")
    adapter = Gosset421Adapter()
    dirs = sphere_directions(3, seed=123)
    fast = adapter.radial_boundary_many(dirs)
    reference = np.array([radial_boundary(row) for row in dirs])
    assert fast == pytest.approx(reference, abs=1e-7)


def test_geometry_adapters_reject_zero_and_nonfinite_directions():
    adapter = Gosset421Adapter()
    with pytest.raises(ValueError):
        adapter.radial_boundary_many(np.zeros((1, 8)))
    invalid = np.ones((1, 8))
    invalid[0, 0] = np.nan
    with pytest.raises(ValueError):
        adapter.radial_boundary_many(invalid)


def test_jobf_caches_base_geometry_for_repeated_direction_samples():
    model = JanusOctadialBreathingField()
    calls = 0
    original = model.geometry.radial_boundary_many

    def counted(directions):
        nonlocal calls
        calls += 1
        return original(directions)

    model.geometry.radial_boundary_many = counted
    dirs = sphere_directions(32, seed=5)
    model.boundary(dirs, 0.0)
    model.boundary(dirs, 0.1)
    assert calls == 1
    model.boundary(dirs.copy(), 0.2)
    assert calls == 1
