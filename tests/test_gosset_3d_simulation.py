import numpy as np
import pytest

try:
    from .. import geometry_adapter
    from ..gosset_421 import E8_ROOTS
    from ..gosset_3d_simulation import deformed_gosset_vertices, seeded_view
    from ..jobf_v0_2 import JanusOctadialBreathingField
except ImportError:
    import geometry_adapter
    from gosset_421 import E8_ROOTS
    from gosset_3d_simulation import deformed_gosset_vertices, seeded_view
    from jobf_v0_2 import JanusOctadialBreathingField


def test_seeded_view_is_reproducible_and_orthonormal():
    first = seeded_view(73)
    second = seeded_view(73)
    assert first.matrix.shape == (3, 8)
    assert np.allclose(first.matrix, second.matrix)
    assert np.allclose(first.matrix @ first.matrix.T, np.eye(3))


def test_jobf_deforms_all_canonical_gosset_vertices():
    model = JanusOctadialBreathingField()
    points, diagnostics = deformed_gosset_vertices(model, 0.37)
    assert points.shape == (240, 8)
    assert np.isfinite(points).all()
    assert diagnostics["channels"].shape == (8,)
    assert len(E8_ROOTS) == 240


def test_halfspace_cache_round_trip_skips_qhull(tmp_path, monkeypatch):
    normals = np.vstack((np.eye(8), -np.eye(8)))
    offsets = np.full(16, -1.0)

    class FakeHull:
        equations = np.column_stack((normals, offsets))

    from scipy import spatial
    monkeypatch.setattr(spatial, "ConvexHull", lambda points: FakeHull())
    geometry_adapter._gosset_halfspaces.cache_clear()
    cache = tmp_path / "halfspaces.npz"
    first = geometry_adapter._gosset_halfspaces(str(cache))
    assert cache.is_file()
    assert first[0].shape == (16, 8)

    def unexpected_hull(*args, **kwargs):
        raise AssertionError("cache hit should bypass Qhull")

    monkeypatch.setattr(spatial, "ConvexHull", unexpected_hull)
    geometry_adapter._gosset_halfspaces.cache_clear()
    second = geometry_adapter._gosset_halfspaces(str(cache))
    assert np.array_equal(first[0], second[0])
    assert np.array_equal(first[1], second[1])
