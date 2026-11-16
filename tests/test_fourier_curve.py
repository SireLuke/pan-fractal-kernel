import cmath
import math

import pytest

from fourier_curve import FourierCurve


def periodic_ellipse(count=256, phase_map=lambda t: t):
    return tuple(
        complex(2.0 * math.cos(2 * math.pi * phase_map(i / count)),
                math.sin(2 * math.pi * phase_map(i / count)))
        for i in range(count)
    )


def test_single_harmonic_reconstructs_ellipse_to_roundoff():
    points = periodic_ellipse()
    curve = FourierCurve.fit(points, harmonics=1)
    report = curve.error_report(points)
    assert report["max_error"] < 1e-12
    assert report["rms_error"] < 1e-12
    assert report["max_error_fraction_of_height"] < 1e-12


def test_more_harmonics_do_not_worsen_training_reconstruction():
    points = periodic_ellipse()
    low = FourierCurve.fit(points, harmonics=0)
    high = FourierCurve.fit(points, harmonics=1)
    assert high.error_report(points)["rms_error"] <= low.error_report(points)["rms_error"]


def test_same_locus_with_different_parameterization_changes_coefficients():
    count = 256
    uniform = periodic_ellipse(count)
    # Smooth monotone periodic warp: same ellipse locus, nonuniform traversal.
    warped = periodic_ellipse(
        count, phase_map=lambda t: (t + 0.12 * math.sin(2 * math.pi * t)) % 1.0
    )
    a = FourierCurve.fit(uniform, harmonics=8)
    b = FourierCurve.fit(warped, harmonics=8)
    assert max(abs(x - y) for x, y in zip(a.coefficients, b.coefficients)) > 1e-3


def test_evaluation_is_periodic():
    curve = FourierCurve.fit(periodic_ellipse(), harmonics=3)
    assert curve.evaluate(0.125) == pytest.approx(curve.evaluate(1.125))


@pytest.mark.parametrize("harmonics", [-1, True, 1.5])
def test_rejects_invalid_harmonic_count(harmonics):
    with pytest.raises(ValueError):
        FourierCurve.fit(periodic_ellipse(), harmonics)


def test_rejects_insufficient_samples_and_nonfinite_values():
    with pytest.raises(ValueError):
        FourierCurve.fit([0j, 1 + 0j, 0 + 1j], harmonics=2)
    with pytest.raises(ValueError):
        FourierCurve.fit([0j, complex(float("inf"), 0), 1j], harmonics=0)


def test_rejects_mismatched_error_samples():
    curve = FourierCurve.fit(periodic_ellipse(), harmonics=1)
    with pytest.raises(ValueError):
        curve.error_report([0j, 1 + 0j])
