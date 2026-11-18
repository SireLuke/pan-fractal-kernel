"""Capability-based routing over a NicheMap.

The choice depends only on capability vectors, declared minimums and context
size.  Model names, vendors and transports never enter the cost.
"""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from .capability import (
    CapabilityVector, fit_cost, validate_minimums, validate_weights,
)
from .registry import NicheMap, Occupant
from .transport import Transport


class NoEligibleOccupant(LookupError):
    """No seated occupant satisfies the task's hard requirements."""


@dataclass(frozen=True, slots=True)
class TaskProfile:
    requirements: CapabilityVector
    weights: tuple[float, ...] = (1.0,) * 8
    minimums: Mapping[str, float] = field(default_factory=dict)
    min_context_tokens: int | None = None
    excess_penalty: float = 0.25

    def __post_init__(self) -> None:
        object.__setattr__(self, "weights", validate_weights(self.weights))
        object.__setattr__(self, "minimums", validate_minimums(self.minimums))
        if self.min_context_tokens is not None and (
                isinstance(self.min_context_tokens, bool) or self.min_context_tokens <= 0):
            raise ValueError("min_context_tokens must be a positive integer")

    def eligible(self, occupant: Occupant) -> bool:
        if any(occupant.vector[axis] < floor for axis, floor in self.minimums.items()):
            return False
        if self.min_context_tokens is not None:
            return (occupant.context_tokens is not None
                    and occupant.context_tokens >= self.min_context_tokens)
        return True


@dataclass(frozen=True, slots=True)
class RouteDecision:
    niche_id: str
    occupant: Occupant
    cost: float
    ranking: tuple[tuple[str, str, float], ...]  # (niche_id, model_id, cost), best first


@dataclass(frozen=True, slots=True)
class DispatchResult:
    decision: RouteDecision
    text: str


def route(task: TaskProfile, niche_map: NicheMap) -> RouteDecision:
    scored = []
    for niche_id, occupant in niche_map.occupants():
        if task.eligible(occupant):
            cost = fit_cost(task.requirements, occupant.vector, task.weights,
                            task.excess_penalty)
            scored.append((cost, niche_id, occupant))
    if not scored:
        raise NoEligibleOccupant("no seated occupant meets the task requirements")
    scored.sort(key=lambda item: (item[0], item[1]))  # deterministic tie-break
    cost, niche_id, occupant = scored[0]
    ranking = tuple((nid, occ.model_id, c) for c, nid, occ in scored)
    return RouteDecision(niche_id, occupant, cost, ranking)


def dispatch(prompt: str, task: TaskProfile, niche_map: NicheMap,
             transports: Mapping[str, Transport], *, timeout: float = 60.0) -> DispatchResult:
    decision = route(task, niche_map)
    try:
        transport = transports[decision.occupant.transport_id]
    except KeyError as exc:
        raise KeyError(f"no transport registered for {decision.occupant.transport_id!r}") from exc
    text = transport.generate(decision.occupant.model_id, prompt, timeout=timeout)
    return DispatchResult(decision, text)
