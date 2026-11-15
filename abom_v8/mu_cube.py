"""μ-cube state containers with explicit identity and recursive references.

A μ-cube is an information/state container. It is not assumed to be a
Euclidean cube or automatically identified with a retained Menger cell.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
import math
from types import MappingProxyType
from typing import Any

from .state import SCHEMA_VERSION, V8State


@dataclass(frozen=True, slots=True)
class MuCube:
    cell_id: str
    state: V8State
    occupancy: float
    resonance: float = 0.5
    scale: float = 1.0
    recursion_level: int = 0
    parent_id: str | None = None
    connections: tuple[str, ...] = ()
    metadata: Mapping[str, Any] = field(default_factory=dict, compare=False)

    def __post_init__(self) -> None:
        if not isinstance(self.cell_id, str) or not self.cell_id.strip():
            raise ValueError("cell_id must be a non-empty string")
        if not isinstance(self.state, V8State):
            raise TypeError("state must be a validated V8State")
        for name in ("occupancy", "resonance"):
            raw = getattr(self, name)
            if isinstance(raw, bool):
                raise ValueError(f"{name} must be numeric, not bool")
            value = float(raw)
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{name} must be finite and in [0, 1]")
            object.__setattr__(self, name, value)
        if isinstance(self.scale, bool):
            raise ValueError("scale must be numeric, not bool")
        scale = float(self.scale)
        if not math.isfinite(scale) or scale <= 0.0:
            raise ValueError("scale must be finite and positive")
        object.__setattr__(self, "scale", scale)
        if isinstance(self.recursion_level, bool) or not isinstance(self.recursion_level, int) or self.recursion_level < 0:
            raise ValueError("recursion_level must be a non-negative integer")
        if self.parent_id is not None:
            if not isinstance(self.parent_id, str) or not self.parent_id.strip() or self.parent_id == self.cell_id:
                raise ValueError("parent_id must be a non-empty id distinct from cell_id")
        links = tuple(self.connections)
        if any(not isinstance(link, str) or not link.strip() for link in links):
            raise ValueError("connections must contain non-empty cell ids")
        if self.cell_id in links or len(set(links)) != len(links):
            raise ValueError("connections cannot contain self-links or duplicates")
        object.__setattr__(self, "connections", links)
        try:
            metadata = MappingProxyType(dict(self.metadata))
        except (TypeError, ValueError) as exc:
            raise ValueError("metadata must be a mapping") from exc
        object.__setattr__(self, "metadata", metadata)

    @property
    def entropy_bits(self) -> float:
        # Resolve the Fermi helper only when entropy is requested, keeping the
        # core ABOM state package independent from optional kernel geometry.
        from .occupancy.fermi import binary_entropy_bits
        return binary_entropy_bits(self.occupancy)

    def as_schema(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "cell_id": self.cell_id,
            "state": self.state.as_schema(),
            "occupancy": self.occupancy,
            "entropy_bits": self.entropy_bits,
            "resonance": self.resonance,
            "scale": self.scale,
            "recursion_level": self.recursion_level,
            "parent_id": self.parent_id,
            "connections": list(self.connections),
            "metadata": dict(self.metadata),
        }


class MuCubeRegistry:
    """Identity index that validates parent containment and explicit links."""

    def __init__(self) -> None:
        self._cells: dict[str, MuCube] = {}

    def register(self, cell: MuCube) -> None:
        if not isinstance(cell, MuCube):
            raise TypeError("registry accepts MuCube instances")
        if cell.cell_id in self._cells:
            raise ValueError(f"duplicate μ-cube identity: {cell.cell_id}")
        self._cells[cell.cell_id] = cell

    def get(self, cell_id: str) -> MuCube:
        return self._cells[cell_id]

    def cells(self) -> tuple[MuCube, ...]:
        return tuple(self._cells.values())

    def children_of(self, parent_id: str) -> tuple[MuCube, ...]:
        if parent_id not in self._cells:
            raise KeyError(parent_id)
        return tuple(cell for cell in self._cells.values() if cell.parent_id == parent_id)

    def validate_links(self, *, require_symmetric: bool = False) -> None:
        for cell in self._cells.values():
            if cell.parent_id is not None and cell.parent_id not in self._cells:
                raise ValueError(f"unknown parent {cell.parent_id!r} for {cell.cell_id!r}")
            for target in cell.connections:
                if target not in self._cells:
                    raise ValueError(f"unknown connection {target!r} from {cell.cell_id!r}")
                if require_symmetric and cell.cell_id not in self._cells[target].connections:
                    raise ValueError(f"connection {cell.cell_id!r} -> {target!r} is not reciprocal")

        # Parent pointers must form a forest; no cell may contain itself indirectly.
        for start in self._cells.values():
            seen: set[str] = set()
            cursor = start
            while cursor.parent_id is not None:
                if cursor.cell_id in seen:
                    raise ValueError(f"recursive containment cycle involving {cursor.cell_id!r}")
                seen.add(cursor.cell_id)
                cursor = self._cells[cursor.parent_id]

        for cell in self._cells.values():
            if cell.parent_id is not None:
                parent = self._cells[cell.parent_id]
                if cell.recursion_level <= parent.recursion_level:
                    raise ValueError(
                        f"child {cell.cell_id!r} must have a greater recursion_level than parent {parent.cell_id!r}"
                    )
