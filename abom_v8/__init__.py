"""ABOM-V8 modular manifold/navigation layer (experimental v0.1)."""

__author__ = "Lucas Thouvenell (@SireLuke)"

from .harmonics import log_phi_ratio, phi_power
from .mu_cube import MuCube, MuCubeRegistry
from .state import COORDINATE_ORDER, SCHEMA_VERSION, V8State
from .trajectory import V8Trajectory

__all__ = [
    "COORDINATE_ORDER", "SCHEMA_VERSION", "V8State", "MuCube",
    "MuCubeRegistry", "V8Trajectory", "phi_power", "log_phi_ratio",
    "__author__",
]
