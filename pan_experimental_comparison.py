"""Immutable comparison reports for PAN experiments.

Comparisons are descriptive diagnostics over caller-supplied states/features.
They do not alter source observations, infer a privileged metric, or validate
physical laws. Geometry-specific E8/Gosset metrics are intentionally left to a
future adapter with its own independently validated distance contract.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Mapping, Sequence

from hydra_semantic_reader import read_semantics
from janus_hydra import V8_KEYS

PAIR_KEYS = ("bubble", "honeycomb", "spiderweb", "chiraldna", "compoundeye")
from spectral_feature_bridge import SpectralFeatureVector
from transition_algebra import V8State


SCHEMA = "pan-experimental-comparison-v1"


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


def _state_mapping(source: object) -> dict[str, float]:
    if hasattr(source, "as_mapping") and callable(source.as_mapping):
        source = source.as_mapping()
    if isinstance(source, Mapping):
        values = dict(source)
        if "T" in values and "tau" not in values:
            values["tau"] = values.pop("T")
        if set(values) != set(V8_KEYS):
            raise ValueError(f"V8 state must contain exactly {V8_KEYS}")
        result = {key: _finite(values[key], key) for key in V8_KEYS}
    elif isinstance(source, Sequence) and not isinstance(source, (str, bytes)):
        if len(source) != 8:
            raise ValueError("ordered V8 state must contain exactly 8 values")
        result = {key: _finite(value, key) for key, value in zip(V8_KEYS, source)}
    else:
        raise TypeError("V8 state must be a canonical mapping or ordered 8-value sequence")
    if any(not 0.0 <= value <= 1.0 for value in result.values()):
        raise ValueError("comparison V8 coordinates must be normalized to [0, 1]")
    return result


def _v8_metrics(left: Mapping[str, float], right: Mapping[str, float],
                weights: Mapping[str, float] | None = None) -> dict[str, object]:
    delta = {key: right[key] - left[key] for key in V8_KEYS}
    weight_values = {key: 1.0 for key in V8_KEYS}
    if weights is not None:
        if set(weights) - set(V8_KEYS):
            raise ValueError("weights contain unknown V8 coordinates")
        for key, value in weights.items():
            weight = _finite(value, f"{key} weight")
            if weight < 0:
                raise ValueError("comparison weights must be non-negative")
            weight_values[key] = weight
    l2 = math.sqrt(math.fsum(value * value for value in delta.values()))
    weighted = math.sqrt(math.fsum(weight_values[key] * delta[key] ** 2 for key in V8_KEYS))
    return {
        "coordinate_delta": delta,
        "l1_distance": math.fsum(abs(value) for value in delta.values()),
        "l2_distance": l2,
        "linf_distance": max(abs(value) for value in delta.values()),
        "rms_distance": math.sqrt(math.fsum(value * value for value in delta.values()) / 8.0),
        "weighted_l2_distance": weighted,
        "weights": weight_values,
    }


@dataclass(frozen=True)
class ComparisonReport:
    comparison_id: str
    left_id: str
    right_id: str
    left_digest: str
    right_digest: str
    metrics_json: str
    schema: str = SCHEMA

    @property
    def digest(self) -> str:
        return sha256(_canonical(asdict(self)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SpectralComparisonReport:
    comparison_id: str
    left_observation_id: str
    right_observation_id: str
    left_observation_digest: str
    right_observation_digest: str
    feature_deltas_json: str
    uncertainty_comparison_json: str
    assumptions_json: str
    schema: str = SCHEMA

    @property
    def digest(self) -> str:
        return sha256(_canonical(asdict(self)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class JanusComparisonReport:
    comparison_id: str
    left_state_json: str
    right_state_json: str
    uhfe_metrics_json: str
    udfe_metrics_json: str
    paired_head_gap_json: str
    schema: str = SCHEMA

    @property
    def digest(self) -> str:
        return sha256(_canonical(asdict(self)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class PathComparisonReport:
    comparison_id: str
    left_path_id: str
    right_path_id: str
    step_metrics_json: str
    endpoint_metrics_json: str
    max_step_l2_distance: float
    cumulative_step_l2_distance: float
    schema: str = SCHEMA

    @property
    def digest(self) -> str:
        return sha256(_canonical(asdict(self)).encode("utf-8")).hexdigest()


def compare_v8_states(
    left: object,
    right: object,
    *,
    comparison_id: str,
    left_id: str = "left",
    right_id: str = "right",
    weights: Mapping[str, float] | None = None,
) -> ComparisonReport:
    """Compare two normalized V8 states without mutating either input."""
    if not isinstance(comparison_id, str) or not comparison_id.strip():
        raise ValueError("comparison_id must be non-empty")
    left_values, right_values = _state_mapping(left), _state_mapping(right)
    metrics = _v8_metrics(left_values, right_values, weights)
    return ComparisonReport(
        comparison_id.strip(), left_id, right_id,
        sha256(_canonical(left_values).encode()).hexdigest(),
        sha256(_canonical(right_values).encode()).hexdigest(),
        _canonical(metrics),
    )


def compare_spectral_features(
    left: SpectralFeatureVector,
    right: SpectralFeatureVector,
    *,
    comparison_id: str,
    assume_independent_observations: bool = False,
) -> SpectralComparisonReport:
    """Compare named features only when both vectors declare matching units.

    Combined standard uncertainty is calculated only when the caller
    explicitly declares the two observations independent.
    """
    if not isinstance(comparison_id, str) or not comparison_id.strip():
        raise ValueError("comparison_id must be non-empty")
    left_features, right_features = left.features, right.features
    if set(left_features) != set(right_features):
        raise ValueError("spectral feature names must match exactly")
    deltas: dict[str, object] = {}
    uncertainty: dict[str, object] = {}
    for name in sorted(left_features):
        a, b = left_features[name], right_features[name]
        if a.unit != b.unit:
            raise ValueError(f"feature {name!r} has incompatible units: {a.unit!r} vs {b.unit!r}")
        delta = _finite(b.value - a.value, f"{name} delta")
        deltas[name] = {
            "left": a.value, "right": b.value, "delta_right_minus_left": delta,
            "unit": a.unit, "left_source": a.source, "left_source_key": a.source_key,
            "right_source": b.source, "right_source_key": b.source_key,
        }
        if assume_independent_observations and (
            a.standard_uncertainty is not None and b.standard_uncertainty is not None
        ):
            combined = math.hypot(a.standard_uncertainty, b.standard_uncertainty)
            uncertainty[name] = {
                "combined_standard_uncertainty": combined,
                "standardized_delta": (delta / combined if combined > 0 else None),
                "method": "independent_observations_quadrature",
                "degenerate_zero_uncertainty": combined == 0,
            }
        else:
            uncertainty[name] = {
                "combined_standard_uncertainty": None,
                "standardized_delta": None,
                "method": "not_computed",
            }
    assumptions = {
        "unit_policy": "exact_declared_unit_label_match",
        "uncertainty_policy": (
            "independent_observations_assumed" if assume_independent_observations
            else "no_cross_observation_independence_assumption"
        ),
        "comparison": "feature_value_difference_only_no_resampling_or_alignment",
    }
    return SpectralComparisonReport(
        comparison_id.strip(), left.observation_id, right.observation_id,
        left.observation_digest, right.observation_digest,
        _canonical(deltas), _canonical(uncertainty), _canonical(assumptions),
    )


def compare_janus_states(
    left: object,
    right: object,
    *,
    comparison_id: str,
) -> JanusComparisonReport:
    """Compare UHFE and UDFE semantic projections separately and side by side."""
    left_values, right_values = _state_mapping(left), _state_mapping(right)
    left_frame, right_frame = read_semantics(left_values), read_semantics(right_values)
    left_uhfe = dict(zip(V8_KEYS, map(float, left_frame.uhfe_channels)))
    right_uhfe = dict(zip(V8_KEYS, map(float, right_frame.uhfe_channels)))
    left_udfe = dict(zip(V8_KEYS, map(float, left_frame.udfe_channels)))
    right_udfe = dict(zip(V8_KEYS, map(float, right_frame.udfe_channels)))
    left_pairs, right_pairs = left_frame.paired_heads, right_frame.paired_heads
    gaps: dict[str, object] = {}
    for head in PAIR_KEYS:
        left_gap = float(left_pairs[head]["formation"]) - float(left_pairs[head]["inverse"])
        right_gap = float(right_pairs[head]["formation"]) - float(right_pairs[head]["inverse"])
        gaps[head] = {
            "left_formation_minus_inverse": left_gap,
            "right_formation_minus_inverse": right_gap,
            "gap_change_right_minus_left": right_gap - left_gap,
        }
    return JanusComparisonReport(
        comparison_id.strip(),
        _canonical(left_values), _canonical(right_values),
        _canonical(_v8_metrics(left_uhfe, right_uhfe)),
        _canonical(_v8_metrics(left_udfe, right_udfe)),
        _canonical(gaps),
    )


def compare_paths(
    left_path: Sequence[object],
    right_path: Sequence[object],
    *,
    comparison_id: str,
    left_path_id: str = "forward",
    right_path_id: str = "reverse",
) -> PathComparisonReport:
    """Compare already aligned paths; no implicit interpolation or resampling."""
    if not isinstance(comparison_id, str) or not comparison_id.strip():
        raise ValueError("comparison_id must be non-empty")
    if not left_path or not right_path:
        raise ValueError("both paths must contain at least one state")
    if len(left_path) != len(right_path):
        raise ValueError("paths must have equal lengths; resampling must be explicit")
    left_states = [_state_mapping(item) for item in left_path]
    right_states = [_state_mapping(item) for item in right_path]
    steps = [
        _v8_metrics(a, b)
        for a, b in zip(left_states, right_states)
    ]
    distances = [float(item["l2_distance"]) for item in steps]
    endpoint = _v8_metrics(left_states[-1], right_states[-1])
    return PathComparisonReport(
        comparison_id.strip(), left_path_id, right_path_id,
        _canonical(steps), _canonical(endpoint),
        max(distances), math.fsum(distances),
    )
