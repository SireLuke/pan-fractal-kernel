import numpy as np
import pytest

from abom_v8.visualization.radial_shells import PHI, golden_angle_shells


def test_shell_count_radius_scaling_and_shape():
    points = golden_angle_shells(shell_count=4, points_per_shell=24)
    assert points.shape == (4, 24, 2)
    radii = np.linalg.norm(points, axis=2)
    means = radii.mean(axis=1)
    assert np.allclose(means[1:] / means[:-1], PHI)


def test_shell_generator_rejects_invalid_parameters():
    with pytest.raises(ValueError):
        golden_angle_shells(shell_count=0)
    with pytest.raises(ValueError):
        golden_angle_shells(points_per_shell=2)
    with pytest.raises(ValueError):
        golden_angle_shells(scale_ratio=1.0)
