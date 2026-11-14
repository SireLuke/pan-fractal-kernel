"""Wilson gradient-flow diagnostic for periodic lattice gauge fields.

The flow is a research diagnostic, separate from Monte Carlo sweeps. It uses
the Wilson-action staple and a traceless anti-Hermitian left force. No claim
of continuum topology or integer charge is made by this module.
"""
from __future__ import annotations

import numpy as np

from lattice_gauge.lattice_gauge import dag


def _traceless_antihermitian(a: np.ndarray) -> np.ndarray:
    ah = 0.5 * (a - dag(a))
    tr = np.einsum("...ii->...", ah) / a.shape[-1]
    return ah - tr[..., None, None] * np.eye(a.shape[-1], dtype=complex)


def wilson_flow_step(g, step_size: float = 0.01) -> None:
    """Advance all links by one explicit Wilson-gradient-flow step in place.

    The update is link-local and uses the force projected onto su(N). The
    matrix exponential is evaluated by Hermitian eigendecomposition, retaining
    unitarity to floating-point accuracy.
    """
    if step_size <= 0 or not np.isfinite(step_size):
        raise ValueError("step_size must be finite and positive")
    for mu in range(g.d):
        force = _traceless_antihermitian(g.U[mu] @ g.staple(mu))
        # force = i H with H Hermitian; exp(-eps * force) is unitary.
        hermitian = -1j * force
        values, vectors = np.linalg.eigh(hermitian)
        phases = np.exp(-1j * step_size * values)
        update = (vectors * phases[..., None, :]) @ dag(vectors)
        g.U[mu] = update @ g.U[mu]


def wilson_flow(g, steps: int, step_size: float = 0.01) -> list[dict[str, float]]:
    """Run flow and return action/charge diagnostics at t=0 and each step.

    Requires a four-dimensional lattice for the clover charge. The returned
    charge is the raw finite-lattice clover integral and is not rounded.
    """
    if g.d != 4:
        raise ValueError("Wilson topology flow requires exactly 4 dimensions")
    if steps < 0:
        raise ValueError("steps must be non-negative")
    from lattice_gauge.topology import clover_topological_charge

    history = [{
        "flow_time": 0.0,
        "action": float(g.action()),
        "topological_charge": float(clover_topological_charge(g)),
    }]
    for index in range(steps):
        wilson_flow_step(g, step_size)
        history.append({
            "flow_time": (index + 1) * step_size,
            "action": float(g.action()),
            "topological_charge": float(clover_topological_charge(g)),
        })
    return history
