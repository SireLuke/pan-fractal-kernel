"""Deterministic spectral uncertainty and sensitivity experiments.

The harness evaluates a caller-supplied linear feature-to-V8 map. It provides
one-feature-at-a-time finite differences, seeded Gaussian Monte Carlo trials,
and a forward/reverse accumulation-order check. These are numerical robustness
tests for the declared model, not physical validation of the mapping.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
import math
import random
from typing import Mapping, Sequence

from spectral_feature_bridge import (
    V8_COORDINATES,
    SpectralFeatureVector,
    _finite_number,
    _validate_covariance,
    project_features_to_v8,
)


@dataclass(frozen=True)
class OneFactorResult:
    feature: str
    perturbation_scale: float
    coordinate_derivatives_json: str
    coordinate_deltas_json: str


@dataclass(frozen=True)
class MonteCarloSummary:
    samples: int
    seed: int
    coordinate_mean_json: str
    coordinate_stddev_json: str
    coordinate_quantiles_json: str


@dataclass(frozen=True)
class SpectralSensitivityReport:
    observation_id: str
    observation_digest: str
    feature_vector_digest: str
    mapping_digest: str
    baseline_state_json: str
    one_factor_results: tuple[OneFactorResult, ...]
    monte_carlo: MonteCarloSummary | None
    forward_reverse_max_abs_delta: float
    assumptions_json: str


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _cholesky_psd(matrix: Sequence[Sequence[float]]) -> list[list[float]]:
    """Return a lower factor L with L L^T = matrix, including PSD zero modes."""
    n = len(matrix)
    scale = max(1.0, max(abs(x) for row in matrix for x in row))
    tol = 1e-10 * scale
    lower = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1):
            residual = matrix[i][j] - math.fsum(
                lower[i][k] * lower[j][k] for k in range(j)
            )
            if i == j:
                if residual < -tol:
                    raise ValueError("covariance matrix is not positive semidefinite")
                lower[i][j] = math.sqrt(max(0.0, residual))
            elif lower[j][j] > math.sqrt(tol):
                lower[i][j] = residual / lower[j][j]
            elif abs(residual) > tol:
                raise ValueError("covariance matrix has an inconsistent singular factor")
    return lower


def _state_values(
    vector: SpectralFeatureVector,
    mapping: Mapping[str, Mapping[str, float]],
    offsets: Mapping[str, float] | None = None,
    *,
    reverse: bool = False,
) -> dict[str, float]:
    features = vector.features
    offsets = offsets or {}
    result: dict[str, float] = {}
    for coordinate in V8_COORDINATES:
        items = list(mapping[coordinate].items())
        if reverse:
            items.reverse()
        terms = [
            _finite_number(coefficient, f"{coordinate}.{name}") * features[name].value
            for name, coefficient in items
        ]
        result[coordinate] = (
            _finite_number(offsets.get(coordinate, 0.0), f"{coordinate} offset")
            + math.fsum(terms)
        )
        if not math.isfinite(result[coordinate]):
            raise ValueError(f"non-finite coordinate {coordinate}")
    return result


def _perturbed_vector(
    vector: SpectralFeatureVector, deltas: Mapping[str, float]
) -> SpectralFeatureVector:
    records = {name: asdict(feature) for name, feature in vector.features.items()}
    for name, delta in deltas.items():
        if name not in records:
            raise KeyError(f"unknown feature {name!r}")
        records[name]["value"] = _finite_number(
            records[name]["value"] + delta, f"perturbed {name}"
        )
    return SpectralFeatureVector(
        observation_id=vector.observation_id,
        observation_digest=vector.observation_digest,
        modality=vector.modality,
        features_json=_canonical(records),
    )


def _percentile(values: Sequence[float], probability: float) -> float:
    ordered = sorted(values)
    position = (len(ordered) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    if lower == upper:
        return ordered[lower]
    fraction = position - lower
    return ordered[lower] * (1.0 - fraction) + ordered[upper] * fraction


def run_spectral_sensitivity(
    vector: SpectralFeatureVector,
    *,
    mapping: Mapping[str, Mapping[str, float]],
    offsets: Mapping[str, float] | None = None,
    feature_covariance: Mapping[str, Mapping[str, float]] | None = None,
    assume_independent_features: bool = False,
    perturbation_scales: Mapping[str, float] | None = None,
    monte_carlo_samples: int = 1000,
    seed: int = 0,
) -> SpectralSensitivityReport:
    """Run OAT finite differences and seeded Gaussian Monte Carlo.

    OAT uses one standard uncertainty per feature unless an explicit positive
    perturbation scale is supplied. Monte Carlo requires a complete supplied
    covariance matrix or an explicit independent-feature assumption.
    """
    if set(mapping) != set(V8_COORDINATES):
        raise ValueError(f"mapping must specify exactly {V8_COORDINATES}")
    features = vector.features
    for coordinate, terms in mapping.items():
        if not isinstance(terms, Mapping) or not terms:
            raise ValueError(f"mapping for {coordinate} must not be empty")
        for name, coefficient in terms.items():
            if name not in features:
                raise KeyError(f"unknown feature {name!r}")
            _finite_number(coefficient, f"{coordinate}.{name}")
    if isinstance(monte_carlo_samples, bool) or not isinstance(monte_carlo_samples, int):
        raise TypeError("monte_carlo_samples must be an integer")
    if monte_carlo_samples < 0:
        raise ValueError("monte_carlo_samples must be non-negative")
    if isinstance(seed, bool) or not isinstance(seed, int):
        raise TypeError("seed must be an integer")
    scales = dict(perturbation_scales or {})
    if set(scales) - set(features):
        raise ValueError("perturbation_scales contains unknown feature names")
    for name, scale in scales.items():
        if _finite_number(scale, f"{name} perturbation scale") <= 0:
            raise ValueError("perturbation scales must be positive")

    # The projection API also computes covariance diagnostics. For OAT and
    # baseline-state evaluation, an independent diagonal is only an internal
    # placeholder; it is not used as a joint sampling model. Monte Carlo's
    # independence policy is checked separately below and remains opt-in.
    projection_uncertainty_kwargs = (
        {"feature_covariance": feature_covariance}
        if feature_covariance is not None
        else {"assume_independent_features": True}
    )
    base_projection = project_features_to_v8(
        vector, mapping=mapping, offsets=offsets, **projection_uncertainty_kwargs
    )
    baseline = base_projection.state.as_mapping()
    one_factor: list[OneFactorResult] = []
    for name, feature in features.items():
        scale = scales.get(name, feature.standard_uncertainty)
        if scale is None:
            continue
        scale = _finite_number(scale, f"{name} perturbation scale")
        if scale <= 0:
            raise ValueError(f"perturbation scale for {name!r} must be positive")
        plus = _perturbed_vector(vector, {name: scale})
        minus = _perturbed_vector(vector, {name: -scale})
        plus_state = project_features_to_v8(
            plus, mapping=mapping, offsets=offsets, **projection_uncertainty_kwargs
        ).state.as_mapping()
        minus_state = project_features_to_v8(
            minus, mapping=mapping, offsets=offsets, **projection_uncertainty_kwargs
        ).state.as_mapping()
        derivatives = {
            coord: (plus_state[coord] - minus_state[coord]) / (2.0 * scale)
            for coord in V8_COORDINATES
        }
        deltas = {
            coord: plus_state[coord] - baseline[coord]
            for coord in V8_COORDINATES
        }
        one_factor.append(
            OneFactorResult(name, scale, _canonical(derivatives), _canonical(deltas))
        )

    covariance = None
    feature_names = tuple(features)
    if feature_covariance is not None:
        covariance = _validate_covariance(feature_names, feature_covariance)
        for i, name in enumerate(feature_names):
            sigma = features[name].standard_uncertainty
            if sigma is not None and not math.isclose(
                covariance[i][i], sigma * sigma, rel_tol=1e-7, abs_tol=1e-12
            ):
                raise ValueError(
                    f"covariance diagonal for {name!r} conflicts with feature uncertainty"
                )
    elif any(item.standard_uncertainty is not None for item in features.values()):
        if not assume_independent_features:
            raise ValueError(
                "Monte Carlo requires covariance or explicit independent-feature assumption"
            )
        covariance = [
            [
                (features[name].standard_uncertainty or 0.0) ** 2 if i == j else 0.0
                for j, name in enumerate(feature_names)
            ]
            for i, name in enumerate(feature_names)
        ]
    elif monte_carlo_samples:
        raise ValueError(
            "Monte Carlo requires declared feature uncertainties/covariance"
        )

    mc_summary = None
    if monte_carlo_samples:
        factor = _cholesky_psd(covariance)
        rng = random.Random(seed)
        samples_by_coordinate = {coord: [] for coord in V8_COORDINATES}
        for _ in range(monte_carlo_samples):
            z = [rng.gauss(0.0, 1.0) for _ in feature_names]
            perturbations = {
                name: math.fsum(factor[i][j] * z[j] for j in range(i + 1))
                for i, name in enumerate(feature_names)
            }
            sample_vector = _perturbed_vector(vector, perturbations)
            state = project_features_to_v8(
                sample_vector, mapping=mapping, offsets=offsets, **projection_uncertainty_kwargs
            ).state.as_mapping()
            for coordinate in V8_COORDINATES:
                samples_by_coordinate[coordinate].append(state[coordinate])
        means = {
            coord: math.fsum(values) / len(values)
            for coord, values in samples_by_coordinate.items()
        }
        stddevs = {
            coord: math.sqrt(
                math.fsum((value - means[coord]) ** 2 for value in values)
                / len(values)
            )
            for coord, values in samples_by_coordinate.items()
        }
        quantiles = {
            coord: {
                str(q): _percentile(values, q)
                for q in (0.025, 0.5, 0.975)
            }
            for coord, values in samples_by_coordinate.items()
        }
        mc_summary = MonteCarloSummary(
            monte_carlo_samples,
            seed,
            _canonical(means),
            _canonical(stddevs),
            _canonical(quantiles),
        )

    forward = _state_values(vector, mapping, offsets, reverse=False)
    reverse = _state_values(vector, mapping, offsets, reverse=True)
    path_delta = max(
        abs(forward[key] - reverse[key]) for key in V8_COORDINATES
    )
    assumptions = {
        "oat_scale": "explicit_perturbation_scale_or_feature_standard_uncertainty",
        "monte_carlo": (
            "provided_covariance"
            if feature_covariance is not None
            else "independent_features_assumed"
            if covariance is not None
            else "not_run"
        ),
        "sampling": "seeded_gaussian_first_order_feature_uncertainty",
        "path_order": "linear_accumulation_order_invariance_check",
        "mapping_interpretation": "caller_defined_model_projection_not_physical_law",
    }
    return SpectralSensitivityReport(
        observation_id=vector.observation_id,
        observation_digest=vector.observation_digest,
        feature_vector_digest=base_projection.feature_vector_digest,
        mapping_digest=hashlib.sha256(
            base_projection.mapping_json.encode("utf-8")
        ).hexdigest(),
        baseline_state_json=_canonical(baseline),
        one_factor_results=tuple(one_factor),
        monte_carlo=mc_summary,
        forward_reverse_max_abs_delta=path_delta,
        assumptions_json=_canonical(assumptions),
    )
