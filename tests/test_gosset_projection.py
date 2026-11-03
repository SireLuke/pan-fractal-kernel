import numpy as np
import pytest

from gosset_421 import E8_ROOTS, ROOT_COUNT
from gosset_projection import (
    ProjectionFrame, coordinate_frame, gosset_edge_indices,
    project_gosset_chain, project_gosset_roots, project_points,
    v8_channel_metadata,
)


def test_coordinate_projection_shapes_and_source_identity():
    result = project_gosset_roots(4)
    assert result.source_points.shape == (240, 8)
    assert result.projected_points.shape == (240, 4)
    assert np.array_equal(result.source_indices, np.arange(240))
    assert result.frame.name == "coordinate_8d_to_4d"


def test_projection_is_explicitly_lossy_and_reports_reconstruction_error():
    result = project_gosset_roots(3)
    assert not result.is_lossless
    assert np.all(result.residual_norms >= 0)
    assert result.maximum_reconstruction_error > 0
    assert result.reconstructed_points.shape == (240, 8)
    assert np.allclose(result.reconstructed_points[:, 3:], 0.0)


def test_identity_frame_is_lossless_and_round_trips():
    points = np.asarray(E8_ROOTS)
    result = project_points(points, coordinate_frame(8, 8))
    assert result.is_lossless
    assert result.maximum_reconstruction_error == pytest.approx(0.0)
    assert result.reconstructed_points == pytest.approx(points)


def test_custom_orthonormal_frame_and_reconstruction():
    angle = 0.37
    frame = ProjectionFrame(np.array([
        [np.cos(angle), np.sin(angle), 0.0, 0.0],
        [-np.sin(angle), np.cos(angle), 0.0, 0.0],
    ]), "rotated_xy")
    points = np.array([[1.0, 2.0, 0.0, 0.0], [-3.0, .5, 0.0, 0.0]])
    result = project_points(points, frame)
    assert result.is_lossless
    assert result.reconstructed_points == pytest.approx(points)


def test_projection_frame_rejects_nonorthonormal_or_nonfinite_matrix():
    with pytest.raises(ValueError):
        ProjectionFrame(np.array([[1.0, 1.0, 0.0]]))
    with pytest.raises(ValueError):
        ProjectionFrame(np.array([[np.nan, 0.0]]))


def test_projection_rejects_bad_points_and_bad_source_indices():
    frame = coordinate_frame(8, 3)
    with pytest.raises(ValueError):
        project_points(np.ones((2, 7)), frame)
    with pytest.raises(ValueError):
        project_points(np.ones((2, 8)), frame, source_indices=[0])
    bad = np.ones((1, 8))
    bad[0, 0] = np.inf
    with pytest.raises(ValueError):
        project_points(bad, frame)


def test_view_ladder_dimensions_and_loss_are_explicit():
    chain = project_gosset_chain()
    assert set(chain) == {8, 4, 3, 2}
    assert chain[8].is_lossless
    assert chain[4].projected_points.shape == (240, 4)
    assert chain[3].projected_points.shape == (240, 3)
    assert chain[2].projected_points.shape == (240, 2)
    assert not chain[4].is_lossless
    assert not chain[3].is_lossless
    assert not chain[2].is_lossless
    assert np.array_equal(chain[4].source_indices, np.arange(ROOT_COUNT))


def test_gosset_adjacency_overlay_is_source_space_and_canonical():
    edges = gosset_edge_indices()
    assert edges.shape == (6720, 2)
    assert np.all(edges[:, 0] < edges[:, 1])
    assert np.all(edges >= 0) and np.all(edges < ROOT_COUNT)
    # Projection collisions do not alter the original edge identity.
    projected = project_gosset_roots(2)
    assert np.array_equal(projected.source_indices[edges[:, 0]], edges[:, 0])


def test_v8_channel_labels_remain_canonical_and_separate_from_root_indices():
    assert v8_channel_metadata() == ("h", "R", "u", "d", "tau", "chi", "s", "f")
    assert len(E8_ROOTS) == 240
