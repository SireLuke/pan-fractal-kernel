"""Semi-transparent Menger geometry as a multiplicative wave-field operator.

This module applies a finite, binary Menger occupancy mask to a caller-supplied
complex scalar field on a matching 3D Cartesian grid. Retained sponge cells
attenuate amplitude and add a configurable phase shift; void cells transmit
unchanged. This is a numerical coupling operator, not a wave-equation solver,
PDE, or physical interaction claim.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

import numpy as np

from menger_sponge import menger_cells


@dataclass(frozen=True, slots=True)
class WaveCouplingResult:
    """Numerical output and diagnostics for one finite-grid coupling run."""

    output: np.ndarray
    mask: np.ndarray
    transmission: np.ndarray
    metrics: dict[str, float | int]


def menger_occupancy_mask(level: int) -> np.ndarray:
    """Return the retained-cell indicator on a cubic grid of side 3**level."""
    if isinstance(level, bool) or not isinstance(level, int) or level < 0:
        raise ValueError("level must be a non-negative integer")
    cells = menger_cells(3, level)
    side = 3**level
    mask = np.zeros((side, side, side), dtype=bool)
    if len(cells):
        mask[tuple(cells.T)] = True
    return mask


def apply_occupancy_coupling(
    wavefield: np.ndarray,
    mask: np.ndarray,
    *,
    opacity: float = 0.25,
    phase_shift: float = 0.0,
) -> WaveCouplingResult:
    """Apply a bounded complex transmission coefficient to a 3D wave field.

    For binary occupancy M(x) in {0, 1}, the operator is

        T(x) = (1 - opacity * M(x)) * exp(i * phase_shift * M(x))
        psi_out(x) = T(x) * psi_in(x).

    opacity is an amplitude attenuation in [0, 1]. The phase term changes
    complex phase but not local power. The mask is supplied explicitly so
    randomized and structure-matched controls can use the same operator.
    """
    psi = np.asarray(wavefield, dtype=np.complex128)
    occupied = np.asarray(mask)
    if psi.ndim != 3 or any(size < 1 for size in psi.shape):
        raise ValueError("wavefield must be a non-empty 3D array")
    if occupied.shape != psi.shape:
        raise ValueError("mask shape must match wavefield shape")
    if occupied.dtype != np.bool_:
        if not np.all(np.isfinite(occupied)) or not np.all(np.isin(occupied, (0, 1))):
            raise ValueError("mask must contain only boolean or binary occupancy values")
        occupied = occupied.astype(bool)
    if not np.all(np.isfinite(psi)):
        raise ValueError("wavefield must contain only finite values")
    if not np.any(np.abs(psi) > 0):
        raise ValueError("wavefield must have non-zero power")
    opacity = float(opacity)
    phase_shift = float(phase_shift)
    if not math.isfinite(opacity) or not 0.0 <= opacity <= 1.0:
        raise ValueError("opacity must be finite and in [0, 1]")
    if not math.isfinite(phase_shift):
        raise ValueError("phase_shift must be finite")

    transmission = (1.0 - opacity * occupied) * np.exp(1j * phase_shift * occupied)
    output = psi * transmission
    input_power_density = np.abs(psi) ** 2
    input_power = float(input_power_density.sum())
    output_power = float((np.abs(output) ** 2).sum())
    weighted_occupancy = float((input_power_density * occupied).sum() / input_power)
    predicted_ratio = 1.0 - weighted_occupancy + weighted_occupancy * (1.0 - opacity) ** 2
    metrics: dict[str, float | int] = {
        "grid_points": int(psi.size),
        "occupied_cells": int(occupied.sum()),
        "geometry_occupancy_fraction": float(occupied.mean()),
        "wave_weighted_occupancy_fraction": weighted_occupancy,
        "input_power": input_power,
        "output_power": output_power,
        "power_transmission_ratio": output_power / input_power,
        "predicted_power_transmission_ratio": predicted_ratio,
        "opacity": opacity,
        "phase_shift_radians": phase_shift,
        "max_transmission_amplitude": float(np.abs(transmission).max()),
    }
    return WaveCouplingResult(output=output, mask=occupied.copy(),
                              transmission=transmission, metrics=metrics)


def menger_wave_coupling(
    wavefield: np.ndarray,
    *,
    level: int,
    opacity: float = 0.25,
    phase_shift: float = 0.0,
) -> WaveCouplingResult:
    """Couple a complex wave field to the finite 3D Menger sponge at level."""
    mask = menger_occupancy_mask(level)
    if np.asarray(wavefield).shape != mask.shape:
        raise ValueError(
            f"wavefield shape must match Menger level {level}: {mask.shape}"
        )
    return apply_occupancy_coupling(
        wavefield, mask, opacity=opacity, phase_shift=phase_shift
    )
