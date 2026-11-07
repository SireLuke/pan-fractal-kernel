"""Deterministic stress tests for the fixed Gosset 4_21 JOBF boundary.

These verify numerical and symmetry contracts, not physical predictions.
"""
from itertools import product

import numpy as np
import pytest

from geometry_adapter import Gosset421Adapter
from gosset_421 import E8_ROOTS, weyl_reflection


@pytest.fixture(scope="module")
def orthant_directions():
    rng = np.random.default_rng(20261103)
    signs = np.asarray(list(product((-1.0, 1.0), repeat=8)), dtype=float)
    magnitudes = rng.uniform(0.05, 1.0, size=signs.shape)
    return signs * magnitudes


def test_gosset_radial_boundary_covers_all_256_sign_orthants(orthant_directions):
    observed = {tuple(np.sign(row).astype(int)) for row in orthant_directions}
    assert len(observed) == 256

    radii = Gosset421Adapter().radial_boundary_many(orthant_directions)
    assert radii.shape == (256,)
    assert np.all(np.isfinite(radii))
    assert np.all(radii > 0.0)


def test_gosset_radial_boundary_is_antipodal_and_scale_invariant(orthant_directions):
    rng = np.random.default_rng(8128)
    adapter = Gosset421Adapter()
    reference = adapter.radial_boundary_many(orthant_directions)
    antipodal = adapter.radial_boundary_many(-orthant_directions)
    scales = rng.uniform(1e-4, 1e4, size=len(orthant_directions))
    rescaled = adapter.radial_boundary_many(orthant_directions * scales[:, None])

    assert antipodal == pytest.approx(reference, abs=1e-8, rel=1e-8)
    assert rescaled == pytest.approx(reference, abs=1e-8, rel=1e-8)


def test_gosset_radial_boundary_is_invariant_under_e8_weyl_reflections(orthant_directions):
    adapter = Gosset421Adapter()
    sample = orthant_directions[::17]
    original_radii = adapter.radial_boundary_many(sample)

    # Twelve distinct E8 root reflections exercise the Weyl symmetry of 4_21.
    for alpha in E8_ROOTS[::20]:
        reflected = np.asarray([
            weyl_reflection(tuple(vector), alpha) for vector in sample
        ])
        assert np.allclose(
            np.linalg.norm(reflected, axis=1),
            np.linalg.norm(sample, axis=1),
            atol=1e-10,
        )
        reflected_radii = adapter.radial_boundary_many(reflected)
        assert reflected_radii == pytest.approx(
            original_radii, abs=2e-7, rel=2e-7
        )


def test_gosset_chunking_does_not_change_boundary_values(orthant_directions):
    reference = Gosset421Adapter(chunk_size=256).radial_boundary_many(orthant_directions)
    chunked = Gosset421Adapter(chunk_size=37).radial_boundary_many(orthant_directions)
    assert chunked == pytest.approx(reference, abs=1e-10, rel=1e-10)
