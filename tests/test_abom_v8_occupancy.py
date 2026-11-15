import math

import pytest

from abom_v8.occupancy.fermi import (
    binary_entropy_bits, focal_radii, lemniscate_area_values,
    occupancy_profile, yin_yang_area_fractions,
)


def test_occupancy_midpoint_and_complement():
    profile = occupancy_profile(energy=1.0, chemical_potential=1.0, temperature=0.5)
    assert profile.occupied == pytest.approx(0.5)
    assert profile.unoccupied == pytest.approx(0.5)
    assert profile.asymmetry == pytest.approx(0.0)
    assert profile.entropy_bits == pytest.approx(1.0)


def test_entropy_is_maximum_at_half():
    assert binary_entropy_bits(0.5) == pytest.approx(1.0)
    assert binary_entropy_bits(0.0) == 0.0
    assert binary_entropy_bits(1.0) == 0.0
    assert binary_entropy_bits(0.25) < 1.0


def test_uploaded_plot_focal_radius_parameterization():
    cp, cm = focal_radii(0.95)
    assert cp == pytest.approx(0.95 / math.sqrt(2))
    assert cm == pytest.approx(0.05 / math.sqrt(2))
    assert cp == pytest.approx(0.672, abs=5e-4)
    assert cm == pytest.approx(0.035, abs=1e-3)


def test_uploaded_plot_eye_area_candidates():
    assert lemniscate_area_values(0.75) == pytest.approx((0.5625, 0.0625))


def test_existing_yin_yang_geometry_partitions_area():
    for n in (0.05, 0.25, 0.5, 0.75, 0.95):
        assert yin_yang_area_fractions(n) == pytest.approx((n, 1.0 - n), abs=1e-12)


@pytest.mark.parametrize("bad", [-0.01, 1.01, float("nan")])
def test_rejects_invalid_occupancy(bad):
    with pytest.raises(ValueError):
        binary_entropy_bits(bad)
