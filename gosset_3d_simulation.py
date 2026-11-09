"""Time-varying 3D view of the Gosset 4_21 boundary under JOBF dynamics.

The canonical object is the 240-vertex E8 root polytope in R^8. This module
shows a deterministic orthographic 3D projection of those vertices and a
sampled radial deformation. It does not claim that the projection is the
full 8D object or a physical manifold.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt

try:
    from .gosset_421 import E8_ROOTS
    from .gosset_projection import ProjectionFrame, project_points
    from .jobf_v0_2 import JanusOctadialBreathingField
except ImportError:
    from gosset_421 import E8_ROOTS
    from gosset_projection import ProjectionFrame, project_points
    from jobf_v0_2 import JanusOctadialBreathingField

KEYS = ("h", "R", "u", "d", "tau", "chi", "s", "f")


def seeded_view(seed: int = 421) -> ProjectionFrame:
    """Return a reproducible, orthonormal 3x8 viewing frame (not canonical)."""
    rng = np.random.default_rng(seed)
    rows = rng.normal(size=(8, 3))
    q, _ = np.linalg.qr(rows)
    return ProjectionFrame(q.T, name=f"seeded_3d_view_{seed}")


def deformed_gosset_vertices(model: JanusOctadialBreathingField, t: float):
    """Evaluate JOBF's radial multiplier on the 240 canonical root directions."""
    roots = np.asarray(E8_ROOTS, dtype=float)
    directions = roots / np.linalg.norm(roots, axis=1, keepdims=True)
    global_breath, channels, state, uh_heads, ud_heads, uh, ud, cross = model.channel_state(t)
    weights = directions ** 2
    weights /= weights.sum(axis=1, keepdims=True)
    exponent = global_breath + weights @ channels
    if model.shape_bias:
        exponent -= model.shape_bias / np.sqrt(2.0 + model.softening ** 2)
    points = roots * np.exp(exponent[:, None])
    diagnostics = {
        "global_breath": float(global_breath),
        "channels": np.asarray(channels, dtype=float),
        "state": state,
        "uh_heads": uh_heads,
        "ud_heads": ud_heads,
        "uh_channels": np.asarray(uh),
        "ud_channels": np.asarray(ud),
        "interference": np.asarray(cross),
    }
    return points, diagnostics


def hull_mesh(points: np.ndarray):
    projected = ConvexHull(points)
    return projected, points[projected.simplices]


def _draw_hull(ax, points, color, alpha):
    hull, triangles = hull_mesh(points)
    ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2],
                    triangles=hull.simplices, color=color, alpha=alpha,
                    linewidth=0.12, edgecolor="0.25")
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("view 1")
    ax.set_ylabel("view 2")
    ax.set_zlabel("view 3")
    return hull


def render_snapshot(model, frame, t: float, path: Path):
    roots = np.asarray(E8_ROOTS, dtype=float)
    base = project_points(roots, frame, source_indices=np.arange(len(roots)))
    deformed, _ = deformed_gosset_vertices(model, t)
    current = project_points(deformed, frame, source_indices=np.arange(len(roots)))
    fig = plt.figure(figsize=(12, 5), constrained_layout=True)
    left = fig.add_subplot(1, 2, 1, projection="3d")
    right = fig.add_subplot(1, 2, 2, projection="3d")
    h0 = _draw_hull(left, base.projected_points, "#6c8ebf", .55)
    h1 = _draw_hull(right, current.projected_points, "#d79b00", .62)
    left.set_title("Static Gosset 4_21 projection (240 roots)")
    right.set_title(f"JOBF deformed root sample, t={t:.3f}")
    fig.suptitle("3D orthographic view of an 8D polytope; projection is lossy")
    fig.savefig(path, dpi=180)
    plt.close(fig)
    return h0, h1


def simulate(steps=101, dt=0.01, seed=421, shape_bias=0.0):
    if steps < 2 or dt <= 0 or not np.isfinite(dt):
        raise ValueError("steps must be >= 2 and dt must be positive and finite")
    model = JanusOctadialBreathingField(dt=dt, shape_bias=shape_bias)
    frame = seeded_view(seed)
    roots = np.asarray(E8_ROOTS, dtype=float)
    base_projection = project_points(roots, frame, source_indices=np.arange(len(roots)))
    base_hull = ConvexHull(base_projection.projected_points)
    rows = []
    times = np.arange(steps) * dt
    for t in times:
        points8, diag = deformed_gosset_vertices(model, float(t))
        projected = project_points(points8, frame, source_indices=np.arange(len(roots)))
        hull = ConvexHull(projected.projected_points)
        scales = np.linalg.norm(points8, axis=1) / np.linalg.norm(roots, axis=1)
        row = {
            "time": float(t),
            "mean_vertex_scale": float(scales.mean()),
            "min_vertex_scale": float(scales.min()),
            "max_vertex_scale": float(scales.max()),
            "projected_hull_volume": float(hull.volume),
            "baseline_projected_hull_volume": float(base_hull.volume),
            "projected_volume_ratio": float(hull.volume / base_hull.volume),
            "global_breath": diag["global_breath"],
        }
        for i, key in enumerate(KEYS):
            row[f"v8_{key}"] = float(getattr(diag["state"], key))
            row[f"breath_channel_{key}"] = float(diag["channels"][i])
        rows.append(row)
    metadata = {
        "canonical_geometry": "Gosset 4_21 = convex hull of 240 E8 roots in R^8",
        "visualization": "lossy 3D orthographic projection of 240 vertices",
        "dynamic_model": "JOBF radial multiplier sampled only at canonical root directions",
        "projection_frame_name": frame.name,
        "projection_matrix_3x8": frame.matrix.tolist(),
        "seed": seed,
        "steps": steps,
        "dt": dt,
        "metrics_scope": "3D projected convex hull volume, not 8D polytope volume",
        "source_indices": list(range(len(roots))),
    }
    return model, frame, times, rows, metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=101)
    parser.add_argument("--dt", type=float, default=0.01)
    parser.add_argument("--seed", type=int, default=421)
    parser.add_argument("--shape-bias", type=float, default=0.0)
    parser.add_argument("--output", type=Path, default=Path("gosset_3d_output"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    model, frame, times, rows, metadata = simulate(
        args.steps, args.dt, args.seed, args.shape_bias)
    with (args.output / "gosset_3d_metrics.csv").open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    (args.output / "gosset_3d_metadata.json").write_text(
        json.dumps(metadata, indent=2), encoding="utf-8")
    render_snapshot(model, frame, float(times[len(times) // 2]),
                    args.output / "gosset_3d_snapshot.png")
    print(f"Saved 3D Gosset projection, {len(rows)} frames of metrics, and metadata to {args.output}")


if __name__ == "__main__":
    main()
