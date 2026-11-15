import numpy as np
import pytest
from lattice_gauge.gradient_flow import wilson_flow
from lattice_gauge.lattice_gauge import Gauge
from run_wilson_flow_sector_scan import scan_one


def test_flow_history_has_raw_charge_and_action_for_every_step():
    g = Gauge(2, (4, 4, 4, 4), beta=2.0, seed=77, hot=True)
    rows = wilson_flow(g, steps=3, step_size=1e-5)
    assert len(rows) == 4
    assert [r["flow_time"] for r in rows] == pytest.approx([0.0, 1e-5, 2e-5, 3e-5])
    assert all(np.isfinite(r["topological_charge"]) for r in rows)
    assert all(np.isfinite(r["action"]) for r in rows)


def test_sector_scan_reports_unrounded_charge_and_declared_thresholds():
    row = scan_one(2, 2.0, seed=83, extent=4, steps=2, step_size=1e-6)
    assert isinstance(row["Q_final_raw"], float)
    assert "distance_to_nearest_integer" in row
    assert "late_flow_Q_span" in row
    assert isinstance(row["late_flow_plateau_candidate"], bool)
    assert len(row["trajectory"]) == 3


def test_scan_records_integrator_and_smoothing_radius():
    row = scan_one(2, 2.0, seed=83, extent=4, steps=5, step_size=0.02)
    assert row["integrator"] == "rk3"
    assert row["smoothing_radius"] == pytest.approx((8 * 0.1) ** 0.5)
    assert row["smoothing_radius_over_half_extent"] == pytest.approx(row["smoothing_radius"] / 2.0)


def test_thermalized_links_are_distinct_unitary_and_flow_tagged():
    from run_wilson_flow_sector_scan import thermalized_links
    out = list(thermalized_links(2, 2.4, seed=5, extent=4, therm=20, n_configs=2, sep=3))
    assert len(out) == 2
    (l0, p0), (l1, p1) = out
    assert not all(np.allclose(a, b) for a, b in zip(l0, l1))
    eye = np.eye(2, dtype=complex)
    for u in l0:
        assert np.max(np.abs(u @ np.swapaxes(u.conj(), -1, -2) - eye)) < 1e-10
    assert 0.0 < p0 < 1.0 and 0.0 < p1 < 1.0
    row = scan_one(2, 2.4, seed=5, extent=4, steps=3, step_size=0.02,
                   links=l0, start_plaquette=p0)
    assert row["start"] == "thermalized" and row["start_plaquette"] == p0
    assert all("t2E" in r for r in row["trajectory"])
    assert row["trajectory"][0]["t2E"] == 0.0
    # flowing the copy must not touch the yielded links
    assert all(np.array_equal(a, b) for a, b in zip(l0, out[0][0]))


def test_campaign_can_be_restricted_to_one_group():
    from run_wilson_flow_sector_scan import run_campaign
    rep = run_campaign(extent=4, steps=2, step_size=0.02, therm=10, sep=2, configs=1,
                       groups=(2,))
    assert rep["design"]["groups"] == ["SU(2)"]
    assert [r["group"] for r in rep["runs"]] == ["SU(2)"]
    with pytest.raises(ValueError, match="beta"):
        run_campaign(extent=4, steps=1, groups=(5,))
    with pytest.raises(ValueError, match="groups"):
        run_campaign(extent=4, steps=1, groups=(1,))


def test_campaign_accepts_general_n_with_explicit_beta():
    from run_wilson_flow_sector_scan import parse_beta_overrides, run_campaign
    assert parse_beta_overrides(["10=45", "2=2.5"]) == {10: 45.0, 2: 2.5}
    with pytest.raises(ValueError):
        parse_beta_overrides(["10"])
    rep = run_campaign(extent=4, steps=2, step_size=0.02, therm=10, sep=2, configs=1,
                       groups=(4,), betas={4: 12.0})
    assert rep["design"]["groups"] == ["SU(4)"]
    assert rep["design"]["betas"] == {"SU(4)": 12.0}
    assert rep["runs"][0]["N"] == 4
