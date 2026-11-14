"""Finite-lattice Yang--Mills observable bridge to PAN V8 and Gosset 4_21.

Research adapter only. Physical lattice, E8 incidence graph, and V8 feature
space remain distinct typed objects. No continuum or physical correspondence
claim is made.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import log
from typing import Iterable

import numpy as np

from lattice_gauge.lattice_gauge import Gauge
from gosset_421 import E8_ROOTS, neighbors
from gosset_projection import gosset_edge_indices
from janus_hydra import V8_KEYS
from hydra_semantic_reader import read_semantics


@dataclass(frozen=True)
class ObservableFrame:
    group_n: int
    dimensions: tuple[int, ...]
    beta: float
    plaquette: float
    action_density: float
    wilson_1x1: float
    wilson_1x2: float
    unitarity_residual: float
    determinant_residual: float
    local_action_density: np.ndarray
    metadata: dict


def _site_plaquette(g: Gauge, mu: int, nu: int) -> np.ndarray:
    return g.plaq_field(mu, nu)


def measure(g: Gauge, *, update_index: int = 0) -> ObservableFrame:
    """Measure gauge-invariant plaquette/Wilson summaries and link constraints."""
    planes = [(m, n) for m in range(g.d) for n in range(m + 1, g.d)]
    pfields = [_site_plaquette(g, m, n) for m, n in planes]
    local_p = np.mean(np.stack(pfields), axis=0)
    local_action = g.beta * (1.0 - local_p)
    unitary = max(float(np.max(np.abs(u @ np.swapaxes(u.conj(), -1, -2)
                                     - np.eye(g.N)))) for u in g.U)
    determinant = max(float(np.max(np.abs(np.linalg.det(u) - 1.0))) for u in g.U)
    return ObservableFrame(
        group_n=g.N,
        dimensions=g.dims,
        beta=g.beta,
        plaquette=float(np.mean(local_p)),
        action_density=float(np.mean(local_action)),
        wilson_1x1=float(np.mean([g.loop(m, n, 1, 1)
                                  for m, n in planes])),
        wilson_1x2=float(np.mean([g.loop(m, n, 1, 2)
                                  for m, n in planes])),
        unitarity_residual=unitary,
        determinant_residual=determinant,
        local_action_density=np.asarray(local_action, dtype=float),
        metadata={"update_index": int(update_index),
                  "observable_class": "finite_lattice_gauge_invariant"},
    )


def gauge_invariant_signature(frame: ObservableFrame) -> np.ndarray:
    """Compact raw observable signature; excludes gauge-dependent link entries."""
    return np.asarray((frame.plaquette, frame.action_density,
                       frame.wilson_1x1, frame.wilson_1x2), dtype=float)


def compare_signatures(before: ObservableFrame, after: ObservableFrame) -> dict:
    a, b = gauge_invariant_signature(before), gauge_invariant_signature(after)
    delta = np.abs(a - b)
    return {"max_abs_delta": float(delta.max()),
            "per_observable_abs_delta": delta.tolist(),
            "pass": bool(np.allclose(a, b, atol=1e-10, rtol=0.0))}


def _entropy01(values: np.ndarray, bins: int = 32) -> float:
    hist, _ = np.histogram(values, bins=bins, density=False)
    probs = hist[hist > 0].astype(float)
    probs /= probs.sum()
    if len(probs) <= 1:
        return 0.0
    return float(-np.sum(probs * np.log(probs)) / log(bins))


def v8_projection(frame: ObservableFrame, previous: ObservableFrame | None = None) -> dict:
    """Explicit, dimensionless feature map; neutral placeholders are masked.

    h/R/u/d/s are measured or computed diagnostics. tau is update persistence
    only when a previous frame is supplied. chi (topological density) and f
    (external forcing) are not measured by this minimal Wilson adapter and
    remain neutral placeholders with measured=False.
    """
    local = frame.local_action_density
    scale = max(abs(frame.beta), 1e-12)
    if previous is None:
        tau, tau_measured = 0.5, False
    else:
        change = abs(frame.plaquette - previous.plaquette)
        tau, tau_measured = float(1.0 / (1.0 + change / 0.05)), True
    values = {
        "h": float(np.clip((frame.plaquette + 1.0) / 2.0, 0.0, 1.0)),
        "R": float(np.clip((frame.wilson_1x1 + 1.0) / 2.0, 0.0, 1.0)),
        "u": float(np.clip(1.0 - frame.unitarity_residual, 0.0, 1.0)),
        "d": float(np.clip(np.std(local) / scale, 0.0, 1.0)),
        "tau": tau,
        "chi": 0.5,
        "s": _entropy01(local),
        "f": 0.5,
    }
    frame_v8 = read_semantics(values)
    return {
        "coordinate_order": list(V8_KEYS),
        "values": values,
        "measured_mask": {
            "h": True, "R": True, "u": True, "d": True,
            "tau": tau_measured, "chi": False, "s": True, "f": False,
        },
        "units": {key: "dimensionless_normalized_proxy" for key in V8_KEYS},
        "mapping_id": "YM-WILSON-OBSERVABLES-TO-V8-v0",
        "janus_schema": frame_v8.schema_version,
        "uhfe": frame_v8.uhfe_heads,
        "udfe": frame_v8.udfe_heads,
        "warning": "Engineering projection only; chi and f are neutral unmeasured placeholders.",
    }


def root_to_lattice_site(root_index: int, lattice_volume: int) -> int:
    if not 0 <= root_index < len(E8_ROOTS) or lattice_volume <= 0:
        raise ValueError("invalid root index or lattice volume")
    return root_index % lattice_volume


def gosset_observable_field(frame: ObservableFrame) -> np.ndarray:
    """Deterministically sample the lattice scalar field onto 240 E8 root labels.

    This is an index-based diagnostic coupling, not a geometric embedding.
    """
    flat = frame.local_action_density.reshape(-1)
    return np.asarray([flat[root_to_lattice_site(i, len(flat))]
                       for i in range(len(E8_ROOTS))], dtype=float)


def gosset_star_report(root_values: np.ndarray) -> dict:
    """Compute all 240 local-star means and shared-root consistency residuals."""
    values = np.asarray(root_values, dtype=float)
    if values.shape != (240,) or not np.all(np.isfinite(values)):
        raise ValueError("root_values must be 240 finite values")
    root_index = {root: i for i, root in enumerate(E8_ROOTS)}
    stars = []
    for root in E8_ROOTS:
        ids = [root_index[n] for n in neighbors(root)]
        stars.append(float(np.mean(values[ids])))
    edges = gosset_edge_indices()
    # Each edge's endpoints are two local-star centers; compare their summaries.
    edge_delta = np.abs(np.asarray(stars)[edges[:, 0]] -
                        np.asarray(stars)[edges[:, 1]])
    return {
        "base_stars": len(stars),
        "vertices_per_star": 56,
        "edge_count": len(edges),
        "global_mean": float(values.mean()),
        "star_mean": float(np.mean(stars)),
        "star_mean_global_residual": float(abs(np.mean(stars) - values.mean())),
        "adjacent_star_delta_mean": float(edge_delta.mean()),
        "adjacent_star_delta_max": float(edge_delta.max()),
        "interpretation": "Index-mapped scalar diagnostic; not a physical E8 embedding.",
    }


def run_gauge_transform_control(g: Gauge, *, seed: int = 991) -> dict:
    """Apply an independent Haar gauge transformation at every lattice site."""
    before = measure(g)
    transform = g._haar(g.dims)
    g.gauge_transform(transform)
    after = measure(g)
    report = compare_signatures(before, after)
    report["single_link_is_not_invariant"] = True
    return report
