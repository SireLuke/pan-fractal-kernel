# PAN V8 Janus Hydra Semantic Pipeline

**Status:** Open computational research specification. These mappings are geometric/semantic engineering constructs, not claims of a new physical field theory.

## Canonical execution path

The **Hydra Semantic Reader is the primary semantic gateway into V8 and JOBF**:

`source / calibrated semantic input
  -> hydra_semantic_reader.coerce_v8_state
  -> Janus Hydra UHFE + UDFE interpretation
  -> explicit paired-head record
  -> two eight-channel V8 projections
  -> JOBF field coupling / boundary evaluation`

All normalized inputs are validated against the canonical V8 order:

`V8 = (h, R, u, d, tau, chi, s, f)`

The reader accepts a `V8State`, a mapping using those exact coordinate names, or an eight-value sequence in that order. The provisional `T` alias is accepted for `tau` only when `tau` is not also supplied. Inputs outside [0,1], missing coordinates, and unexpected keys are rejected; values are never silently clamped.

The reader returns a `HydraSemanticFrame` containing the validated state, five UHFE heads, five distinctly named UDFE inverse heads, explicit pair records, and two independent eight-channel projections. JOBF and the observational/GRMHD ingestion bridge consume this frame rather than reimplementing the semantic mapping.

## Janus Hydra vocabulary

Janus Hydra is the canonical name for the coupled formation/dissolution semantic architecture. UHFE and UDFE are not two halves of the geometry: they are distinct semantic fields evaluated over the same complete V8 domain.

| UHFE head | V8 support | UDFE inverse head |
|---|---|---|
| Bubble | (h, R, u) | `antibubble_cavitation` |
| Honeycomb | (tau, s) | `inversehoneycomb` |
| SpiderWeb | (f, h, R) | `inversespiderweb_radialvoid` |
| ChiralDNA | (chi, tau, R) | `chiralvoid` |
| CompoundEye | (s, h, d) | `discretesingulardots_inversecompoundeye` |

The inverse names are intentionally not renamed to match the UHFE keys. The semantic reader pairs them explicitly, preserving the Janus distinction and the provenance of each inverse rule.

Baseline UHFE scores:

[
B=(h+R+u)/3,quad H=(tau+s)/2,quad W=(f+h+R)/3
]
[
C=(chi+tau+R)/3,quad E=(s+h+d)/3.
]

The normalized complement is (C(x)=1-x), with (C(C(x))=x). The reference UDFE scores are:

[
B^-=(d+(1-u)+(1-h))/3
]
[
H^-=((1-tau)+(1-s))/2,quad W^-=((1-f)+(1-h)+(1-R))/3
]
[
C^-=((1-chi)+(1-tau)+(1-R))/3,quad E^-=((1-s)+(1-h)+d)/3.
]

The d term is deliberately retained in AntiBubble and inverse CompoundEye as a dissolution-side signal. Preserve this as a versioned semantic rule.

## Shared geometry and independent fields

The geometric domain remains the whole 8D cross-polytope:

[
H_8={qin R^8:sum_i |q_i|leq1},quad rho_0(n)=1/sum_i|n_i|
]

for unit direction n. The origin is the shared waist/reference point. Do not split the polytope into formation and dissolution halves.

UHFE and UDFE maintain independent histories and parameters. Do not impose (U_D=1-U_H). JOBF uses centered field deviations and an explicit interaction term to deform the radial boundary. For finite exponents, the exponential radial law remains positive. This is a candidate computational shape-evolution rule, not a law derived from physics.

The eight V8 coordinate channels are distinct from the 256 sign orthants of R^8. Sign-symmetric directional weights use (w_i=n_i^2/sum_j n_j^2); chirality requires a separately specified orientation-sensitive operator.

## Validation contract

1. V8 order is stable: (h, R, u, d, tau, chi, s, f).
2. The reader rejects malformed, non-finite, and out-of-range inputs.
3. Exactly five UHFE and five UDFE heads are produced with their own vocabulary.
4. Each UHFE head is explicitly paired to its named UDFE inverse.
5. Both projections contain eight finite channels over the same domain.
6. The origin remains shared; the domain is not divided into two half-polytopes.
7. Finite JOBF inputs produce finite positive radial boundaries.
8. Numerical success validates implementation invariants, not a physical interpretation.

## Data ingestion

Gaia DR3 and GRMHD adapters map their source observables/primitives into provisional normalized V8 proxy vectors. Those vectors must pass through the Hydra Semantic Reader before JOBF. The proxy mappings remain engineering assumptions, not direct measurements of V8 semantics; retain source values and provenance and do not conflate datasets without calibration.
