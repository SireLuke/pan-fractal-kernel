"""Model-agnostic capability placement and routing (experimental v0.1).

Models are interchangeable occupants of a fixed niche topology; capability
coordinates, not vendor names, decide placement and routing.  Finite-grid
software only: see README.md for the evidence boundary.
"""
from .capability import (
    AXES, PROFILE_SCHEMA, CapabilityVector, fit_cost, l1_distance,
)
from .params import NahtChannelParameters
from .placement import BenchmarkMap, Placement, PlacementError, place
from .registry import Niche, NicheMap, Occupant, PlacementDecision
from .router import (
    DispatchResult, NoEligibleOccupant, RouteDecision, TaskProfile, dispatch, route,
)
from .transport import OllamaTransport, Transport, TransportError

__all__ = [
    "AXES", "PROFILE_SCHEMA", "CapabilityVector", "fit_cost", "l1_distance",
    "NahtChannelParameters", "BenchmarkMap", "Placement", "PlacementError", "place",
    "Niche", "NicheMap", "Occupant", "PlacementDecision", "DispatchResult",
    "NoEligibleOccupant", "RouteDecision", "TaskProfile", "dispatch", "route",
    "OllamaTransport", "Transport", "TransportError",
]
