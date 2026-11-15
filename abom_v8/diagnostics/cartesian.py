"""Finite-difference vector differential operators on a uniform 3D Cartesian grid.

These operators are intentionally limited to smooth fields on a regular Cartesian
grid. They are not generalized automatically to Menger graphs, Gosset geometry,
or the eight-dimensional V8 state space.
"""
from __future__ import annotations

import math
from collections.abc import Sequence

import numpy as np
from numpy.typing import NDArray

FloatArray = NDArray[np.float64]


def _spacing(value: float | Sequence[float]) -> tuple[float, float, float]:
    if np.isscalar(value):
        spacing = (float(value),) * 3
    else:
        spacing_array = np.asarray(value, dtype=float)
        if spacing_array.shape != (3,):
            raise ValueError("spacing must be a positive finite scalar or three-vector")
        spacing = tuple(float(v) for v in spacing_array)
    if len(spacing) != 3 or any(not math.isfinite(v) or v <= 0.0 for v in spacing):
        raise ValueError("spacing must be a positive finite scalar or three-vector")
    return spacing


def _scalar_field(field: NDArray[np.floating]) -> FloatArray:
    values = np.asarray(field, dtype=float)
    if values.ndim != 3 or any(n < 3 for n in values.shape):
        raise ValueError("scalar field must be a 3D array with at least 3 points per axis")
    if not np.all(np.isfinite(values)):
        raise ValueError("field values must be finite")
    return values


def _vector_field(field: NDArray[np.floating]) -> FloatArray:
    values = np.asarray(field, dtype=float)
    if values.ndim != 4 or values.shape[0] != 3 or any(n < 3 for n in values.shape[1:]):
        raise ValueError("vector field must have shape (3, nx, ny, nz), with each grid dimension >= 3")
    if not np.all(np.isfinite(values)):
        raise ValueError("field values must be finite")
    return values


def gradient(field: NDArray[np.floating],
             spacing: float | Sequence[float] = 1.0) -> FloatArray:
    """Return Cartesian gradient with shape (3, nx, ny, nz)."""
    values = _scalar_field(field)
    steps = _spacing(spacing)
    return np.stack(np.gradient(values, *steps, edge_order=2), axis=0)


def divergence(field: NDArray[np.floating],
               spacing: float | Sequence[float] = 1.0) -> FloatArray:
    """Return Cartesian divergence of a 3-component vector field."""
    values = _vector_field(field)
    steps = _spacing(spacing)
    return sum(
        np.gradient(values[axis], steps[axis], axis=axis, edge_order=2)
        for axis in range(3)
    )


def curl(field: NDArray[np.floating],
         spacing: float | Sequence[float] = 1.0) -> FloatArray:
    """Return Cartesian curl with shape (3, nx, ny, nz)."""
    values = _vector_field(field)
    dx, dy, dz = _spacing(spacing)
    d_fz_dy = np.gradient(values[2], dy, axis=1, edge_order=2)
    d_fy_dz = np.gradient(values[1], dz, axis=2, edge_order=2)
    d_fx_dz = np.gradient(values[0], dz, axis=2, edge_order=2)
    d_fz_dx = np.gradient(values[2], dx, axis=0, edge_order=2)
    d_fy_dx = np.gradient(values[1], dx, axis=0, edge_order=2)
    d_fx_dy = np.gradient(values[0], dy, axis=1, edge_order=2)
    return np.stack((
        d_fz_dy - d_fy_dz,
        d_fx_dz - d_fz_dx,
        d_fy_dx - d_fx_dy,
    ), axis=0)


def laplacian(field: NDArray[np.floating],
              spacing: float | Sequence[float] = 1.0) -> FloatArray:
    """Return scalar Cartesian Laplacian on the same grid."""
    values = _scalar_field(field)
    steps = _spacing(spacing)
    result = np.zeros_like(values)
    for axis, step in enumerate(steps):
        first = np.gradient(values, step, axis=axis, edge_order=2)
        result += np.gradient(first, step, axis=axis, edge_order=2)
    return result
