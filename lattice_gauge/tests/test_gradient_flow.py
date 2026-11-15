import numpy as np
import pytest
from lattice_gauge.gradient_flow import wilson_flow, wilson_flow_step
from lattice_gauge.lattice_gauge import Gauge


@pytest.mark.parametrize("n", [2, 3])
def test_wilson_flow_preserves_suN_links(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=31, hot=True)
    wilson_flow_step(g, step_size=1e-5)
    eye = np.eye(n, dtype=complex)
    for link in g.U:
        assert np.max(np.abs(link @ np.swapaxes(link.conj(), -1, -2) - eye)) < 1e-10
        assert np.max(np.abs(np.linalg.det(link) - 1)) < 1e-9


@pytest.mark.parametrize("n", [2, 3])
def test_wilson_flow_action_descent_for_small_step(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=37, hot=True)
    before = g.action()
    wilson_flow_step(g, step_size=1e-6)
    after = g.action()
    assert after <= before + 1e-9


@pytest.mark.parametrize("n", [2, 3])
def test_cold_configuration_is_fixed(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=41, hot=False)
    before = [u.copy() for u in g.U]
    hist = wilson_flow(g, steps=2, step_size=1e-4)
    assert len(hist) == 3
    for old, new in zip(before, g.U):
        assert np.allclose(old, new, atol=1e-12)


def test_flow_rejects_non_four_dimensional_topology():
    g = Gauge(2, (4, 4), beta=1.0, seed=43, hot=True)
    with pytest.raises(ValueError, match="exactly 4 dimensions"):
        wilson_flow(g, steps=1)


@pytest.mark.parametrize("n", [2, 3])
def test_rk3_flow_preserves_suN_links(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=47, hot=True)
    wilson_flow(g, steps=2, step_size=0.02, integrator="rk3")
    eye = np.eye(n, dtype=complex)
    for link in g.U:
        assert np.max(np.abs(link @ np.swapaxes(link.conj(), -1, -2) - eye)) < 1e-10
        assert np.max(np.abs(np.linalg.det(link) - 1)) < 1e-9


def test_rk3_is_third_order_and_euler_is_first_order():
    def flowed(eps, integ):
        g = Gauge(2, (4, 4, 4, 4), beta=2.0, seed=5, hot=True)
        wilson_flow(g, steps=int(round(0.04 / eps)), step_size=eps, integrator=integ)
        return g.U

    ref = flowed(0.0005, "rk3")

    def err(eps, integ):
        return max(np.abs(a - b).max() for a, b in zip(flowed(eps, integ), ref))

    assert 1.7 < err(0.01, "euler") / err(0.005, "euler") < 2.3
    assert 6.5 < err(0.01, "rk3") / err(0.005, "rk3") < 9.5


def test_cold_configuration_is_fixed_under_rk3():
    g = Gauge(3, (4, 4, 4, 4), beta=1.0, seed=41, hot=False)
    before = [u.copy() for u in g.U]
    wilson_flow(g, steps=2, step_size=0.02, integrator="rk3")
    for old, new in zip(before, g.U):
        assert np.allclose(old, new, atol=1e-12)


def test_flow_rejects_unknown_integrator():
    g = Gauge(2, (4, 4, 4, 4), beta=1.0, seed=43, hot=True)
    with pytest.raises(ValueError, match="integrator"):
        wilson_flow(g, steps=1, integrator="rk4")
