import numpy as np
import pytest

from lattice_gauge.gradient_flow import wilson_flow, wilson_flow_step
from lattice_gauge.lattice_gauge import Gauge


@pytest.mark.parametrize("n", [2, 3])
def test_wilson_flow_preserves_link_unitarity(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=31, hot=True)
    wilson_flow_step(g, step_size=1e-4)
    identity = np.eye(n, dtype=complex)
    for link in g.U:
        product = link @ np.swapaxes(link.conj(), -1, -2)
        assert np.max(np.abs(product - identity)) < 1e-10
        assert np.max(np.abs(np.linalg.det(link) - 1.0)) < 1e-9


@pytest.mark.parametrize("n", [2, 3])
def test_wilson_flow_does_not_increase_wilson_action(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=37, hot=True)
    before = g.action()
    wilson_flow_step(g, step_size=1e-5)
    after = g.action()
    assert after <= before + 1e-9


@pytest.mark.parametrize("n", [2, 3])
def test_cold_configuration_is_fixed_by_wilson_flow(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=41, hot=False)
    before = [u.copy() for u in g.U]
    history = wilson_flow(g, steps=2, step_size=1e-3)
    assert len(history) == 3
    for old, new in zip(before, g.U):
        assert np.allclose(old, new, atol=1e-12)


def test_wilson_flow_rejects_non_four_dimensional_topology_run():
    g = Gauge(2, (4, 4), beta=1.0, seed=43, hot=True)
    with pytest.raises(ValueError, match="exactly 4 dimensions"):
        wilson_flow(g, steps=1)
