"""Shared data-to-V8 execution bridge for PAN V8 / JOBF.

Raw scientific values remain in their source files. This module only maps
calibrated [0,1] proxies into V8 and records JOBF response diagnostics.
"""
from __future__ import annotations
import numpy as np
from janus_hydra import V8State
from jobf_v0_2 import JanusOctadialBreathingField, sphere_directions, aggregate_heads
from janus_hydra import formation_heads, inverse_heads

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
    """Inject one normalized V8 state into JOBF and return its diagnostics."""
    vector = np.asarray(vector, dtype=float)
    if vector.shape != (8,) or not np.all(np.isfinite(vector)):
        raise ValueError("V8 vector must contain 8 finite values")
    vector = np.clip(vector, 0.0, 1.0)
    state = V8State(**dict(zip(V8_KEYS, map(float, vector))))
    state.validate()

    model = JanusOctadialBreathingField(dt=dt, shape_bias=shape_bias)
    model.base = vector.copy()
    model.state_amp = np.zeros(8, dtype=float)
    baseline = model._state_at(0.0)
    model.h_base = aggregate_heads(formation_heads(baseline))
    model.d_base = aggregate_heads(inverse_heads(baseline), inverse=True)

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
