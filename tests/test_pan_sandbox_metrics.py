import json

import pytest

from pan_sandbox_metrics import (
    SandboxMetric,
    SandboxMetricSet,
    blend_primary_and_sandbox_score,
    compare_sandbox_metrics,
    historical_sandbox_reference_profile,
)


def metric_set(experiment_id, value, *, evidence="synthetic_exploratory"):
    return SandboxMetricSet(
        experiment_id=experiment_id,
        provenance_id=f"fixture-{experiment_id}",
        metrics=(
            SandboxMetric(
                "phase_lock_error_reduction_pct", value, "percent",
                "higher_is_better", "phase_lock_30run_synthetic_v1",
                evidence, sample_count=30,
            ),
            SandboxMetric(
                "backward_perturbation_amplification", 100.0, "factor",
                "context_only", "sandbox_v02_backward_perturbation_v1",
                "software_numerical", role="context",
            ),
        ),
    )


def test_comparison_scores_only_matched_eligible_metrics_and_keeps_context():
    left, right = metric_set("left", 80.0), metric_set("right", 90.0)
    report = compare_sandbox_metrics(left, right, comparison_id="sandbox-compare")
    rows = json.loads(report.metric_comparisons_json)
    assert report.scored_metric_count == 1
    assert report.context_metric_count == 1
    assert rows["phase_lock_error_reduction_pct"]["relative_advantage"] == pytest.approx(1 / 9)
    assert rows["backward_perturbation_amplification"]["relative_advantage"] is None
    assert report.right_secondary_quality_score == pytest.approx((1 + 1 / 9) / 2)
    assert len(report.digest) == 64


def test_synthetic_evidence_is_downweighted_against_reference_evidence():
    synthetic = metric_set("synthetic", 80.0, evidence="synthetic_exploratory")
    reference = metric_set("reference", 80.0, evidence="reference_comparison")
    assert synthetic.metrics[0].evidence_class != reference.metrics[0].evidence_class
    with pytest.raises(ValueError, match="incompatible comparison contract"):
        compare_sandbox_metrics(synthetic, reference, comparison_id="mismatch")


def test_secondary_blend_is_capped_at_ten_percent_and_primary_dominates():
    report = compare_sandbox_metrics(metric_set("a", 80), metric_set("b", 90),
                                     comparison_id="blend")
    blended = blend_primary_and_sandbox_score(0.8, report)
    assert blended.secondary_weight == 0.10
    assert blended.primary_weight == 0.90
    assert blended.combined_score == pytest.approx(0.9 * 0.8 + 0.1 * report.right_secondary_quality_score)
    with pytest.raises(ValueError, match="0, 0.10"):
        blend_primary_and_sandbox_score(0.8, report, secondary_weight=0.2)


def test_historical_profile_separates_score_metrics_from_context_only_diagnostics():
    profile = historical_sandbox_reference_profile()
    by_id = {item.metric_id: item for item in profile.metrics}
    assert by_id["dual_hydra_roundtrip_error"].role == "score"
    assert by_id["backward_perturbation_amplification"].role == "context"
    assert by_id["reverse_replay_error_v01"].role == "context"
    assert by_id["fermi_filling_fraction"].role == "context"
    assert len(profile.digest) == 64


def test_incompatible_protocol_units_and_metric_ids_are_not_silently_compared():
    left = metric_set("left", 80)
    altered = SandboxMetricSet("right", (
        SandboxMetric("phase_lock_error_reduction_pct", 90, "rad", "higher_is_better",
                      "phase_lock_30run_synthetic_v1", "synthetic_exploratory"),
    ), "right-source")
    with pytest.raises(ValueError, match="incompatible comparison contract"):
        compare_sandbox_metrics(left, altered, comparison_id="bad")
