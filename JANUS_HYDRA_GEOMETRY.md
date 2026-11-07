# PAN V8 Janus Hydra Semantic Pipeline

**Status:** Open computational research specification. These mappings are geometric/semantic engineering constructs, not claims of a new physical field theory.

## Canonical execution path

The Hydra Semantic Reader is the primary semantic gateway into V8 and JOBF:

    source / calibrated semantic input
      -> hydra_semantic_reader.coerce_v8_state
      -> Janus Hydra semantic translation
      -> separate UHFE formation and UDFE dissolution outputs
      -> explicit paired-head record
      -> two eight-channel V8 projections
      -> JOBF field coupling / boundary evaluation

All normalized inputs are validated against the canonical V8 order:

    V8 = (h, R, u, d, tau, chi, s, f)

The reader accepts a V8State, a mapping using those exact coordinate names, or an eight-value sequence in that order. The provisional T alias is accepted for tau only when tau is not also supplied. Inputs outside [0,1], missing coordinates, and unexpected keys are rejected; values are never silently clamped.

## Architecture boundary

Janus Hydra is the fractal-geometric semantic translator. It is distinct from the V8 manifold and does not equal either output field.

- V8: canonical eight-coordinate input manifold/state.
- Janus Hydra: translates V8 states into paired semantic head representations.
- UHFE: formation-side semantic field and heads.
- UDFE: dissolution-side semantic field and inverse heads.
- Gosset 4_21: primary eight-dimensional geometric foundation.

Do not conflate Janus Hydra with UHFE or UDFE. They are separate architectural layers.

## Five semantic pairs

| UHFE formation head | Formation support | UDFE inverse head | Inverse support |
|---|---|---|---|
| Bubble | (h, R, u) | antibubble_cavitation | (d, u, h) |
| CompoundEye | (s, h, d) | discretesingulardots_inversecompoundeye | (d, s, h) |
| Honeycomb | (tau, s) | inversehoneycomb | (d, tau, s) |
| SpiderWeb | (f, h, R) | inversespiderweb_radialvoid | (d, f, h, R) |
| ChiralDNA | (chi, tau, R) | chiralvoid | (d, chi, tau, R) |

All eight V8 coordinates are covered by the five formation heads and by the five inverse heads. Each inverse head explicitly couples dissolution density d.

## Canonical JANUS-HYDRA-DYNAMIC-INVERSE-v1 equations

Formation scores:

    B=(h+R+u)/3
    E=(s+h+d)/3
    H=(tau+s)/2
    W=(f+h+R)/3
    C=(chi+tau+R)/3

Inverse scores:

    B^-=(d+(1-u)+(1-h))/3
    E^-=(d+(1-s)+(1-h))/3
    H^-=(d+(1-tau)+(1-s))/3
    W^-=(d+(1-f)+(1-h)+(1-R))/4
    C^-=(d+(1-chi)+(1-tau)+(1-R))/4

For each pair, delta_k = H_k + D_k - 1. The exact identities are:

- Bubble: (R+d-1)/3
- CompoundEye: (2d-1)/3
- Honeycomb: (tau+s+2d-2)/6
- SpiderWeb: (f+h+R+3d-3)/12
- ChiralDNA: (chi+tau+R+3d-3)/12

These are model discrepancies/diagnostics. A nonzero defect has no implied physical meaning and requires interpretation and calibration.

## Gosset geometry and projection separation

The primary shared geometric domain is the Gosset 4_21 polytope, the convex hull of the 240 E8 roots in R^8. The canonical root normalization is ||alpha||^2=2. Its 1-skeleton has 240 vertices, 56 nearest neighbors per vertex, and 6,720 edges.

The 8D cross-polytope remains a separate comparison geometry, not a substitute for Gosset 4_21. Eight V8 semantic coordinates are not the 240 E8 roots and are not the 256 sign orthants of R^8.

The projection engine retains original E8 coordinates and root indices. Lower-dimensional views report reconstruction residuals and do not redefine adjacency. The experimental V9 affine-E8 view family adds a normalized traversal parameter xi in [0,1]; xi changes the orthogonal display frame, not the canonical root set or V8 semantic state. Continuous display rotations are not generally E8 lattice automorphisms.

## Validation contract

1. V8 order is stable: (h, R, u, d, tau, chi, s, f).
2. The reader rejects malformed, non-finite, and out-of-range inputs.
3. Exactly five UHFE and five UDFE heads are produced with distinct vocabularies.
4. Every inverse head uses density d under the canonical v1 baseline.
5. The five exact pair-defect identities are regression tested.
6. Formation and inverse projection support maps are separate and each covers all eight coordinates.
7. Geometry/view operations do not mutate V8 records or Janus semantic scores.
8. Numerical success validates implementation invariants, not a physical interpretation.

## Data ingestion

Gaia DR3 and GRMHD adapters map their source observables/primitives into provisional normalized V8 proxy vectors. Those vectors must pass through the Hydra Semantic Reader before JOBF. The proxy mappings remain engineering assumptions, not direct measurements of V8 semantics; retain source values and provenance and do not conflate datasets without calibration.
