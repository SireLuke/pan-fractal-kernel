import math

import pytest

from abom_v8.lattice import (
    ALPHA, BETA, FIBONACCI_START_NUMBERS, MicrotubuleLattice,
)

MT = MicrotubuleLattice()


def test_nominal_13_3_geometry():
    assert (MT.n_protofilaments, MT.start) == (13, 3)
    assert MT.seam_vector == (13, -3)
    assert MT.rise_per_turn_nm == pytest.approx(12.0)
    assert MT.dimer_nm == pytest.approx(8.0)
    assert MT.protofilament_offset_nm == pytest.approx(12.0 / 13.0)
    assert MT.seam_shift_dimers == pytest.approx(1.5)
    assert 10.0 < MT.pitch_angle_deg < 12.0   # nominal radius, not a measurement


def test_going_once_around_lands_on_the_same_physical_site():
    for i in range(-20, 40):
        for k in range(-4, 6):
            ic, kc = MT.canonical(i, k)
            assert 0 <= ic < 13
            assert MT.axial_nm(i, k) == pytest.approx(MT.axial_nm(ic, kc))
            assert MT.canonical(ic, kc) == (ic, kc)            # idempotent
    assert MT.canonical(13, 0) == (0, 3)
    assert MT.canonical(-1, 0) == (12, -3)


def test_unwrapped_strip_matches_cartesian_height():
    for i, k in [(0, 0), (5, 2), (12, -1), (17, 3)]:
        pf, z = MT.unwrapped(i, k)
        assert 0 <= pf < 13
        assert MT.position(i, k)[2] == pytest.approx(z)
        x, y, _ = MT.position(i, k)
        assert math.hypot(x, y) == pytest.approx(MT.radius_nm)


def test_b_lattice_is_homotypic_except_across_the_seam():
    contacts = [MT.lateral_contact_is_homotypic(i, 0) for i in range(13)]
    assert contacts[:12] == [True] * 12
    assert contacts[12] is False                                # PF13 -> PF1
    assert MT.subunit_type(0, 0) == ALPHA and MT.subunit_type(0, 1) == BETA
    # across the seam alpha meets beta
    assert MT.subunit_type(12, 0) == ALPHA
    assert MT.subunit_type(*MT.lateral_neighbour(12, 0)) == BETA


def test_seam_register_shift_is_half_a_dimer_modulo_the_dimer_repeat():
    assert MT.seam_is_heterotypic is True
    assert (MT.seam_shift_dimers % 1.0) == pytest.approx(0.5)
    even = MicrotubuleLattice(n_protofilaments=14, start=4)
    assert even.seam_is_heterotypic is False
    assert even.lateral_contact_is_homotypic(13, 0) is True    # a 14_4 seam keeps register


def test_helix_start_numbers_of_the_primary_vectors():
    assert MT.start_number(1, 0) == 3        # monomer helix
    assert MT.start_number(0, 1) == 13       # straight protofilaments
    assert MT.start_number(6, -1) == 5
    assert MT.start_number(-6, 2) == 8
    assert MT.start_number(13, -3) == 0      # the seam vector spans nothing


def test_canonical_helix_vectors_for_fibonacci_start_numbers():
    assert FIBONACCI_START_NUMBERS == (3, 5, 8, 13)
    assert MT.canonical_helix(3) == (1, 0)
    assert MT.canonical_helix(5) == (6, -1)
    assert MT.canonical_helix(8) == (-6, 2)
    assert MT.canonical_helix(13) == (0, 1)
    for s in FIBONACCI_START_NUMBERS:
        assert MT.start_number(*MT.canonical_helix(s)) == s


def test_fibonacci_vector_sums_close_modulo_the_seam():
    assert MT.families_are_fibonacci_closed() is True
    v3, v5, v8, v13 = (MT.canonical_helix(s) for s in FIBONACCI_START_NUMBERS)
    assert MT.reduce_step(v3[0] + v5[0], v3[1] + v5[1]) == MT.reduce_step(*v8)   # 3 + 5 = 8
    assert (v5[0] + v8[0], v5[1] + v8[1]) == v13                                  # 5 + 8 = 13
    assert MicrotubuleLattice(n_protofilaments=14, start=4).families_are_fibonacci_closed() is False


def test_reduce_step_is_invariant_under_the_seam_vector():
    for di in range(-20, 21):
        for dk in range(-4, 5):
            red = MT.reduce_step(di, dk)
            assert -6 <= red[0] <= 6
            assert MT.reduce_step(di + 13, dk - 3) == red
            assert MT.start_number(*red) == MT.start_number(di, dk)


def test_relative_handedness_uses_the_chosen_representative():
    assert MT.handedness(1, 0) == 1
    assert MT.handedness(0, 1) == 0
    assert MT.handedness(*MT.canonical_helix(5)) == 1
    # Same family, other representative modulo the seam: handedness flips,
    # which is why a convention-fixed representative is required.
    assert MT.handedness(7, -1) == 1 and MT.handedness(-6, 2) == -1
    assert MT.start_number(7, -1) == MT.start_number(-6, 2) == 8


def test_unreachable_start_number_is_rejected():
    even = MicrotubuleLattice(n_protofilaments=14, start=4)
    with pytest.raises(ValueError):
        even.canonical_helix(3)       # gcd(4, 14) = 2 does not divide 3


@pytest.mark.parametrize("kwargs", [
    {"n_protofilaments": 1}, {"start": 0}, {"monomer_nm": 0.0}, {"radius_nm": float("nan")},
])
def test_invalid_lattice_parameters_are_rejected(kwargs):
    with pytest.raises(ValueError):
        MicrotubuleLattice(**kwargs)


def test_non_integer_site_indices_are_rejected():
    with pytest.raises(ValueError):
        MT.canonical(1.5, 0)
    with pytest.raises(ValueError):
        MT.axial_nm(0, True)
