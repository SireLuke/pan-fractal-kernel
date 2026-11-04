"""Immutable spectroscopy provenance records and Janus history adapters.

Raw instrument observations are retained as canonical JSON strings. Derived
values, uncertainty, calibration, instrument metadata, and source provenance
are stored separately. Janus events reference the same observation; the
formation/dissolution labels describe paired processing channels, not a claim
that the measured signal itself is physically created or destroyed.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Mapping

from transition_algebra import History, JanusPair, Transition

SCHEMA = "pan-spectral-observation-v1"
RAW_SCHEMA = "pan-spectral-raw-v1"


def _canonical_json(name: str, value: Mapping[str, object], *, required: bool = False) -> str:
    if not isinstance(value, Mapping):
        raise TypeError(f"{name} must be a mapping")
    if required and not value:
        raise ValueError(f"{name} must not be empty")
    try:
        return json.dumps(dict(value), sort_keys=True, separators=(",", ":"), allow_nan=False)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name} must contain finite, JSON-serializable data") from exc


def _decode(value: str) -> dict[str, object]:
    # Always return a fresh object: callers cannot mutate the retained record.
    return json.loads(value)


@dataclass(frozen=True)
class SpectralObservation:
    """Frozen, content-addressable record of one spectral observation.

    raw_measurements and units preserve submitted values and unit labels.
    Derived values never replace raw measurements. Mapping inputs are copied
    into canonical JSON at construction time.
    """

    observation_id: str
    modality: str
    raw_measurements_json: str
    units_json: str
    derived_values_json: str
    uncertainty_json: str
    instrument_json: str
    calibration_json: str
    provenance_json: str
    acquired_at: str | None = None
    schema: str = SCHEMA

    @classmethod
    def create(
        cls,
        *,
        observation_id: str,
        modality: str,
        raw_measurements: Mapping[str, object],
        units: Mapping[str, object],
        derived_values: Mapping[str, object] | None = None,
        uncertainty: Mapping[str, object] | None = None,
        instrument: Mapping[str, object] | None = None,
        calibration: Mapping[str, object] | None = None,
        provenance: Mapping[str, object] | None = None,
        acquired_at: str | None = None,
    ) -> "SpectralObservation":
        if not isinstance(observation_id, str) or not observation_id.strip():
            raise ValueError("observation_id must be a non-empty string")
        if not isinstance(modality, str) or not modality.strip():
            raise ValueError("modality must be a non-empty string")
        if acquired_at is not None and (not isinstance(acquired_at, str) or not acquired_at.strip()):
            raise ValueError("acquired_at must be a non-empty timestamp string or None")
        raw_json = _canonical_json("raw_measurements", raw_measurements, required=True)
        units_json = _canonical_json("units", units, required=True)
        raw_keys = set(json.loads(raw_json))
        if not set(json.loads(units_json)).issubset(raw_keys):
            raise ValueError("units keys must refer to raw measurement keys")
        return cls(
            observation_id=observation_id.strip(),
            modality=modality.strip().lower(),
            raw_measurements_json=raw_json,
            units_json=units_json,
            derived_values_json=_canonical_json("derived_values", derived_values or {}),
            uncertainty_json=_canonical_json("uncertainty", uncertainty or {}),
            instrument_json=_canonical_json("instrument", instrument or {}),
            calibration_json=_canonical_json("calibration", calibration or {}),
            provenance_json=_canonical_json("provenance", provenance or {}),
            acquired_at=acquired_at,
        )

    @property
    def raw_measurements(self) -> dict[str, object]:
        return _decode(self.raw_measurements_json)

    @property
    def units(self) -> dict[str, object]:
        return _decode(self.units_json)

    @property
    def derived_values(self) -> dict[str, object]:
        return _decode(self.derived_values_json)

    @property
    def uncertainty(self) -> dict[str, object]:
        return _decode(self.uncertainty_json)

    @property
    def instrument(self) -> dict[str, object]:
        return _decode(self.instrument_json)

    @property
    def calibration(self) -> dict[str, object]:
        return _decode(self.calibration_json)

    @property
    def provenance(self) -> dict[str, object]:
        return _decode(self.provenance_json)

    def canonical_record(self) -> dict[str, object]:
        """Return a detached, JSON-ready copy of the complete record."""
        return {
            "schema": self.schema,
            "observation_id": self.observation_id,
            "modality": self.modality,
            "acquired_at": self.acquired_at,
            "raw_measurements": self.raw_measurements,
            "units": self.units,
            "derived_values": self.derived_values,
            "uncertainty": self.uncertainty,
            "instrument": self.instrument,
            "calibration": self.calibration,
            "provenance": self.provenance,
        }

    @property
    def digest(self) -> str:
        encoded = json.dumps(
            self.canonical_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        ).encode("utf-8")
        return sha256(encoded).hexdigest()

    def to_janus_pair(self, event_id_prefix: str) -> JanusPair[Transition]:
        """Create paired UHFE/UDFE events carrying identical evidence.

        The events differ only in their processing-channel label. They do not
        negate, modify, or synthesize the measured spectrum.
        """
        if not isinstance(event_id_prefix, str) or not event_id_prefix.strip():
            raise ValueError("event_id_prefix must be a non-empty string")
        # Canonical JSON string keeps nested evidence immutable in Transition payloads.
        observation_json = json.dumps(
            self.canonical_record(), sort_keys=True, separators=(",", ":"), allow_nan=False
        )
        base_payload = {
            "schema": RAW_SCHEMA,
            "observation_json": observation_json,
            "observation_digest": self.digest,
        }
        formation_payload = dict(base_payload, janus_channel="UHFE_formation")
        dissolution_payload = dict(base_payload, janus_channel="UDFE_dissolution")
        prefix = event_id_prefix.strip()
        return JanusPair(
            formation=Transition(prefix + ":uhfe", "spectral_observation", formation_payload),
            dissolution=Transition(prefix + ":udfe", "spectral_observation", dissolution_payload),
        )


def append_spectral_janus(
    history: History,
    observation: SpectralObservation,
    event_id_prefix: str,
) -> History:
    """Append both paired spectral events, preserving prior History entries."""
    pair = observation.to_janus_pair(event_id_prefix)
    updated = history.append(pair.formation)
    return updated.append(pair.dissolution)
