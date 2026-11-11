"""Parameter-free length-scale rules for sampling hydrogen on E8 / 5_21 shell views.

``hydrogen_shell_modes`` leaves the a0-per-unit ``length_scale`` as a free input. This module
fixes it by rules stated BEFORE the comparison is run, so the result cannot be tuned. Shell n
of the 5_21 patch (Euclidean norm^2 = 2n) is tied to principal quantum number n.

Rules (``p`` = unit-sphere-normalised 3D view of shell n, ``rho = |p|``):
  mean_radius : s_n = <r>_ns / mean(rho),  with <r>_ns = 3 n^2 / 2 a0   (expectation radius of ns)
  max_radius  : s_n = 2 n^2 / max(rho)                                  (classical l=0 turning radius)
  lattice_unit: s_n = sqrt(2 n)  i.e. one raw lattice unit = 1 a0       (no hydrogen input at all)

Pre-registered criterion (``PREREGISTERED_FACTOR``): the E8 cross-(l,m) overlap over the states
with n' <= n must be below 0.25 x the minimum of a direction-shuffled null (same radii, random
directions). It is undefined for shell 1 (a single state).

Units bookkeeping (``physical_bookkeeping``) converts a scale to metres and Planck lengths using
the kernel's spectroscopy constants, a CODATA Bohr radius, and G. It is a unit conversion only:
it asserts no minimum length, no discretisation, and no physical size for the lattice.
Reduced-mass (finite proton mass) corrections to a0 are ignored.
"""
from __future__ import annotations

import math

import numpy as np

try:
    from . import hydrogen_shell_modes as H
    from .spectroscopy import (LIGHT_SPEED_M_S, PLANCK_J_S, RYDBERG_H_M_INV, rydberg_wavelength_m)
except ImportError:
    import hydrogen_shell_modes as H
    from spectroscopy import (LIGHT_SPEED_M_S, PLANCK_J_S, RYDBERG_H_M_INV, rydberg_wavelength_m)

RULES = ("mean_radius", "max_radius", "lattice_unit")
PREREGISTERED_FACTOR = 0.25
BOHR_RADIUS_M = 5.29177210544e-11     # CODATA 2022
G_NEWTON = 6.67430e-11                # CODATA 2018/2022, rel. u = 2.2e-5
HBAR = PLANCK_J_S / (2.0 * math.pi)
PLANCK_LENGTH_M = math.sqrt(HBAR * G_NEWTON / LIGHT_SPEED_M_S**3)


def scale_for_shell(rule: str, n: int, seed: int = 421) -> float:
    """a0 per unit of the unit-normalised 3D view, from a named rule."""
    if rule not in RULES:
        raise ValueError(f"rule must be one of {RULES}")
    if n not in (1, 2, 3):
        raise ValueError("n must be 1, 2 or 3")
    rho = np.linalg.norm(H.shell_view(n, seed), axis=1)
    if rule == "mean_radius":
        return 1.5 * n * n / float(np.mean(rho))
    if rule == "max_radius":
        return 2.0 * n * n / float(np.max(rho))
    return math.sqrt(2.0 * n)


def hydrogen_energy_j(n: int) -> float:
    """Bohr level energy E_n = -h c R_H / n^2 using the kernel's spectroscopy constants."""
    if not (isinstance(n, int) and n >= 1):
        raise ValueError("n must be a positive integer")
    return -PLANCK_J_S * LIGHT_SPEED_M_S * RYDBERG_H_M_INV / n**2


def physical_bookkeeping(scale_a0_per_unit: float, n: int) -> dict:
    """Metres and Planck lengths per raw lattice unit for shell n (a0 per unit-normalised unit / sqrt(2n))."""
    if not (math.isfinite(scale_a0_per_unit) and scale_a0_per_unit > 0):
        raise ValueError("scale must be finite and positive")
    a0_per_lattice_unit = scale_a0_per_unit / math.sqrt(2.0 * n)
    metres = a0_per_lattice_unit * BOHR_RADIUS_M
    return {"a0_per_lattice_unit": a0_per_lattice_unit, "metres_per_lattice_unit": metres,
            "planck_lengths_per_lattice_unit": metres / PLANCK_LENGTH_M,
            "note": "unit conversion only; asserts no minimum length or physical lattice size"}


def evaluate_rule(rule: str, n: int, seed: int = 421, null_trials: int = 200, null_seed: int = 4242) -> dict:
    """Pre-registered comparison for one (rule, shell). Returns a JSON-ready dict."""
    scale = scale_for_shell(rule, n, seed)
    p = H.shell_view(n, seed)
    out = {"rule": rule, "shell": n, "points": len(p), "scale_a0_per_unit": scale,
           "bookkeeping": physical_bookkeeping(scale, n)}
    if n == 1:
        out.update(e8=None, null_min=None, null_median=None, passes=None,
                   note="single state; cross-(l,m) overlap undefined")
        return out
    states = H.states_up_to(n)
    rho = np.linalg.norm(p, axis=1)
    e8 = H.max_cross_lm_overlap(p, states, length_scale=scale)
    rng = np.random.default_rng([null_seed, n])
    nulls = []
    for _ in range(null_trials):
        d = rng.normal(size=p.shape)
        d /= np.linalg.norm(d, axis=1)[:, None]
        nulls.append(H.max_cross_lm_overlap(d * rho[:, None], states, length_scale=scale))
    nmin, nmed = float(min(nulls)), float(np.median(nulls))
    out.update(e8=e8, null_min=nmin, null_median=nmed, null_trials=null_trials,
               ratio_to_null_min=e8 / nmin, passes=bool(e8 < PREREGISTERED_FACTOR * nmin))
    return out


def halpha_check() -> dict:
    """Consistency of the kernel's Rydberg wavelength with Bohr energies (h c / (E3 - E2))."""
    lam = rydberg_wavelength_m(2, 3)
    via_levels = PLANCK_J_S * LIGHT_SPEED_M_S / (hydrogen_energy_j(3) - hydrogen_energy_j(2))
    return {"lambda_rydberg_m": lam, "lambda_from_bohr_levels_m": via_levels,
            "relative_difference": abs(lam - via_levels) / lam}
