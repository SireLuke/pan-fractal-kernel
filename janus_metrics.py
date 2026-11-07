"""Closed-form metrics for the Janus Hydra head maps (diagnostic layer).

The UHFE and UDFE heads in ``janus_hydra`` are affine maps of the normalized
V8 vector x in [0,1]^8:  H = W_f x,  D = W_i x + b_i.  This module recovers
(W_f, W_i, b_i) by probing the *shipped* functions, so it can never drift from
them, and reports structural metrics:

* pair defect  delta_k = H_k + D_k - 1  (identically 0 means the inverse head
  carries no information beyond its formation head),
* ranks / nullities of the head maps,
* the L-infinity Lipschitz constant,
* the uniform-x covariance and correlation of the formation heads,
  Cov = W_f W_f^T / 12 (each coordinate has variance 1/12),
* participation ratio (effective number of independent heads).

Nothing here is a physical claim; the weights are semantic design choices.
"""
from __future__ import annotations

import numpy as np

from janus_hydra import V8_KEYS, V8State, formation_heads, inverse_heads
from hydra_semantic_reader import INVERSE_NAMES, PAIR_KEYS

__all__ = ["head_matrices", "pair_defect", "head_metrics"]


def _state(vec: np.ndarray) -> V8State:
    return V8State(**{k: float(v) for k, v in zip(V8_KEYS, vec)})


def head_matrices() -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (W_f, W_i, b_i), each row ordered as ``PAIR_KEYS``."""
    zero = np.zeros(8)
    f0 = np.array([formation_heads(_state(zero))[k] for k in PAIR_KEYS])
    i0 = np.array([inverse_heads(_state(zero))[INVERSE_NAMES[k]] for k in PAIR_KEYS])
    wf = np.zeros((5, 8))
    wi = np.zeros((5, 8))
    for j in range(8):
        e = np.zeros(8)
        e[j] = 1.0
        fj = formation_heads(_state(e))
        ij = inverse_heads(_state(e))
        wf[:, j] = [fj[k] - f0[r] for r, k in enumerate(PAIR_KEYS)]
        wi[:, j] = [ij[INVERSE_NAMES[k]] - i0[r] for r, k in enumerate(PAIR_KEYS)]
    return wf, wi, i0


def pair_defect(state: V8State) -> dict[str, float]:
    """delta_k = H_k + D_k - 1 for every Janus pair."""
    f, i = formation_heads(state), inverse_heads(state)
    return {k: f[k] + i[INVERSE_NAMES[k]] - 1.0 for k in PAIR_KEYS}


def head_metrics(atol: float = 1e-12) -> dict[str, object]:
    wf, wi, _ = head_matrices()
    sv = np.linalg.svd(wf, compute_uv=False)
    cov = wf @ wf.T / 12.0
    sd = np.sqrt(np.diag(cov))
    corr = cov / np.outer(sd, sd)
    eig = np.linalg.eigvalsh(corr)
    tautological = [k for r, k in enumerate(PAIR_KEYS) if np.allclose(wi[r], -wf[r], atol=atol)]
    return {
        "rank_formation": int(np.linalg.matrix_rank(wf)),
        "rank_stacked": int(np.linalg.matrix_rank(np.vstack([wf, wi]))),
        "nullity_formation": 8 - int(np.linalg.matrix_rank(wf)),
        "singular_values": tuple(float(s) for s in sv),
        "condition_number": float(sv[0] / sv[-1]),
        "lipschitz_linf": float(np.abs(wf).sum(axis=1).max()),
        "participation_ratio": float(eig.sum() ** 2 / (eig ** 2).sum()),
        "correlation": corr,
        "tautological_pairs": tautological,
        "informative_pairs": [k for k in PAIR_KEYS if k not in tautological],
        "coordinate_coverage": {key: int((wf[:, j] > 0).sum()) for j, key in enumerate(V8_KEYS)},
    }
