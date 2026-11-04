import pytest

from spectral_provenance import SpectralObservation, append_spectral_janus
from transition_algebra import History, Transition, ubp_log


def sample_observation(**overrides):
    values = {
        "observation_id": "spec-001",
        "modality": "UV-Vis",
        "raw_measurements": {"wavelength": [400.0, 500.0], "intensity": [0.8, 0.6]},
        "units": {"wavelength": "nm", "intensity": "fraction"},
        "derived_values": {"absorbance": [0.09691, 0.22185]},
        "uncertainty": {"intensity_std": 0.002},
        "instrument": {"manufacturer": "Example", "model": "UV-1"},
        "calibration": {"reference": "blank-2026-11"},
        "provenance": {"source": "synthetic test fixture", "operator": "test"},
        "acquired_at": "2026-11-04T00:00:00Z",
    }
    values.update(overrides)
    return SpectralObservation.create(**values)


def test_observation_preserves_raw_measurements_and_metadata():
    raw = {"frequency": [4.0e14, 5.0e14]}
    observation = sample_observation(raw_measurements=raw, units={"frequency": "Hz"})
    raw["frequency"][0] = 0.0
    assert observation.raw_measurements["frequency"][0] == 4.0e14
    assert observation.units == {"frequency": "Hz"}
    assert observation.instrument["model"] == "UV-1"
    assert observation.calibration["reference"] == "blank-2026-11"
    assert observation.provenance["source"] == "synthetic test fixture"


def test_observation_digest_is_stable_and_changes_when_evidence_changes():
    first = sample_observation()
    same = sample_observation(raw_measurements={"intensity": [0.8, 0.6], "wavelength": [400.0, 500.0]})
    changed = sample_observation(raw_measurements={"wavelength": [400.0, 500.0], "intensity": [0.8, 0.61]})
    assert first.digest == same.digest
    assert first.digest != changed.digest
    assert len(first.digest) == 64


def test_janus_pair_carries_identical_observation_evidence():
    observation = sample_observation()
    pair = observation.to_janus_pair("evt-1")
    assert pair.formation.event_id == "evt-1:uhfe"
    assert pair.dissolution.event_id == "evt-1:udfe"
    assert pair.formation.payload["observation_json"] == pair.dissolution.payload["observation_json"]
    assert pair.formation.payload["observation_digest"] == observation.digest
    assert pair.dissolution.payload["observation_digest"] == observation.digest
    assert pair.formation.payload["janus_channel"] == "UHFE_formation"
    assert pair.dissolution.payload["janus_channel"] == "UDFE_dissolution"


def test_append_spectral_janus_is_append_only_and_changes_history_fingerprint():
    initial = History((Transition("prior", "existing", {"keep": True}),))
    updated = append_spectral_janus(initial, sample_observation(), "evt-2")
    assert updated.events[:1] == initial.events
    assert [event.event_id for event in updated.events] == [
        "prior", "evt-2:uhfe", "evt-2:udfe"
    ]
    assert ubp_log(updated).digest != ubp_log(initial).digest


def test_duplicate_janus_event_ids_fail_without_mutating_original_history():
    initial = append_spectral_janus(History(), sample_observation(), "evt-3")
    with pytest.raises(ValueError, match="duplicate event_id"):
        append_spectral_janus(initial, sample_observation(observation_id="spec-002"), "evt-3")
    assert len(initial.events) == 2


@pytest.mark.parametrize(
    "kwargs",
    [
        {"observation_id": ""},
        {"modality": " "},
        {"raw_measurements": {}},
        {"units": {}},
        {"units": {"unknown": "nm"}},
        {"raw_measurements": {"signal": float("nan")}},
        {"raw_measurements": {"signal": object()}},
        {"uncertainty": {"sigma": float("inf")}},
    ],
)
def test_invalid_observation_records_are_rejected(kwargs):
    with pytest.raises((TypeError, ValueError)):
        sample_observation(**kwargs)


def test_event_prefix_must_be_nonempty():
    with pytest.raises(ValueError):
        sample_observation().to_janus_pair(" ")
