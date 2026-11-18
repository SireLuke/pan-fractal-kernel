"""Placement provenance: how a model's coordinates were obtained, and proof they
have not been altered since.

This is a small ordered ladder of auditable categories, not a trust score.  It
is separate from STRATA claim levels, which grade claims about the framework.

What it does and does not establish:
- The digest is tamper-evident: change the model id, the coordinates or any
  recorded field and `verify` fails.
- It does not establish that the benchmarks were run honestly, and attester
  names are caller-asserted strings (no signatures or identity checks here).
"""
from __future__ import annotations

from dataclasses import dataclass
from enum import IntEnum
import hashlib
import hmac
import json
import re

from .capability import CapabilityVector

PROVENANCE_SCHEMA = "urn:pan:abom-v8:placement-provenance:0.1"
_HEX64 = re.compile(r"^[0-9a-f]{64}$")


class EvidenceLevel(IntEnum):
    DECLARED = 0                   # asserted by the caller, nothing recorded
    BENCHMARKED = 1                # computed from named source results via a versioned calibration
    REPRODUCED = 2                 # re-run and attested by at least one party
    INDEPENDENTLY_REPRODUCED = 3   # re-run and attested by at least two distinct parties


_MIN_ATTESTERS = {
    EvidenceLevel.DECLARED: 0,
    EvidenceLevel.BENCHMARKED: 0,
    EvidenceLevel.REPRODUCED: 1,
    EvidenceLevel.INDEPENDENTLY_REPRODUCED: 2,
}


def canonical_json(payload: object) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(model_id: str, vector: CapabilityVector, level: EvidenceLevel,
            calibration_version: str, sources: tuple[str, ...],
            attested_by: tuple[str, ...]) -> str:
    payload = {
        "schema": PROVENANCE_SCHEMA,
        "model_id": model_id,
        "vector": list(vector.values),
        "level": int(level),
        "calibration_version": calibration_version,
        "sources": list(sources),
        "attested_by": list(attested_by),
    }
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class Provenance:
    level: EvidenceLevel
    calibration_version: str
    sources: tuple[str, ...]
    attested_by: tuple[str, ...]
    digest: str

    def __post_init__(self) -> None:
        level = EvidenceLevel(self.level)
        object.__setattr__(self, "level", level)
        object.__setattr__(self, "sources", tuple(self.sources))
        object.__setattr__(self, "attested_by", tuple(self.attested_by))
        if not self.calibration_version.strip():
            raise ValueError("calibration_version must be non-empty")
        if any(not s.strip() for s in self.sources + self.attested_by):
            raise ValueError("sources and attesters must be non-empty strings")
        if level >= EvidenceLevel.BENCHMARKED and not self.sources:
            raise ValueError(f"{level.name} provenance requires at least one source")
        if len(set(self.attested_by)) != len(self.attested_by):
            raise ValueError("attesters must be distinct")
        if len(self.attested_by) < _MIN_ATTESTERS[level]:
            raise ValueError(
                f"{level.name} provenance requires at least {_MIN_ATTESTERS[level]} attester(s)"
            )
        if not _HEX64.match(self.digest):
            raise ValueError("digest must be 64 lowercase hex characters")

    @classmethod
    def create(cls, model_id: str, vector: CapabilityVector, level: EvidenceLevel,
               calibration_version: str, sources: tuple[str, ...] = (),
               attested_by: tuple[str, ...] = ()) -> "Provenance":
        level = EvidenceLevel(level)
        sources, attested_by = tuple(sources), tuple(attested_by)
        return cls(level, calibration_version, sources, attested_by,
                   _digest(model_id, vector, level, calibration_version, sources, attested_by))

    def verify(self, model_id: str, vector: CapabilityVector) -> bool:
        expected = _digest(model_id, vector, self.level, self.calibration_version,
                           self.sources, self.attested_by)
        return hmac.compare_digest(self.digest, expected)
