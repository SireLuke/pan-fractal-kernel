import numpy as np
import pytest

from abom_v8.diagnostics.cartesian import curl, divergence, gradient, laplacian


def grid(n=9):
    axis = np.linspace(-2.0, 2.0, n)
    return np.meshgrid(axis, axis, axis, indexing="ij"), axis[1] - axis[0]


def test_gradient_and_laplacian_of_quadratic_scalar_field():
    (x, y, z), step = grid()
    field = x*x + y*y
    grad = gradient(field, step)
    lap = laplacian(field, step)
    expected = np.stack((2*x, 2*y, np.zeros_like(z)))
    assert np.allclose(grad[:, 2:-2, 2:-2, 2:-2], expected[:, 2:-2, 2:-2, 2:-2])
    assert np.allclose(lap[2:-2, 2:-2, 2:-2], 4.0, atol=1e-10)


def test_divergence_of_radial_linear_field():
    (x, y, z), step = grid()
    field = np.stack((x, y, z))
    assert np.allclose(divergence(field, step), 3.0, atol=1e-10)


def test_curl_of_planar_rotation_matches_reference_example():
    (x, y, z), step = grid()
    field = np.stack((-y, x, np.zeros_like(z)))
    result = curl(field, step)
    assert np.allclose(result[0], 0.0, atol=1e-10)
    assert np.allclose(result[1], 0.0, atol=1e-10)
    assert np.allclose(result[2], 2.0, atol=1e-10)


def test_operator_input_validation():
    with pytest.raises(ValueError):
        gradient(np.zeros((3, 3)), 1.0)
    with pytest.raises(ValueError):
        divergence(np.zeros((2, 3, 3, 3)), 1.0)
    with pytest.raises(ValueError):
        gradient(np.zeros((3, 3, 3)), 0.0)
