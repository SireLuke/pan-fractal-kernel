"""Fixed niche topology with swappable occupants.

The niche set is fixed at construction.  Seating, replacing or vacating an
occupant never adds or removes a niche, so the topology survives any change of
model.  Everything here depends only on capability vectors, never on a model's
name or vendor.
"""
from __future__ import annotations

from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field

from .capability import (
    CapabilityVector, l1_distance, validate_minimums, validate_weights,
)
from .ledger import PlacementLedger
from .params import NahtChannelParameters
from .placement import DEFAULT_CALIBRATION
from .provenance import EvidenceLevel, Provenance


@dataclass(frozen=True, slots=True)
class Niche:
    niche_id: str
    anchor: CapabilityVector
    weights: tuple[float, ...] = (1.0,) * 8
    minimums: Mapping[str, float] = field(default_factory=dict)
    min_evidence: EvidenceLevel | None = None

    def __post_init__(self) -> None:
        if not self.niche_id.strip():
            raise ValueError("niche_id must be non-empty")
        object.__setattr__(self, "weights", validate_weights(self.weights))
        object.__setattr__(self, "minimums", validate_minimums(self.minimums))
        if self.min_evidence is not None:
            object.__setattr__(self, "min_evidence", EvidenceLevel(self.min_evidence))

    def accepts(self, vector: CapabilityVector) -> bool:
        return all(vector[axis] >= floor for axis, floor in self.minimums.items())

    def admits(self, occupant: "Occupant") -> bool:
        """Capability floors plus, when required, verified provenance of enough rank."""
        if not self.accepts(occupant.vector):
            return False
        if self.min_evidence is None:
            return True
        return occupant.provenance_ok and occupant.provenance.level >= self.min_evidence

    def cost(self, vector: CapabilityVector) -> float:
        return l1_distance(vector, self.anchor, self.weights)


@dataclass(frozen=True, slots=True)
class Occupant:
    model_id: str
    transport_id: str
    vector: CapabilityVector
    calibration_version: str = DEFAULT_CALIBRATION
    evidence: tuple[str, ...] = ()
    context_tokens: int | None = None
    naht: NahtChannelParameters = NahtChannelParameters()
    provenance: Provenance | None = None

    def __post_init__(self) -> None:
        if not self.model_id.strip() or not self.transport_id.strip():
            raise ValueError("model_id and transport_id must be non-empty")
        if self.context_tokens is not None and (
                isinstance(self.context_tokens, bool) or self.context_tokens <= 0):
            raise ValueError("context_tokens must be a positive integer")

    @property
    def provenance_ok(self) -> bool:
        """True when provenance is present and still matches this id and vector."""
        return (self.provenance is not None
                and self.provenance.verify(self.model_id, self.vector))


@dataclass(frozen=True, slots=True)
class PlacementDecision:
    niche_id: str | None
    seated: bool
    displaced: Occupant | None
    cost: float | None
    reason: str


class NicheMap:
    def __init__(self, niches: Iterable[Niche], ledger: PlacementLedger | None = None) -> None:
        self.ledger = ledger
        self._niches = tuple(niches)
        if not self._niches:
            raise ValueError("a niche map needs at least one niche")
        ids = [n.niche_id for n in self._niches]
        if len(ids) != len(set(ids)):
            raise ValueError("niche ids must be unique")
        self._occupants: dict[str, Occupant] = {}

    @property
    def niches(self) -> tuple[Niche, ...]:
        return self._niches

    @property
    def niche_ids(self) -> tuple[str, ...]:
        return tuple(n.niche_id for n in self._niches)

    def niche(self, niche_id: str) -> Niche:
        for item in self._niches:
            if item.niche_id == niche_id:
                return item
        raise KeyError(f"unknown niche: {niche_id}")

    def occupant(self, niche_id: str) -> Occupant | None:
        self.niche(niche_id)
        return self._occupants.get(niche_id)

    def occupants(self) -> tuple[tuple[str, Occupant], ...]:
        return tuple((n.niche_id, self._occupants[n.niche_id])
                     for n in self._niches if n.niche_id in self._occupants)

    def niche_of(self, model_id: str) -> str | None:
        for niche_id, occupant in self._occupants.items():
            if occupant.model_id == model_id:
                return niche_id
        return None

    def seat(self, niche_id: str, occupant: Occupant) -> Occupant | None:
        """Put `occupant` in `niche_id`; return whoever it displaced."""
        niche = self.niche(niche_id)
        if not niche.admits(occupant):
            raise ValueError(
                f"{occupant.model_id!r} does not meet the minimums or evidence level of {niche_id!r}"
            )
        elsewhere = self.niche_of(occupant.model_id)
        if elsewhere is not None and elsewhere != niche_id:
            raise ValueError(f"{occupant.model_id!r} already occupies {elsewhere!r}")
        displaced = self._occupants.get(niche_id)
        self._occupants[niche_id] = occupant
        if self.ledger is not None:
            digest = occupant.provenance.digest if occupant.provenance else None
            self.ledger.append("seat", niche_id, occupant.model_id, digest)
        return displaced

    def vacate(self, niche_id: str) -> Occupant | None:
        self.niche(niche_id)
        removed = self._occupants.pop(niche_id, None)
        if removed is not None and self.ledger is not None:
            digest = removed.provenance.digest if removed.provenance else None
            self.ledger.append("vacate", niche_id, removed.model_id, digest)
        return removed

    def place(self, occupant: Occupant) -> PlacementDecision:
        """Seat `occupant` in its nearest accepting niche.

        An incumbent is displaced only by a strictly closer occupant (ties keep
        the incumbent), and re-placing the same model id refreshes it in place.
        """
        candidates = [(n.cost(occupant.vector), n.niche_id)
                      for n in self._niches if n.admits(occupant)]
        if not candidates:
            return PlacementDecision(None, False, None, None, "no niche accepts this occupant")
        cost, niche_id = min(candidates)
        incumbent = self._occupants.get(niche_id)
        existing = self.niche_of(occupant.model_id)
        if incumbent is not None and incumbent.model_id != occupant.model_id:
            if cost >= self.niche(niche_id).cost(incumbent.vector):
                return PlacementDecision(niche_id, False, None, cost,
                                         "incumbent is at least as close to the anchor")
        if existing is not None and existing != niche_id:
            self.vacate(existing)
        displaced = self.seat(niche_id, occupant)
        if displaced is not None and displaced.model_id == occupant.model_id:
            displaced = None
        return PlacementDecision(niche_id, True, displaced, cost, "seated")
