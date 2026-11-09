"""Finite patches of the 5_21 honeycomb (vertex set = E8 lattice; symmetry = affine E8, "E9").

Scope: exact integer arithmetic on the E8 lattice in DOUBLED coordinates (v = 2x, so
half-integers are exact), Euclidean shells around a vertex, affine reflections, and a
view ladder over a finite patch. The honeycomb is infinite; nothing here says anything
about global incidence (cells/facets) and a finite patch is not the honeycomb.

Naming: "E9" here means affine E8 (E8^(1)), the Coxeter group [3^{5,2,1}] of the 5_21
honeycomb. It is not the hyperbolic E10 and not a finite Lie group.
"""
from __future__ import annotations

from functools import lru_cache

import numpy as np

try:
    from .gosset_421 import E8_ROOTS
    from .view_ladder import (ViewLadder, build_ladder, nested_frames, seeded_3d_rows)
    from .gosset_projection import ProjectionFrame, coordinate_frame
except ImportError:
    from gosset_421 import E8_ROOTS
    from view_ladder import (ViewLadder, build_ladder, nested_frames, seeded_3d_rows)
    from gosset_projection import ProjectionFrame, coordinate_frame

ROOTS2 = tuple(tuple(int(round(2 * c)) for c in r) for r in E8_ROOTS)   # doubled integer roots
THETA_COUNTS = {0: 1, 1: 240, 2: 2160, 3: 6720}   # E8 theta series coefficients (norm^2 = 2n)
MAX_SHELL = 3


def is_e8_doubled(v) -> bool:
    """v = 2x is in the E8 lattice iff all entries share parity and sum(v) % 4 == 0."""
    v = tuple(int(a) for a in v)
    return len(v) == 8 and len({a % 2 for a in v}) == 1 and sum(v) % 4 == 0


def norm2(v) -> float:
    """Euclidean norm^2 of x = v/2."""
    return sum(a * a for a in v) / 4.0


def neighbors(v) -> list:
    """The 240 nearest lattice neighbours v + alpha (exact)."""
    return [tuple(a + b for a, b in zip(v, r)) for r in ROOTS2]


@lru_cache(maxsize=None)
def shell(n: int) -> tuple:
    """Lattice vectors of Euclidean norm^2 = 2n around the origin (n <= 3), sorted, doubled ints."""
    if n not in THETA_COUNTS:
        raise ValueError(f"shell n must be in 0..{MAX_SHELL}")
    if n == 0:
        return ((0,) * 8,)
    if n == 1:
        return tuple(sorted(ROOTS2))
    found = {t for p in shell(n - 1) for t in neighbors(p) if norm2(t) == 2 * n}
    return tuple(sorted(found))


def patch(max_shell: int = 1) -> tuple:
    """All lattice vectors with norm^2 <= 2*max_shell (doubled ints), origin first."""
    if not (0 <= max_shell <= MAX_SHELL):
        raise ValueError(f"max_shell must be in 0..{MAX_SHELL}")
    return tuple(v for n in range(max_shell + 1) for v in shell(n))


def affine_reflection(v, root_index: int, k: int = 0) -> tuple:
    """Reflect lattice point v in the affine hyperplane {x : x.alpha = k} (exact).

    x -> x - (x.alpha - k) alpha. x.alpha is an integer for lattice x, so the result is exact.
    These reflections (k=0 gives the finite Weyl group) generate the affine Weyl group.
    """
    if not is_e8_doubled(v):
        raise ValueError("v must be an E8 lattice point (doubled integer coordinates)")
    a2 = ROOTS2[root_index]
    dot4 = sum(x * y for x, y in zip(v, a2))
    assert dot4 % 4 == 0
    c = dot4 // 4 - int(k)
    return tuple(x - c * y for x, y in zip(v, a2))


def five21_ladder(max_shell: int = 1, kind: str = "coordinate", seed: int = 421) -> ViewLadder:
    """View ladder over the finite patch (origin + shells <= max_shell) of the 5_21 vertex set."""
    ids = patch(max_shell)
    pts = np.asarray(ids, dtype=float) / 2.0
    if kind == "coordinate":
        frames = [ProjectionFrame(np.eye(8), "identity_8d")] + [
            ProjectionFrame(coordinate_frame(8, d).matrix, f"coordinate_8d_to_{d}d") for d in (4, 3, 2)]
    elif kind == "seeded":
        frames = nested_frames(seeded_3d_rows(seed), seed)
    else:
        raise ValueError("kind must be 'coordinate' or 'seeded'")
    return build_ladder(
        f"five21_patch_s{max_shell}_{kind}",
        f"5_21 honeycomb vertex set (E8 lattice), finite patch: origin + shells 1..{max_shell}",
        pts, [list(v) for v in ids], "e8_lattice_doubled_int8", frames,
        "Finite patch only. The honeycomb is infinite with affine-E8 ('E9') symmetry; views "
        "say nothing about global cell incidence.")
