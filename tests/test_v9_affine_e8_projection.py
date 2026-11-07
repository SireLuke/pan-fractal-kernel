import numpy as np
import pytest
from gosset_421 import E8_ROOTS, ROOT_COUNT
from gosset_projection import coordinate_frame, project_gosset_roots
from v9_affine_e8_projection import (
    affine_e8_projection_frame, is_e8_lattice_point, normalize_point_cloud,
    orthogonal_xi_frame, project_gosset_chain_at_xi,
    project_gosset_roots_at_xi, reverse_xi_frame, translate_e8_lattice_points,
)

def test_canonical_e8_roots_are_e8_lattice_points():
    assert len(E8_ROOTS) == ROOT_COUNT == 240
    assert all(is_e8_lattice_point(root) for root in E8_ROOTS)

def test_affine_translation_preserves_lattice_membership_and_differences():
    roots = np.asarray(E8_ROOTS, dtype=float)
    shift = np.asarray(E8_ROOTS[0], dtype=float)
    translated = translate_e8_lattice_points(roots, shift)
    assert all(is_e8_lattice_point(point) for point in translated)
    assert np.allclose(translated[:, None, :] - translated[None, :, :],
                       roots[:, None, :] - roots[None, :, :], atol=1e-12, rtol=0)
    assert not np.array_equal(translated, roots)

def test_center_scale_normalization_is_translation_and_scale_invariant():
    roots = np.asarray(E8_ROOTS, dtype=float)
    shifted = translate_e8_lattice_points(roots, np.asarray(E8_ROOTS[0]))
    assert np.allclose(normalize_point_cloud(roots), normalize_point_cloud(shifted))
    assert np.allclose(normalize_point_cloud(roots), normalize_point_cloud(3.25 * roots))

@pytest.mark.parametrize("xi", [0.0, 0.125, 0.25, 0.5, 0.75, 1.0])
def test_xi_frame_is_orthogonal_and_reverse_is_exact(xi):
    q = orthogonal_xi_frame(xi)
    assert np.allclose(q.T @ q, np.eye(8), atol=1e-12, rtol=0)
    assert np.linalg.det(q) == pytest.approx(1.0, abs=1e-12)
    assert np.allclose(reverse_xi_frame(xi) @ q, np.eye(8), atol=1e-12, rtol=0)

def test_neutral_xi_recovers_existing_coordinate_projection():
    assert np.array_equal(affine_e8_projection_frame(4, 0).matrix, coordinate_frame(8, 4).matrix)
    base, neutral = project_gosset_roots(4), project_gosset_roots_at_xi(4, 0)
    assert np.array_equal(base.projected_points, neutral.projected_points)
    assert np.array_equal(base.source_indices, neutral.source_indices)

def test_full_8d_xi_frame_is_lossless_and_preserves_distances():
    roots = np.asarray(E8_ROOTS, dtype=float)
    for xi in (0.0, 0.125, 0.5, 1.0):
        result = project_gosset_roots_at_xi(8, xi)
        assert result.is_lossless
        assert np.allclose(result.reconstructed_points, roots, atol=1e-12)
        assert np.linalg.norm(result.projected_points[0] - result.projected_points[1]) == pytest.approx(
            np.linalg.norm(roots[0] - roots[1]), abs=1e-12)

def test_lower_dimensional_view_is_lossy_but_retains_root_provenance():
    result = project_gosset_roots_at_xi(2, 0.5)
    assert not result.is_lossless
    assert result.source_points.shape == (240, 8)
    assert result.projected_points.shape == (240, 2)
    assert np.array_equal(result.source_indices, np.arange(240))

def test_xi_chain_is_deterministic_and_keeps_root_indices():
    first, second = project_gosset_chain_at_xi(0.37), project_gosset_chain_at_xi(0.37)
    assert set(first) == {8, 4, 3, 2}
    for dim in (8, 4, 3, 2):
        assert np.array_equal(first[dim].source_indices, np.arange(240))
        assert np.array_equal(first[dim].projected_points, second[dim].projected_points)

def test_xi_and_lattice_inputs_are_validated():
    with pytest.raises(ValueError): orthogonal_xi_frame(-0.01)
    with pytest.raises(ValueError): orthogonal_xi_frame(float("nan"))
    with pytest.raises(ValueError): translate_e8_lattice_points(np.asarray(E8_ROOTS), (0.1,) * 8)
