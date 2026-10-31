#!/usr/bin/env python3
"""JOBF v0.2 — Janus Octadial Breathing Field driven by Janus Hydra.

All semantic interpretation is routed through hydra_semantic_reader.py:
normalized V8 -> paired UHFE/UDFE head language -> eight V8 channels -> JOBF.
Dependencies: numpy, matplotlib
"""
from __future__ import annotations

import argparse
import csv
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

try:
    from .janus_hydra import V8State, golden_angle_phases
    from .hydra_semantic_reader import read_semantics, project_heads, HEAD_SUPPORT, INVERSE_NAMES
except ImportError:
    from janus_hydra import V8State, golden_angle_phases
    from hydra_semantic_reader import read_semantics, project_heads, HEAD_SUPPORT, INVERSE_NAMES

DIM = 8
KEYS = ("h", "R", "u", "d", "tau", "chi", "s", "f")
SUPPORT = HEAD_SUPPORT


def sphere_directions(count: int, seed: int = 19) -> np.ndarray:
    rng = np.random.default_rng(seed)
    directions = rng.normal(size=(count, DIM))
    return directions / np.linalg.norm(directions, axis=1, keepdims=True)


def base_radius(directions: np.ndarray) -> np.ndarray:
    """Radial function for H8={q: sum_i |q_i| <= 1}, unit directions."""
    return 1.0 / np.maximum(np.abs(directions).sum(axis=1), 1e-12)


def aggregate_heads(head_scores: dict[str, float], inverse: bool = False) -> np.ndarray:
    """Compatibility wrapper; canonical projection lives in the semantic reader."""
    return project_heads(head_scores, inverse=inverse)


class JanusOctadialBreathingField:
    """JOBF dynamics with the Hydra Semantic Reader as its sole semantic gateway."""

    def __init__(self, dt=0.01, shape_bias=0.0, softening=0.25):
        if dt <= 0 or not np.isfinite(dt):
            raise ValueError("dt must be finite and positive")
        self.dt = float(dt)
        self.shape_bias = float(shape_bias)
        self.softening = float(softening)
        if self.softening <= 0:
            raise ValueError("softening must be positive")

        self.base = np.array([.60, .62, .58, .38, .61, .55, .64, .57])
        self.state_amp = np.array([.035, .030, .032, .028, .025, .030, .027, .033])
        self.state_omega = np.array([.83, .91, .77, 1.09, .72, .96, .88, 1.03])
        self.phase = np.asarray(golden_angle_phases())
        self.phase_offset = self.phase[::-1].copy()

        self.global_amp, self.global_omega = .10, 1.0
        self.local_amp, self.local_omega = .045, 1.17
        self.k_h, self.k_d, self.k_hd = 1.0, 1.0, .20
        self.k_global_coupling = .12

        baseline = read_semantics(self._state_at(0.0))
        self.h_base = baseline.uhfe_channels.copy()
        self.d_base = baseline.udfe_channels.copy()

    def _state_at(self, t: float) -> V8State:
        values = self.base + self.state_amp * np.cos(self.state_omega*t + self.phase)
        return V8State(**dict(zip(KEYS, map(float, values))))

    def fields(self, t: float):
        """Read one V8 state through the canonical Janus semantic pipeline."""
        frame = read_semantics(self._state_at(t))
        return (frame.state, frame.uhfe_heads, frame.udfe_heads,
                frame.uhfe_channels, frame.udfe_channels)

    def channel_state(self, t: float):
        state, uh_heads, ud_heads, uh, ud = self.fields(t)
        uh_delta, ud_delta = uh-self.h_base, ud-self.d_base
        cross = uh_delta * ud_delta
        local = self.local_amp * np.cos(self.local_omega*t + self.phase_offset)
        channels = self.k_h*uh_delta - self.k_d*ud_delta + self.k_hd*cross + local
        field_contrast = float(np.mean(uh_delta - ud_delta))
        global_breath = (
            self.global_amp*np.cos(self.global_omega*t)
            + self.k_global_coupling*field_contrast
        )
        return global_breath, channels, state, uh_heads, ud_heads, uh, ud, cross

    def boundary(self, directions: np.ndarray, t: float):
        if directions.ndim != 2 or directions.shape[1] != DIM:
            raise ValueError("directions must have shape (N, 8)")
        rho0 = base_radius(directions)
        weights = directions**2
        weights /= weights.sum(axis=1, keepdims=True)
        gb, channels, state, uh_heads, ud_heads, uh, ud, cross = self.channel_state(t)
        exponent = gb + weights @ channels
        if self.shape_bias:
            q = directions * rho0[:, None]
            r2 = np.sum(q*q, axis=1)
            exponent += -self.shape_bias / np.sqrt(r2 + self.softening**2)
        rho = rho0 * np.exp(exponent)
        diagnostics = {
            "global_breath": gb, "channels": channels, "state": state,
            "uhfe_heads": uh_heads, "udfe_heads": ud_heads,
            "uhfe_channels": uh, "udfe_channels": ud, "interference": cross,
        }
        return rho, rho0, exponent, diagnostics

    def simulate(self, steps=1200, samples=4096, seed=19):
        if steps < 2 or samples < 100:
            raise ValueError("Use steps >= 2 and samples >= 100.")
        directions = sphere_directions(samples, seed)
        times = np.arange(steps)*self.dt
        rows, snapshots = [], {}
        snap_ids = set(np.linspace(0, steps-1, 7, dtype=int))
        previous_mean = None
        for k, t in enumerate(times):
            rho, rho0, _, diag = self.boundary(directions, float(t))
            mean_r = float(rho.mean())
            velocity = 0.0 if previous_mean is None else (mean_r-previous_mean)/self.dt
            previous_mean = mean_r
            row = {
                "time": float(t), "mean_radius": mean_r,
                "baseline_mean_radius": float(rho0.mean()),
                "mean_radial_velocity": velocity,
                "min_radius": float(rho.min()), "max_radius": float(rho.max()),
                "global_breath": float(diag["global_breath"]),
                "uhfe_mean": float(np.mean(list(diag["uhfe_heads"].values()))),
                "udfe_mean": float(np.mean(list(diag["udfe_heads"].values()))),
                "mean_abs_interference": float(np.abs(diag["interference"]).mean()),
                "channel_spread": float(diag["channels"].std()),
                "boundary_positive": bool(np.all(np.isfinite(rho)) and np.all(rho > 0)),
            }
            for i, key in enumerate(KEYS):
                row[f"v8_{key}"] = float(getattr(diag["state"], key))
                row[f"uhfe_channel_{key}"] = float(diag["uhfe_channels"][i])
                row[f"udfe_channel_{key}"] = float(diag["udfe_channels"][i])
                row[f"breath_channel_{key}"] = float(diag["channels"][i])
            rows.append(row)
            if k in snap_ids:
                snapshots[k] = rho.copy()
        return times, directions, rows, snapshots


def write_metrics(rows, path):
    with path.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def plot_diagnostics(model, times, directions, rows, snapshots, path):
    fig, axes = plt.subplots(2, 2, figsize=(14, 10), constrained_layout=True)
    ax = axes[0, 0]
    ax.plot(times, [r["mean_radius"] for r in rows], label="deformed boundary")
    ax.plot(times, [r["baseline_mean_radius"] for r in rows], "--", label="H8 baseline")
    ax.set(title="Whole-domain breathing", xlabel="model time", ylabel="mean radius")
    ax.legend()
    ax = axes[0, 1]
    for key in KEYS:
        ax.plot(times, [r[f"breath_channel_{key}"] for r in rows], label=key)
    ax.set(title="Eight Hydra-reader-driven V8 channels", xlabel="model time", ylabel="channel deformation")
    ax.legend(ncol=2, fontsize=8)
    ax = axes[1, 0]
    ax.plot(times, [r["uhfe_mean"] for r in rows], label="UHFE head mean")
    ax.plot(times, [r["udfe_mean"] for r in rows], label="UDFE inverse-head mean")
    ax.set(title="Independent Janus Hydra fields", xlabel="model time", ylabel="mean head score")
    ax.legend()
    ax = axes[1, 1]
    for k, rho in snapshots.items():
        points = directions*rho[:, None]
        ax.scatter(points[:, 0], points[:, 1], s=3, alpha=.20, label=f"t={times[k]:.2f}")
    ax.set_aspect("equal", adjustable="datalim")
    ax.set(title="2D projection of sampled 8D boundary", xlabel="q1", ylabel="q2")
    ax.legend(fontsize=7)
    fig.suptitle("JOBF v0.2 — Janus Hydra semantic-reader-driven breathing field")
    fig.savefig(path, dpi=180)
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=1200)
    parser.add_argument("--dt", type=float, default=.01)
    parser.add_argument("--samples", type=int, default=4096)
    parser.add_argument("--shape-bias", type=float, default=0.0)
    parser.add_argument("--output", type=Path, default=Path("jobf_output"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model = JanusOctadialBreathingField(args.dt, args.shape_bias)
    times, directions, rows, snapshots = model.simulate(args.steps, args.samples)
    csv_path = args.output/"jobf_v0_2_metrics.csv"
    png_path = args.output/"jobf_v0_2_diagnostics.png"
    write_metrics(rows, csv_path)
    plot_diagnostics(model, times, directions, rows, snapshots, png_path)
    print("JOBF v0.2 complete")
    print(f"steps={args.steps}; dt={args.dt}; samples={args.samples}")
    print(f"all_boundaries_positive={all(r['boundary_positive'] for r in rows)}")
    print(f"mean_radius_range=({min(r['mean_radius'] for r in rows):.6f}, "
          f"{max(r['mean_radius'] for r in rows):.6f})")
    print(f"metrics: {csv_path}")
    print(f"plot: {png_path}")


if __name__ == "__main__":
    main()
