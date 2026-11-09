# 5_21 neighborhood-engine experiment and R10 clarification

**Date:** 2026-11-09
**Branch:** research/m-theory-11d-5_21-integration
**Baseline:** JANUS-HYDRA-DYNAMIC-INVERSE-v1 unchanged.
**Execution:** Independent local Python calculations; repository pytest/CI not executed.
**Repository changes:** Documentation only.

## 1. Two distinct R^10 constructions

### M-theory spatial slice
In the usual Lorentzian 11D description, spacetime is locally R^(1,10): one time and ten spatial directions. A constant-time flat spatial slice is R^10 (general backgrounds may have curved spatial slices).

### Du Val / Coxeter 5_21 coordinates
Coxeter's “Regular and Semi-Regular Polytopes III” (Math. Z. 200, 1988, pp. 3–45) records Du Val's ten-coordinate realization of the same 5_21 lattice in Euclidean R^10. The coordinates obey two independent linear constraints:
- x1+x2+x3+x4+x5 = 0
- x6+x7+x8+x9+x10 = 0

These constraints leave an 8-dimensional linear subspace. Congruence conditions modulo 5 then select the lattice points. This is a constrained ten-coordinate representation of an 8D Euclidean lattice, not a ten-dimensional 5_21 honeycomb.

The numerical coincidence with M-theory's ten spatial directions is intriguing as a representation question, but it does not identify the two spaces physically. Keep typed objects separate:
- M-theory spatial tangent space: dimension 10, equipped with the physical spatial metric/background.
- Du Val coordinate ambient space: Euclidean R^10 with two linear constraints, whose allowed subspace is dimension 8.
- V8 semantic coordinate R: remains the existing radial/boundary semantic feature; do not rename it R10.

A physical map would require an explicitly declared metric-compatible embedding and field/compactification ansatz. No such physical identification is assumed.

## 2. Local 5_21 / Gosset neighborhood calculation

Constructed the canonical E8 roots:
- 112 integral roots with exactly two nonzero entries ±1;
- 128 half-integral roots with all entries ±1/2 and even minus-sign parity.

Let Phi be the 240 roots. For a lattice vertex p, its nearest neighbors are p+Phi. For adjacent centers p=0 and q=alpha, where alpha is a root, the independent calculation returned:

| Invariant | Result |
|---|---:|
| E8 roots | 240 |
| Nearest lattice neighbors per center | 240 |
| Vertices in local Gosset 4_21 figure | 240 |
| Edges in local Gosset 4_21 graph | 6,720 |
| Degree of every local vertex | 56 |
| Squared distance between adjacent centers | 2 |
| Shared nearest neighbors of adjacent centers | 56 |
| Local incidence after translation to common origin | Identical |

The local adjacency condition is inner product 1 between distinct roots, equivalently squared distance 2. A shared neighbor beta of centers 0 and alpha requires both beta and beta-alpha to be roots, which gives beta·alpha=1. There are exactly 56 such roots.

This validates the local neighborhood primitive and translation-equivariance of its vertex-figure incidence. It does not yet enumerate every simplex/orthoplex cell and all global 5_21 incidence relations.

## 3. Candidate neighborhood engine

A separate pure adapter can implement:
1. exact integer/half-integer lattice coordinate tuples;
2. 240 nearest-neighbor transitions p -> p+alpha;
3. stable root labels and edge provenance;
4. cached local 4_21 figures;
5. deterministic BFS shells and reversible parent-edge paths;
6. explicit bounded-depth limits and shell-size/memory reporting.

The graph has unbounded depth. Finite BFS runs only establish finite-radius counts and performance; they do not establish a maximum geometric depth.

## 4. Architecture invariants

- 5_21: infinite, locally finite 8D Euclidean honeycomb, with affine E8 Weyl symmetry.
- 4_21: local Gosset vertex figure, 240 roots.
- 11D M-theory context: 10 spatial dimensions in the flat local Lorentzian model.
- V8: unchanged (h,R,u,d,tau,chi,s,f), normalized [0,1].
- Janus Hydra: unchanged five formation/inverse pairs and canonical v1 equations.
- UHFE/UDFE: separate receivers.
- No assumption M11 = M8 x B3; no implicit identification of Du Val R10 with physical M-theory spatial R10.

## 5. Execution status and next tests

**Independent calculation passed:** 240 roots, 240 nearest neighbors, 6,720 local edges, uniform degree 56, adjacent-center distance squared 2, 56 shared neighbors, translated local incidence identity.

**Not run:** repository pytest, GitHub Actions, full global 5_21 cell/facet incidence enumeration, large-radius BFS performance, Coxeter-plane Sierpinski orbit study, 11D supergravity field equations, or physical compactification.

Next:
1. Implement five21_neighborhood.py as a separate adapter.
2. Add exact-arithmetic tests for all invariants above.
3. Add bounded BFS shell tests and scaling benchmarks.
4. Implement the Du Val constrained R10 coordinate conversion and prove equivalence with the canonical E8 lattice representation in R8.
5. Separately assess whether any physical M-theory background supplies a meaningful map to that constrained coordinate space.
6. Preserve all canonical Janus v1 tests unchanged.

## 6. Sources

- Coxeter, “Regular and Semi-Regular Polytopes III,” Math. Z. 200 (1988), 3–45: https://roice3.org/ruen/Regular_and_Semi-Regular_Polytopes_III.pdf
- E8 lattice and 5_21 relation: https://en.wikipedia.org/wiki/E8_lattice
- 5_21 honeycomb structure and 4_21 vertex figure: https://en.wikipedia.org/wiki/5_21_honeycomb
- 11D supergravity and hidden symmetries: https://arxiv.org/abs/2303.12682

**Scientific status:** Exact combinatorial lattice calculations and established coordinate representation facts. No physical identification with M-theory's ten spatial dimensions is claimed.
