"""Shared data-to-V8 execution bridge for PAN V8 / JOBF.

Raw scientific values remain in their source files. Calibrated [0,1] proxies
enter the canonical Janus Hydra Semantic Reader before JOBF evaluation.
"""
from __future__ import annotations
import numpy as np
from hydra_semantic_reader import read_semantics
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions

V8_KEYS = ("h", "R", "u", "d", "tau", "chi", "s", "f")


def robust01(values):
    x = np.asarray(values, dtype=float)
    finite = np.isfinite(x)
    if not finite.any():
        raise ValueError("Cannot scale a feature with no finite values")
    lo, hi = np.nanpercentile(x[finite], [5, 95])
    y = np.full(x.shape, .5) if hi <= lo else np.clip((x-lo)/(hi-lo), 0, 1)
    y[~finite] = .5
    return y


def run_v8_jobf(vector, *, steps=24, dt=.01, samples=256, seed=17, shape_bias=0.0):
    """Inject one normalized V8 state through the semantic reader into JOBF."""
    frame = read_semantics(vector)
    state = frame.state
    vector = np.asarray([getattr(state, key) for key in V8_KEYS], dtype=float)

    model = JanusOctadialBreathingField(dt=dt, shape_bias=shape_bias)
    model.base = vector.copy()
    model.state_amp = np.zeros(8, dtype=float)
    baseline = read_semantics(state)
    model.h_base = baseline.uhfe_channels.copy()
    model.d_base = baseline.udfe_channels.copy()

    directions = sphere_directions(samples, seed=seed)
    times = np.arange(steps, dtype=float) * dt
    mean_radius, interference = [], []
    positive = True
    for t in times:
        rho, _, _, diag = model.boundary(directions, float(t))
        mean_radius.append(float(np.mean(rho)))
        interference.append(float(np.mean(np.abs(diag["interference"]))))
        positive &= bool(np.all(np.isfinite(rho)) and np.all(rho > 0))
    return {
        "jobf_radius_initial": mean_radius[0],
        "jobf_radius_final": mean_radius[-1],
        "jobf_radius_min": min(mean_radius),
        "jobf_radius_max": max(mean_radius),
        "jobf_interference_mean_abs": float(np.mean(interference)),
        "jobf_boundary_positive": positive,
    }
