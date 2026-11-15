from abom_v8.strata import lemniscate_strata_record


def test_lemniscate_record_preserves_not_tested_dimensions():
    record = lemniscate_strata_record()
    data = record.to_dict()
    statuses = {item["dimension"]: item["status"] for item in data["dimensions"]}
    assert data["protocol"] == "STRATA-0.1"
    assert statuses["two_independent_domains"] == "not_tested"
    assert statuses["held_out_predictive_evaluation"] == "not_tested"
    assert data["promotion_eligible"] is False


def test_resolution_scale_is_not_claimed_as_physical_scale():
    record = lemniscate_strata_record()
    scale = next(x for x in record.dimensions if x.dimension == "three_meaningful_scales")
    assert scale.status == "not_tested"
    assert "not three meaningful scales" in scale.detail
