"""Y/Delta baryonic-network geometry helpers for NAHT.

This is a geometric benchmark, not a QCD solver. Inputs are three source
positions in a common Euclidean coordinate frame. The returned Delta
quantity is the conventional half-perimeter geometric measure; it is not
by itself a potential-energy prediction or an automatic model selector.
"""
from __future__ import annotations

from math import acos, isfinite, pi, sqrt
from typing import Sequence


def _point(value: Sequence[float], name: str) -> tuple[float, ...]:
    result = tuple(float(x) for x in value)
    if len(result) < 2:
        raise ValueError(f"{name} must have at least two coordinates")
    if not all(isfinite(x) for x in result):
        raise ValueError(f"{name} coordinates must be finite")
    return result


def _distance(a: tuple[float, ...], b: tuple[float, ...]) -> float:
    return sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))


def _cross_norm(u: tuple[float, ...], v: tuple[float, ...]) -> float:
    if len(u) == 2:
        return abs(u[0] * v[1] - u[1] * v[0])
    if len(u) == 3:
        cross = (
            u[1] * v[2] - u[2] * v[1],
            u[2] * v[0] - u[0] * v[2],
            u[0] * v[1] - u[1] * v[0],
        )
        return sqrt(sum(x * x for x in cross))
    raise ValueError("triangle area is supported in 2D or 3D")


def _angle_at(a: tuple[float, ...], vertex: tuple[float, ...],
              c: tuple[float, ...]) -> float:
    u = tuple(x - y for x, y in zip(a, vertex))
    v = tuple(x - y for x, y in zip(c, vertex))
    nu = sqrt(sum(x * x for x in u))
    nv = sqrt(sum(x * x for x in v))
    if nu == 0.0 or nv == 0.0:
        return 0.0
    cosine = sum(x * y for x, y in zip(u, v)) / (nu * nv)
    return acos(max(-1.0, min(1.0, cosine)))


def triangle_network_lengths(
    points: Sequence[Sequence[float]], *, tolerance: float = 1e-12
) -> dict[str, float | str]:
    """Return Y-Steiner and Delta half-perimeter geometric measures.

    In a non-degenerate triangle with all angles < 120 degrees, the
    Steiner point has three 120-degree arms and the Y length is
    sqrt((a^2+b^2+c^2+4*sqrt(3)*area)/2). If an angle is >=120 degrees,
    the minimizing tree is the two sides incident on that vertex.

    These are geometric lengths only. A QCD potential comparison must also
    apply the separately specified string-tension coefficients, Coulomb
    terms, offsets, and fit conventions for each ansatz.
    """
    if len(points) != 3:
        raise ValueError("exactly three source points are required")
    p = tuple(_point(point, f"point[{i}]") for i, point in enumerate(points))
    dimension = len(p[0])
    if any(len(point) != dimension for point in p):
        raise ValueError("all source points must have the same dimension")
    if dimension not in (2, 3):
        raise ValueError("source points must be in 2D or 3D")
    if not isfinite(tolerance) or tolerance < 0.0:
        raise ValueError("tolerance must be finite and nonnegative")

    a = _distance(p[1], p[2])
    b = _distance(p[0], p[2])
    c = _distance(p[0], p[1])
    delta = 0.5 * (a + b + c)

    # Coincident terminals make the Steiner tree the segment between the
    # coincident location and the remaining point (not twice that segment).
    pairs = ((0, 1), (0, 2), (1, 2))
    coincident = next(((i, j) for i, j in pairs
                       if _distance(p[i], p[j]) <= tolerance), None)
    if coincident is not None:
        remaining = next(k for k in range(3) if k not in coincident)
        y_length = _distance(p[coincident[0]], p[remaining])
        regime = "coincident_pair"
    elif max(a, b, c) <= tolerance:
        y_length = 0.0
        regime = "coincident"
    else:
        angles = (
            _angle_at(p[1], p[0], p[2]),
            _angle_at(p[0], p[1], p[2]),
            _angle_at(p[0], p[2], p[1]),
        )
        largest_index = max(range(3), key=angles.__getitem__)
        if angles[largest_index] >= 2.0 * pi / 3.0 - tolerance:
            y_length = sum(_distance(p[largest_index], p[j])
                           for j in range(3) if j != largest_index)
            regime = "vertex"
        else:
            u = tuple(p[1][i] - p[0][i] for i in range(dimension))
            v = tuple(p[2][i] - p[0][i] for i in range(dimension))
            area = 0.5 * _cross_norm(u, v)
            radicand = (a*a + b*b + c*c + 4.0*sqrt(3.0)*area) / 2.0
            y_length = sqrt(max(0.0, radicand))
            regime = "steiner_120"

    return {
        "y_length": y_length,
        "delta_half_perimeter": delta,
        "steiner_regime": regime,
        "delta_minus_y": delta - y_length,
    }


def compare_networks(points: Sequence[Sequence[float]]) -> dict[str, float | str]:
    """Return both geometric measures; never infer a physical winner."""
    return triangle_network_lengths(points)
