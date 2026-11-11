import math

import numpy as np
import pytest

import hydrogen_shell_modes as H
import hydrogen_shell_scale as S


def test_lattice_unit_rule_is_sqrt_2n():
    for n in (1, 2, 3):
        assert S.scale_for_shell("lattice_unit", n) == pytest.approx(math.sqrt(2 * n))


def test_mean_and_max_radius_rules_hit_their_targets():
    for n in (1, 2, 3):
        rho = np.linalg.norm(H.shell_view(n, 421), axis=1)
        assert S.scale_for_shell("mean_radius", n) * rho.mean() == pytest.approx(1.5 * n * n)
        assert S.scale_for_shell("max_radius", n) * rho.max() == pytest.approx(2.0 * n * n)


def test_rule_validation():
    with pytest.raises(ValueError):
        S.scale_for_shell("tuned", 2)
    with pytest.raises(ValueError):
        S.scale_for_shell("mean_radius", 4)
    with pytest.raises(ValueError):
        S.physical_bookkeeping(0.0, 2)
    with pytest.raises(ValueError):
        S.hydrogen_energy_j(0)


def test_halpha_from_kernel_matches_bohr_levels():
    chk = S.halpha_check()
    assert chk["relative_difference"] < 1e-12
    assert chk["lambda_rydberg_m"] == pytest.approx(656.47e-9, rel=1e-4)


def test_planck_length_and_bookkeeping():
    assert S.PLANCK_LENGTH_M == pytest.approx(1.616255e-35, rel=1e-4)
    b = S.physical_bookkeeping(2.0 * math.sqrt(2 * 2), 2)     # scale chosen so 2 a0 per lattice unit
    assert b["a0_per_lattice_unit"] == pytest.approx(2.0)
    assert b["metres_per_lattice_unit"] == pytest.approx(2.0 * S.BOHR_RADIUS_M)
    assert b["planck_lengths_per_lattice_unit"] == pytest.approx(2.0 * S.BOHR_RADIUS_M / S.PLANCK_LENGTH_M)


def test_shell_one_is_undefined_not_passed():
    r = S.evaluate_rule("lattice_unit", 1, null_trials=2)
    assert r["passes"] is None and r["e8"] is None


def test_recorded_outcomes_of_the_preregistered_comparison():
    """Regression pin of the documented result (deterministic seeds; 40 null trials)."""
    for n in (2, 3):
        assert S.evaluate_rule("lattice_unit", n, null_trials=40)["passes"] is True
        assert S.evaluate_rule("mean_radius", n, null_trials=40)["passes"] is False
        assert S.evaluate_rule("max_radius", n, null_trials=40)["passes"] is False
