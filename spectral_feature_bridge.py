"""Explicit spectral feature extraction and opt-in V8 projection.

No feature is inferred from a modality name and no V8 coordinate is assigned
automatically. Callers must declare each source field, reducer, unit, and all
eight coordinate mappings. Projections are model inputs, not physical laws.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
from typing import Mapping, Sequence

from spectral_provenance import SpectralObservation
from transition_algebra import V8State

V8_COORDINATES = ("h", "R", "u", "d", "tau", "chi", "s", "f")
REDUCERS = ("scalar", "mean", "min", "max", "rms")


def _finite_number(value: object, name: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} must be a numeric scalar")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{name} must be finite")
    return result


@dataclass(frozen=True)
class FeatureSpec:
    """Explicit instruction for extracting one named feature."""

    name: str
    source: str
    key: str
    unit: str
    reducer: str = "scalar"
    uncertainty_key: str | None = None

    def __post_init__(self) -> None:
        if not self.name.strip() or not self.key.strip() or not self.unit.strip():
            raise ValueError("feature name, key, and unit must be non-empty")
        if self.source not in ("raw", "derived"):
            raise ValueError("feature source must be 'raw' or 'derived'")
        if self.reducer not in REDUCERS:
            raise ValueError(f"reducer must be one of {REDUCERS}")


@dataclass(frozen=True)
class SpectralFeature:
    value: float
    unit: str
    source: str
    source_key: str
    reducer: str
    standard_uncertainty: float | None = None
    uncertainty_source_key: str | None = None
    uncertainty_assumption: str | None = None


@dataclass(frozen=True)
class SpectralFeatureVector:
    observation_id: str
    observation_digest: str
    modality: str
    features_json: str

    @property
    def features(self) -> dict[str, SpectralFeature]:
        raw = json.loads(self.features_json)
        return {name: SpectralFeature(**item) for name, item in raw.items()}


@dataclass(frozen=True)
class V8Projection:
    state: V8State
    observation_id: str
    observation_digest: str
    feature_vector_digest: str
    mapping_json: str


def _reduce(value: object, reducer: str, key: str) -> float:
    if reducer == "scalar":
        return _finite_number(value, key)
    if not isinstance(value, (list, tuple)) or not value:
        raise ValueError(f"{key} must be a non-empty sequence for reducer {reducer}")
    values = [_finite_number(item, key) for item in value]
    if reducer == "mean":
        return math.fsum(values) / len(values)
    if reducer == "min":
        return min(values)
    if reducer == "max":
        return max(values)
    if reducer == "rms":
        return math.sqrt(math.fsum(item * item for item in values) / len(values))
    raise ValueError(f"unsupported reducer: {reducer}")


def extract_spectral_features(
    observation: SpectralObservation,
    specs: Sequence[FeatureSpec],
) -> SpectralFeatureVector:
    """Extract only caller-declared scalar/sequence features from an observation."""
    if not specs:
        raise ValueError("at least one FeatureSpec is required")
    names = [spec.name for spec in specs]
    if len(set(names)) != len(names):
        raise ValueError("feature names must be unique")
    extracted: dict[str, dict[str, object]] = {}
    for spec in specs:
        source_values = (
            observation.raw_measurements if spec.source == "raw"
            else observation.derived_values
        )
        if spec.key not in source_values:
            raise KeyError(f"{spec.source} observation has no key {spec.key!r}")
        if spec.source == "raw":
            declared_unit = observation.units.get(spec.key)
            if declared_unit is None:
                raise ValueError(f"raw observation has no unit declaration for {spec.key!r}")
            if spec.unit != declared_unit:
                raise ValueError(
                    f"feature {spec.name!r} unit {spec.unit!r} does not match "
                    f"raw observation unit {declared_unit!r}"
                )
        source_value = source_values[spec.key]
        value = _reduce(source_value, spec.reducer, spec.key)
        standard_uncertainty = None
        uncertainty_assumption = None
        if spec.uncertainty_key is not None:
            uncertainty_data = observation.uncertainty
            if spec.uncertainty_key not in uncertainty_data:
                raise KeyError(f"uncertainty record has no key {spec.uncertainty_key!r}")
            sigma_value = uncertainty_data[spec.uncertainty_key]
            if spec.reducer == "scalar":
                standard_uncertainty = _finite_number(sigma_value, spec.uncertainty_key)
            else:
                if not isinstance(source_value, (list, tuple)) or not isinstance(sigma_value, (list, tuple)):
                    raise ValueError("sequence reducers require sequence measurements and sequence uncertainties")
                if len(source_value) != len(sigma_value) or not source_value:
                    raise ValueError("measurement and uncertainty sequences must have equal non-zero length")
                samples = [_finite_number(item, spec.key) for item in source_value]
                sigmas = [_finite_number(item, spec.uncertainty_key) for item in sigma_value]
                if any(item < 0 for item in sigmas):
                    raise ValueError("standard uncertainties must be non-negative")
                if spec.reducer == "mean":
                    standard_uncertainty = math.sqrt(math.fsum(item * item for item in sigmas)) / len(sigmas)
                elif spec.reducer in ("min", "max"):
                    index = min(range(len(samples)), key=samples.__getitem__) if spec.reducer == "min" else max(range(len(samples)), key=samples.__getitem__)
                    standard_uncertainty = sigmas[index]
                elif spec.reducer == "rms":
                    standard_uncertainty = (
                        math.sqrt(math.fsum((samples[i] * sigmas[i]) ** 2 for i in range(len(samples))))
                        / (len(samples) * value)
                        if value != 0 else math.sqrt(math.fsum(item * item for item in sigmas)) / len(sigmas)
                    )
                uncertainty_assumption = "independent_samples_first_order"
            if standard_uncertainty < 0:
                raise ValueError("standard uncertainties must be non-negative")
            if not math.isfinite(standard_uncertainty):
                raise ValueError("standard uncertainty must be finite")
        extracted[spec.name] = {
            "value": value,
            "unit": spec.unit,
            "source": spec.source,
            "source_key": spec.key,
            "reducer": spec.reducer,
            "standard_uncertainty": standard_uncertainty,
            "uncertainty_source_key": spec.uncertainty_key,
            "uncertainty_assumption": uncertainty_assumption,
        }
    encoded = json.dumps(extracted, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return SpectralFeatureVector(
        observation_id=observation.observation_id,
        observation_digest=observation.digest,
        modality=observation.modality,
        features_json=encoded,
    )


def project_features_to_v8(
    vector: SpectralFeatureVector,
    *,
    mapping: Mapping[str, Mapping[str, float]],
    offsets: Mapping[str, float] | None = None,
) -> V8Projection:
    """Apply a fully explicit linear feature-to-V8 map.

    mapping[coordinate][feature_name] is a caller-supplied coefficient.
    Every canonical V8 coordinate must be specified. No clipping, scaling,
    normalization, or physical interpretation is silently introduced.
    """
    if set(mapping) != set(V8_COORDINATES):
        raise ValueError(f"mapping must specify exactly {V8_COORDINATES}")
    features = vector.features
    offset_values = dict(offsets or {})
    if set(offset_values) - set(V8_COORDINATES):
        raise ValueError("offsets contain unknown V8 coordinates")
    values: dict[str, float] = {}
    canonical_mapping: dict[str, dict[str, float]] = {}
    for coordinate in V8_COORDINATES:
        terms = mapping[coordinate]
        if not isinstance(terms, Mapping) or not terms:
            raise ValueError(f"mapping for {coordinate} must contain at least one feature")
        coefficients: dict[str, float] = {}
        total = _finite_number(offset_values.get(coordinate, 0.0), f"{coordinate} offset")
        for feature_name, coefficient in terms.items():
            if feature_name not in features:
                raise KeyError(f"unknown feature {feature_name!r} in {coordinate} mapping")
            coefficient_value = _finite_number(coefficient, f"{coordinate}.{feature_name} coefficient")
            coefficients[feature_name] = coefficient_value
            total += coefficient_value * features[feature_name].value
        if not math.isfinite(total):
            raise ValueError(f"projected coordinate {coordinate} is non-finite")
        values[coordinate] = total
        canonical_mapping[coordinate] = dict(sorted(coefficients.items()))
    state = V8State(**values)
    mapping_record = {
        "schema": "pan-spectral-feature-to-v8-map-v1",
        "mapping": canonical_mapping,
        "offsets": {key: _finite_number(value, f"{key} offset")
                    for key, value in sorted(offset_values.items())},
        "feature_units": {key: value.unit for key, value in sorted(features.items())},
    }
    mapping_json = json.dumps(mapping_record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    vector_digest = hashlib.sha256(vector.features_json.encode("utf-8")).hexdigest()
    return V8Projection(
        state=state,
        observation_id=vector.observation_id,
        observation_digest=vector.observation_digest,
        feature_vector_digest=vector_digest,
        mapping_json=mapping_json,
    )
