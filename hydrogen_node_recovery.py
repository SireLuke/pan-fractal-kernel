"""Node recovery: can the projected E8 / 5_21 shell cloud reproduce hydrogen's nodal-domain count?

A real orbital psi_nlm restricted to the ball of radius r_max has
    domains = (1 + #radial nodes of R_nl below r_max) x A(l, m),
    A(l, 0) = l + 1,   A(l, m != 0) = 2|m| (l - |m| + 1).
(radial shells are separated by nodal spheres; within a shell the angular nodal cones and
planes cut the shell into A(l, m) pieces). This module counts strong nodal domains of psi on the
cloud (connected components of the positive and negative sets, inside a fixed k-nearest-neighbour
graph) and scores exact recovery against that ground truth and against a direction-shuffled null.

Declared procedure (fixed before the evaluation run; see HYDROGEN_NODE_RECOVERY.md):
  * graph: symmetrised k-nearest-neighbour graph in 3D, k fixed per run;
  * a point is "near zero" if |psi| < EPS_FRACTION * max|psi| and is excluded;
  * components smaller than MIN_COMPONENT_FRACTION * N are ignored as sampling noise;
  * a state is NOT scored if one of its radial nodes lies within AMBIGUOUS_BAND * r_max.
A recovery score is a software/numerical result on a finite point cloud, not evidence of a
physical correspondence.
"""
from __future__ import annotations

import math

import numpy as np
from scipy.sparse import coo_matrix
from scipy.sparse.csgraph import connected_components
from scipy.spatial import cKDTree

try:
    from . import hydrogen_shell_modes as H
    from . import hydrogen_shell_scale as S
except ImportError:
    import hydrogen_shell_modes as H
    import hydrogen_shell_scale as S

EPS_FRACTION = 0.05
MIN_COMPONENT_FRACTION = 0.005
AMBIGUOUS_BAND = (0.8, 1.0)      # radial nodes in this fraction of r_max make a state unscored
PRIMARY_K = 10
SENSITIVITY_K = (6, 10, 16)


def radial_node_radii(n: int, l: int) -> tuple:
    """Exact radial node radii (a0) of R_nl for the supported states."""
    r3 = math.sqrt(3.0)
    nodes = {(1, 0): (), (2, 0): (2.0,), (2, 1): (), (3, 0): (1.5 * (3 - r3), 1.5 * (3 + r3)),
             (3, 1): (6.0,), (3, 2): (), (4, 2): (12.0,)}
    if (n, l) not in nodes:
        raise ValueError(f"unsupported state (n={n}, l={l})")
    return nodes[(n, l)]


def angular_domain_count(l: int, m: int) -> int:
    if l < 0 or abs(m) > l:
        raise ValueError("require |m| <= l")
    return l + 1 if m == 0 else 2 * abs(m) * (l - abs(m) + 1)


def expected_domains(n: int, l: int, m: int, r_max: float):
    """Ground-truth nodal-domain count inside radius r_max, or None if a node is ambiguous."""
    if not (math.isfinite(r_max) and r_max > 0):
        raise ValueError("r_max must be finite and positive")
    lo, hi = AMBIGUOUS_BAND
    inside = 0
    for r0 in radial_node_radii(n, l):
        if lo * r_max <= r0 <= hi * r_max:
            return None
        if r0 < lo * r_max:
            inside += 1
    return (1 + inside) * angular_domain_count(l, m)


def knn_graph(points: np.ndarray, k: int):
    """Symmetrised k-nearest-neighbour adjacency (CSR, unweighted)."""
    if not (isinstance(k, int) and 1 <= k < len(points)):
        raise ValueError("k must be an integer with 1 <= k < N")
    _, idx = cKDTree(points).query(points, k=k + 1)
    rows = np.repeat(np.arange(len(points)), k)
    a = coo_matrix((np.ones(rows.size), (rows, idx[:, 1:].reshape(-1))), shape=(len(points),) * 2).tocsr()
    return ((a + a.T) > 0).astype(np.int8).tocsr()


def count_domains(psi: np.ndarray, graph) -> int:
    """Strong nodal domains of psi on the graph (see module docstring for the filters)."""
    psi = np.asarray(psi, dtype=float)
    scale = float(np.max(np.abs(psi)))
    if not scale > 0:
        raise ValueError("psi vanishes on every sampled point")
    keep_min = max(1, int(math.ceil(MIN_COMPONENT_FRACTION * len(psi))))
    total = 0
    for sign in (1.0, -1.0):
        idx = np.where(sign * psi > EPS_FRACTION * scale)[0]
        if idx.size == 0:
            continue
        sub = graph[idx][:, idx]
        _, lab = connected_components(sub, directed=False)
        total += int(np.sum(np.bincount(lab) >= keep_min))
    return total


def score_cloud(points: np.ndarray, scale: float, states, k: int = PRIMARY_K) -> dict:
    """Recovery of expected domain counts on one cloud (scored states only)."""
    r_max = scale * float(np.max(np.linalg.norm(points, axis=1)))
    graph = knn_graph(points, k)
    hits, errs, rows = 0, [], []
    for n, l, m in states:
        exp = expected_domains(n, l, m, r_max)
        if exp is None:
            continue
        got = count_domains(H.hydrogen_psi(n, l, m, points, scale), graph)
        hits += int(got == exp)
        errs.append(abs(got - exp))
        rows.append({"state": [n, l, m], "expected": exp, "got": got})
    scored = len(rows)
    return {"scored": scored, "recovery_rate": hits / scored if scored else None,
            "mean_abs_error": float(np.mean(errs)) if errs else None, "per_state": rows, "r_max_a0": r_max}


def evaluate(n_shell: int, rule: str, seed: int = 421, k: int = PRIMARY_K, null_trials: int = 100,
             null_seed: int = 777) -> dict:
    """E8 recovery vs a direction-shuffled null (same radii, random directions)."""
    scale = S.scale_for_shell(rule, n_shell, seed)
    p = H.shell_view(n_shell, seed)
    states = H.states_up_to(n_shell)
    e8 = score_cloud(p, scale, states, k)
    rho = np.linalg.norm(p, axis=1)
    rng = np.random.default_rng([null_seed, n_shell, k])
    rates, maes = [], []
    for _ in range(null_trials):
        d = rng.normal(size=p.shape)
        d /= np.linalg.norm(d, axis=1)[:, None]
        r = score_cloud(d * rho[:, None], scale, states, k)
        rates.append(r["recovery_rate"]); maes.append(r["mean_abs_error"])
    rates = np.array(rates, dtype=float)
    p95 = float(np.percentile(rates, 95))
    return {"shell": n_shell, "rule": rule, "seed": seed, "k": k, "scale_a0_per_unit": scale,
            "e8": e8, "null_trials": null_trials, "null_rate_mean": float(rates.mean()),
            "null_rate_p95": p95, "null_mae_mean": float(np.mean(maes)),
            "passes": bool(e8["recovery_rate"] is not None and e8["recovery_rate"] > p95 and e8["recovery_rate"] >= 0.5)}


def evaluate_subsampled(n_shell: int, rule: str, n_sub: int, trials: int = 20, seed: int = 421,
                        k: int = PRIMARY_K, null_seed: int = 888) -> dict:
    """Low-N stress (exploratory): random n_sub-point subsets of the shell view vs direction-shuffled
    subsets with the same radii. Reports mean recovery rates; no pass/fail criterion."""
    scale = S.scale_for_shell(rule, n_shell, seed)
    p = H.shell_view(n_shell, seed)
    if not (isinstance(n_sub, int) and k < n_sub <= len(p)):
        raise ValueError("require k < n_sub <= shell size")
    states = H.states_up_to(n_shell)
    rng = np.random.default_rng([null_seed, n_shell, n_sub])
    e8_rates, null_rates = [], []
    for _ in range(trials):
        sub = p[rng.choice(len(p), size=n_sub, replace=False)]
        e8_rates.append(score_cloud(sub, scale, states, k)["recovery_rate"])
        d = rng.normal(size=sub.shape)
        d /= np.linalg.norm(d, axis=1)[:, None]
        null_rates.append(score_cloud(d * np.linalg.norm(sub, axis=1)[:, None], scale, states, k)["recovery_rate"])
    return {"shell": n_shell, "rule": rule, "n_sub": n_sub, "trials": trials,
            "e8_mean_rate": float(np.mean(e8_rates)), "null_mean_rate": float(np.mean(null_rates))}
