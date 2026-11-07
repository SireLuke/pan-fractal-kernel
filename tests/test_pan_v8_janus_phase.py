import math

import pytest

from pan_v8_janus_phase import JanusPhaseCoupler


BASE = {
    "h": 0.8, "R": 0.7, "u": 0.75, "d": 0.25,
    "tau": 0.65, "chi": 0.6, "s": 0.72, "f": 0.55,
}


def coupler(**kwargs):
    defaults = dict(
        timestamp=0.0,
        phases=(0.0,) * 8,
        angular_frequencies=(math.pi / 2,) * 8,
        offsets=(0.0,) * 8,
        temperature=0.5,
        chemical_potential=0.0,
    )
    defaults.update(kwargs)
    return JanusPhaseCoupler(**defaults)


def test_alternates_formation_and_dissolution_pulses():
    model = coupler()
    first = model.step(1.0, BASE)
    second = model.step(2.0, BASE)
    third = model.step(3.0, BASE)

    assert (first.active_layer, second.active_layer, third.active_layer) == (
        "UHFE", "UDFE", "UHFE"
    )
    assert (first.polarity, second.polarity, third.polarity) == (1, -1, 1)
    assert (first.pulse_index, second.pulse_index, third.pulse_index) == (0, 1, 2)


def test_phase_alignment_modulates_active_channel_values():
    aligned = coupler(angular_frequencies=(0.0,) * 8)
    misaligned = coupler(angular_frequencies=(math.pi,) * 8)
    a = aligned.step(1.0, BASE, geometric_reference_phase=0.0)
    b = misaligned.step(1.0, BASE, geometric_reference_phase=0.0)
    assert a.pulse_channels == pytest.approx(a.uhfe_channels)
    assert b.pulse_channels == pytest.approx(tuple(-x for x in b.uhfe_channels))


def test_fermi_occupancy_and_holes_are_bounded_complements():
    frame = coupler().step(0.25, BASE)
    assert len(frame.fermi_occupancy) == len(frame.fermi_holes) == 8
    for occupied, hole in zip(frame.fermi_occupancy, frame.fermi_holes):
        assert 0.0 <= occupied <= 1.0
        assert 0.0 <= hole <= 1.0
        assert occupied + hole == pytest.approx(1.0)


def test_bad_semantic_input_does_not_consume_pulse_or_timestamp():
    model = coupler()
    with pytest.raises(ValueError):
        model.step(1.0, {**BASE, "h": 2.0})
    assert model.pulse_index == 0
    frame = model.step(0.5, BASE)
    assert frame.timestamp == 0.5
    assert frame.active_layer == "UHFE"


def test_timestamp_must_be_monotonic_and_reference_finite():
    model = coupler()
    # Invalid reference must fail before consuming time or a pulse.
    with pytest.raises(ValueError):
        model.step(1.0, BASE, geometric_reference_phase=math.nan)
    assert model.pulse_index == 0

    # A valid timestamp advances the model; a later backward timestamp fails.
    model.step(1.0, BASE)
    with pytest.raises(ValueError):
        model.step(0.5, BASE)
    assert model.pulse_index == 1


def test_invalid_temperature_rejected():
    with pytest.raises(ValueError):
        coupler(temperature=-0.1)
