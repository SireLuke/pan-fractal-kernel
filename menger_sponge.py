"""Finite-level d-dimensional Menger sponge: exact audits and spectral-dimension estimates.

A level-k sponge lives on the integer grid {0, ..., 3^k - 1}^d. A cell is kept when,
at every base-3 digit position, at most one coordinate has digit 1 (the "middle
third"). Per level this keeps N_d = 2^d + d * 2^(d-1) of the 3^d sub-cells, so

    d = 2 -> Sierpinski carpet (8 of 9),   d = 3 -> Menger sponge (20 of 27),
    d = 4 -> 48 of 81,  d = 8 -> 1280 of 6561,  d = 10 -> 6144 of 59049,

with similarity dimension ln(N_d) / ln(3). The graph used here joins face-adjacent
kept cells. Everything is a statement about this finite graph; nothing here is a
physical claim, and `spectral_dimension` is a finite-size, window-dependent estimate
that is validated against the Sierpinski gasket (exact value 2 ln 3 / ln 5) in the tests.
"""
from __future__ import annotations

import argparse
import json
from itertools import product
from math import log

import numpy as np
import scipy.sparse as sp
from scipy.sparse.csgraph import connected_components

MAX_CELLS = 5_000_000


def cells_per_level(d: int) -> int:
    """Number of kept sub-cells per subdivision step in d dimensions."""
    _check_dim(d)
    return 2**d + d * 2 ** (d - 1)


def similarity_dimension(d: int) -> float:
    return log(cells_per_level(d)) / log(3.0)


def _check_dim(d: int) -> None:
    if not isinstance(d, int) or d < 1:
        raise ValueError("d must be a positive integer")


def _check_level(level: int) -> None:
    if not isinstance(level, int) or level < 0:
        raise ValueError("level must be a non-negative integer")


def menger_cells(d: int, level: int) -> np.ndarray:
    """Integer coordinates (n, d) of the kept cells of the level-`level` sponge."""
    _check_dim(d)
    _check_level(level)
    if cells_per_level(d) ** level > MAX_CELLS:
        raise ValueError(f"sponge would have more than {MAX_CELLS} cells")
    patterns = np.array([p for p in product((0, 1, 2), repeat=d) if sum(x == 1 for x in p) <= 1],
                        dtype=np.int64)
    cells = np.zeros((1, d), dtype=np.int64)
    for _ in range(level):
        cells = np.concatenate([3 * cells + p for p in patterns], axis=0)
    return cells


def adjacency(cells: np.ndarray, side: int) -> sp.csr_matrix:
    """Symmetric 0/1 adjacency of face-adjacent cells (no wrap-around)."""
    n, d = cells.shape
    weights = side ** np.arange(d, dtype=np.int64)
    keys = cells @ weights
    order = np.argsort(keys)
    sorted_keys = keys[order]
    rows, cols = [], []
    for axis in range(d):
        ok = cells[:, axis] + 1 < side
        src = np.nonzero(ok)[0]
        target = keys[src] + weights[axis]
        pos = np.searchsorted(sorted_keys, target)
        pos[pos == n] = n - 1
        hit = sorted_keys[pos] == target
        rows.append(src[hit])
        cols.append(order[pos[hit]])
    r = np.concatenate(rows) if rows else np.array([], dtype=np.int64)
    c = np.concatenate(cols) if cols else np.array([], dtype=np.int64)
    upper = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(n, n))
    return (upper + upper.T).tocsr()


def box_counts(cells: np.ndarray, level: int) -> list[int]:
    """Occupied boxes of side 3^j for j = 0..level (j = level is the single root box)."""
    return [len(np.unique(cells // 3**j, axis=0)) for j in range(level + 1)]


def box_counting_dimension(cells: np.ndarray, level: int) -> float:
    """Slope of log(occupied boxes) against log(1/box size) over all scales."""
    if level < 1:
        raise ValueError("need level >= 1 for a slope")
    counts = np.array(box_counts(cells, level), dtype=float)
    log_inverse_size = (level - np.arange(level + 1)) * log(3.0)
    slope, _ = np.polyfit(log_inverse_size, np.log(counts), 1)
    return float(slope)


def audit_menger(d: int, level: int) -> dict:
    """Exact counts, degree histogram, connectivity and box-counting dimension."""
    cells = menger_cells(d, level)
    side = 3**level
    adj = adjacency(cells, side)
    degrees = np.asarray(adj.sum(axis=1)).ravel().astype(int)
    components, _ = connected_components(adj, directed=False)
    out = {
        "d": d,
        "level": level,
        "cells": int(len(cells)),
        "expected_cells": cells_per_level(d) ** level,
        "edges": int(adj.nnz // 2),
        "degree_histogram": {str(k): int((degrees == k).sum()) for k in sorted(set(degrees))},
        "connected_components": int(components),
        "similarity_dimension": similarity_dimension(d),
        "box_counts": box_counts(cells, level),
    }
    if level >= 1:
        out["box_counting_dimension"] = box_counting_dimension(cells, level)
    return out


def sierpinski_gasket_graph(stage: int) -> sp.csr_matrix:
    """Sierpinski gasket graph at `stage`: (3^(stage+1)+3)/2 vertices, 3^(stage+1) edges.

    Same construction as the stage audit in PANoRAMic.os (experiments/moonshine_sierpinski),
    used here only as a reference fractal with a known spectral dimension.
    """
    _check_level(stage)
    vertices = {(0, 0), (1, 0), (0, 1)}
    edges = {((0, 0), (1, 0)), ((0, 0), (0, 1)), ((0, 1), (1, 0))}
    for level in range(stage):
        side = 2**level
        shifts = ((0, 0), (side, 0), (0, side))
        vertices_next, edges_next = set(), set()
        for sx, sy in shifts:
            vertices_next.update((x + sx, y + sy) for x, y in vertices)
            for a, b in edges:
                a2, b2 = (a[0] + sx, a[1] + sy), (b[0] + sx, b[1] + sy)
                edges_next.add((a2, b2) if a2 < b2 else (b2, a2))
        vertices, edges = vertices_next, edges_next
    ordered = sorted(vertices)
    index = {v: i for i, v in enumerate(ordered)}
    r = [index[a] for a, _ in edges]
    c = [index[b] for _, b in edges]
    upper = sp.coo_matrix((np.ones(len(r)), (r, c)), shape=(len(ordered),) * 2)
    return (upper + upper.T).tocsr()


def return_probabilities(adj: sp.csr_matrix, starts, steps: int) -> np.ndarray:
    """Mean return probability p_t(x, x), t = 0..steps, of the lazy random walk
    P = (I + D^-1 A) / 2, averaged over `starts`. Lazy so there is no parity effect."""
    degrees = np.asarray(adj.sum(axis=1)).ravel()
    if np.any(degrees == 0):
        raise ValueError("graph has isolated vertices")
    walk = (sp.identity(adj.shape[0], format="csr") + sp.diags(1.0 / degrees) @ adj) / 2.0
    walk_t = walk.T.tocsr()
    out = np.zeros(steps + 1)
    for x in starts:
        p = np.zeros(adj.shape[0])
        p[x] = 1.0
        out[0] += 1.0
        for t in range(1, steps + 1):
            p = walk_t @ p
            out[t] += p[x]
    return out / len(starts)


def spectral_dimension(adj: sp.csr_matrix, steps: int = 400, n_starts: int = 12,
                       window: tuple[int, int] | None = None, seed: int = 0) -> dict:
    """Estimate d_s from p_t(x,x) ~ t^(-d_s/2) by a log-log fit over `window` (steps).

    Window-dependent and finite-size limited: valid only for t well below the walk's
    relaxation time on this graph. Default window is [steps/20, steps/2].
    """
    rng = np.random.default_rng(seed)
    n = adj.shape[0]
    starts = rng.choice(n, size=min(n_starts, n), replace=False)
    p = return_probabilities(adj, starts, steps)
    lo, hi = window if window else (max(2, steps // 20), steps // 2)
    t = np.arange(lo, hi + 1)
    slope, _ = np.polyfit(np.log(t), np.log(p[lo:hi + 1]), 1)
    return {"d_s": float(-2.0 * slope), "window": [int(lo), int(hi)],
            "starts": int(len(starts)), "steps": int(steps), "vertices": int(n)}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--d", type=int, default=3)
    parser.add_argument("--level", type=int, default=3)
    parser.add_argument("--spectral", action="store_true", help="also estimate d_s")
    parser.add_argument("--steps", type=int, default=400)
    args = parser.parse_args()
    report = audit_menger(args.d, args.level)
    if args.spectral:
        report["spectral"] = spectral_dimension(adjacency(menger_cells(args.d, args.level), 3**args.level),
                                                steps=args.steps)
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
