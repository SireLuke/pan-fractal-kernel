"""NAHT parameter block carried by each occupant.

NAHT is the Non-Abelian History Transport subsystem (NAHT_QCD_JUNCTIONS.md):
a proposed three-channel retained-history state q = (r, e, p) with
r relational, e environmental, p phase/path.

Model routing does not define how routing history maps onto those channels, and
this package does not invent such a mapping.  The block exists so the three
channels and their required provenance metadata have a typed home; by default
every channel is unassigned.  Per the NAHT spec, once any channel is assigned
its units, normalization, provenance and calibration version must be stored.
"""
from __future__ import annotations

from dataclasses import dataclass
import math

_CHANNELS = ("r", "e", "p")
_METADATA = ("units", "normalization", "provenance", "calibration_version")


@dataclass(frozen=True, slots=True)
class NahtChannelParameters:
    r: float | None = None
    e: float | None = None
    p: float | None = None
    units: str | None = None
    normalization: str | None = None
    provenance: str | None = None
    calibration_version: str | None = None

    def __post_init__(self) -> None:
        for name in _CHANNELS:
            value = getattr(self, name)
            if value is None:
                continue
            if isinstance(value, bool) or not math.isfinite(float(value)):
                raise ValueError(f"NAHT channel {name} must be a finite number")
        if self.assigned:
            missing = [m for m in _METADATA
                       if not (getattr(self, m) or "").strip()]
            if missing:
                raise ValueError(
                    f"assigned NAHT channels require metadata: {', '.join(missing)}"
                )

    @property
    def assigned(self) -> bool:
        return any(getattr(self, name) is not None for name in _CHANNELS)
