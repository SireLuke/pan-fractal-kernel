import math

import pytest

from abom_v8.harmonics import PHI, log_phi_ratio, phi_power


@pytest.mark.parametrize("n", [-3, -2, -1, 0, 1, 2, 3])
def test_phi_power_and_log_inverse(n):
    scale = phi_power(n)
    assert scale == pytest.approx(PHI ** n)
    assert log_phi_ratio(scale, 1.0) == pytest.approx(n)


def test_log_phi_requires_dimensionless_positive_ratio():
    assert log_phi_ratio(10.0, 10.0) == pytest.approx(0.0)
    with pytest.raises(ValueError):
        log_phi_ratio(0.0, 1.0)
    with pytest.raises(ValueError):
        log_phi_ratio(math.inf, 1.0)
    assert math.isfinite(log_phi_ratio(1e308, 1e-308))
