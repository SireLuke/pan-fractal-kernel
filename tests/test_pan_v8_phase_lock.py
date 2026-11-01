import math

import pytest

from pan_v8_phase_lock import (
    AbazithGlyph,
    AcousticFeatures,
    PHI,
    PhaseLockState,
    V8State,
    fermi_hole_occupancy,
    fermi_occupancy,
    golden_hallways,
    hyperoctahedron_vertices,
    rotate_8d_plane,
    wrap_phase,
)


def test_v8_canonical_order_and_finite_validation():
    state = V8State(1, 2, 3, 4, 5, 6, 7, 8)
    assert state.as_tuple() == (1, 2, 3, 4, 5, 6, 7, 8)
    with pytest.raises(ValueError):
        V8State(1, 2, math.nan, 4, 5, 6, 7, 8).as_tuple()


def test_phase_advance_uses_external_monotonic_timestamp():
    state = PhaseLockState(10.0, (0.0,) * 8, (math.pi / 2,) * 8, (0.0,) * 8)
    advanced = state.advance(11.0)
    assert advanced.timestamp == 11.0
    assert all(math.isclose(x, math.pi / 2) for x in advanced.phases)
    with pytest.raises(ValueError):
        advanced.advance(10.5)


def test_phase_error_is_wrapped_and_per_channel():
    state = PhaseLockState(0, (math.pi,) * 8, (0.0,) * 8, (0.0,) * 8)
    assert state.phase_errors(0) == (math.pi,) * 8
    assert wrap_phase(3 * math.pi) == pytest.approx(math.pi)


def test_rotation_is_confined_to_selected_plane_and_preserves_norm():
    vector = (1.0, 0, 0, 0, 0, 0, 0, 0)
    rotated = rotate_8d_plane(vector, 0, 1, math.pi / 2)
    assert rotated[0] == pytest.approx(0.0, abs=1e-12)
    assert rotated[1] == pytest.approx(1.0)
    assert sum(x*x for x in rotated) == pytest.approx(1.0)
    assert rotated[2:] == (0.0,) * 6


def test_cross_polytope_has_16_signed_unit_vertices():
    vertices = hyperoctahedron_vertices()
    assert len(vertices) == 16
    assert len(set(vertices)) == 16
    assert all(sum(x*x for x in v) == 1.0 for v in vertices)


def test_golden_hallways_use_phi_and_negative_reciprocal():
    positive, negative = golden_hallways(1.0)
    assert positive == pytest.approx(PHI)
    assert negative == pytest.approx(-1 / PHI)
    assert positive != pytest.approx(-negative)


def test_fermi_occupancy_and_holes_are_complementary_and_bounded():
    for energy in (-1000.0, -1.0, 0.0, 1.0, 1000.0):
        occupied = fermi_occupancy(energy, 0.0, 1.0)
        hole = fermi_hole_occupancy(energy, 0.0, 1.0)
        assert 0.0 <= occupied <= 1.0
        assert 0.0 <= hole <= 1.0
        assert occupied + hole == pytest.approx(1.0)
    assert fermi_occupancy(-1, 0, 0) == 1
    assert fermi_occupancy(1, 0, 0) == 0
    assert fermi_occupancy(0, 0, 0) == 0.5


def test_fermi_rejects_negative_temperature():
    with pytest.raises(ValueError):
        fermi_occupancy(1, 0, -1)


def test_abazith_glyph_is_metadata_not_an_assumed_frequency_map():
    glyph = AbazithGlyph(
        element_id="AE",
        register=1,
        glyph_id="AE-r1",
        pronunciation="example",
        acoustic_features=AcousticFeatures(fundamental_hz=220.0, duration_seconds=0.4),
    )
    assert glyph.acoustic_features.fundamental_hz == 220.0
    with pytest.raises(ValueError):
        AbazithGlyph("AE", 6, "bad-register")


def test_acoustic_features_reject_negative_measurements():
    with pytest.raises(ValueError):
        AcousticFeatures(fundamental_hz=-1.0)
