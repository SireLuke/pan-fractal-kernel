from fractions import Fraction
import math

import pytest

from abom_v8.occupancy import (
    FLUX_MAXIMUM, binary_entropy_bits, flux_from_asymmetry, lemniscate_flux,
    menger_cells_per_level, menger_hausdorff_dimension, menger_volume_fraction,
    mu_cube_volume, occupancy_profile,
)


def test_volume_fraction_is_exact_power_of_twenty_over_twenty_seven():
    assert menger_cells_per_level(3) == 20
    assert menger_volume_fraction(0) == 1.0
    assert menger_volume_fraction(1) == pytest.approx(20 / 27)
    assert menger_volume_fraction(2) == pytest.approx(float(Fraction(400, 729)))
    assert menger_volume_fraction(5) == pytest.approx((20 / 27) ** 5)


def test_other_dimensions_follow_the_kernel_construction():
    assert menger_volume_fraction(1, d=2) == pytest.approx(8 / 9)   # Sierpinski carpet
    assert menger_volume_fraction(1, d=4) == pytest.approx(48 / 81)


def test_hausdorff_dimension_is_ln20_over_ln3():
    expected = math.log(20) / math.log(3)
    assert menger_hausdorff_dimension(3) == pytest.approx(expected)
    assert round(expected, 3) == 2.727
    assert menger_hausdorff_dimension(2) == pytest.approx(math.log(8) / math.log(3))


def test_volume_decays_geometrically_consistent_with_the_dimension():
    # Volume ~ 3**(-(d - D) * level): ratio between levels is 20/27 = 3**(D - 3).
    d_h = menger_hausdorff_dimension(3)
    ratio = menger_volume_fraction(7) / menger_volume_fraction(6)
    assert ratio == pytest.approx(3.0 ** (d_h - 3.0))


def test_mu_cube_volume_scales_linearly_with_occupancy():
    assert mu_cube_volume(0.0) == 0.0
    assert mu_cube_volume(1.0, level=2) == pytest.approx((20 / 27) ** 2)
    assert mu_cube_volume(0.5, level=2) == pytest.approx(0.5 * (20 / 27) ** 2)
    assert mu_cube_volume(0.25, level=1) == pytest.approx(0.25 * 20 / 27)


def test_flux_peaks_at_one_quarter_at_equilibrium():
    assert lemniscate_flux(0.5) == FLUX_MAXIMUM == 0.25
    assert lemniscate_flux(0.0) == 0.0
    assert lemniscate_flux(1.0) == 0.0
    for n in (0.05, 0.25, 0.4, 0.5):
        assert lemniscate_flux(n) <= FLUX_MAXIMUM
        assert lemniscate_flux(n) == pytest.approx(lemniscate_flux(1.0 - n))


def test_flux_equals_one_minus_delta_squared_over_four():
    for energy in (-3.0, -1.0, 0.0, 0.7, 2.5):
        p = occupancy_profile(energy, 0.0, 1.0)
        assert lemniscate_flux(p.occupied) == pytest.approx(flux_from_asymmetry(p.asymmetry))
        # delta = -tanh((E - mu) / 2T)
        assert p.asymmetry == pytest.approx(-math.tanh(energy / 2.0))
        assert lemniscate_flux(p.occupied) == pytest.approx(
            (1.0 - math.tanh(energy / 2.0) ** 2) / 4.0
        )


def test_flux_is_not_the_entropy_but_shares_its_peak_location():
    # Both peak at n = 1/2, but they are different functions.
    assert binary_entropy_bits(0.5) == 1.0 and lemniscate_flux(0.5) == 0.25
    assert binary_entropy_bits(0.1) != pytest.approx(4.0 * lemniscate_flux(0.1))


@pytest.mark.parametrize("bad", [-0.1, 1.1, float("nan"), float("inf")])
def test_invalid_occupancy_is_rejected(bad):
    with pytest.raises(ValueError):
        lemniscate_flux(bad)
    with pytest.raises(ValueError):
        mu_cube_volume(bad)


@pytest.mark.parametrize("bad", [-1, 1.5, True])
def test_invalid_level_is_rejected(bad):
    with pytest.raises(ValueError):
        menger_volume_fraction(bad)


def test_invalid_asymmetry_is_rejected():
    with pytest.raises(ValueError):
        flux_from_asymmetry(1.01)
