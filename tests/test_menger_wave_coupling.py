import numpy as np
import pytest

from menger_wave_coupling import (
    apply_occupancy_coupling,
    menger_occupancy_mask,
    menger_wave_coupling,
)


def plane_wave(side):
    axis = np.arange(side, dtype=float)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    return np.exp(1j * (0.21 * x + 0.13 * y - 0.17 * z))


def gaussian_wavepacket(side):
    axis = np.linspace(-1.0, 1.0, side)
    x, y, z = np.meshgrid(axis, axis, axis, indexing="ij")
    envelope = np.exp(-4.0 * (x * x + y * y + z * z))
    phase = np.exp(1j * (2.0 * x - 0.7 * y + 0.4 * z))
    return envelope * phase


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_menger_mask_has_exact_cell_count_and_shape(level):
    mask = menger_occupancy_mask(level)
    assert mask.shape == (3**level,) * 3
    assert int(mask.sum()) == 20**level
    assert mask.dtype == np.bool_


def test_zero_coupling_is_exact_identity():
    mask = menger_occupancy_mask(2)
    psi = plane_wave(9)
    result = apply_occupancy_coupling(psi, mask, opacity=0.0, phase_shift=0.0)
    assert np.array_equal(result.output, psi)
    assert result.metrics["power_transmission_ratio"] == pytest.approx(1.0)


def test_phase_only_coupling_preserves_power_and_changes_complex_field():
    mask = menger_occupancy_mask(2)
    psi = plane_wave(9)
    result = apply_occupancy_coupling(psi, mask, opacity=0.0, phase_shift=0.7)
    assert np.sum(np.abs(result.output) ** 2) == pytest.approx(np.sum(np.abs(psi) ** 2))
    assert not np.allclose(result.output, psi)
    assert np.allclose(np.abs(result.transmission), 1.0)


@pytest.mark.parametrize("field_factory", [plane_wave, gaussian_wavepacket])
def test_attenuation_matches_occupancy_weighted_power_identity(field_factory):
    psi = field_factory(27)
    result = menger_wave_coupling(psi, level=3, opacity=0.3, phase_shift=0.4)
    assert result.metrics["power_transmission_ratio"] == pytest.approx(
        result.metrics["predicted_power_transmission_ratio"], abs=1e-12
    )
    assert result.metrics["power_transmission_ratio"] <= 1.0
    assert result.metrics["max_transmission_amplitude"] <= 1.0


def test_void_cells_transmit_unchanged_and_retained_cells_attenuate():
    mask = menger_occupancy_mask(1)
    psi = np.ones(mask.shape, dtype=np.complex128)
    result = apply_occupancy_coupling(psi, mask, opacity=0.25, phase_shift=0.0)
    assert np.all(result.output[~mask] == 1.0)
    assert np.all(result.output[mask] == 0.75)


def test_equal_occupancy_shuffled_mask_is_a_distinct_randomized_control():
    rng = np.random.default_rng(20261116)
    mask = menger_occupancy_mask(2)
    shuffled = rng.permutation(mask.ravel()).reshape(mask.shape)
    assert int(shuffled.sum()) == int(mask.sum())
    psi = gaussian_wavepacket(9)
    structured = apply_occupancy_coupling(psi, mask, opacity=0.35)
    randomized = apply_occupancy_coupling(psi, shuffled, opacity=0.35)
    assert structured.metrics["geometry_occupancy_fraction"] == pytest.approx(
        randomized.metrics["geometry_occupancy_fraction"]
    )
    assert not np.allclose(structured.output, randomized.output)


def test_input_validation():
    mask = menger_occupancy_mask(1)
    psi = np.ones(mask.shape, dtype=np.complex128)
    with pytest.raises(ValueError, match="shape"):
        apply_occupancy_coupling(np.ones((2, 2, 2)), mask)
    with pytest.raises(ValueError, match="opacity"):
        apply_occupancy_coupling(psi, mask, opacity=1.1)
    with pytest.raises(ValueError, match="phase_shift"):
        apply_occupancy_coupling(psi, mask, phase_shift=float("nan"))
    with pytest.raises(ValueError, match="non-zero power"):
        apply_occupancy_coupling(np.zeros(mask.shape), mask)
    with pytest.raises(ValueError, match="binary"):
        apply_occupancy_coupling(psi, np.full(mask.shape, 0.5))
    with pytest.raises(ValueError, match="level"):
        menger_occupancy_mask(-1)


def test_fully_opaque_limit_blocks_only_retained_cells():
    mask = menger_occupancy_mask(1)
    psi = plane_wave(3)
    result = apply_occupancy_coupling(psi, mask, opacity=1.0)
    assert np.all(result.output[mask] == 0.0)
    assert np.allclose(result.output[~mask], psi[~mask])
