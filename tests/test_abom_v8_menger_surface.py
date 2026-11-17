from fractions import Fraction

import pytest

from abom_v8.occupancy import (
    exposed_face_count, menger_surface_area, menger_surface_area_exact,
    menger_volume_fraction, surface_face_count,
)


def test_known_levels():
    assert [surface_face_count(n) for n in range(4)] == [6, 72, 1056, 18048]
    assert menger_surface_area_exact(0) == 6
    assert menger_surface_area_exact(1) == 8
    assert menger_surface_area_exact(2) == Fraction(352, 27)
    assert menger_surface_area_exact(3) == Fraction(6016, 243)


@pytest.mark.parametrize("level", [0, 1, 2, 3])
def test_closed_form_matches_independent_face_count(level):
    assert exposed_face_count(level) == surface_face_count(level)


def test_closed_form_matches_formula_in_ninths():
    for n in range(12):
        expected = 2 * Fraction(20, 9) ** n + 4 * Fraction(8, 9) ** n
        assert menger_surface_area_exact(n) == expected


def test_area_grows_while_volume_shrinks():
    for n in range(40):
        assert menger_surface_area_exact(n + 1) > menger_surface_area_exact(n)
        assert menger_surface_area_exact(n) > n
        assert menger_volume_fraction(n + 1) < menger_volume_fraction(n)
        assert menger_volume_fraction(n) <= 1.0


def test_float_form_and_validation():
    assert menger_surface_area(1) == 8.0
    for bad in (-1, 1.5, True, "2"):
        with pytest.raises(ValueError):
            menger_surface_area_exact(bad)
