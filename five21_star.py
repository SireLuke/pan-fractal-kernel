"""Independent exact reconstruction of the 5_21 cell star and a translation-propagation audit.

Cells of the 5_21 honeycomb are the Delaunay cells of the E8 lattice:
  * 8-simplex:   9 lattice points pairwise at squared distance 2 (circumradius^2 = 8/9);
  * 8-orthoplex: 16 lattice points at distance 1 from a deep hole c = v/2, v in the norm-4 shell.
Everything is exact integer arithmetic in doubled coordinates (p2 = 2p). Cell vertex sets are
frozensets of such tuples. The star at 0 is translated to any vertex u by adding u, which is
valid because the E8 lattice is translation-invariant; the audit checks that this is consistent.
"""
from __future__ import annotations

from collections import Counter
from itertools import combinations

import numpy as np

try:
    from . import five21_neighborhood as nb
except ImportError:
    import five21_neighborhood as nb

ZERO = (0,) * 8
ROOTS = nb.ROOTS2


def _add(p, q):  return tuple(a + b for a, b in zip(p, q))
def _sub(p, q):  return tuple(a - b for a, b in zip(p, q))


def root_adjacency():
    """adj[i] = set of root indices j with alpha_i . alpha_j = 1 (doubled dot = 4)."""
    R = np.array(ROOTS, dtype=np.int64)
    G = R @ R.T                                   # = 4 * (alpha_i . alpha_j)
    return [set(np.nonzero(G[i] == 4)[0].tolist()) for i in range(len(ROOTS))]


def simplex_cells_at_origin():
    """All 8-cliques of the root graph, each completed by the origin -> 9-point simplex cells."""
    adj = root_adjacency()
    out = []

    def extend(clique, cand):
        if len(clique) == 8:
            out.append(tuple(clique)); return
        for v in sorted(cand):
            if clique and v < clique[-1]: continue
            extend(clique + [v], {w for w in cand if w > v and w in adj[v]})

    for i in range(len(ROOTS)):
        extend([i], {w for w in adj[i] if w > i})
    return [frozenset([ZERO] + [ROOTS[i] for i in c]) for c in out]


def orthoplex_cells_at_origin():
    """For each norm-4 vector v: cell = {0, v} + roots alpha with alpha . v = 2 (16 points)."""
    cells = []
    for v in nb.shell(2):
        pts = [ZERO, v] + [r for r in ROOTS if sum(a * b for a, b in zip(r, v)) == 8]   # doubled dot 8 == dot 2
        cells.append(frozenset(pts))
    return cells


def cell_facets(cell, kind):
    """Facets (as frozensets of 8 vertices) of a simplex (drop 1 vertex) or orthoplex (1 per antipodal pair)."""
    pts = sorted(cell)
    if kind == "simplex":
        return [frozenset(pts[:i] + pts[i + 1:]) for i in range(len(pts))]
    ctr = tuple(sum(c) for c in zip(*pts))            # sum of 16 points = 16 * centre
    mate = {p: tuple(ctr[k] // 8 - p[k] for k in range(8)) for p in pts}   # 2*centre - p
    assert all(mate[p] in cell and mate[mate[p]] == p for p in pts)
    pairs = sorted({tuple(sorted((p, mate[p]))) for p in pts})
    assert len(pairs) == 8
    from itertools import product
    return [frozenset(pr[b] for pr, b in zip(pairs, bits)) for bits in product((0, 1), repeat=8)]


def delaunay_check(cells, radius2_times_81):
    """Vertices of each cell at the common distance; no lattice point (shells 0,1) strictly inside."""
    cand = np.array(nb.patch(1), dtype=np.int64)              # 241 points: all that can be inside
    bad_eq = bad_in = 0
    for c in cells:
        P = np.array(sorted(c), dtype=np.int64); n = len(P)
        S = P.sum(axis=0)                                      # centre2 = S / n
        d_v = ((n * P - S) ** 2).sum(axis=1)                   # = n^2 * |p2 - c2|^2
        d_c = ((n * cand - S) ** 2).sum(axis=1)
        if not np.all(d_v == d_v[0]): bad_eq += 1
        if np.any(d_c < d_v[0]): bad_in += 1
    return bad_eq, bad_in


def audit() -> dict:
    simp, orth = simplex_cells_at_origin(), orthoplex_cells_at_origin()
    res = {"simplex_cells": len(simp), "orthoplex_cells": len(orth)}
    res["simplex_delaunay_violations"] = delaunay_check(simp, None)
    res["orthoplex_delaunay_violations"] = delaunay_check(orth, None)

    # --- local ridge closure at the origin
    cnt, kinds = Counter(), {}
    for kind, cells in (("simplex", simp), ("orthoplex", orth)):
        for c in cells:
            for f in cell_facets(c, kind):
                if ZERO in f:
                    cnt[f] += 1; kinds.setdefault(f, []).append(kind)
    res["facets_from_simplex"] = sum(1 for f, k in kinds.items() for x in k if x == "simplex")
    res["facets_from_orthoplex"] = sum(1 for f, k in kinds.items() for x in k if x == "orthoplex")
    res["distinct_origin_facets"] = len(cnt)
    res["facets_multiplicity_histogram"] = {str(k): v for k, v in Counter(cnt.values()).items()}
    res["ridge_cell_type_pairs"] = {"+".join(sorted(k)): n for k, n in Counter(tuple(sorted(k)) for k in kinds.values()).items()}

    # --- propagation 1: adjacent-vertex star compatibility
    cells = {c: "simplex" for c in simp} | {c: "orthoplex" for c in orth}
    star0 = set(cells)
    by_vertex = {}
    for c in cells:
        for p in c: by_vertex.setdefault(p, []).append(c)
    bad = checked = 0
    for a in ROOTS:                                   # for every neighbour a of the origin
        containing = by_vertex.get(a, [])
        shifted = {frozenset(_sub(p, a) for p in c) for c in containing}
        checked += len(containing)
        if not shifted <= star0: bad += 1
        # converse: cells of star(a) that contain 0 are exactly {c + a : c in star0, -a in c}
        conv = {frozenset(_add(p, a) for p in c) for c in by_vertex.get(tuple(-x for x in a), [])}
        if {c for c in conv if ZERO in c} != set(containing): bad += 1
    res["neighbour_star_incidences_checked"] = checked
    res["neighbour_star_violations"] = bad

    # --- propagation 2: every ridge of every origin cell (not only those through 0) is in exactly 2 cells
    off, rcount = 0, 0
    seen = set()
    for c, kind in cells.items():
        for f in cell_facets(c, kind):
            if f in seen: continue
            seen.add(f); rcount += 1
            u = min(f)
            if cnt.get(frozenset(_sub(p, u) for p in f)) != 2: off += 1
    res["ridges_in_origin_cells"] = rcount
    res["ridges_not_in_exactly_two_cells"] = off
    return res


if __name__ == "__main__":
    import json
    print(json.dumps(audit(), indent=2, default=str))
