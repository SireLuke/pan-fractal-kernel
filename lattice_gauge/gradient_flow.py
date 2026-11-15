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


def _exp_antihermitian(a: np.ndarray) -> np.ndarray:
    """exp(A) for anti-Hermitian A, via the Hermitian generator H = -iA (A = iH)."""
    values, vectors = np.linalg.eigh(-1j * a)
    return (vectors * np.exp(1j * values)[..., None, :]) @ dag(vectors)


def wilson_flow_step_rk3(g, step_size: float = 0.01) -> None:
    """One third-order Runge-Kutta Wilson-flow step in place (Luscher, arXiv:1006.4518, App. C).

    Same flow equation and force as `wilson_flow_step`, with Z(V) = -force(V):
        W1 = exp(Z0/4) W0
        W2 = exp(8/9 Z1 - 17/36 Z0) W1
        W3 = exp(3/4 Z2 - 8/9 Z1 + 17/36 Z0) W2
    where Z_i = step_size * Z(W_i). Third order in step_size, so much larger steps
    are stable than for the explicit Euler step.
    """
    if not np.isfinite(step_size) or step_size <= 0:
        raise ValueError("step_size must be finite and positive")

    def z_field(links):
        g.U = links
        return [-step_size * _project_suN(links[mu] @ g.staple(mu)) for mu in range(g.d)]

    w0 = [u.copy() for u in g.U]
    z0 = z_field(w0)
    w1 = [_exp_antihermitian(z / 4.0) @ w for z, w in zip(z0, w0)]
    z1 = z_field(w1)
    w2 = [_exp_antihermitian(8.0 / 9.0 * b - 17.0 / 36.0 * a) @ w
          for a, b, w in zip(z0, z1, w1)]
    z2 = z_field(w2)
    g.U = [_exp_antihermitian(0.75 * c - 8.0 / 9.0 * b + 17.0 / 36.0 * a) @ w
           for a, b, c, w in zip(z0, z1, z2, w2)]


def wilson_flow(g, steps: int, step_size: float = 0.001,
                integrator: str = "euler") -> list[dict[str, float]]:
    """Return raw Wilson action and clover charge at t=0 and every step.

    integrator: "euler" (default, original behaviour) or "rk3" (Luscher third-order).
    """
    steppers = {"euler": wilson_flow_step, "rk3": wilson_flow_step_rk3}
    if integrator not in steppers:
        raise ValueError(f"integrator must be one of {sorted(steppers)}")
    step = steppers[integrator]
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
        step(g, step_size)
        history.append({
            "flow_time": (i + 1) * step_size,
            "action": float(g.action()),
            "topological_charge": float(clover_topological_charge(g)),
        })
    return history
