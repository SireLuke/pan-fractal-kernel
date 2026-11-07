import json

import pytest

from spectral_feature_bridge import (
    FeatureSpec,
    V8_COORDINATES,
    extract_spectral_features,
)
from spectral_provenance import SpectralObservation
from spectral_sensitivity import run_spectral_sensitivity


def make_vector():
    observation = SpectralObservation.create(
        observation_id="sensitivity-001",
        modality="UV-Vis",
        raw_measurements={"peak": 2.0, "width": 4.0},
        units={"peak": "AU", "width": "nm"},
        uncertainty={"peak_sigma": 0.1, "width_sigma": 0.2},
    )
    return extract_spectral_features(
        observation,
        [
            FeatureSpec("peak", "raw", "peak", "AU", uncertainty_key="peak_sigma"),
            FeatureSpec("width", "raw", "width", "nm", uncertainty_key="width_sigma"),
        ],
    )


def make_mapping():
    mapping = {coordinate: {"peak": 0.0, "width": 0.0} for coordinate in V8_COORDINATES}
    mapping["h"] = {"peak": 2.0, "width": 1.0}
    mapping["R"] = {"peak": -1.0, "width": 0.5}
    return mapping


def test_one_factor_sweep_reports_expected_linear_derivatives():
    report = run_spectral_sensitivity(
        make_vector(),
        mapping=make_mapping(),
        monte_carlo_samples=0,
    )
    assert [item.feature for item in report.one_factor_results] == ["peak", "width"]
    peak = json.loads(report.one_factor_results[0].coordinate_derivatives_json)
    width = json.loads(report.one_factor_results[1].coordinate_derivatives_json)
    assert peak["h"] == pytest.approx(2.0)
    assert peak["R"] == pytest.approx(-1.0)
    assert width["h"] == pytest.approx(1.0)
    assert width["R"] == pytest.approx(0.5)


def test_seeded_monte_carlo_is_reproducible_and_reports_quantiles():
    kwargs = dict(
        mapping=make_mapping(),
        feature_covariance={
            "peak": {"peak": 0.01, "width": 0.005},
            "width": {"peak": 0.005, "width": 0.04},
        },
        monte_carlo_samples=500,
        seed=8128,
    )
    first = run_spectral_sensitivity(make_vector(), **kwargs)
    second = run_spectral_sensitivity(make_vector(), **kwargs)
    assert first.monte_carlo == second.monte_carlo
    summary = first.monte_carlo
    assert summary.samples == 500
    assert summary.seed == 8128
    means = json.loads(summary.coordinate_mean_json)
    stddevs = json.loads(summary.coordinate_stddev_json)
    quantiles = json.loads(summary.coordinate_quantiles_json)
    assert means["h"] == pytest.approx(8.0, abs=0.03)
    assert stddevs["h"] > 0
    assert quantiles["h"]["0.025"] < quantiles["h"]["0.5"] < quantiles["h"]["0.975"]


def test_monte_carlo_requires_explicit_independence_or_covariance():
    with pytest.raises(ValueError, match="explicit independent-feature"):
        run_spectral_sensitivity(
            make_vector(),
            mapping=make_mapping(),
            monte_carlo_samples=10,
        )


def test_independent_feature_assumption_is_recorded():
    report = run_spectral_sensitivity(
        make_vector(),
        mapping=make_mapping(),
        assume_independent_features=True,
        monte_carlo_samples=50,
        seed=7,
    )
    assumptions = json.loads(report.assumptions_json)
    assert assumptions["monte_carlo"] == "independent_features_assumed"


def test_oat_can_run_with_explicit_scales_without_measurement_uncertainties():
    vector = make_vector()
    report = run_spectral_sensitivity(
        vector,
        mapping=make_mapping(),
        perturbation_scales={"peak": 0.25},
        monte_carlo_samples=0,
    )
    assert len(report.one_factor_results) == 1
    assert report.one_factor_results[0].perturbation_scale == pytest.approx(0.25)


def test_path_order_check_and_provenance_are_retained():
    report = run_spectral_sensitivity(
        make_vector(),
        mapping=make_mapping(),
        monte_carlo_samples=0,
    )
    assert report.observation_id == "sensitivity-001"
    assert len(report.observation_digest) == 64
    assert len(report.feature_vector_digest) == 64
    assert len(report.mapping_digest) == 64
    assert report.forward_reverse_max_abs_delta == 0.0
    assert json.loads(report.baseline_state_json)["h"] == pytest.approx(8.0)


@pytest.mark.parametrize(
    "kwargs",
    [
        {"monte_carlo_samples": -1},
        {"monte_carlo_samples": 2.5},
        {"seed": 1.5},
        {"perturbation_scales": {"missing": 1.0}},
        {"perturbation_scales": {"peak": 0.0}},
    ],
)
def test_invalid_sensitivity_parameters_are_rejected(kwargs):
    base = {"mapping": make_mapping(), "monte_carlo_samples": 0}
    base.update(kwargs)
    with pytest.raises((TypeError, ValueError)):
        run_spectral_sensitivity(make_vector(), **base)
