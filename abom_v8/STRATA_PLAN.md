# STRATA integration plan for ABOM-V8

**Protocol authority:** PANoRAMic.os `experiments/strata/STRATA_PROTOCOL_v0.1.md`.
**Status:** protocol-aligned experimental plan; no empirical cross-domain claim.

## Claim under test

The initial ABOM experiment asks whether candidate lemniscate geometries preserve selected geometric descriptors under declared scale normalization and increasing sampling resolution. This is a geometric software experiment, not a claim of a universal invariant, physical transport law or cross-domain equivalence.

## Pipeline

1. Source/provenance: analytic Gerono and Bernoulli parameterizations implemented in `transport/curves.py`.
2. Quality checks: finite samples, exact sampled origin crossings, closed path, positive scale parameters.
3. Feature extraction: bounding width/height, polygonal lobe areas, area asymmetry, polyline arc length, discrete curvature proxy.
4. Scale transition: 401, 801 and 1601 samples.
5. Representation transition: analytic parameterization to sampled polyline and normalized descriptor report.
6. Controls: compare equal-width, equal-lobe-area and equal-arc-length conditions separately; report unmatched descriptors rather than optimizing them away.
7. Held-out evaluation: `not_tested`; no predictive dataset is part of this geometric smoke experiment.
8. Report: JSON-serializable output from `compare_lemniscates` and `resolution_sweep`.

## Required STRATA dimensions

| Dimension | Status | Reason |
|---|---|---|
| Three meaningful scales | not_tested | 401/801/1601 are numerical discretization resolutions, not three meaningful scales under STRATA |
| Two independent domains | not_tested | only analytic curve families are compared |
| Two representations | pass, limited | parametric curves and sampled polylines |
| Observer/implementation checks | not_tested | independent implementation is a future control |
| Randomized control | not_tested | deterministic geometric comparison has no stochastic hypothesis |
| Structure-preserving control | not_tested | add a separately specified control before any invariant claim |
| Held-out predictive evaluation | not_tested | no predictive transfer claim |

These statuses do not satisfy the full STRATA promotion requirements for scale-persistent, cross-domain or predictive claims. The result remains a reproducible domain-level geometry comparison.

## Failure and uncertainty policy

A result fails if declared origin crossings, lobe symmetry, closure or matched-measure tolerance is violated. Resolution sensitivity is reported rather than hidden. Polygonal area and arc length are discretization-dependent estimates; curvature is a discrete proxy. No universal curvature or transport inference is made.

## Promotion gate

No promotion beyond a reproducible domain pattern without a preregistered three-scale/two-domain/two-representation study, independent implementation checks, randomized and structure-preserving controls, uncertainty estimates, and held-out predictive evaluation. Synthetic fixtures remain software tests only.

## Lean boundary

Lean formalization targets exact finite statements (coordinate count, occupancy complementarity and discrete combinatorial contracts). Numerical integration, sampled curvature and empirical claims remain executable experiments with explicit error analysis; they are not treated as exact Lean theorems.
