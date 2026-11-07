"""Foundational spectroscopy calculations for the PAN Fractal Kernel.

All functions use explicit SI inputs unless the function name/docstring says
otherwise. Returned wavenumbers are in cm^-1; chemical shifts are in ppm.
These are transparent reference calculations, not instrument fitting models.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

PLANCK_J_S = 6.62607015e-34
LIGHT_SPEED_M_S = 299792458.0
RYDBERG_H_M_INV = 1.096775834e7


def _positive_finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value) or value <= 0.0:
        raise ValueError(f"{name} must be finite and positive")
    return value


def _finite(name: str, value: float) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite")
    return value


def photon_energy_j(frequency_hz: float) -> float:
    """Planck-Einstein relation E=h*nu; frequency in Hz, energy in joules."""
    return PLANCK_J_S * _positive_finite("frequency_hz", frequency_hz)


def frequency_from_wavelength_hz(wavelength_m: float) -> float:
    """Return nu=c/lambda; wavelength is in metres."""
    return LIGHT_SPEED_M_S / _positive_finite("wavelength_m", wavelength_m)


def wavelength_from_frequency_m(frequency_hz: float) -> float:
    """Return lambda=c/nu; frequency is in Hz."""
    return LIGHT_SPEED_M_S / _positive_finite("frequency_hz", frequency_hz)


def photon_energy_from_wavelength_j(wavelength_m: float) -> float:
    """Return E=h*c/lambda; wavelength is in metres."""
    return PLANCK_J_S * frequency_from_wavelength_hz(wavelength_m)


def wavenumber_cm_inverse(wavelength_m: float) -> float:
    """Convert vacuum wavelength in metres to spectroscopic wavenumber cm^-1."""
    return 1.0 / (_positive_finite("wavelength_m", wavelength_m) * 100.0)


def beer_lambert_absorbance(
    molar_absorptivity_l_mol_cm: float,
    path_length_cm: float,
    concentration_mol_l: float,
) -> float:
    """Beer-Lambert A=epsilon*b*c with epsilon in L mol^-1 cm^-1."""
    epsilon = _positive_finite("molar_absorptivity_l_mol_cm", molar_absorptivity_l_mol_cm)
    path = _positive_finite("path_length_cm", path_length_cm)
    concentration = _finite("concentration_mol_l", concentration_mol_l)
    if concentration < 0.0:
        raise ValueError("concentration_mol_l must be non-negative")
    return epsilon * path * concentration


def absorbance_from_intensities(incident_intensity: float, transmitted_intensity: float) -> float:
    """Return A=-log10(I/I0); both intensities must be positive."""
    incident = _positive_finite("incident_intensity", incident_intensity)
    transmitted = _positive_finite("transmitted_intensity", transmitted_intensity)
    return -math.log10(transmitted / incident)


def transmittance_from_absorbance(absorbance: float) -> float:
    """Return fractional transmittance T=10^-A (not percent transmittance)."""
    value = _finite("absorbance", absorbance)
    try:
        return 10.0 ** (-value)
    except OverflowError as exc:
        raise ValueError("absorbance magnitude is outside the supported numeric range") from exc


def reduced_mass_kg(mass_1_kg: float, mass_2_kg: float) -> float:
    """Return diatomic reduced mass m1*m2/(m1+m2), masses in kg."""
    m1 = _positive_finite("mass_1_kg", mass_1_kg)
    m2 = _positive_finite("mass_2_kg", mass_2_kg)
    # This form avoids the unnecessary intermediate product m1*m2.
    return min(m1, m2) / (1.0 + min(m1, m2) / max(m1, m2))


def vibrational_wavenumber_cm_inverse(force_constant_n_m: float, reduced_mass: float) -> float:
    """Harmonic diatomic wavenumber; k in N/m, reduced mass in kg."""
    force_constant = _positive_finite("force_constant_n_m", force_constant_n_m)
    mass = _positive_finite("reduced_mass", reduced_mass)
    return math.sqrt(force_constant / mass) / (2.0 * math.pi * LIGHT_SPEED_M_S * 100.0)


def larmor_frequency_hz(gyromagnetic_ratio_rad_s_t: float, field_t: float) -> float:
    """Magnitude of nu=gamma*B0/(2*pi); gamma in rad s^-1 T^-1."""
    gamma = abs(_finite("gyromagnetic_ratio_rad_s_t", gyromagnetic_ratio_rad_s_t))
    field = _positive_finite("field_t", field_t)
    return gamma * field / (2.0 * math.pi)


def chemical_shift_ppm(
    sample_frequency_hz: float,
    reference_frequency_hz: float,
    operating_frequency_hz: float,
) -> float:
    """Return delta=(nu_sample-nu_ref)/nu_operating*1e6 in ppm."""
    sample = _finite("sample_frequency_hz", sample_frequency_hz)
    reference = _finite("reference_frequency_hz", reference_frequency_hz)
    operating = _positive_finite("operating_frequency_hz", operating_frequency_hz)
    return (sample - reference) / operating * 1.0e6


def rydberg_wavelength_m(
    n_lower: int,
    n_upper: int,
    rydberg_constant_m_inverse: float = RYDBERG_H_M_INV,
) -> float:
    """Hydrogen-like transition wavelength; n_upper must exceed n_lower >= 1.

    The supplied default is the infinite-nuclear-mass hydrogen Rydberg
    constant approximation. Use an isotope-specific reduced-mass constant
    when higher precision for a particular isotope is required.
    """
    if isinstance(n_lower, bool) or isinstance(n_upper, bool):
        raise ValueError("principal quantum numbers must be positive integers")
    if not isinstance(n_lower, int) or not isinstance(n_upper, int):
        raise ValueError("principal quantum numbers must be integers")
    if n_lower < 1 or n_upper <= n_lower:
        raise ValueError("require 1 <= n_lower < n_upper")
    rydberg = _positive_finite("rydberg_constant_m_inverse", rydberg_constant_m_inverse)
    inverse_lambda = rydberg * (1.0 / n_lower**2 - 1.0 / n_upper**2)
    return 1.0 / inverse_lambda


def moseley_frequency_hz(
    atomic_number: float,
    coefficient_sqrt_hz: float,
    screening_constant: float,
) -> float:
    """Return nu=[a*(Z-sigma)]^2 for a transition-specific Moseley fit.

    The coefficient has units sqrt(Hz); this empirical form is not a
    universal line predictor and requires Z > screening_constant.
    """
    z = _positive_finite("atomic_number", atomic_number)
    coefficient = _positive_finite("coefficient_sqrt_hz", coefficient_sqrt_hz)
    screening = _finite("screening_constant", screening_constant)
    effective_z = z - screening
    if effective_z <= 0.0:
        raise ValueError("atomic_number must exceed screening_constant")
    return (coefficient * effective_z) ** 2


@dataclass(frozen=True)
class PhotonObservation:
    """A photon represented by one measured frequency and derived quantities."""

    frequency_hz: float
    energy_j: float
    wavelength_m: float
    wavenumber_cm_inverse: float

    @classmethod
    def from_frequency(cls, frequency_hz: float) -> "PhotonObservation":
        frequency = _positive_finite("frequency_hz", frequency_hz)
        wavelength = wavelength_from_frequency_m(frequency)
        return cls(
            frequency_hz=frequency,
            energy_j=photon_energy_j(frequency),
            wavelength_m=wavelength,
            wavenumber_cm_inverse=wavenumber_cm_inverse(wavelength),
        )
