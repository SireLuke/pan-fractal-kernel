import numpy as np
import pytest

from lattice_gauge.lattice_gauge import Gauge
from gosset_421 import E8_ROOTS, weyl_reflection
from yang_mills_v8_gosset import (
    compare_signatures,
    gosset_observable_field,
    gosset_star_report,
    measure,
    run_gauge_transform_control,
    v8_projection,
)


@pytest.mark.parametrize("n,beta", [(2, 1.7), (3, 5.5)])
def test_gauge_invariant_observables_survive_random_local_gauge_transform(n, beta):
    g = Gauge(n, (4, 4, 4, 4), beta, seed=123, hot=True)
    result = run_gauge_transform_control(g)
    assert result["pass"]
    assert result["max_abs_delta"] < 1e-10


@pytest.mark.parametrize("n,beta", [(2, 1.7), (3, 5.5)])
def test_v8_bridge_preserves_canonical_order_and_masks_unmeasured_channels(n, beta):
    g = Gauge(n, (4, 4), beta, seed=44, hot=True)
    frame = measure(g)
    projected = v8_projection(frame)
    assert projected["coordinate_order"] == ["h", "R", "u", "d", "tau", "chi", "s", "f"]
    assert set(projected["values"]) == set(projected["coordinate_order"])
    assert projected["measured_mask"]["chi"] is False
    assert projected["measured_mask"]["f"] is False
    assert projected["measured_mask"]["tau"] is False
    assert all(0.0 <= x <= 1.0 for x in projected["values"].values())
    assert len(projected["uhfe"]) == 5
    assert len(projected["udfe"]) == 5


def test_tau_is_only_marked_measured_when_a_second_snapshot_exists():
    g = Gauge(2, (4, 4), 1.5, seed=9, hot=True)
    first = measure(g, update_index=0)
    one = v8_projection(first)
    g.sweep(hits=1)
    second = measure(g, update_index=1)
    two = v8_projection(second, first)
    assert one["measured_mask"]["tau"] is False
    assert two["measured_mask"]["tau"] is True


def test_gosset_mapping_has_240_vertices_and_local_global_reconciliation():
    g = Gauge(2, (4, 4), 1.5, seed=8, hot=True)
    frame = measure(g)
    values = gosset_observable_field(frame)
    report = gosset_star_report(values)
    assert report["base_stars"] == 240
    assert report["vertices_per_star"] == 56
    assert report["edge_count"] == 6720
    assert report["star_mean_global_residual"] < 1e-12
    assert report["adjacent_star_delta_max"] >= report["adjacent_star_delta_mean"]


def test_gosset_star_diagnostics_are_weyl_relabeling_invariant():
    g = Gauge(2, (4, 4), 1.5, seed=8, hot=True)
    values = gosset_observable_field(measure(g))
    alpha = E8_ROOTS[0]
    permutation = {
        tuple(round(x, 10) for x in weyl_reflection(root, alpha)): i
        for i, root in enumerate(E8_ROOTS)
    }
    assert len(permutation) == 240
    relabeled = np.asarray([
        values[permutation[tuple(round(x, 10) for x in root)]]
        for root in E8_ROOTS
    ])
    a, b = gosset_star_report(values), gosset_star_report(relabeled)
    for key in ("global_mean", "star_mean", "star_mean_global_residual",
                "adjacent_star_delta_mean", "adjacent_star_delta_max"):
        assert a[key] == pytest.approx(b[key], abs=1e-12)


def test_invalid_gosset_field_rejected():
    with pytest.raises(ValueError):
        gosset_star_report(np.zeros(239))
