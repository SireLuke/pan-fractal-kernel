# The Grout Line: Cross-Domain Emergence and Structural Invariants

**Study ID:** GL-001  
**Protocol:** v0.1 (preregistration scaffold)  
**Status:** research-only; no results claimed  
**Owner:** SireLuke (@SireLuke)

## Research question

Do independently implemented systems exhibit reproducible structural invariants when compared across scale, representation, and domain, or do apparent correspondences disappear under independent controls?

The "grout line" is the interface between models. It is not an assumption that the models are equivalent, share a physical substrate, or instantiate a new law.

## Scope

This branch is an isolated research workspace. It must not be imported by production packages, registered in built-in plugin registries, invoked by production boot, or merged into `main` without explicit authorization.

### Study tracks

1. **Cellular automata:** Conway's Game of Life (B3/S23) and selected one-dimensional elementary cellular automata (including Rule 110 as a complex-dynamics case and Rule 30 as a stochastic-looking control).
2. **Nonlinear transport:** viscous and inviscid Burgers equation as a controlled PDE/numerics benchmark, with exact or manufactured solutions where available.
3. **Recursive geometry:** Menger sponge occupancy/surface observables; Gosset 4_21/E8 only where a mathematically justified mapping is specified. The Gosset polytope remains the primary high-dimensional geometry target; hyperoctahedral objects are comparison/projection tools only.
4. **Occupancy dynamics:** Fermi-Dirac occupancy and the exact disk-partition identity, keeping geometric identities distinct from physical interpretation.
5. **Ordered transport:** NAHT/SU(2) path-ordered transport as a separate track. Use synthetic or explicitly user-owned logs only; no surveillance or third-party location trails.

## Operational definition of a candidate invariant

A candidate invariant must be:
- defined before evaluation, with units, domain, and representation specified;
- computed independently in at least two implementations or representations;
- compared across at least three declared scales and two genuinely distinct domains before any cross-domain claim;
- evaluated on held-out seeds/initial conditions, not used to tune the candidate;
- robust against randomized and structure-preserving null controls;
- accompanied by uncertainty, sensitivity, and baseline comparisons;
- reported with reproducible inputs, code revision, environment, and seeds.

A matching scalar summary alone is insufficient. Preserve path/order information where relevant (e.g. holonomy).

## Evidence labels

Use only: `pass`, `fail`, `inconclusive`, `not_tested`. Software tests establish implementation behavior, not physical validity. Synthetic fixtures are never empirical validation. A passing arithmetic or Lean proof does not establish a scientific law.

## Architectural boundaries

- PAN V8 coordinate order and meanings remain unchanged: `(h, R, u, d, tau, chi, s, f)`.
- Janus Hydra is a semantic/geometric translator, not a validation authority.
- UHFE and UDFE remain distinct coupled constructs; neither is silently substituted for the other.
- Gosset 4_21 / E8 remains the primary geometry target where relevant.
- STRATA is the audit/evaluation protocol, not an oracle.
- No canonical data mutation, production boot wiring, built-in plugin registration, or production import from this study.

## Initial deliverables

- preregistered protocol and dataset manifest;
- deterministic reference implementations and property tests;
- independent implementations for selected observables;
- null/control generators;
- held-out evaluation runner and machine-readable STRATA records;
- Lean proofs only for discrete arithmetic/finite combinatorial claims that fit the formal boundary.

## Current status

This initial commit contains specification only. No experiments have been executed and no result is claimed.
