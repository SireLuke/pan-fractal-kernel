"""Cross-subsystem contracts for the PAN V8 validation harness.

These tests validate software interfaces and numerical invariants only.
They do not establish new physical laws or validate proxy calibrations.
"""
import numpy as np
import pytest

from geometry_adapter import CrossPolytopeAdapter, Gosset421Adapter
from gosset_421 import E8_ROOTS, ROOT_COUNT
from gosset_projection import project_gosset_chain
from hydra_semantic_reader import read_semantics
from janus_hydra import V8State
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions
from naht_su2 import SU2
from v8_ingest_common import robust01, run_v8_jobf


@pytest.fixture
def canonical_state():
    return V8State(
        h=0.8, R=0.7, u=0.75, d=0.25,
        tau=0.65, chi=0.6, s=0.72, f=0.55,
    )


def test_canonical_v8_state_survives_semantic_to_jobf_pipeline(canonical_state):
    frame = read_semantics(canonical_state)
    model = JanusOctadialBreathingField(dt=0.01)
    model.base = np.asarray([getattr(canonical_state, key)
                             for key in ("h", "R", "u", "d", "tau", "chi", "s", "f")])
    model.state_amp = np.zeros(8, dtype=float)
    model.h_base = frame.uhfe_channels.copy()
    model.d_base = frame.udfe_channels.copy()
    directions = sphere_directions(100, seed=2026)

    radius, baseline, exponent, diagnostics = model.boundary(directions, 0.25)

    assert frame.coordinate_order == ("h", "R", "u", "d", "tau", "chi", "s", "f")
    assert frame.uhfe_channels.shape == frame.udfe_channels.shape == (8,)
    assert radius.shape == baseline.shape == exponent.shape == (100,)
    assert np.all(np.isfinite(radius)) and np.all(radius > 0.0)
    assert diagnostics["geometry"] == Gosset421Adapter.name
    assert np.allclose(diagnostics["uhfe_channels"], frame.uhfe_channels)
    assert np.allclose(diagnostics["udfe_channels"], frame.udfe_channels)


def test_jobf_boundary_is_fixed_to_gosset_and_h8_is_comparison_only(canonical_state):
    frame = read_semantics(canonical_state)
    model = JanusOctadialBreathingField(dt=0.01)
    base = np.asarray([getattr(canonical_state, key)
                       for key in ("h", "R", "u", "d", "tau", "chi", "s", "f")])
    model.base = base.copy()
    model.state_amp = np.zeros(8, dtype=float)
    model.h_base = frame.uhfe_channels.copy()
    model.d_base = frame.udfe_channels.copy()
    directions = sphere_directions(64, seed=81)

    gosset_radius, _, _, diagnostics = model.boundary(directions, 0.4)
    h8_comparison_radius = CrossPolytopeAdapter().radial_boundary_many(directions)

    assert isinstance(model.geometry, Gosset421Adapter)
    assert diagnostics["geometry"] == Gosset421Adapter.name
    assert not np.allclose(gosset_radius, h8_comparison_radius)
    assert np.allclose(diagnostics["uhfe_channels"], frame.uhfe_channels)
    assert np.allclose(diagnostics["udfe_channels"], frame.udfe_channels)
    assert diagnostics["state"] == frame.state

    with pytest.raises(TypeError):
        JanusOctadialBreathingField(dt=0.01, geometry="cross_polytope")


def test_gosset_projection_ladder_preserves_canonical_root_identity():
    chain = project_gosset_chain()
    assert len(E8_ROOTS) == ROOT_COUNT == 240
    assert set(chain) == {8, 4, 3, 2}
    for dimension in (8, 4, 3, 2):
        result = chain[dimension]
        source_dimension = {8: 8, 4: 8, 3: 4, 2: 3}[dimension]
        assert result.source_points.shape == (240, source_dimension)
        assert result.projected_points.shape == (240, dimension)
        assert np.array_equal(result.source_indices, np.arange(240))
    assert chain[8].is_lossless
    assert all(not chain[d].is_lossless for d in (4, 3, 2))


def test_ingestion_bridge_is_reproducible_and_emits_positive_jobf_metrics(canonical_state):
    vector = canonical_state.__dict__
    first = run_v8_jobf(vector, steps=3, samples=100, seed=17)
    second = run_v8_jobf(vector, steps=3, samples=100, seed=17)

    assert first == second
    assert first["jobf_boundary_positive"] is True
    for key in (
        "jobf_radius_initial", "jobf_radius_final",
        "jobf_radius_min", "jobf_radius_max",
        "jobf_interference_mean_abs",
    ):
        assert np.isfinite(first[key])
    assert first["jobf_radius_min"] > 0.0


def test_robust_ingestion_scaler_handles_constants_and_missing_values():
    scaled = robust01(np.array([2.0, 2.0, np.nan, 2.0]))
    assert scaled == pytest.approx(np.array([0.5, 0.5, 0.5, 0.5]))

    varied = robust01(np.array([1.0, 2.0, 3.0, 4.0, 5.0]))
    assert np.all(np.isfinite(varied))
    assert np.all((0.0 <= varied) & (varied <= 1.0))


def test_su2_transport_composition_matches_matrix_representation():
    a = SU2.from_axis_angle((1.0, 0.0, 0.0), 0.73)
    b = SU2.from_axis_angle((0.0, 0.0, 1.0), -1.17)
    composed = (a @ b).to_matrix()
    left, right = a.to_matrix(), b.to_matrix()
    product = tuple(
        tuple(sum(left[i][k] * right[k][j] for k in range(2)) for j in range(2))
        for i in range(2)
    )
    for i in range(2):
        for j in range(2):
            assert composed[i][j] == pytest.approx(product[i][j])
