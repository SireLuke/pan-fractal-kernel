import numpy as np
import pytest

from lattice_gauge.lattice_gauge import Gauge
from lattice_gauge.topology import (
    clover_field_strength,
    clover_topological_charge,
    clover_topological_density,
)


@pytest.mark.parametrize("n", [2, 3])
def test_cold_start_has_zero_clover_topological_density(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=3, hot=False)
    q = clover_topological_density(g)
    assert q.shape == (4, 4, 4, 4)
    assert np.max(np.abs(q)) < 1e-14
    assert abs(clover_topological_charge(g)) < 1e-14


@pytest.mark.parametrize("n", [2, 3])
def test_clover_field_strength_is_hermitian_traceless(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=7, hot=True)
    f = clover_field_strength(g, 0, 1)
    assert np.max(np.abs(f - np.swapaxes(f.conj(), -1, -2))) < 1e-12
    assert np.max(np.abs(np.trace(f, axis1=-2, axis2=-1))) < 1e-12


@pytest.mark.parametrize("n", [2, 3])
def test_clover_topological_density_is_local_gauge_invariant(n):
    g = Gauge(n, (4, 4, 4, 4), beta=1.0, seed=11, hot=True)
    before = clover_topological_density(g)
    transform = g._haar(g.dims)
    g.gauge_transform(transform)
    after = clover_topological_density(g)
    assert np.allclose(before, after, atol=1e-10, rtol=0.0)


def test_clover_topology_rejects_non_four_dimensional_lattice():
    g = Gauge(2, (4, 4), beta=1.0, seed=13, hot=True)
    with pytest.raises(ValueError, match="exactly 4 dimensions"):
        clover_topological_density(g)


def test_clover_field_strength_antisymmetric_in_indices():
    g = Gauge(2, (4, 4, 4, 4), beta=1.0, seed=17, hot=True)
    assert np.allclose(
        clover_field_strength(g, 1, 0),
        -clover_field_strength(g, 0, 1),
        atol=1e-12,
    )
