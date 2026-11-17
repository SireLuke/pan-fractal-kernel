"""Exact surface area of the finite 3D Menger sponge (counting, no physics).

For the unit cube, the level-``n`` sponge has surface area

    S(n) = 2 * (20/9)**n + 4 * (8/9)**n

so ``S(0) = 6`` and ``S(1) = 8``. In units of one level-``n`` cell face
(area ``9**-n``) the area is the integer ``2 * 20**n + 4 * 8**n``. Together with
the volume ``(20/27)**n`` this shows the standard picture: volume falls to zero
while surface area grows without bound (``S(n) > n`` for every ``n``).

These are statements about the finite construction at each level and about the
limit of the sequence. They are not measurements of any material.
``exposed_face_count`` recounts the area directly from the cell coordinates, as
an independent check on the closed form.
"""
from __future__ import annotations

from fractions import Fraction

from .menger import _check_level


def surface_face_count(level: int) -> int:
    """Exposed cell faces of the level-``level`` sponge: 2 * 20**n + 4 * 8**n."""
    n = _check_level(level)
    return 2 * 20**n + 4 * 8**n


def menger_surface_area_exact(level: int) -> Fraction:
    """Surface area of the unit-cube level-``level`` sponge, as an exact fraction."""
    n = _check_level(level)
    return Fraction(surface_face_count(n), 9**n)


def menger_surface_area(level: int) -> float:
    """Float form of :func:`menger_surface_area_exact`."""
    return float(menger_surface_area_exact(level))


def exposed_face_count(level: int) -> int:
    """Count exposed faces directly from the kept cells (independent of the formula).

    A face is exposed when the neighbouring cell across it is outside the sponge
    or outside the cube. Needs ``numpy`` through ``menger_sponge`` and is meant
    for small levels (the cell count is ``20**level``).
    """
    from menger_sponge import menger_cells

    n = _check_level(level)
    cells = {tuple(int(x) for x in row) for row in menger_cells(3, n)}
    exposed = 0
    for x, y, z in cells:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            if (x + dx, y + dy, z + dz) not in cells:
                exposed += 1
    return exposed
