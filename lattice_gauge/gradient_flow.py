"""Wilson gradient-flow diagnostic for periodic SU(N) lattice gauge fields.

The force is the traceless anti-Hermitian part of U_mu(x) C_mu(x), where
C_mu is the staple oriented from x+mu back to x. It therefore transforms at
the base site and acts by left multiplication on U_mu(x).
"""
from __future__ import annotations
import numpy as np
from lattice_gauge.lattice_gauge import dag


def _project_suN(a: np.ndarray) -> np.ndarray:
    ah = 0.5 * (a - dag(a))
    tr = np.einsum("...ii->...", ah) / a.shape[-1]
    return ah - tr[..., None, None] * np.eye(a.shape[-1], dtype=complex)


def wilson_flow_step(g, step_size: float = 0.001) -> None:
    """One explicit, simultaneous-link Wilson-flow Euler step in place.

    The sign is chosen for descent of S_W = beta sum_p (1 - ReTr U_p/N).
    A small step is required; callers should verify action monotonicity.
    """
    if not np.isfinite(step_size) or step_size <= 0:
        raise ValueError("step_size must be finite and positive")
    old_links = [u.copy() for u in g.U]
    updates = []
    for mu in range(g.d):
        force = _project_suN(old_links[mu] @ g.staple(mu))
        # Force is anti-Hermitian; diagonalize its Hermitian generator.
        hermitian = -1j * force
        values, vectors = np.linalg.eigh(hermitian)
        # exp(-eps * force) is unitary and has determinant one after
        # traceless projection (up to floating-point roundoff).
        phases = np.exp(-1j * step_size * values)
        exp_force = (vectors * phases[..., None, :]) @ dag(vectors)
        updates.append(exp_force @ old_links[mu])
    g.U = updates


def wilson_flow(g, steps: int, step_size: float = 0.001) -> list[dict[str, float]]:
    """Return raw Wilson action and clover charge at t=0 and every step."""
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
    for i in range(steps):
        wilson_flow_step(g, step_size)
        history.append({
            "flow_time": (i + 1) * step_size,
            "action": float(g.action()),
            "topological_charge": float(clover_topological_charge(g)),
        })
    return history
