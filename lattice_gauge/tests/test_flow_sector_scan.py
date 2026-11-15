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
