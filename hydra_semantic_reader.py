"""Canonical Janus Hydra semantic reader and V8 projection pipeline.

Janus Hydra is the semantic translator. UHFE and UDFE are distinct formation
and decoherence outputs produced from the same validated V8 state.
"""
from __future__ import annotations
from dataclasses import dataclass
from collections.abc import Mapping, Sequence
import math
import numpy as np
from janus_hydra import (
    V8State, V8_KEYS, JANUS_BASELINE, formation_heads, inverse_heads, paired_heads,
)

HEAD_SUPPORT = {
    "bubble": ("h", "R", "u"),
    "honeycomb": ("tau", "s"),
    "spiderweb": ("f", "h", "R"),
    "chiraldna": ("chi", "tau", "R"),
    "compoundeye": ("s", "h", "d"),
}
INVERSE_SUPPORT = {
    "bubble": ("d", "u", "h"),
    "honeycomb": ("d", "tau", "s"),
    "spiderweb": ("d", "f", "h", "R"),
    "chiraldna": ("d", "chi", "tau", "R"),
    "compoundeye": ("d", "s", "h"),
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
    """One validated V8 state translated into separate UHFE/UDFE outputs."""
    state: V8State
    uhfe_heads: dict[str, float]
    udfe_heads: dict[str, float]
    paired_heads: dict[str, dict[str, float | str]]
    uhfe_channels: np.ndarray
    udfe_channels: np.ndarray
    coordinate_order: tuple[str, ...] = V8_KEYS
    reader: str = "janus_hydra_semantic_reader"
    schema_version: str = JANUS_BASELINE

def coerce_v8_state(source: V8State | Mapping | Sequence[float]) -> V8State:
    """Read V8State, canonical-key mapping, or ordered eight-value sequence."""
    if isinstance(source, V8State):
        state = source
    elif isinstance(source, Mapping):
        values = dict(source)
        if "T" in values:
            if "tau" in values:
                raise ValueError("Supply tau or its provisional alias T, not both")
            values["tau"] = values.pop("T")
        missing, extra = set(V8_KEYS) - set(values), set(values) - set(V8_KEYS)
        if missing or extra:
            raise ValueError(f"V8 mapping keys mismatch; missing={sorted(missing)}, unexpected={sorted(extra)}")
        state = V8State(**{key: float(values[key]) for key in V8_KEYS})
    elif (isinstance(source, Sequence) or isinstance(source, np.ndarray)) and not isinstance(source, (str, bytes)):
        if len(source) != 8:
            raise ValueError("Ordered V8 input must contain exactly 8 values")
        state = V8State(**dict(zip(V8_KEYS, map(float, source))))
    else:
        raise TypeError("V8 input must be V8State, canonical mapping, or 8-value sequence")
    state.validate()
    return state

def project_heads(head_scores: Mapping[str, float], *, inverse: bool = False) -> np.ndarray:
    """Project named heads using distinct formation or inverse support maps."""
    expected = {INVERSE_NAMES[name] if inverse else name for name in PAIR_KEYS}
    if set(head_scores) != expected:
        raise ValueError(f"Unexpected {'UDFE' if inverse else 'UHFE'} head vocabulary: expected={sorted(expected)}, received={sorted(head_scores)}")
    support_map = INVERSE_SUPPORT if inverse else HEAD_SUPPORT
    sums, counts = np.zeros(8, dtype=float), np.zeros(8, dtype=float)
    for forward_name, support in support_map.items():
        key = INVERSE_NAMES[forward_name] if inverse else forward_name
        value = float(head_scores[key])
        if not math.isfinite(value) or not 0.0 <= value <= 1.0:
            raise ValueError(f"Head score {key} must be finite and in [0, 1]")
        for coordinate in support:
            index = V8_KEYS.index(coordinate)
            sums[index] += value
            counts[index] += 1.0
    if np.any(counts == 0.0):
        raise RuntimeError("Semantic support map leaves a V8 coordinate uncovered")
    return sums / counts

def read_semantics(source: V8State | Mapping | Sequence[float]) -> HydraSemanticFrame:
    """Canonical pipeline: V8 input -> Janus translator -> UHFE/UDFE outputs."""
    state = coerce_v8_state(source)
    uhfe, udfe, pairs = formation_heads(state), inverse_heads(state), paired_heads(state)
    uhfe_channels, udfe_channels = project_heads(uhfe), project_heads(udfe, inverse=True)
    if len(pairs) != 5 or uhfe_channels.shape != (8,) or udfe_channels.shape != (8,):
        raise RuntimeError("Janus semantic projection violated its 5-head / 8-channel contract")
    return HydraSemanticFrame(state, uhfe, udfe, pairs, uhfe_channels, udfe_channels)
