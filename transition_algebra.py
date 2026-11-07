"""Typed, testable transition algebra for PAN V8.

This is a software/modeling layer, not a claim that these operators are physical laws.
Raw event history is retained; the UBP digest is a versioned, lossy index.
"""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
import json
from typing import Callable, Generic, Mapping, Sequence, TypeVar

T = TypeVar("T")
U = TypeVar("U")


@dataclass(frozen=True)
class V8State:
    """Canonical ordered PAN V8 coordinates."""
    h: float
    R: float
    u: float
    d: float
    tau: float
    chi: float
    s: float
    f: float

    def as_tuple(self) -> tuple[float, ...]:
        return (self.h, self.R, self.u, self.d, self.tau, self.chi, self.s, self.f)

    def as_mapping(self) -> dict[str, float]:
        return dict(zip(("h", "R", "u", "d", "tau", "chi", "s", "f"), self.as_tuple()))


@dataclass(frozen=True)
class Transition:
    event_id: str
    operator: str
    payload: Mapping[str, object]

    def __post_init__(self) -> None:
        if not self.event_id.strip():
            raise ValueError("event_id must be non-empty")
        if not self.operator.strip():
            raise ValueError("operator must be non-empty")


@dataclass(frozen=True)
class History:
    events: tuple[Transition, ...] = ()

    def append(self, event: Transition) -> "History":
        if any(item.event_id == event.event_id for item in self.events):
            raise ValueError(f"duplicate event_id: {event.event_id}")
        return History(self.events + (event,))

    @property
    def revision(self) -> int:
        return len(self.events)


@dataclass(frozen=True)
class UBPLog:
    """Versioned lossy fingerprint; never a replacement for History."""
    schema: str
    event_count: int
    digest: str


@dataclass(frozen=True)
class Identity:
    state: V8State
    history: History
    log: UBPLog


@dataclass(frozen=True)
class JanusPair(Generic[T]):
    formation: T
    dissolution: T


def potential(state: T, generator: Callable[[T], Sequence[U]]) -> tuple[U, ...]:
    """Omega_P: generate reachable candidates without mutating the input."""
    candidates = tuple(generator(state))
    if not candidates:
        raise ValueError("potential generator must return at least one candidate")
    return candidates


def emergence(candidates: Sequence[T], selector: Callable[[Sequence[T]], int]) -> T:
    """E: select one candidate by an explicit policy."""
    if not candidates:
        raise ValueError("emergence requires at least one candidate")
    index = selector(candidates)
    if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(candidates):
        raise ValueError("selector must return a valid candidate index")
    return candidates[index]


def structure(value: T, stabilizer: Callable[[T], T]) -> T:
    """Sigma: apply a caller-defined stabilization map."""
    return stabilizer(value)


def compression(value: T, encoder: Callable[[T], bytes]) -> bytes:
    """C: explicit, caller-defined compression/encoding boundary."""
    encoded = encoder(value)
    if not isinstance(encoded, bytes):
        raise TypeError("compression encoder must return bytes")
    return encoded


def janus(value: T, formation: Callable[[T], U], dissolution: Callable[[T], U]) -> JanusPair[U]:
    """J: evaluate paired UHFE/UDFE channels from the same input."""
    return JanusPair(formation(value), dissolution(value))


def hydra(value: T, branchers: Mapping[str, Callable[[T], U]]) -> dict[str, U]:
    """H: named, deterministic branch expansion."""
    if not branchers:
        raise ValueError("hydra requires at least one named branch")
    return {name: branch(value) for name, branch in branchers.items()}


def memory(history: History, event: Transition) -> History:
    """M: append-only event recording with unique event identifiers."""
    return history.append(event)


def ubp_log(history: History) -> UBPLog:
    """Phi: stable SHA-256 fingerprint over canonical event serialization.

    The digest is intentionally lossy. Keep History for audit/reconstruction.
    """
    records = [
        {"event_id": e.event_id, "operator": e.operator, "payload": dict(e.payload)}
        for e in history.events
    ]
    canonical = json.dumps(records, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return UBPLog("pan-ubp-json-sha256-v1", len(history.events),
                  sha256(canonical.encode("utf-8")).hexdigest())


def becoming(state: V8State, history: History) -> Identity:
    """B/Psi: assemble an identity from current state and retained history."""
    return Identity(state, history, ubp_log(history))


def identity_distance(a: Identity, b: Identity, *, state_weight: float = 1.0,
                      history_weight: float = 1.0) -> float:
    """Transparent Euclidean state + history-revision distance.

    This baseline metric is deliberately not advertised as a universal physical
    metric. Distinct histories with equal revisions are distinguished by digest.
    """
    import math
    if state_weight < 0 or history_weight < 0:
        raise ValueError("metric weights must be non-negative")
    state_sq = sum((x-y)**2 for x, y in zip(a.state.as_tuple(), b.state.as_tuple()))
    history_term = 0.0
    if a.log.digest != b.log.digest:
        history_term = float(max(1, abs(a.log.event_count - b.log.event_count)))
        if a.log.event_count == b.log.event_count:
            history_term = 1.0
    return math.sqrt(state_weight * state_sq + history_weight * history_term)


def no_reset_holds(before: Identity, after: Identity) -> bool:
    """Operational no-reset check for append-only histories.

    It is guaranteed only when a new unique event is appended; it is not a
    theorem for arbitrary state updates or lossy projections alone.
    """
    return (after.history.revision > before.history.revision
            and after.history.events[:before.history.revision] == before.history.events
            and after.log.digest != before.log.digest)
