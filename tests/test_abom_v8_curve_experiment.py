import pytest

from abom_v8.transport.experiments import compare_lemniscates, resolution_sweep


@pytest.mark.parametrize("mode,measure", [
    ("same_bounding_width", "bounding_width"),
    ("same_total_lobe_area", "total_lobe_area"),
    ("same_polyline_length", "polyline_length"),
])
def test_comparison_matches_one_declared_measure(mode, measure):
    report = compare_lemniscates(n_samples=401)
    values = [report["comparisons"][mode]["curves"][name][measure]
              for name in ("gerono", "bernoulli")]
    assert values[0] == pytest.approx(values[1], rel=1e-10, abs=1e-10)


def test_each_curve_has_two_balanced_lobes():
    report = compare_lemniscates(n_samples=801)
    for name in ("gerono", "bernoulli"):
        metrics = report["raw"][name]
        assert metrics["lobe_area_1"] > 0
        assert metrics["lobe_area_2"] > 0
        assert metrics["lobe_area_asymmetry"] < 1e-8


def test_resolution_sweep_records_requested_resolutions():
    report = resolution_sweep((101, 201, 401))
    assert report["resolutions"] == [101, 201, 401]
    assert len(report["runs"]) == 3


def test_resolution_sweep_rejects_single_resolution():
    with pytest.raises(ValueError):
        resolution_sweep((401,))
