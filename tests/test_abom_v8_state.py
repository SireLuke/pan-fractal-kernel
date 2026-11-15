import pytest

from abom_v8.state import COORDINATE_ORDER, V8State


def test_order_and_round_trip():
    state = V8State.from_sequence([0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8])
    assert COORDINATE_ORDER == ("h", "R", "u", "d", "tau", "chi", "s", "f")
    assert tuple(state.as_mapping()) == COORDINATE_ORDER
    assert V8State.from_mapping(state.as_mapping()) == state
    assert state.as_schema()["coordinates"] == list(state.coordinates)


def test_temporal_alias_t_maps_to_tau():
    mapping = dict(zip(COORDINATE_ORDER, [0.1] * 8))
    mapping["T"] = mapping.pop("tau")
    assert V8State.from_mapping(mapping).coordinates[4] == pytest.approx(0.1)


def test_rejects_both_alias_and_canonical_tau():
    values = {key: 0.5 for key in COORDINATE_ORDER}
    values["T"] = 0.5
    with pytest.raises(ValueError, match="tau or"):
        V8State.from_mapping(values)


@pytest.mark.parametrize("bad", [
    [0.0] * 7, [0.0] * 9, [-0.01] + [0.5] * 7,
    [1.01] + [0.5] * 7, [float("nan")] + [0.5] * 7,
    [float("inf")] + [0.5] * 7, [True] + [0.5] * 7,
])
def test_rejects_invalid_states(bad):
    with pytest.raises(ValueError):
        V8State.from_sequence(bad)
