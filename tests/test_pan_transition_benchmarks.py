import pytest

from pan_transition_benchmarks import (
    altermagnetic_path_order_benchmark,
    quasi_star_lifecycle_benchmark,
)


def test_quasi_star_lifecycle_exercises_transition_operators_and_no_reset():
    result = quasi_star_lifecycle_benchmark()
    summary = result["summary"]
    assert result["metadata"]["geometry_boundary"] == "gosset_4_21_e8_root_polytope"
    assert result["potential_candidate_count"] == 2
    assert summary["janus_channels_distinct"]
    assert summary["hydra_branch_count"] == 3
    assert summary["all_identity_updates_nonzero"]
    assert summary["no_reset_invariant_holds"]
    assert all(summary["append_only_no_reset_checks"])
    assert summary["raw_history_retained"]
    assert result["history_revision"] == 8


def test_altermagnetic_reversed_paths_have_same_endpoint_and_distinct_history():
    result = altermagnetic_path_order_benchmark()
    assert result["summary"]["identical_endpoints"]
    assert result["summary"]["equal_path_lengths"]
    assert result["oriented_history_area"]["A"] == pytest.approx(0.0)
    assert result["oriented_history_area"]["B"] == pytest.approx(0.225)
    assert result["normalized_history_coordinate"] == {"A": 0.0, "B": 0.5}
    assert result["summary"]["history_proxy_spectral_max_difference"] > 0


def test_endpoint_only_null_model_has_no_path_order_splitting():
    result = altermagnetic_path_order_benchmark(history_coupling=0.0)
    assert result["summary"]["history_proxy_spectral_max_difference"] == pytest.approx(0.0)
    assert result["spectra"]["A"] == result["spectra"]["B"]


def test_altermagnetic_path_validation():
    with pytest.raises(ValueError):
        altermagnetic_path_order_benchmark(delta=0.0)
    with pytest.raises(ValueError):
        altermagnetic_path_order_benchmark(k_points=((float("nan"), 0.2),))
