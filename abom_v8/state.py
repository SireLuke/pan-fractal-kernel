"""Typed, versioned V8 coordinate state.

Coordinates remain ordered (h, R, u, d, tau, chi, s, f), each normalized to [0, 1].
The legacy input spelling T is accepted only as an alias for tau.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math
from typing import Any

SCHEMA_VERSION = "0.1"
COORDINATE_ORDER = ("h", "R", "u", "d", "tau", "chi", "s", "f")


@dataclass(frozen=True, slots=True)
class V8State:
    """Immutable normalized V8 coordinate vector."""

    coordinates: tuple[float, ...]
    schema_version: str = SCHEMA_VERSION

    def __post_init__(self) -> None:
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"unsupported ABOM-V8 schema version: {self.schema_version!r}")
        try:
            raw = tuple(self.coordinates)
        except TypeError as exc:
            raise TypeError("coordinates must be an iterable of eight numeric values") from exc
        if len(raw) != len(COORDINATE_ORDER):
            raise ValueError("V8 state must contain exactly eight coordinates")
        values: list[float] = []
        for name, item in zip(COORDINATE_ORDER, raw):
            if isinstance(item, bool):
                raise ValueError(f"coordinate {name} must be numeric, not bool")
            try:
                value = float(item)
            except (TypeError, ValueError) as exc:
                raise ValueError(f"coordinate {name} must be numeric") from exc
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"coordinate {name} must be finite and in [0, 1]")
            values.append(value)
        object.__setattr__(self, "coordinates", tuple(values))

    @classmethod
    def from_sequence(cls, values: Sequence[float]) -> "V8State":
        return cls(tuple(values))

    @classmethod
    def from_mapping(cls, values: Mapping[str, Any]) -> "V8State":
        data = dict(values)
        if "T" in data:
            if "tau" in data:
                raise ValueError("supply tau or its provisional alias T, not both")
            data["tau"] = data.pop("T")
        missing = set(COORDINATE_ORDER) - set(data)
        extra = set(data) - set(COORDINATE_ORDER)
        if missing or extra:
            raise ValueError(
                f"V8 mapping keys mismatch; missing={sorted(missing)}, unexpected={sorted(extra)}"
            )
        return cls(tuple(data[key] for key in COORDINATE_ORDER))

    def as_mapping(self) -> dict[str, float]:
        return dict(zip(COORDINATE_ORDER, self.coordinates))

    def as_schema(self, *, profile: str | None = None,
                  metadata: Mapping[str, Any] | None = None) -> dict[str, Any]:
        result: dict[str, Any] = {
            "schema_version": self.schema_version,
            "coordinate_order": list(COORDINATE_ORDER),
            "coordinates": list(self.coordinates),
        }
        if profile is not None:
            result["profile"] = profile
        if metadata is not None:
            result["metadata"] = dict(metadata)
        return result
