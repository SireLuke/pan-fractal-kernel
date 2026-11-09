"""Continuous 3D view of the Gosset 4_21 boundary under JOBF dynamics.

The canonical object is the 240-vertex E8 root polytope in R^8. The live
window shows a deterministic, lossy orthographic 3D projection and updates the
JOBF radial deformation continuously. This is a visualization, not a physical
manifold or a full 8D rendering.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
from pathlib import Path

import numpy as np
from scipy.spatial import ConvexHull
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation

try:
    from .gosset_421 import E8_ROOTS
    from .gosset_projection import ProjectionFrame, project_points
    from .view_ladder import gosset_seeded_ladder
    from .jobf_v0_2 import JanusOctadialBreathingField
except ImportError:
    from gosset_421 import E8_ROOTS
    from gosset_projection import ProjectionFrame, project_points
    from view_ladder import gosset_seeded_ladder
    from jobf_v0_2 import JanusOctadialBreathingField

KEYS = ("h", "R", "u", "d", "tau", "chi", "s", "f")


def seeded_view(seed: int = 421) -> ProjectionFrame:
    """Return a reproducible, orthonormal 3x8 viewing frame (not canonical)."""
    rng = np.random.default_rng(seed)
    rows = rng.normal(size=(8, 3))
    q, _ = np.linalg.qr(rows)
    return ProjectionFrame(q.T, name=f"seeded_3d_view_{seed}")


def deformed_gosset_vertices(model: JanusOctadialBreathingField, t: float):
    """Evaluate JOBF's radial multiplier on all 240 canonical root directions."""
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


def _draw_hull(ax, points, color, alpha):
    hull = ConvexHull(points)
    artist = ax.plot_trisurf(points[:, 0], points[:, 1], points[:, 2],
                            triangles=hull.simplices, color=color, alpha=alpha,
                            linewidth=0.12, edgecolor="0.25")
    ax.set_box_aspect((1, 1, 1))
    ax.set_xlabel("view 1")
    ax.set_ylabel("view 2")
    ax.set_zlabel("view 3")
    return hull, artist


def _metric_row(t, points8, diagnostics, frame, baseline_volume):
    roots = np.asarray(E8_ROOTS, dtype=float)
    projection = project_points(points8, frame, source_indices=np.arange(len(roots)))
    hull = ConvexHull(projection.projected_points)
    scales = np.linalg.norm(points8, axis=1) / np.linalg.norm(roots, axis=1)
    row = {
        "time": float(t),
        "mean_vertex_scale": float(scales.mean()),
        "min_vertex_scale": float(scales.min()),
        "max_vertex_scale": float(scales.max()),
        "projected_hull_volume": float(hull.volume),
        "baseline_projected_hull_volume": float(baseline_volume),
        "projected_volume_ratio": float(hull.volume / baseline_volume),
        "global_breath": diagnostics["global_breath"],
    }
    for i, key in enumerate(KEYS):
        row[f"v8_{key}"] = float(getattr(diagnostics["state"], key))
        row[f"breath_channel_{key}"] = float(diagnostics["channels"][i])
    return row, projection.projected_points, hull


def simulate(steps=101, dt=0.01, seed=421, shape_bias=0.0):
    """Compute a finite metric series without opening an animation window."""
    if steps < 2 or dt <= 0 or not np.isfinite(dt):
        raise ValueError("steps must be >= 2 and dt must be positive and finite")
    model = JanusOctadialBreathingField(dt=dt, shape_bias=shape_bias)
    frame = seeded_view(seed)
    roots = np.asarray(E8_ROOTS, dtype=float)
    base_points = project_points(roots, frame, source_indices=np.arange(len(roots))).projected_points
    baseline_volume = float(ConvexHull(base_points).volume)
    times, rows = np.arange(steps) * dt, []
    for t in times:
        points8, diagnostics = deformed_gosset_vertices(model, float(t))
        row, _, _ = _metric_row(float(t), points8, diagnostics, frame, baseline_volume)
        rows.append(row)
    return model, frame, times, rows


def _metadata(frame, seed, dt, shape_bias):
    return {
        "canonical_geometry": "Gosset 4_21: convex hull of 240 E8 roots in R^8",
        "visualization": "lossy orthographic 3D projection, updated continuously",
        "dynamic_model": "JOBF radial multiplier sampled at the 240 canonical root directions",
        "projection_frame_name": frame.name,
        "projection_matrix_3x8": frame.matrix.tolist(),
        "seed": seed,
        "model_dt": dt,
        "shape_bias": shape_bias,
        "metrics_scope": "3D projected hull volume, not 8D polytope volume",
        "source_indices": list(range(len(E8_ROOTS))),
        "view_ladder": gosset_seeded_ladder(seed).to_schema(),
    }


def run_live(dt=0.01, fps=20, seed=421, shape_bias=0.0,
             output=Path("gosset_3d_output"), frames=None):
    """Run an interactive animation until the window closes (or frames elapse).

    With frames=None the simulation is unbounded. Metrics are appended and
    flushed on each animation tick so an interrupted run still leaves data.
    """
    if dt <= 0 or not np.isfinite(dt):
        raise ValueError("dt must be positive and finite")
    if fps <= 0 or not np.isfinite(fps):
        raise ValueError("fps must be positive and finite")
    if frames is not None and frames < 1:
        raise ValueError("frames must be positive when supplied")

    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    model = JanusOctadialBreathingField(dt=dt, shape_bias=shape_bias)
    frame = seeded_view(seed)
    roots = np.asarray(E8_ROOTS, dtype=float)
    base_points = project_points(roots, frame, source_indices=np.arange(len(roots))).projected_points
    base_hull = float(ConvexHull(base_points).volume)

    fig = plt.figure(figsize=(12, 6), constrained_layout=True)
    left = fig.add_subplot(1, 2, 1, projection="3d")
    right = fig.add_subplot(1, 2, 2, projection="3d")
    _draw_hull(left, base_points, "#6c8ebf", .48)
    left.set_title("Static Gosset 4_21 (240 roots)")
    right.set_title("JOBF deformation")
    fig.suptitle("Gosset 4_21: live lossy 3D projection of the 8D polytope")
    (artist,) = _draw_hull(right, base_points, "#d79b00", .62)[1:2]
    rows_path = output / "gosset_3d_live_metrics.csv"
    stream = rows_path.open("w", newline="", encoding="utf-8")
    writer = None
    tick = 0

    (output / "gosset_3d_live_metadata.json").write_text(
        json.dumps(_metadata(frame, seed, dt, shape_bias), indent=2), encoding="utf-8")

    def update(_frame_index):
        nonlocal artist, writer, tick
        t = tick * dt
        points8, diagnostics = deformed_gosset_vertices(model, t)
        row, points3, hull = _metric_row(t, points8, diagnostics, frame, base_hull)
        if writer is None:
            writer = csv.DictWriter(stream, fieldnames=list(row))
            writer.writeheader()
        writer.writerow(row)
        stream.flush()
        artist.remove()
        artist = right.plot_trisurf(
            points3[:, 0], points3[:, 1], points3[:, 2],
            triangles=hull.simplices, color="#d79b00", alpha=.62,
            linewidth=0.12, edgecolor="0.25")
        right.set_title(f"JOBF live deformation  |  t={t:.3f}  |  hull V={hull.volume:.4f}")
        tick += 1
        return (artist,)

    animation_frames = range(frames) if frames is not None else itertools.count()
    animation = FuncAnimation(
        fig, update, frames=animation_frames, interval=1000.0 / fps,
        blit=False, cache_frame_data=False, repeat=False)
    fig._gosset_animation = animation
    try:
        plt.show(block=True)
    finally:
        stream.close()
    return tick


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dt", type=float, default=0.01, help="model-time increment per frame")
    parser.add_argument("--fps", type=float, default=20, help="animation refresh rate")
    parser.add_argument("--seed", type=int, default=421)
    parser.add_argument("--shape-bias", type=float, default=0.0)
    parser.add_argument("--frames", type=int, default=None,
                        help="stop after this many frames; default runs until the window closes")
    parser.add_argument("--output", type=Path, default=Path("gosset_3d_output"))
    args = parser.parse_args()
    count = run_live(args.dt, args.fps, args.seed, args.shape_bias, args.output, args.frames)
    print(f"Live Gosset run ended after {count} frames; metrics saved under {args.output}")


if __name__ == "__main__":
    main()
