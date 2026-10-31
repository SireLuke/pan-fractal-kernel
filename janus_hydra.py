"""PAN V8 Janus Hydra geometric-language kernel.

Reference projections for the five UHFE heads and their UDFE inverse
vocabulary. Inputs are normalized V8 coordinates in [0, 1]. This is a
computational geometry layer, not a physical field solver.
"""
from __future__ import annotations
from dataclasses import dataclass, asdict
import math

V8_KEYS = ("h", "R", "u", "d", "tau", "chi", "s", "f")
PHI = (1.0 + math.sqrt(5.0)) / 2.0

@dataclass(frozen=True)
class V8State:
    h: float
    R: float
    u: float
    d: float
    tau: float
    chi: float
    s: float
    f: float

    def validate(self) -> None:
        for key, value in asdict(self).items():
            if not math.isfinite(value) or not 0.0 <= value <= 1.0:
                raise ValueError(f"{key} must be finite and normalized to [0, 1]")

def complement(x: float) -> float:
    """Involutive complement on [0,1]."""
    if not math.isfinite(x) or not 0.0 <= x <= 1.0:
        raise ValueError("complement input must be finite and in [0,1]")
    return 1.0 - x

def formation_heads(v: V8State) -> dict[str, float]:
    """UHFE: Bubble, Honeycomb, SpiderWeb, ChiralDNA, CompoundEye."""
    v.validate()
    return {
        "bubble": (v.h + v.R + v.u) / 3.0,
        "honeycomb": (v.tau + v.s) / 2.0,
        "spiderweb": (v.f + v.h + v.R) / 3.0,
        "chiraldna": (v.chi + v.tau + v.R) / 3.0,
        "compoundeye": (v.s + v.h + v.d) / 3.0,
    }

def inverse_heads(v: V8State) -> dict[str, float]:
    """UDFE inverse language; d remains an explicit dissolution signal
    in AntiBubble and inverse CompoundEye, following the project mapping.
    """
    v.validate()
    c = complement
    return {
        "antibubble_cavitation": (v.d + c(v.u) + c(v.h)) / 3.0,
        "inversehoneycomb": (c(v.tau) + c(v.s)) / 2.0,
        "inversespiderweb_radialvoid": (c(v.f) + c(v.h) + c(v.R)) / 3.0,
        "chiralvoid": (c(v.chi) + c(v.tau) + c(v.R)) / 3.0,
        "discretesingulardots_inversecompoundeye": (c(v.s) + c(v.h) + v.d) / 3.0,
    }

def paired_heads(v: V8State) -> dict[str, dict[str, float | str]]:
    f, inv = formation_heads(v), inverse_heads(v)
    pairs = {
        "bubble": "antibubble_cavitation",
        "honeycomb": "inversehoneycomb",
        "spiderweb": "inversespiderweb_radialvoid",
        "chiraldna": "chiralvoid",
        "compoundeye": "discretesingulardots_inversecompoundeye",
    }
    return {k: {"formation": f[k], "inverse": inv[j],
                "inverse_rule": "semantic_complement_v1"} for k, j in pairs.items()}

def cross_polytope_radius(direction: tuple[float, ...]) -> float:
    """Radial boundary for the unit 8D cross-polytope sum(|q_i|)<=1."""
    if len(direction) != 8 or any(not math.isfinite(x) for x in direction):
        raise ValueError("direction must contain exactly 8 finite coordinates")
    norm = math.sqrt(sum(x*x for x in direction))
    if norm == 0.0:
        raise ValueError("zero vector has no radial direction")
    return 1.0 / sum(abs(x / norm) for x in direction)

def octadial_weights(direction: tuple[float, ...]) -> tuple[float, ...]:
    """Eight sign-symmetric channel weights; chirality is handled separately."""
    if len(direction) != 8 or any(not math.isfinite(x) for x in direction):
        raise ValueError("direction must contain exactly 8 finite coordinates")
    denom = sum(x*x for x in direction)
    if denom == 0.0:
        raise ValueError("zero vector has no directional weights")
    return tuple(x*x / denom for x in direction)

def golden_angle_phases() -> tuple[float, ...]:
    """Eight phase offsets; a scheduling heuristic, not an 8D rotation."""
    theta = 2.0 * math.pi / (PHI * PHI)
    return tuple(i * theta for i in range(8))

def inverse_involution_holds() -> bool:
    return all(abs(complement(complement(x)) - x) < 1e-12
               for x in (0.0, .125, .25, .5, .75, .875, 1.0))

if __name__ == "__main__":
    state = V8State(.8, .7, .75, .25, .65, .6, .72, .55)
    print("UHFE:", formation_heads(state))
    print("UDFE:", inverse_heads(state))
    print("Paired:", paired_heads(state))
    print("Complement involution:", inverse_involution_holds())
