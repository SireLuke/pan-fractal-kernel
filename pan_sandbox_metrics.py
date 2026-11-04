"""Lightly weighted PAN sandbox diagnostics for comparative experiments.

Sandbox metrics are supporting evidence, not substitutes for primary
measurements or physical validation. Only explicitly score-eligible metrics
contribute to the secondary score. Synthetic results receive a conservative
evidence multiplier; context-only diagnostics are retained but never scored.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from hashlib import sha256
import json
import math
from typing import Iterable

SCHEMA = "pan-sandbox-metrics-v1"
EVIDENCE_FACTORS = {
    "synthetic_exploratory": 0.25,
    "software_numerical": 0.50,
    "reference_comparison": 0.75,
}


def _canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _finite(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{label} must be numeric")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"{label} must be finite")
    return result


@dataclass(frozen=True)
class SandboxMetric:
    metric_id: str
    value: float
    unit: str
    direction: str
    protocol_id: str
    evidence_class: str
    role: str = "score"
    metric_weight: float = 1.0
    sample_count: int | None = None
    provenance_note: str = ""

    def __post_init__(self) -> None:
        if not self.metric_id.strip() or not self.unit.strip() or not self.protocol_id.strip():
            raise ValueError("metric_id, unit, and protocol_id must be non-empty")
        _finite(self.value, f"{self.metric_id} value")
        if self.direction not in ("higher_is_better", "lower_is_better", "context_only"):
            raise ValueError("invalid metric direction")
        if self.evidence_class not in EVIDENCE_FACTORS:
            raise ValueError("unknown evidence_class")
        if self.role not in ("score", "context"):
            raise ValueError("role must be 'score' or 'context'")
        if self.role == "score" and self.direction == "context_only":
            raise ValueError("scored metrics need a declared better-direction")
        if self.role == "context" and self.direction != "context_only":
            raise ValueError("context metrics must use direction='context_only'")
        weight = _finite(self.metric_weight, "metric_weight")
        if weight <= 0:
            raise ValueError("metric_weight must be positive")
        if self.sample_count is not None and (
            isinstance(self.sample_count, bool)
            or not isinstance(self.sample_count, int)
            or self.sample_count < 1
        ):
            raise ValueError("sample_count must be a positive integer or None")


@dataclass(frozen=True)
class SandboxMetricSet:
    experiment_id: str
    metrics: tuple[SandboxMetric, ...]
    provenance_id: str

    def __post_init__(self) -> None:
        if not self.experiment_id.strip() or not self.provenance_id.strip():
            raise ValueError("experiment_id and provenance_id must be non-empty")
        ids = [item.metric_id for item in self.metrics]
        if len(ids) != len(set(ids)):
            raise ValueError("metric_id values must be unique within a metric set")

    @property
    def digest(self) -> str:
        return sha256(_canonical(asdict(self)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SandboxComparisonReport:
    comparison_id: str
    left_experiment_id: str
    right_experiment_id: str
    left_digest: str
    right_digest: str
    metric_comparisons_json: str
    right_relative_advantage: float
    right_secondary_quality_score: float
    effective_weight_total: float
    scored_metric_count: int
    context_metric_count: int
    schema: str = SCHEMA

    @property
    def digest(self) -> str:
        return sha256(_canonical(asdict(self)).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class BlendedComparisonScore:
    comparison_id: str
    primary_score: float
    secondary_score: float
    secondary_weight: float
    primary_weight: float
    combined_score: float
    interpretation: str = (
        "Caller-defined primary score blended with a capped secondary sandbox "
        "diagnostic; not a physical validity or universal quality score."
    )


def compare_sandbox_metrics(
    left: SandboxMetricSet,
    right: SandboxMetricSet,
    *,
    comparison_id: str,
) -> SandboxComparisonReport:
    """Compare matched sandbox metrics; right_relative_advantage is in [-1, 1].

    Values are compared only when metric ID, unit, protocol, direction, evidence
    class, role, and declared metric weight agree. Relative differences are
    bounded to prevent a large-magnitude metric from dominating by units alone.
    """
    if not isinstance(comparison_id, str) or not comparison_id.strip():
        raise ValueError("comparison_id must be non-empty")
    left_by_id = {item.metric_id: item for item in left.metrics}
    right_by_id = {item.metric_id: item for item in right.metrics}
    common = sorted(set(left_by_id) & set(right_by_id))
    comparisons: dict[str, object] = {}
    weighted_sum = 0.0
    effective_weight_total = 0.0
    scored_count = 0
    context_count = 0

    for metric_id in common:
        a, b = left_by_id[metric_id], right_by_id[metric_id]
        contract_a = (a.unit, a.direction, a.protocol_id, a.evidence_class, a.role, a.metric_weight)
        contract_b = (b.unit, b.direction, b.protocol_id, b.evidence_class, b.role, b.metric_weight)
        if contract_a != contract_b:
            raise ValueError(f"incompatible comparison contract for metric {metric_id!r}")
        delta = _finite(b.value - a.value, f"{metric_id} delta")
        row: dict[str, object] = {
            "left": a.value,
            "right": b.value,
            "delta_right_minus_left": delta,
            "unit": a.unit,
            "direction": a.direction,
            "protocol_id": a.protocol_id,
            "evidence_class": a.evidence_class,
            "role": a.role,
            "sample_count_left": a.sample_count,
            "sample_count_right": b.sample_count,
            "provenance_left": a.provenance_note,
            "provenance_right": b.provenance_note,
        }
        if a.role == "context":
            row["relative_advantage"] = None
            row["effective_weight"] = 0.0
            context_count += 1
        else:
            oriented_delta = delta if a.direction == "higher_is_better" else -delta
            denominator = max(abs(a.value), abs(b.value), 1e-15)
            relative = max(-1.0, min(1.0, oriented_delta / denominator))
            evidence_factor = EVIDENCE_FACTORS[a.evidence_class]
            effective_weight = a.metric_weight * evidence_factor
            row["relative_advantage"] = relative
            row["evidence_factor"] = evidence_factor
            row["effective_weight"] = effective_weight
            weighted_sum += relative * effective_weight
            effective_weight_total += effective_weight
            scored_count += 1
        comparisons[metric_id] = row

    if scored_count == 0 or effective_weight_total <= 0:
        raise ValueError("no common score-eligible sandbox metrics to compare")

    advantage = weighted_sum / effective_weight_total
    return SandboxComparisonReport(
        comparison_id.strip(),
        left.experiment_id,
        right.experiment_id,
        left.digest,
        right.digest,
        _canonical(comparisons),
        advantage,
        (advantage + 1.0) / 2.0,
        effective_weight_total,
        scored_count,
        context_count,
    )


def blend_primary_and_sandbox_score(
    primary_score: float,
    sandbox_report: SandboxComparisonReport,
    *,
    secondary_weight: float = 0.10,
) -> BlendedComparisonScore:
    """Blend [0,1] higher-is-better scores with a hard 10% secondary cap."""
    primary = _finite(primary_score, "primary_score")
    weight = _finite(secondary_weight, "secondary_weight")
    if not 0.0 <= primary <= 1.0:
        raise ValueError("primary_score must lie in [0, 1]")
    if not 0.0 <= weight <= 0.10:
        raise ValueError("secondary_weight must lie in [0, 0.10]")
    secondary = _finite(sandbox_report.right_secondary_quality_score, "secondary score")
    combined = (1.0 - weight) * primary + weight * secondary
    return BlendedComparisonScore(
        sandbox_report.comparison_id,
        primary,
        secondary,
        weight,
        1.0 - weight,
        combined,
    )


def historical_sandbox_reference_profile() -> SandboxMetricSet:
    """Return a clearly labelled historical snapshot of selected sandbox results.

    These are reported software/synthetic benchmark values, not measurements
    from nature. Protocol IDs intentionally prevent comparison against a
    differently configured test without an explicit protocol match.
    """
    metrics = (
        SandboxMetric(
            "phase_lock_error_reduction_pct", 97.44, "percent", "higher_is_better",
            "phase_lock_30run_synthetic_v1", "synthetic_exploratory",
            sample_count=30,
            provenance_note="Synthetic feedback loop; 30 runs; mean phase error 1.3814 to 0.0253 rad.",
        ),
        SandboxMetric(
            "phase_reconstruction_rmse_after", 0.0465, "rad", "lower_is_better",
            "phase_reconstruction_known_offsets_v1", "synthetic_exploratory",
            provenance_note="Synthetic known cyclic offsets; offsets were supplied, not inferred.",
        ),
        SandboxMetric(
            "honeycomb_smoothing_rmse_after", 0.2037, "normalized_rmse", "lower_is_better",
            "honeycomb_radius3_37node_90edge_v1", "synthetic_exploratory",
            provenance_note="Synthetic radius-3 lattice, 37 nodes and 90 connections; alternative-structure comparison still needed.",
        ),
        SandboxMetric(
            "dual_hydra_roundtrip_error", 1.78e-15, "absolute_error", "lower_is_better",
            "dual_hydra_roundtrip_v1", "software_numerical",
            provenance_note="Floating-point-scale round-trip error; software inverse consistency only.",
        ),
        SandboxMetric(
            "hamiltonian_roundtrip_error", 4.03e-14, "absolute_error", "lower_is_better",
            "hamiltonian_roundtrip_v02", "software_numerical",
            provenance_note="Numerical Hamiltonian round-trip check.",
        ),
        SandboxMetric(
            "noether_drift_10000_steps", 5.30e-13, "absolute_drift", "lower_is_better",
            "noether_10000_steps_v1", "software_numerical",
            provenance_note="Numerical conservation drift over 10,000 integration steps.",
        ),
        SandboxMetric(
            "chern_number_deviation", 6.88e-15, "absolute_deviation", "lower_is_better",
            "chern_reference_check_v1", "software_numerical",
            provenance_note="Numerical deviation from an integer-valued reference invariant.",
        ),
        SandboxMetric(
            "su2_link_unitarity_error", 1.11e-15, "absolute_error", "lower_is_better",
            "su2_link_unitarity_v1", "software_numerical",
            provenance_note="SU(2) link unitarity numerical check; not real-time Yang-Mills validation.",
        ),
        SandboxMetric(
            "stable_landmark_persistence", 0.950, "fraction", "higher_is_better",
            "synthetic_temporal_persistence_30frame_v1", "synthetic_exploratory",
            provenance_note="Synthetic 30-frame scene; supplied poses/features and selected parameters.",
        ),
        SandboxMetric(
            "dual_hydra_corruption_detection_count", 73.0, "cases", "context_only",
            "dual_hydra_corruption_known_original_v1", "software_numerical",
            role="context",
            provenance_note="73/118 corruptions detected; verifier relied on access to known originals, so not scored as standalone detection quality.",
        ),
        SandboxMetric(
            "backward_perturbation_amplification", 165717.0, "amplification_factor", "context_only",
            "sandbox_v02_backward_perturbation_v1", "software_numerical",
            role="context",
            provenance_note="Large observed backward amplification; diagnostic/stability warning, not a higher/lower-is-better score.",
        ),
        SandboxMetric(
            "dissipative_contraction_after_4000_steps", 6.03e-6, "contraction_factor", "context_only",
            "sandbox_v02_dissipative_4000_steps_v1", "software_numerical",
            role="context",
            provenance_note="Expected dissipative contraction depends on the chosen operator; not scored as universally better.",
        ),
        SandboxMetric(
            "reverse_replay_error_v01", 0.8805, "absolute_error", "context_only",
            "sandbox_v01_reverse_replay_2000_cases", "software_numerical",
            role="context",
            provenance_note="Historical v0.1 reverse-replay failure retained as regression context, not current performance.",
        ),
        SandboxMetric(
            "fermi_filling_fraction", 0.37, "fraction", "context_only",
            "sandbox_v02_number_conserving_fermi_v1", "software_numerical",
            role="context",
            provenance_note="Configured filling fraction; conservation residual was below 1e-15. The target value itself is not a quality score.",
        ),
    )
        SandboxMetric(
            "schrodinger_l2_norm_drift", 1.11e-15, "absolute_drift", "lower_is_better",
            "schrodinger_norm_200_steps_v1", "software_numerical",
            provenance_note="Historical solver invariant; 200 steps; two tested scale factors. Not V8 validation.",
        ),
        SandboxMetric(
            "lotka_volterra_invariant_drift", 2.52e-10, "absolute_drift", "lower_is_better",
            "lotka_volterra_dt_0p01_6000_steps_v1", "software_numerical",
            provenance_note="Historical numerical invariant at dt=0.01 over 6,000 steps; separate solver benchmark.",
        ),
        SandboxMetric(
            "schwarzschild_reduced_invariant_drift", 3.75e-16, "absolute_drift", "lower_is_better",
            "schwarzschild_reduced_dt_0p005_12566_steps_v1", "software_numerical",
            provenance_note="Reduced Schwarzschild solver invariant; not a full GRMHD or black-hole simulation.",
        ),
        SandboxMetric(
            "maxwell_1d_e_rms_error", 8.55e-3, "normalized_rms_error", "lower_is_better",
            "maxwell_1d_periodic_vacuum_256grid_v1", "reference_comparison",
            sample_count=256,
            provenance_note="1D periodic transverse vacuum wave, epsilon0=mu0=1, cosine analytic reference, Courant 0.4969.",
        ),
        SandboxMetric(
            "maxwell_1d_b_rms_error", 6.13e-5, "normalized_rms_error", "lower_is_better",
            "maxwell_1d_periodic_vacuum_256grid_v1", "reference_comparison",
            sample_count=256,
            provenance_note="Same restricted 1D Maxwell analytic-reference run; zero energy drift was run-specific.",
        ),
        SandboxMetric(
            "v8_holdout_accuracy", 0.30, "fraction", "context_only",
            "v8_cluster_holdout_four_coordinates_v1", "reference_comparison",
            role="context",
            provenance_note="Historical holdout accuracy 0.30; only 4/8 coordinates scored. Weak/non-predictive result retained as caution.",
        ),
        SandboxMetric(
            "v8_clustering_adjusted_rand_index", 0.047, "ari", "context_only",
            "v8_cluster_holdout_four_coordinates_v1", "reference_comparison",
            role="context",
            provenance_note="Historical ARI 0.047 with permutation p=0.77; clustering unstable and coordinate ablation non-informative.",
        ),
        SandboxMetric(
            "randomized_v8_bounded_state_rate", 1.0, "fraction", "higher_is_better",
            "v8_randomized_quadrant_2000_seeded_v1", "synthetic_exploratory",
            sample_count=2000,
            provenance_note="2,000 seeded random V8 states; 100% bounded-state compliance is a software stress result, not physical evidence.",
        ),
        SandboxMetric(
            "golden_ratio_identity_error", 0.0, "absolute_error", "lower_is_better",
            "golden_ratio_phi_identity_v1", "software_numerical",
            provenance_note="Algebraic identity check phi^2=phi+1; exact arithmetic/property check, not empirical evidence.",
        ),
        SandboxMetric(
            "quadrant_classification_means", 0.0, "placeholder", "context_only",
            "v8_randomized_quadrant_2000_seeded_v1", "synthetic_exploratory",
            role="context",
            provenance_note="Historical formation/dissolution quadrant counts and means; means are classification-circular and intentionally not scored.",
        ),
    return SandboxMetricSet(
        experiment_id="pan_sandbox_historical_reference",
        metrics=metrics,
        provenance_id="prior_sandbox_reports_2026-10",
    )
