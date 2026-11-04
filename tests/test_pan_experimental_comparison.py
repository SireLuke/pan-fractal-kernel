import json

import pytest

from pan_experimental_comparison import (
    compare_janus_states,
    compare_paths,
    compare_spectral_features,
    compare_v8_states,
)
from spectral_feature_bridge import FeatureSpec, extract_spectral_features
from spectral_provenance import SpectralObservation
from transition_algebra import V8State


def state(offset=0.0):
    values = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8]
    values = [value + offset for value in values]
    return V8State(*values)


def observation(observation_id, peak, sigma):
    raw = {"peak": peak, "width": 2.0}
    record = SpectralObservation.create(
        observation_id=observation_id,
        modality="UV-Vis",
        raw_measurements=raw,
        units={"peak": "AU", "width": "nm"},
        uncertainty={"peak_sigma": sigma, "width_sigma": 0.2},
        provenance={"fixture": "comparison tests"},
    )
    return extract_spectral_features(
        record,
        [
            FeatureSpec("peak", "raw", "peak", "AU", uncertainty_key="peak_sigma"),
            FeatureSpec("width", "raw", "width", "nm", uncertainty_key="width_sigma"),
        ],
    )


def test_v8_comparison_reports_signed_deltas_and_standard_metrics():
    left, right = state(), state(0.1)
    report = compare_v8_states(left, right, comparison_id="state-1")
    metrics = json.loads(report.metrics_json)
    assert metrics["coordinate_delta"]["h"] == pytest.approx(0.1)
    assert metrics["l1_distance"] == pytest.approx(0.8)
    assert metrics["l2_distance"] == pytest.approx((8 * 0.1**2) ** 0.5)
    assert metrics["linf_distance"] == pytest.approx(0.1)
    assert len(report.digest) == 64
    assert left == state()  # comparison did not mutate its inputs


def test_v8_comparison_supports_explicit_nonnegative_weights():
    report = compare_v8_states(
        state(), state(0.1), comparison_id="weighted",
        weights={"h": 4.0, "R": 0.0},
    )
    metrics = json.loads(report.metrics_json)
    assert metrics["weighted_l2_distance"] == pytest.approx((0.04 + 6 * 0.01) ** 0.5)
    with pytest.raises(ValueError, match="non-negative"):
        compare_v8_states(state(), state(0.1), comparison_id="bad", weights={"h": -1})


def test_spectral_comparison_checks_units_and_preserves_uncertainty_policy():
    left, right = observation("obs-a", 2.0, 0.1), observation("obs-b", 2.3, 0.2)
    report = compare_spectral_features(left, right, comparison_id="spectra")
    deltas = json.loads(report.feature_deltas_json)
    uncertainty = json.loads(report.uncertainty_comparison_json)
    assert deltas["peak"]["delta_right_minus_left"] == pytest.approx(0.3)
    assert uncertainty["peak"]["combined_standard_uncertainty"] is None
    independent = compare_spectral_features(
        left, right, comparison_id="spectra-independent",
        assume_independent_observations=True,
    )
    result = json.loads(independent.uncertainty_comparison_json)["peak"]
    assert result["combined_standard_uncertainty"] == pytest.approx(0.05**0.5)
    assert result["standardized_delta"] == pytest.approx(0.3 / (0.05**0.5))


def test_spectral_comparison_rejects_feature_set_and_unit_mismatch():
    left = observation("obs-a", 2.0, 0.1)
    other_record = SpectralObservation.create(
        observation_id="obs-c", modality="UV-Vis",
        raw_measurements={"peak": 2.0, "width": 2.0},
        units={"peak": "mAU", "width": "nm"},
        uncertainty={"peak_sigma": 0.1, "width_sigma": 0.2},
    )
    other = extract_spectral_features(
        other_record,
        [
            FeatureSpec("peak", "raw", "peak", "mAU", uncertainty_key="peak_sigma"),
            FeatureSpec("width", "raw", "width", "nm", uncertainty_key="width_sigma"),
        ],
    )
    with pytest.raises(ValueError, match="incompatible units"):
        compare_spectral_features(left, other, comparison_id="bad-units")


def test_janus_comparison_keeps_formation_and_dissolution_metrics_separate():
    report = compare_janus_states(state(), state(0.05), comparison_id="janus")
    uhfe = json.loads(report.uhfe_metrics_json)
    udfe = json.loads(report.udfe_metrics_json)
    gaps = json.loads(report.paired_head_gap_json)
    assert set(gaps) == {"bubble", "honeycomb", "spiderweb", "chiraldna", "compoundeye"}
    assert uhfe["l2_distance"] >= 0
    assert udfe["l2_distance"] >= 0
    assert all("gap_change_right_minus_left" in item for item in gaps.values())
    assert len(report.digest) == 64


def test_path_comparison_requires_alignment_and_reports_endpoint_separately():
    left = [state(), state(0.02), state(0.04)]
    right = [state(), state(0.03), state(0.04)]
    report = compare_paths(left, right, comparison_id="paths")
    steps = json.loads(report.step_metrics_json)
    endpoint = json.loads(report.endpoint_metrics_json)
    assert len(steps) == 3
    assert report.max_step_l2_distance > 0
    assert report.cumulative_step_l2_distance >= report.max_step_l2_distance
    assert endpoint["l2_distance"] == pytest.approx(0.0)
    with pytest.raises(ValueError, match="equal lengths"):
        compare_paths(left, right[:2], comparison_id="misaligned")


@pytest.mark.parametrize(
    "left,right",
    [
        ({}, state()),
        ({"h": 0.0}, state()),
        ([0.0] * 7, state()),
        ([0.0] * 9, state()),
        ([-0.1] + [0.5] * 7, state()),
        ([float("nan")] + [0.5] * 7, state()),
    ],
)
def test_invalid_v8_comparison_inputs_are_rejected(left, right):
    with pytest.raises((TypeError, ValueError)):
        compare_v8_states(left, right, comparison_id="invalid")


def test_empty_paths_and_empty_comparison_id_are_rejected():
    with pytest.raises(ValueError):
        compare_paths([], [state()], comparison_id="empty")
    with pytest.raises(ValueError):
        compare_v8_states(state(), state(), comparison_id=" ")
