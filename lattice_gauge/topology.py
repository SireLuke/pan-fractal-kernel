"""Clover topological-density diagnostic for periodic 4D SU(N) lattices.

This is an unsmoothed finite-lattice estimator. Its normalization is a
convention for a dimensionless diagnostic; it is not claimed to be integer
quantized at finite spacing or to establish continuum topology.
"""
from __future__ import annotations

import numpy as np

from lattice_gauge.lattice_gauge import dag


def _shifted_plaquette(g, mu: int, nu: int, offset: dict[int, int]):
    """Plaquette based at x+offset, parallel-transported back to x."""
    links = [g.sh(u, offset) for u in g.U]
    p = (
        links[mu]
        @ g.sh(links[nu], {mu: 1})
        @ dag(g.sh(links[mu], {nu: 1}))
        @ dag(links[nu])
    )
    if not offset:
        return p
    if offset == {mu: -1}:
        # W transports color from x-mu to x. W† P W transforms at x.
        transporter = g.sh(g.U[mu], {mu: -1})
    elif offset == {nu: -1}:
        transporter = g.sh(g.U[nu], {nu: -1})
    elif offset == {mu: -1, nu: -1}:
        # Path from x-mu-nu to x: first +mu, then +nu.
        u_mu = g.sh(g.U[mu], {mu: -1, nu: -1})
        u_nu = g.sh(g.U[nu], {nu: -1})
        transporter = u_mu @ u_nu
    else:
        raise ValueError("unsupported clover offset")
    return dag(transporter) @ p @ transporter


def clover_field_strength(g, mu: int, nu: int) -> np.ndarray:
    """Hermitian traceless clover F_mu_nu at every lattice site."""
    if g.d != 4:
        raise ValueError("clover topological density requires exactly 4 dimensions")
    if not (0 <= mu < 4 and 0 <= nu < 4 and mu != nu):
        raise ValueError("mu and nu must be distinct axes in [0, 3]")
    if mu > nu:
        return -clover_field_strength(g, nu, mu)

    offsets = (
        {},
        {mu: -1},
        {mu: -1, nu: -1},
        {nu: -1},
    )
    q = sum((_shifted_plaquette(g, mu, nu, off) for off in offsets))
    f = (q - dag(q)) / (8.0j)
    trace = np.einsum("...ii->...", f) / g.N
    f = f - trace[..., None, None] * np.eye(g.N, dtype=complex)
    return f


def clover_topological_density(g) -> np.ndarray:
    """Return local q(x) = Tr(F01 F23 - F02 F13 + F03 F12)/(4 pi^2)."""
    if g.d != 4:
        raise ValueError("clover topological density requires exactly 4 dimensions")
    f01 = clover_field_strength(g, 0, 1)
    f02 = clover_field_strength(g, 0, 2)
    f03 = clover_field_strength(g, 0, 3)
    f12 = clover_field_strength(g, 1, 2)
    f13 = clover_field_strength(g, 1, 3)
    f23 = clover_field_strength(g, 2, 3)

    def trace_product(a, b):
        return np.einsum("...ij,...ji->...", a, b).real

    return (
        trace_product(f01, f23)
        - trace_product(f02, f13)
        + trace_product(f03, f12)
    ) / (4.0 * np.pi**2)


def clover_topological_charge(g) -> float:
    """Volume integral of the unsmoothed clover density."""
    return float(np.sum(clover_topological_density(g)))
