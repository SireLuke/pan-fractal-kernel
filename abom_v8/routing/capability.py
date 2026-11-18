"""Capability-space profile used to place and route model occupants.

This is a separate, versioned engineering profile.  It is NOT the canonical
V8 coordinate vector (see abom_v8/COORDINATE_CONTRACT.md): the eight axes below
describe what a model can do, they do not redefine (h, R, u, d, tau, chi, s, f).
Any mapping between the two spaces must be explicit, versioned and validated.
"""
from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import math

PROFILE_SCHEMA = "urn:pan:abom-v8:capability-profile:0.1"

# Each axis is normalised to [0, 1].  Bipolar descriptions name both poles.
AXES = (
    "recursive_depth",     # 0 shallow single-step  .. 1 deep multi-level recursion
    "temporal_horizon",    # 0 immediate            .. 1 long-horizon planning
    "creativity",          # 0 deterministic        .. 1 generative / exploratory
    "symbolic",            # 0 statistical          .. 1 symbolic / formal
    "memory_bandwidth",    # 0 stateless            .. 1 high retained-state throughput
    "context_coherence",   # 0 drifts quickly       .. 1 stays coherent over long context
    "tool_use",            # 0 none                 .. 1 reliable structured tool calls
    "coordination",        # 0 solo only            .. 1 multi-agent coordination
)


def _unit(name: str, value: object) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{name} must be numeric, not bool")
    try:
        number = float(value)  # type: ignore[arg-type]
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must be numeric") from exc
    if not math.isfinite(number) or not 0.0 <= number <= 1.0:
        raise ValueError(f"{name} must be finite and in [0, 1]")
    return number


def validate_weights(weights: Sequence[float] | None) -> tuple[float, ...]:
    """Per-axis non-negative weights; at least one must be positive."""
    if weights is None:
        return (1.0,) * len(AXES)
    result = tuple(weights)
    if len(result) != len(AXES):
        raise ValueError(f"weights must have exactly {len(AXES)} entries")
    checked: list[float] = []
    for axis, item in zip(AXES, result):
        if isinstance(item, bool):
            raise ValueError(f"weight for {axis} must be numeric, not bool")
        value = float(item)
        if not math.isfinite(value) or value < 0.0:
            raise ValueError(f"weight for {axis} must be finite and non-negative")
        checked.append(value)
    if not any(w > 0.0 for w in checked):
        raise ValueError("at least one weight must be positive")
    return tuple(checked)


def validate_minimums(minimums: Mapping[str, float]) -> dict[str, float]:
    """Per-axis hard floors, e.g. {"tool_use": 0.5}."""
    checked: dict[str, float] = {}
    for axis, value in minimums.items():
        if axis not in AXES:
            raise ValueError(f"unknown capability axis: {axis!r}")
        checked[axis] = _unit(f"minimum for {axis}", value)
    return checked


@dataclass(frozen=True, slots=True)
class CapabilityVector:
    """Immutable, validated 8-axis capability profile in [0, 1]."""

    values: tuple[float, ...]
    schema: str = PROFILE_SCHEMA

    def __post_init__(self) -> None:
        if self.schema != PROFILE_SCHEMA:
            raise ValueError(f"unsupported capability profile schema: {self.schema!r}")
        try:
            raw = tuple(self.values)
        except TypeError as exc:
            raise TypeError("values must be an iterable of eight numbers") from exc
        if len(raw) != len(AXES):
            raise ValueError(f"capability vector must contain exactly {len(AXES)} values")
        object.__setattr__(
            self, "values", tuple(_unit(axis, item) for axis, item in zip(AXES, raw))
        )

    @classmethod
    def from_mapping(cls, values: Mapping[str, float]) -> "CapabilityVector":
        missing = set(AXES) - set(values)
        extra = set(values) - set(AXES)
        if missing or extra:
            raise ValueError(
                f"capability mapping must name exactly the axes {AXES}; "
                f"missing={sorted(missing)}, extra={sorted(extra)}"
            )
        return cls(tuple(values[axis] for axis in AXES))

    def as_mapping(self) -> dict[str, float]:
        return dict(zip(AXES, self.values))

    def __getitem__(self, axis: str) -> float:
        try:
            return self.values[AXES.index(axis)]
        except ValueError as exc:
            raise KeyError(axis) from exc


def l1_distance(a: CapabilityVector, b: CapabilityVector,
                weights: Sequence[float] | None = None) -> float:
    """Weighted L1 distance; a metric when every weight is positive."""
    w = validate_weights(weights)
    return sum(wi * abs(x - y) for wi, x, y in zip(w, a.values, b.values))


def fit_cost(required: CapabilityVector, offered: CapabilityVector,
             weights: Sequence[float] | None = None,
             excess_penalty: float = 0.25) -> float:
    """Cost of serving `required` with `offered`.

    Shortfall (offered below required) costs 1 per unit; excess capability costs
    `excess_penalty` per unit, so over-qualified occupants lose ties to a closer
    fit.  With excess_penalty == 1 this equals l1_distance.
    """
    if not math.isfinite(excess_penalty) or excess_penalty < 0.0:
        raise ValueError("excess_penalty must be finite and non-negative")
    w = validate_weights(weights)
    total = 0.0
    for wi, need, have in zip(w, required.values, offered.values):
        total += wi * (max(need - have, 0.0) + excess_penalty * max(have - need, 0.0))
    return total
