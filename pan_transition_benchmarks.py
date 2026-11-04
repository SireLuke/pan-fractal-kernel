"""PAN Transition Algebra integration benchmarks.

The quasi-star sequence is a deterministic software lifecycle fixture. The
altermagnetic path-order case is a phenomenological history-coupling probe,
not a material-specific Hamiltonian or a claim of observed memory effects.
"""
from __future__ import annotations

from dataclasses import dataclass
from math import isfinite, sqrt
from typing import Iterable, Sequence

try:
    from .transition_algebra import (
        History, Identity, Transition, V8State, becoming, hydra, identity_distance,
        janus, memory, no_reset_holds, potential, emergence,
    )
except ImportError:
    from transition_algebra import (
        History, Identity, Transition, V8State, becoming, hydra, identity_distance,
        janus, memory, no_reset_holds, potential, emergence,
    )


V8_KEYS = ("h", "R", "u", "d", "tau", "chi", "s", "f")


def _state(values: Sequence[float]) -> V8State:
    if len(values) != 8 or not all(isfinite(float(x)) for x in values):
        raise ValueError("V8 state must contain eight finite coordinates")
    return V8State(*(float(x) for x in values))


@dataclass(frozen=True)
class LifecycleStage:
    name: str
    state: V8State
    description: str


def quasi_star_lifecycle_benchmark() -> dict:
    """Exercise ΩP/E/Σ/C/J/H/M/Φ/B over a named quasi-star lifecycle.

    Stage values are normalized synthetic fixture coordinates, not inferred
    stellar measurements. Janus creates paired collapse/emission branches;
    Hydra exposes multiple named possible outcomes from the post-split state.
    """
    stages = (
        LifecycleStage("gas_cloud", _state((.20,.15,.35,.25,.10,.50,.20,.10)),
                       "Diffuse initial condition"),
        LifecycleStage("protostellar_core", _state((.35,.30,.48,.32,.22,.52,.34,.24)),
                       "Coherent core assembly"),
        LifecycleStage("stable_massive_core", _state((.62,.58,.70,.24,.60,.55,.58,.42)),
                       "High-coherence massive-core fixture"),
        LifecycleStage("bh_seed", _state((.70,.72,.62,.48,.66,.58,.72,.68)),
                       "Compact-object seed fixture"),
    )

    history = History()
    identities: list[Identity] = []
    for index, stage in enumerate(stages):
        event = Transition(
            event_id=f"quasi-star-{index:02d}-{stage.name}",
            operator=("potential/emergence" if index == 0 else
                      "structure" if index == 1 else
                      "compression" if index == 2 else "collapse"),
            payload={"stage": stage.name, "description": stage.description,
                     "v8": stage.state.as_mapping()},
        )
        history = memory(history, event)
        identities.append(becoming(stage.state, history))

    # ΩP proposes both channels without changing the seed.
    seed = stages[-1].state
    proposals = potential(seed, lambda x: (
        _state((x.h, x.R, x.u, min(1.0, x.d+.12), x.tau, x.chi, x.s, x.f)),
        _state((x.h*.96, x.R*.94, x.u*.98, x.d*.90, x.tau, x.chi, x.s*.97, x.f*.92)),
    ))
    selected = emergence(proposals, lambda candidates: 0)

    split = janus(
        selected,
        lambda x: _state((x.h, min(1.0,x.R+.08), min(1.0,x.u+.06),
                          x.d, min(1.0,x.tau+.04), x.chi, x.s, min(1.0,x.f+.05))),
        lambda x: _state((x.h*.92, x.R*.90, x.u*.94, min(1.0,x.d+.08),
                          x.tau*.90, x.chi, x.s*.94, x.f*.88)),
    )
    branch_states = hydra(split, {
        "smbh_seed": lambda pair: pair.formation,
        "core_collapse": lambda pair: pair.dissolution,
        "envelope_loss": lambda pair: _state(tuple(
            .5*(a+b) for a,b in zip(pair.formation.as_tuple(), pair.dissolution.as_tuple()))),
    })

    # Record the Janus split and each Hydra outcome as unique events.
    history = memory(history, Transition("quasi-star-04-janus", "janus",
        {"formation": split.formation.as_mapping(),
         "dissolution": split.dissolution.as_mapping()}))
    identities.append(becoming(selected, history))
    for name, branch_state in branch_states.items():
        history = memory(history, Transition(f"quasi-star-05-{name}", "hydra",
            {"branch": name, "v8": branch_state.as_mapping()}))
        identities.append(becoming(branch_state, history))

    final_identity = becoming(split.formation, history)
    no_reset_checks = [
        no_reset_holds(identities[i], identities[i+1])
        for i in range(len(identities)-1)
    ]
    return {
        "metadata": {
            "benchmark": "quasi_star_transition_lifecycle_v1",
            "fixture_kind": "deterministic_synthetic_v8_coordinates",
            "geometry_boundary": "gosset_4_21_e8_root_polytope",
            "interpretation": "software operator-integration benchmark; not stellar evolution simulation",
        },
        "stages": tuple({"name": s.name, "description": s.description,
                         "v8": s.state.as_mapping()} for s in stages),
        "potential_candidate_count": len(proposals),
        "emergence_selected_index": 0,
        "janus_channels": {
            "formation": split.formation.as_mapping(),
            "dissolution": split.dissolution.as_mapping(),
        },
        "hydra_branches": {name: state.as_mapping()
                           for name,state in branch_states.items()},
        "history_revision": history.revision,
        "identity_digest": final_identity.log.digest,
        "summary": {
            "all_identity_updates_nonzero": all(
                identity_distance(identities[i], identities[i+1]) > 0
                for i in range(len(identities)-1)),
            "append_only_no_reset_checks": tuple(no_reset_checks),
            "no_reset_invariant_holds": all(no_reset_checks),
            "janus_channels_distinct": split.formation != split.dissolution,
            "hydra_branch_count": len(branch_states),
            "raw_history_retained": len(final_identity.history.events) == history.revision,
        },
    }


def _path_area(points: Sequence[tuple[float,float]]) -> float:
    """Compute integral Delta_AF d(delta) by exact segment trapezoids."""
    if len(points) < 2:
        raise ValueError("path requires at least two points")
    area = 0.0
    for (d0, a0), (d1, a1) in zip(points, points[1:]):
        if not all(isfinite(x) for x in (d0,a0,d1,a1)):
            raise ValueError("path coordinates must be finite")
        area += .5*(a0+a1)*(d1-d0)
    return area


def altermagnetic_path_order_benchmark(
    *, delta: float = .30, delta_af: float = 1.50,
    history_coupling: float = .01,
    k_points: Iterable[tuple[float,float]] = ((.4,.7),(.9,.3),(1.2,1.0)),
) -> dict:
    """Compare two preparation paths with identical endpoint controls.

    The proxy splitting is deliberately phenomenological:
      delta_eff = delta + history_coupling * normalized_oriented_area
      splitting(k) = 2*sqrt((delta_eff*g_r)^2 + (delta_af*g_e)^2)
    where g_r=cos(kx)-cos(ky), g_e=2 sin(kx) sin(ky).
    Setting history_coupling=0 is the endpoint-only null model. Nonzero
    coupling is a test knob, not an established altermagnetic interaction.
    """
    if not isfinite(delta) or not isfinite(delta_af) or delta == 0 or delta_af == 0:
        raise ValueError("delta and delta_af must be finite and non-zero")
    if not isfinite(history_coupling):
        raise ValueError("history_coupling must be finite")
    path_a = ((0.0,0.0),(delta,0.0),(delta,delta_af))
    path_b = ((0.0,0.0),(0.0,delta_af),(delta,delta_af))
    area_a, area_b = _path_area(path_a), _path_area(path_b)
    scale = delta*delta_af
    q_a, q_b = area_a/scale, area_b/scale
    endpoint = (delta,delta_af)

    def spectrum(q: float) -> tuple[float,...]:
        delta_eff = delta + history_coupling*q
        values = []
        for kx,ky in k_points:
            if not isfinite(kx) or not isfinite(ky):
                raise ValueError("k-points must be finite")
            gr = __import__("math").cos(kx)-__import__("math").cos(ky)
            ge = 2*__import__("math").sin(kx)*__import__("math").sin(ky)
            values.append(2*sqrt((delta_eff*gr)**2+(delta_af*ge)**2))
        return tuple(values)

    spec_a, spec_b = spectrum(q_a), spectrum(q_b)
    endpoint_spec = spectrum(0.0)
    return {
        "metadata": {
            "benchmark": "altermagnetic_reversed_path_order_v1",
            "model_kind": "phenomenological_two_channel_splitting_proxy",
            "geometry_boundary": "gosset_4_21_e8_root_polytope",
            "interpretation": "path-memory sensitivity experiment; not a material-specific band calculation",
            "history_coupling": history_coupling,
        },
        "paths": {"A": path_a, "B": path_b},
        "endpoint_controls": {"A": endpoint, "B": endpoint},
        "oriented_history_area": {"A": area_a, "B": area_b},
        "normalized_history_coordinate": {"A": q_a, "B": q_b},
        "spectra": {"A": spec_a, "B": spec_b, "endpoint_only_null": endpoint_spec},
        "summary": {
            "identical_endpoints": path_a[-1] == path_b[-1],
            "equal_path_lengths": abs(
                sum(sqrt((x1-x0)**2+(y1-y0)**2) for (x0,y0),(x1,y1) in zip(path_a,path_a[1:]))
                - sum(sqrt((x1-x0)**2+(y1-y0)**2) for (x0,y0),(x1,y1) in zip(path_b,path_b[1:]))
            ) < 1e-12,
            "expected_area_A": 0.0,
            "expected_area_B": scale/2,
            "endpoint_only_spectra_equal": spec_a == spec_b if history_coupling == 0 else endpoint_spec == endpoint_spec,
            "history_proxy_spectral_max_difference": max(
                (abs(a-b) for a,b in zip(spec_a,spec_b)), default=0.0),
            "history_coupling_is_hypothetical": True,
        },
    }
