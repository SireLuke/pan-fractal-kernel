import numpy as np
import pytest

from abom_v8.transport.curves import (
    curve_metrics, rescale_to_bounding_width, sample_bernoulli, sample_gerono,
)


@pytest.mark.parametrize("sampler,kwargs", [
    (sample_gerono, {"a": 2.0, "b": 0.8}),
    (sample_bernoulli, {"c": 1.5}),
])
def test_candidates_are_closed_and_cross_origin_twice(sampler, kwargs):
    curve = sampler(**kwargs, n_samples=401)
    assert np.allclose(curve.points[0], curve.points[-1], atol=1e-12)
    assert curve_metrics(curve)["sampled_origin_crossings"] == 2


def test_gerono_independent_lobe_scales():
    curve = sample_gerono(a=2.5, b=0.75)
    metrics = curve_metrics(curve)
    assert metrics["bounding_width"] == pytest.approx(5.0)
    assert metrics["bounding_height"] == pytest.approx(1.5)


def test_width_normalization_allows_fair_comparison():
    curve = rescale_to_bounding_width(sample_bernoulli(c=1.0), 4.0)
    assert curve_metrics(curve)["bounding_width"] == pytest.approx(4.0)


@pytest.mark.parametrize("kwargs", [
    {"a": 0.0}, {"b": -1.0}, {"n_samples": 400}, {"n_samples": 3},
])
def test_gerono_rejects_invalid_configuration(kwargs):
    with pytest.raises(ValueError):
        sample_gerono(**kwargs)


def test_bernoulli_rejects_invalid_configuration():
    with pytest.raises(ValueError):
        sample_bernoulli(c=float("nan"))
