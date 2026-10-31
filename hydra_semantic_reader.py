"""Canonical Janus Hydra semantic reader and V8 projection pipeline.

All normalized V8 inputs should pass through this module before UHFE/UDFE
interpretation or JOBF evaluation. The reader preserves the distinct inverse
vocabulary while pairing each inverse head with its formation counterpart.
"""
from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import math
import numpy as np

from janus_hydra import (
    V8State, V8_KEYS, formation_heads, inverse_heads, paired_heads,
)

HEAD_SUPPORT = {
    "bubble": ("h", "R", "u"),
    "honeycomb": ("tau", "s"),
    "spiderweb": ("f", "h", "R"),
    "chiraldna": ("chi", "tau", "R"),
    "compoundeye": ("s", "h", "d"),
}
INVERSE_NAMES = {
    "bubble": "antibubble_cavitation",
    "honeycomb": "inversehoneycomb",
    "spiderweb": "inversespiderweb_radialvoid",
    "chiraldna": "chiralvoid",
    "compoundeye": "discretesingulardots_inversecompoundeye",
}
PAIR_KEYS = tuple(HEAD_SUPPORT)


@dataclass(frozen=True)
class HydraSemanticFrame:
    """One validated V8 state interpreted through both Janus semantic fields."""
    state: V8State
    uhfe_heads: dict[str, float]
    udfe_heads: dict[str, float]
    paired_heads: dict[str, dict[str, float | str]]
    uhfe_channels: np.ndarray
    udfe_channels: np.ndarray
    coordinate_order: tuple[str, ...] = V8_KEYS
    reader: str = "janus_hydra_semantic_reader"
    schema_version: str = "1.0"


def coerce_v8_state(source: V8State | Mapping | Sequence[float]) -> V8State:
    """Read a V8State, canonical-key mapping, or eight-value ordered sequence.

    Mapping keys must use canonical V8 names. A provisional 'T' alias is
    accepted for tau only when tau is absent. Values are never silently clamped.
    """
    if isinstance(source, V8State):
        state = source
    elif isinstance(source, Mapping):
        values = dict(source)
        if "T" in values:
            if "tau" in values:
                raise ValueError("Supply tau or its provisional alias T, not both")
            values["tau"] = values.pop("T")
        missing = set(V8_KEYS) - set(values)
        extra = set(values) - set(V8_KEYS)
        if missing or extra:
            raise ValueError(
                f"V8 mapping keys mismatch; missing={sorted(missing)}, "
                f"unexpected={sorted(extra)}"
            )
        state = V8State(**{key: float(values[key]) for key in V8_KEYS})
    elif isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
        if len(source) != 8:
            raise ValueError("Ordered V8 input must contain exactly 8 values")
        state = V8State(**dict(zip(V8_KEYS, map(float, source))))
    else:
        raise TypeError("V8 input must be V8State, canonical mapping, or 8-value sequence")
    state.validate()
    return state


def project_heads(head_scores: Mapping[str, float], *, inverse: bool = False) -> np.ndarray:
    """Project five named heads to the shared ordered eight-channel V8 basis."""
    expected = {
        INVERSE_NAMES[name] if inverse else name for name in PAIR_KEYS
    }
    if set(head_scores) != expected:
        raise ValueError(
            f"Unexpected {'UDFE' if inverse else 'UHFE'} head vocabulary: "
            f"expected={sorted(expected)}, received={sorted(head_scores)}"
        )
    sums = np.zeros(8, dtype=float)
    counts = np.zeros(8, dtype=float)
    for forward_name, support in HEAD_SUPPORT.items():
        key = INVERSE_NAMES[forward_name] if inverse else forward_name
        value = float(head_scores[key])
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"Head score {key} must be finite and in [0, 1]")
        for coordinate in support:
            index = V8_KEYS.index(coordinate)
            sums[index] += value
            counts[index] += 1.0
    return sums / counts


def read_semantics(source: V8State | Mapping | Sequence[float]) -> HydraSemanticFrame:
    """Canonical pipeline: V8 input -> Janus heads -> paired semantics -> V8 channels."""
    state = coerce_v8_state(source)
    uhfe = formation_heads(state)
    udfe = inverse_heads(state)
    pairs = paired_heads(state)
    uhfe_channels = project_heads(uhfe)
    udfe_channels = project_heads(udfe, inverse=True)
    if len(pairs) != 5 or uhfe_channels.shape != (8,) or udfe_channels.shape != (8,):
        raise RuntimeError("Janus semantic projection violated its 5-head / 8-channel contract")
    return HydraSemanticFrame(
        state=state,
        uhfe_heads=uhfe,
        udfe_heads=udfe,
        paired_heads=pairs,
        uhfe_channels=uhfe_channels,
        udfe_channels=udfe_channels,
    )
