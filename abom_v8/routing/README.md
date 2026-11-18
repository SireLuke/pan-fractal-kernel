# ABOM-V8 model routing (experimental v0.1)

A model-agnostic layer in which models are interchangeable **occupants** of a
fixed set of **niches**. Capability coordinates, not vendor names, decide where a
model sits and which task it receives. Ollama is one transport, not the design.

```
Model        = occupant           (swappable)
Niche        = function / region  (fixed topology)
NicheMap     = governance layer   (placement + eligibility rules)
Transport    = execution substrate (Ollama first; anything with generate())
```

## Capability profile (not the V8 vector)

Eight axes in `[0, 1]`, versioned as `urn:pan:abom-v8:capability-profile:0.1`:
`recursive_depth`, `temporal_horizon`, `creativity` (0 deterministic .. 1
generative), `symbolic` (0 statistical .. 1 symbolic), `memory_bandwidth`,
`context_coherence`, `tool_use`, `coordination`.

This profile is separate from the canonical V8 vector `(h, R, u, d, tau, chi, s, f)`
(`../COORDINATE_CONTRACT.md`). No mapping between the two is defined here; if one
is wanted it must be explicit, versioned and validated.

## Flow for a newly released model

1. Benchmark it (outside this package).
2. `place(results, calibration)` turns scores into a `CapabilityVector`. You supply
   the calibration (`BenchmarkMap`: benchmark -> axis, score range, weight) and its
   version. No default calibration ships, and an axis with no evidence yields no
   vector rather than a default value.
3. `NicheMap.place(Occupant(...))` seats it in the nearest niche whose minimums it
   meets. An incumbent is displaced only by a strictly closer occupant.
4. `route(TaskProfile(...), niche_map)` ranks seated occupants by `fit_cost`
   (shortfall costs 1 per unit, excess costs `excess_penalty`, default 0.25), with
   hard minimums and a context-size floor. Ties break by niche id.
5. `dispatch(prompt, task, niche_map, transports)` sends the prompt through the
   chosen occupant's transport.

`OllamaTransport.list_models()` lists installed models so unplaced ones can be found.

## Invariants

- The niche set never changes when occupants are seated, replaced or vacated.
- Routing and placement never read a model or vendor name.
- Results are deterministic for the same inputs.

The per-axis distance metric properties and seating-preserves-occupancy are
stated in `formal/PAN/ABOM/Routing.lean` (integer model, not the float router).

## NAHT parameters

Each occupant carries a `NahtChannelParameters` block for the Non-Abelian History
Transport channels `(r, e, p)` (`../../NAHT_QCD_JUNCTIONS.md`). All channels are
unassigned by default; assigning any requires units, normalization, provenance
and calibration version. No routing-to-NAHT mapping is defined here.

## Evidence boundary

Software and arithmetic only. A capability coordinate is a declared engineering
descriptor derived from supplied benchmark scores; nothing here claims it
describes a model's cognition, nor that the fractal topology has any property
beyond the stated invariants. STRATA record `ABOM-V8-MODEL-ROUTING-001` is a
`software-smoke-test` and promotion-ineligible
(`../../MODEL_ROUTING_STRATA_PROTOCOL.md`).

## Example

```python
from abom_v8.routing import (
    AXES, CapabilityVector, Niche, NicheMap, Occupant, TaskProfile, route,
)

def vec(**kw):
    return CapabilityVector.from_mapping({**{a: 0.5 for a in AXES}, **kw})

niches = NicheMap([
    Niche("reasoning", vec(symbolic=0.9, recursive_depth=0.9)),
    Niche("coding", vec(tool_use=0.9, symbolic=0.7), minimums={"tool_use": 0.6}),
])
niches.place(Occupant("qwen-coder", "ollama", vec(tool_use=0.9, symbolic=0.7)))
niches.place(Occupant("deepseek-r", "ollama", vec(symbolic=0.9, recursive_depth=0.9)))

decision = route(TaskProfile(vec(tool_use=0.9, symbolic=0.7)), niches)
print(decision.niche_id, decision.occupant.model_id)   # coding qwen-coder
```

The vectors above are illustrative, not measurements. See
`tests/test_abom_v8_model_routing.py` for end-to-end usage including `dispatch`
through `OllamaTransport` against a local stub server.
