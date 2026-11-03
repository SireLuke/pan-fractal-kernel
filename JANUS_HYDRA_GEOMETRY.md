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

The primary shared geometric domain is the **Gosset 4_21 polytope**, the convex hull of the 240 E8 roots in R^8. The canonical root normalization is ||alpha||^2=2. Its 1-skeleton has 240 vertices, 56 nearest neighbors per vertex, and 6,720 edges. See `GOSSET_421_GEOMETRY.md` and `gosset_421.py` for the exact root construction and invariants.

JOBF evaluates the radial function of this convex body from the shared origin. For a unit direction n,

[
rho_G(n)=max{r >= 0 : r n in conv(E8_ROOTS)}.
]

The implementation uses a cached convex-hull facet representation and vectorized ray/facet intersections. It does **not** use the support function as though it were the radial function, and it does not solve one linear program per sample in the simulation hot loop. The optional LP in `gosset_421.py` remains a reference/checking method.

The 8D cross-polytope H8={q in R^8: sum_i |q_i|<=1} is retained as an explicitly named legacy/comparison geometry, with radial function rho_H(n)=1/sum_i|n_i| for unit n. It is not interchangeable with Gosset 4_21 and is no longer the JOBF default. Select it explicitly with `geometry="cross_polytope"` or the CLI option `--geometry cross_polytope`; the default is `geometry="gosset"`.

The origin is the shared waist/reference point. UHFE and UDFE are not assigned opposite geometric halves and are not split into separate domains. They maintain independent histories and parameters. Do not impose (U_D=1-U_H). JOBF uses centered field deviations and an explicit interaction term to deform the chosen base radial boundary. For finite exponents, the exponential radial law remains positive. This is a candidate computational shape-evolution rule, not a law derived from physics.

The eight V8 coordinate channels remain distinct from the 256 sign orthants of R^8 and from the 240 E8 root vertices. Sign-symmetric directional weights use (w_i=n_i^2/sum_j n_j^2); chirality requires a separately specified orientation-sensitive operator. The geometry adapter changes the spatial boundary calculation only; it does not mutate V8 records or alter UHFE/UDFE head semantics.

## Validation contract

1. V8 order is stable: (h, R, u, d, tau, chi, s, f).
2. The reader rejects malformed, non-finite, and out-of-range inputs.
3. Exactly five UHFE and five UDFE heads are produced with their own vocabulary.
4. Each UHFE head is explicitly paired to its named UDFE inverse.
5. Both projections contain eight finite channels over the same domain.
6. The origin remains shared; the domain is not divided into two half-polytopes.
7. Finite JOBF inputs produce finite positive radial boundaries under the selected adapter.
8. Gosset 4_21 is the default JOBF geometry; cross-polytope H8 remains explicitly selectable as a comparison baseline.
9. Geometry selection does not alter V8 coordinate order, semantic head values, or the paired UHFE/UDFE records.
10. Numerical success validates implementation invariants, not a physical interpretation.

## Data ingestion

Gaia DR3 and GRMHD adapters map their source observables/primitives into provisional normalized V8 proxy vectors. Those vectors must pass through the Hydra Semantic Reader before JOBF. The proxy mappings remain engineering assumptions, not direct measurements of V8 semantics; retain source values and provenance and do not conflate datasets without calibration.
