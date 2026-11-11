import math

import numpy as np
import pytest

import hydrogen_shell_modes as H

STATES = [(1, 0), (2, 0), (2, 1), (3, 0), (3, 1), (3, 2), (4, 2)]


@pytest.mark.parametrize("n,l", STATES)
def test_radial_functions_are_normalised(n, l):
    r = np.linspace(0.0, 250.0, 1_000_001)
    R = H.hydrogen_radial(n, l, r)
    assert abs(np.trapezoid(R * R * r * r, r) - 1.0) < 1e-9


@pytest.mark.parametrize("n,l", STATES)
def test_radial_node_count_matches_n_minus_l_minus_1(n, l):
    r = np.linspace(1e-6, 120.0, 2_000_001)
    R = H.hydrogen_radial(n, l, r)
    crossings = int(np.sum(np.sign(R[:-1]) != np.sign(R[1:])))
    assert crossings == H.radial_node_count(n, l) == n - l - 1


def test_known_radial_node_positions():
    assert abs(float(H.hydrogen_radial(2, 0, 2.0))) < 1e-14
    assert abs(float(H.hydrogen_radial(3, 1, 6.0))) < 1e-14
    assert abs(float(H.hydrogen_radial(4, 2, 12.0))) < 1e-14          # the 12 a0 node in the reel
    for r0 in (1.5 * (3 - math.sqrt(3)), 1.5 * (3 + math.sqrt(3))):   # 3s nodes
        assert abs(float(H.hydrogen_radial(3, 0, r0))) < 1e-12


def _sphere_quadrature(deg=12):
    x, w = np.polynomial.legendre.leggauss(deg)
    phi = (np.arange(2 * deg) + 0.5) * math.pi / deg
    ct, ph = np.meshgrid(x, phi, indexing="ij")
    st = np.sqrt(1 - ct**2)
    xyz = np.stack([st * np.cos(ph), st * np.sin(ph), ct], axis=-1).reshape(-1, 3)
    wt = (np.repeat(w[:, None], 2 * deg, axis=1) * (math.pi / deg)).reshape(-1)
    return xyz, wt


def test_real_ylm_are_orthonormal_on_the_sphere():
    xyz, wt = _sphere_quadrature()
    cols = np.stack([H.real_ylm(l, m, xyz) for l, m in H.solid_basis_labels()], axis=1)
    gram = cols.T @ (cols * wt[:, None])
    assert np.allclose(gram, np.eye(9), atol=1e-12)


def test_y20_conical_node_is_the_magic_angle():
    theta = math.acos(1 / math.sqrt(3))
    p = np.array([[math.sin(theta), 0.0, math.cos(theta)]])
    assert abs(float(H.real_ylm(2, 0, p)[0])) < 1e-14
    assert abs(math.degrees(theta) - 54.7356103172) < 1e-9


def test_projected_radius_moments():
    assert H.projected_radius_moment(0) == pytest.approx(1.0)
    assert H.projected_radius_moment(1) == pytest.approx(3 / 8)      # 3 of 8 dimensions
    assert H.projected_radius_moment(2) == pytest.approx(3 / 8 * 5 / 10)


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("seed", [421, 7, 73])
def test_shell_solid_harmonic_gram_is_exactly_isotropic(n, seed):
    """Spherical 7-design + harmonic polynomials: exact for every orthonormal 3-frame."""
    assert H.solid_gram_error(H.shell_view(n, seed)) < 1e-12


@pytest.mark.parametrize("n", [1, 2, 3])
def test_iid_null_is_not_exact(n):
    rng = np.random.default_rng(2026 + n)
    N = len(H.shell_unit_points(n))
    u = rng.normal(size=(N, 8))
    u /= np.linalg.norm(u, axis=1)[:, None]
    err = H.solid_gram_error(H.project_points(u, H.seeded_3d_rows(421)))
    assert err > 1e-4


def test_design_boundary_radial_moments_exact_to_degree_7_only():
    p = H.shell_view(1, 421)
    rho2 = (p**2).sum(1)
    for k in (1, 2, 3):
        assert abs(np.mean(rho2**k) - H.projected_radius_moment(k)) < 1e-12
    assert abs(np.mean(rho2**4) - H.projected_radius_moment(4)) > 1e-6   # degree 8: no longer a design


@pytest.mark.parametrize("n", [1, 2, 3])
def test_hydrogen_cross_lm_overlap_beats_direction_shuffled_null_at_small_scale(n):
    """Same radii, random directions as null. Advantage is claimed at length_scale 2 only."""
    states = H.states_up_to(3)
    p = H.shell_view(n, 421)
    rho = np.linalg.norm(p, axis=1)
    e8 = H.max_cross_lm_overlap(p, states, length_scale=2.0)
    rng = np.random.default_rng(99 + n)
    nulls = []
    for _ in range(20):
        d = rng.normal(size=p.shape)
        d /= np.linalg.norm(d, axis=1)[:, None]
        nulls.append(H.max_cross_lm_overlap(d * rho[:, None], states, length_scale=2.0))
    assert e8 < 0.25 * min(nulls)


def test_input_validation():
    with pytest.raises(ValueError):
        H.hydrogen_radial(5, 0, 1.0)
    with pytest.raises(ValueError):
        H.solid_harmonic(3, 0, np.zeros((1, 3)))
    with pytest.raises(ValueError):
        H.solid_harmonic(1, 2, np.zeros((1, 3)))
    with pytest.raises(ValueError):
        H.hydrogen_psi(1, 0, 0, np.ones((2, 3)), length_scale=0.0)
    with pytest.raises(ValueError):
        H.hydrogen_psi(1, 0, 0, np.ones((2, 3)), length_scale=float("nan"))
    with pytest.raises(ValueError):
        H.project_points(np.ones((2, 8)), np.ones((3, 8)))
    with pytest.raises(ValueError):
        H.radial_node_count(2, 2)
    with pytest.raises(ValueError):
        H.states_up_to(4)
    with pytest.raises(ValueError):
        H.hydrogen_overlap_matrix(np.zeros((3, 3)), [(1, 0, 0), (2, 1, 0)])
