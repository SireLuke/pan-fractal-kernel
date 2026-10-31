import pytest
from qcd_reference import alpha_s_one_loop, asymptotically_free, beta_alpha_s, lambda_from_reference
from qcd_ingest import QCDMeasurement, calibrated_v8_frame, compare_one_loop, load_alpha_s_csv


def test_one_loop_running_decreases_with_scale():
    lam = lambda_from_reference(91.1876, 0.118, nf=5)
    assert alpha_s_one_loop(10.0, lam, nf=5) > alpha_s_one_loop(1000.0, lam, nf=5) > 0
    assert alpha_s_one_loop(91.1876, lam, nf=5) == pytest.approx(0.118)


def test_beta_function_and_asymptotic_freedom():
    assert beta_alpha_s(0.1, nc=3, nf=5) < 0
    assert asymptotically_free(3, 6)
    assert not asymptotically_free(3, 17)


@pytest.mark.parametrize("mu,lam", [(0, 0.2), (1, 1), (1, 0), (float("nan"), 0.2)])
def test_invalid_scales_rejected(mu, lam):
    with pytest.raises(ValueError):
        alpha_s_one_loop(mu, lam)


def test_csv_preserves_provenance_and_extra_metadata(tmp_path):
    path = tmp_path / "alpha.csv"
    path.write_text(
        "mu_GeV,alpha_s,uncertainty,source,observable,scheme,nf,correlation_group\n"
        "100,0.116,0.002,CMS,dijet,MSbar,5,fit-A\n", encoding="utf-8")
    rows = load_alpha_s_csv(path)
    assert rows[0].source == "CMS"
    assert rows[0].metadata["correlation_group"] == "fit-A"


def test_csv_requires_metadata_columns(tmp_path):
    path = tmp_path / "bad.csv"
    path.write_text("mu_GeV,alpha_s\n100,0.1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Missing required"):
        load_alpha_s_csv(path)


def test_comparison_reports_residual_pull_and_source():
    item = QCDMeasurement(100, 0.115, 0.002, "test", "dijet", "MSbar", 5, {})
    lam = lambda_from_reference(91.1876, 0.118, nf=5)
    row = compare_one_loop([item], lambda_qcd_gev=lam)[0]
    assert row["pull"] == pytest.approx(row["residual"] / row["uncertainty"])
    assert row["source"] == "test"


def test_v8_handoff_requires_explicit_eight_coordinate_calibration():
    keys = ("h", "R", "u", "d", "tau", "chi", "s", "f")
    coords = dict(zip(keys, (0.6, 0.6, 0.5, 0.4, 0.7, 0.5, 0.8, 0.6)))
    frame, provenance = calibrated_v8_frame(
        coords, source_id="qcd-example-001", calibration_id="cal-v0")
    assert frame.state.h == pytest.approx(0.6)
    assert provenance["mapping_status"] == "explicit_calibration_supplied_by_caller"
    with pytest.raises(ValueError):
        calibrated_v8_frame({"alpha_s": 0.118}, source_id="x", calibration_id="y")
