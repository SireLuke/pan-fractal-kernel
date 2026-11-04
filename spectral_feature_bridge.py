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
    coordinate_uncertainties_json: str = "{}"
    coordinate_covariance_json: str = "{}"


def _validate_covariance(
    names: Sequence[str], covariance: Mapping[str, Mapping[str, float]]
) -> list[list[float]]:
    """Validate a complete symmetric positive-semidefinite covariance matrix."""
    expected = set(names)
    if set(covariance) != expected:
        raise ValueError("covariance rows must cover exactly the feature names")
    matrix: list[list[float]] = []
    for row_name in names:
        row = covariance[row_name]
        if not isinstance(row, Mapping) or set(row) != expected:
            raise ValueError("each covariance row must cover exactly the feature names")
        matrix.append([_finite_number(row[col], f"covariance[{row_name},{col}]") for col in names])
    n = len(names)
    scale = max(1.0, max(abs(value) for row in matrix for value in row))
    tol = 1e-10 * scale
    for i in range(n):
        for j in range(n):
            if abs(matrix[i][j] - matrix[j][i]) > tol:
                raise ValueError("feature covariance matrix must be symmetric")
    # Jacobi eigenvalue iteration for a small dense matrix; reject negative
    # eigenvalues beyond floating-point tolerance (PSD permits zero modes).
    a = [row[:] for row in matrix]
    for _ in range(max(1, 50 * n * n)):
        p, q, largest = 0, 0, 0.0
        for i in range(n):
            for j in range(i + 1, n):
                if abs(a[i][j]) > largest:
                    p, q, largest = i, j, abs(a[i][j])
        if largest <= tol:
            break
        angle = 0.5 * math.atan2(2.0 * a[p][q], a[q][q] - a[p][p])
        cosine, sine = math.cos(angle), math.sin(angle)
        app, aqq, apq = a[p][p], a[q][q], a[p][q]
        a[p][p] = cosine*cosine*app - 2*sine*cosine*apq + sine*sine*aqq
        a[q][q] = sine*sine*app + 2*sine*cosine*apq + cosine*cosine*aqq
        a[p][q] = a[q][p] = 0.0
        for k in range(n):
            if k in (p, q):
                continue
            akp, akq = a[k][p], a[k][q]
            a[k][p] = a[p][k] = cosine*akp - sine*akq
            a[k][q] = a[q][k] = sine*akp + cosine*akq
    if any(a[i][i] < -tol for i in range(n)):
        raise ValueError("feature covariance matrix must be positive semidefinite")
    return matrix


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
                    if value == 0:
                        raise ValueError("RMS uncertainty is undefined at an all-zero feature vector")
                    standard_uncertainty = (
                        math.sqrt(math.fsum((samples[i] * sigmas[i]) ** 2 for i in range(len(samples))))
                        / (len(samples) * value)
                    )
                uncertainty_assumption = (
                    "selected_extremum_first_order" if spec.reducer in ("min", "max")
                    else "independent_samples_first_order"
                )
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
    feature_covariance: Mapping[str, Mapping[str, float]] | None = None,
    assume_independent_features: bool = False,
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
    feature_names = tuple(features)
    covariance_matrix = None
    if feature_covariance is not None:
        covariance_matrix = _validate_covariance(feature_names, feature_covariance)
        for index, name in enumerate(feature_names):
            sigma = features[name].standard_uncertainty
            if sigma is not None and not math.isclose(
                covariance_matrix[index][index], sigma * sigma, rel_tol=1e-7, abs_tol=1e-12
            ):
                raise ValueError(f"covariance diagonal for {name!r} conflicts with declared standard uncertainty")
    elif any(item.standard_uncertainty is not None for item in features.values()):
        if not assume_independent_features:
            raise ValueError(
                "feature uncertainties supplied without covariance; provide feature_covariance "
                "or explicitly set assume_independent_features=True"
            )
        covariance_matrix = [
            [(features[name].standard_uncertainty or 0.0) ** 2 if i == j else 0.0
             for j, name in enumerate(feature_names)]
            for i, name in enumerate(feature_names)
        ]
    coordinate_covariance: dict[str, dict[str, float]] = {}
    coordinate_uncertainties: dict[str, float] = {}
    if covariance_matrix is not None:
        for left in V8_COORDINATES:
            coordinate_covariance[left] = {}
            for right in V8_COORDINATES:
                total_cov = math.fsum(
                    canonical_mapping[left].get(name, 0.0)
                    * covariance_matrix[i][j]
                    * canonical_mapping[right].get(other, 0.0)
                    for i, name in enumerate(feature_names)
                    for j, other in enumerate(feature_names)
                )
                coordinate_covariance[left][right] = total_cov
            variance = coordinate_covariance[left][left]
            if variance < -1e-10:
                raise ValueError(f"negative propagated variance for {left}")
            coordinate_uncertainties[left] = math.sqrt(max(0.0, variance))
    mapping_record = {
        "schema": "pan-spectral-feature-to-v8-map-v1",
        "mapping": canonical_mapping,
        "offsets": {key: _finite_number(value, f"{key} offset")
                    for key, value in sorted(offset_values.items())},
        "feature_units": {key: value.unit for key, value in sorted(features.items())},
        "uncertainty_method": (
            "provided_covariance" if feature_covariance is not None
            else "independent_features_assumed" if covariance_matrix is not None
            else "not_propagated"
        ),
    }
    mapping_json = json.dumps(mapping_record, sort_keys=True, separators=(",", ":"), allow_nan=False)
    vector_digest = hashlib.sha256(vector.features_json.encode("utf-8")).hexdigest()
    return V8Projection(
        state=state,
        observation_id=vector.observation_id,
        observation_digest=vector.observation_digest,
        feature_vector_digest=vector_digest,
        mapping_json=mapping_json,
        coordinate_uncertainties_json=json.dumps(
            coordinate_uncertainties, sort_keys=True, separators=(",", ":"), allow_nan=False
        ),
        coordinate_covariance_json=json.dumps(
            coordinate_covariance, sort_keys=True, separators=(",", ":"), allow_nan=False
        ),
    )
