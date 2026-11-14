import math

import pytest

import fermi_yinyang as Y
from janus_hydra import golden_angle_phases


def test_closed_form_areas_are_n_and_one_minus_n():
    for n in (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0):
        w, b = Y.lobe_area_fractions(n)
        assert w == pytest.approx(n, abs=1e-12)
        assert b == pytest.approx(1 - n, abs=1e-12)


def test_head_diameters_sum_to_disk_diameter():
    for n in (0.0, 0.3, 0.5, 0.9, 1.0):
        d1, d2 = Y.head_diameters(n)
        assert d1 + d2 == pytest.approx(2.0)
        assert d1 >= 0 and d2 >= 0


def test_delta_equals_minus_tanh():
    for x in (-3.0, -0.5, 0.0, 1.2, 4.0):
        n = Y.occupancy(x, 0.0, 1.0)
        assert Y.delta(n) == pytest.approx(-math.tanh(x / 2), abs=1e-12)


def test_grid_area_matches_closed_form():
    m = 600
    for n in (0.25, 0.5, 0.8):
        inside = white = 0
        for i in range(m):
            x = -1 + (i + 0.5) * 2 / m
            for j in range(m):
                y = -1 + (j + 0.5) * 2 / m
                if x * x + y * y <= 1:
                    inside += 1
                    white += Y.is_white(x, y, n)
        assert white / inside == pytest.approx(n, abs=3e-3)


def test_limits_are_the_two_infinities():
    assert Y.lobe_area_fractions(Y.occupancy(-1e6, 0, 1))[0] == pytest.approx(1.0)
    assert Y.lobe_area_fractions(Y.occupancy(1e6, 0, 1))[0] == pytest.approx(0.0)
    assert Y.occupancy(0.0, 0.0, 1.0) == pytest.approx(0.5)
    assert Y.occupancy(2, 2, 0) == 0.5 and Y.occupancy(1, 2, 0) == 1.0 and Y.occupancy(3, 2, 0) == 0.0


def test_invalid_inputs_rejected():
    with pytest.raises(ValueError):
        Y.delta(1.1)
    with pytest.raises(ValueError):
        Y.occupancy(0.0, 0.0, -1.0)
    with pytest.raises(ValueError):
        Y.occupancy(float("nan"), 0.0, 1.0)


def test_golden_angle_constants_and_kernel_phases():
    assert Y.GOLDEN_ANGLE_DEG == pytest.approx(137.5077640500378, abs=1e-9)
    assert Y.INVERSE_GOLDEN_ANGLE_DEG == pytest.approx(222.4922359499622, abs=1e-9)
    assert Y.GOLDEN_ANGLE_DEG + Y.INVERSE_GOLDEN_ANGLE_DEG == pytest.approx(360.0)
    assert golden_angle_phases()[1] == pytest.approx(Y.GOLDEN_ANGLE_RAD)
