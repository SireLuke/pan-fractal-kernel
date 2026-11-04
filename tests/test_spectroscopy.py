import math

import pytest

from spectroscopy import (
    LIGHT_SPEED_M_S,
    PLANCK_J_S,
    PhotonObservation,
    absorbance_from_intensities,
    beer_lambert_absorbance,
    chemical_shift_ppm,
    frequency_from_wavelength_hz,
    larmor_frequency_hz,
    moseley_frequency_hz,
    photon_energy_from_wavelength_j,
    photon_energy_j,
    reduced_mass_kg,
    rydberg_wavelength_m,
    transmittance_from_absorbance,
    vibrational_wavenumber_cm_inverse,
    wavelength_from_frequency_m,
    wavenumber_cm_inverse,
)


def test_planck_wave_and_wavenumber_relations_are_consistent():
    wavelength = 500e-9
    frequency = frequency_from_wavelength_hz(wavelength)
    assert frequency == pytest.approx(LIGHT_SPEED_M_S / wavelength)
    assert wavelength_from_frequency_m(frequency) == pytest.approx(wavelength)
    assert photon_energy_j(frequency) == pytest.approx(PLANCK_J_S * frequency)
    assert photon_energy_from_wavelength_j(wavelength) == pytest.approx(
        PLANCK_J_S * LIGHT_SPEED_M_S / wavelength
    )
    assert wavenumber_cm_inverse(wavelength) == pytest.approx(20000.0)


def test_photon_observation_derives_consistent_quantities():
    observation = PhotonObservation.from_frequency(6.0e14)
    assert observation.energy_j == pytest.approx(PLANCK_J_S * 6.0e14)
    assert observation.wavelength_m == pytest.approx(LIGHT_SPEED_M_S / 6.0e14)
    assert observation.wavenumber_cm_inverse == pytest.approx(
        1.0 / (observation.wavelength_m * 100.0)
    )


def test_beer_lambert_and_intensity_absorbance_agree():
    absorbance = beer_lambert_absorbance(100.0, 1.0, 0.01)
    assert absorbance == pytest.approx(1.0)
    transmittance = transmittance_from_absorbance(absorbance)
    assert transmittance == pytest.approx(0.1)
    assert absorbance_from_intensities(10.0, 1.0) == pytest.approx(absorbance)


def test_reduced_mass_and_harmonic_vibrational_wavenumber():
    proton = 1.67262192369e-27
    carbon = 1.9944235e-26
    mu = reduced_mass_kg(proton, carbon)
    assert mu == pytest.approx(proton * carbon / (proton + carbon))
    wn = vibrational_wavenumber_cm_inverse(500.0, mu)
    assert math.isfinite(wn) and wn > 0.0


def test_proton_larmor_frequency_and_chemical_shift():
    gamma_proton = 2.6752218744e8  # rad s^-1 T^-1
    operating = larmor_frequency_hz(gamma_proton, 9.4)
    assert operating == pytest.approx(400.2e6, rel=2e-3)
    assert chemical_shift_ppm(operating + 400.2, operating, operating) == pytest.approx(1.0)


def test_rydberg_balmer_alpha_is_visible_red_line():
    wavelength = rydberg_wavelength_m(2, 3)
    assert wavelength * 1e9 == pytest.approx(656.3, rel=2e-3)


def test_moseley_scaling_and_screening_domain():
    low_z = moseley_frequency_hz(20, 1.0e7, 2.0)
    high_z = moseley_frequency_hz(30, 1.0e7, 2.0)
    assert high_z > low_z
    assert high_z / low_z == pytest.approx(((30 - 2) / (20 - 2)) ** 2)
    with pytest.raises(ValueError):
        moseley_frequency_hz(2, 1.0, 2.0)


@pytest.mark.parametrize(
    "call",
    [
        lambda: photon_energy_j(0),
        lambda: frequency_from_wavelength_hz(float("nan")),
        lambda: wavenumber_cm_inverse(-1),
        lambda: beer_lambert_absorbance(1, 1, -0.1),
        lambda: absorbance_from_intensities(1, 0),
        lambda: reduced_mass_kg(1, float("inf")),
        lambda: vibrational_wavenumber_cm_inverse(1, 0),
        lambda: larmor_frequency_hz(float("nan"), 1),
        lambda: chemical_shift_ppm(1, 0, 0),
        lambda: rydberg_wavelength_m(0, 3),
        lambda: rydberg_wavelength_m(2.0, 3),
        lambda: moseley_frequency_hz(10, 1, 10),
        lambda: PhotonObservation.from_frequency(-1),
    ],
)
def test_invalid_spectroscopy_inputs_are_rejected(call):
    with pytest.raises(ValueError):
        call()
