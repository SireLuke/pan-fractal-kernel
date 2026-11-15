"""Golden-angle radial shell point generator for visualization experiments.

This is a configurable 2D point layout. It is not an E8 root generator,
quasicrystal cut-and-project construction, or proof of Gosset incidence.
"""
from __future__ import annotations

import math

import numpy as np
from numpy.typing import NDArray

PHI = (1.0 + math.sqrt(5.0)) / 2.0
GOLDEN_ANGLE = 2.0 * math.pi / (PHI * PHI)


def golden_angle_shells(*, shell_count: int = 5, points_per_shell: int = 32,
                        base_radius: float = 1.0, scale_ratio: float = PHI,
                        phase: float = 0.0) -> NDArray[np.float64]:
    """Return points with shape (shell_count, points_per_shell, 2).

    Each shell is a ring with radius base_radius * scale_ratio**shell_index;
    successive rings are offset by the golden angle.
    """
    if isinstance(shell_count, bool) or not isinstance(shell_count, int) or shell_count < 1:
        raise ValueError("shell_count must be a positive integer")
    if isinstance(points_per_shell, bool) or not isinstance(points_per_shell, int) or points_per_shell < 3:
        raise ValueError("points_per_shell must be an integer >= 3")
    if not math.isfinite(base_radius) or base_radius <= 0.0:
        raise ValueError("base_radius must be finite and positive")
    if not math.isfinite(scale_ratio) or scale_ratio <= 1.0:
        raise ValueError("scale_ratio must be finite and greater than 1")
    if not math.isfinite(phase):
        raise ValueError("phase must be finite")
    rings = []
    for shell in range(shell_count):
        radius = base_radius * scale_ratio ** shell
        theta0 = phase + shell * GOLDEN_ANGLE
        angles = theta0 + 2.0 * math.pi * np.arange(points_per_shell) / points_per_shell
        rings.append(np.column_stack((radius * np.cos(angles), radius * np.sin(angles))))
    return np.stack(rings, axis=0)
