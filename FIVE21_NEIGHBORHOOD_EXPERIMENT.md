# 5_21 neighborhood-engine experiment and 11D spatial R^10 clarification

**Date:** 2026-11-09
**Research branch:** research/m-theory-11d-5_21-integration
**Canonical semantic baseline:** JANUS-HYDRA-DYNAMIC-INVERSE-v1 (unchanged)
**Execution:** Independent local Python experiment; repository pytest/CI not executed.
**Repository state:** Documentation-only addition; no production code or canonical files changed.

## 1. Clarifying R^10 in the 11D discussion

The standard Lorentzian 11D spacetime notation is M^(1,10), locally modeled in the flat case by R^(1,10): one time direction and ten spatial directions. A constant-time spatial slice is therefore R^10 (or a curved 10D spatial manifold in a general background).

This is distinct from the PAN V8 coordinate R, which remains the radial/boundary feature in V8=(h,R,u,d,tau,chi,s,f). Do not rename that semantic coordinate R10.

The E8 lattice and 5_21 honeycomb live in Euclidean R^8. An abstract linear isometric embedding R^8 -> R^10 exists, with a two-dimensional orthogonal complement, but choosing such an embedding is not a physical compactification. A physical M-theory compactification requires a specified metric, topology, field ansatz, and equations. No preferred R^8 x R^2 decomposition is assumed here.

## 2. Local 5_21 / Gosset neighborhood experiment

Constructed the canonical 240 E8 roots:
- 112 integral roots with exactly two nonzero coordinates ±1;
- 128 half-integral roots with coordinates ±1/2 and even minus-sign parity.

Then constructed local neighborhoods around two adjacent E8 lattice vertices:
- center p = 0;
- center q = alpha, where alpha is one E8 root (so ||q-p||^2 = 2).

For any lattice vertex p, its nearest lattice neighbors are p + Phi, where Phi is the 240-root set. This is the local vertex set of the 5_21 honeycomb. The induced local vertex figure is Gosset 4_21.

### Computed results

| Invariant | Result |
|---|---:|
| E8 roots | 240 |
| Nearest lattice neighbors per 5_21 vertex | 240 |
| Vertices in each local 4_21 figure | 240 |
| Edges in each local 4_21 figure | 6,720 |
| Local 4_21 degree | 56 at every vertex |
| Squared distance between adjacent centers | 2 |
| Shared nearest-neighbor vertices of adjacent centers | 56 |

The local edge criterion is inner product 1 between distinct E8 roots, equivalent to squared distance 2. The local adjacency edge-index set is identical at both centers after translating each neighborhood back to its center. This verifies that the local Gosset vertex figures are translationally congruent.

The 56 common neighbors are not accidental: for adjacent centers 0 and alpha, a root beta is shared when beta and beta-alpha are both E8 roots. Since each has squared norm 2, this requires beta·alpha=1, exactly the 56-neighbor relation in the Gosset 4_21 graph.

### Interpretation

This gives a concrete neighborhood-engine primitive:
- lattice vertex p;
- local neighbors p + Phi;
- local Gosset adjacency inherited from the 240-root inner-product graph;
- source vertex/root indices retained as provenance;
- translation between lattice centers preserves the local vertex-figure incidence structure.

This is a verified local neighborhood construction, not yet a complete enumerator for all 5_21 cells, facets, or global cell-incidence relations.

## 3. Depth and traversal implications

A next implementation can build a deterministic graph traversal over E8 lattice vertices:
1. represent each lattice vertex by an exact integer/half-integer coordinate tuple;
2. enumerate its 240 nearest neighbors by adding the 240 roots;
3. preserve root labels and edge provenance;
4. cache local 4_21 vertex figures by lattice vertex;
5. use canonical ordering to guarantee deterministic replay;
6. expose bounded BFS shells and reversible parent-edge paths.

For a bounded traversal, growth must be reported as exact unique lattice vertices per shell, not inferred from a continuous projection. The graph is infinite; a finite run only explores a finite radius.

## 4. Geometric depth versus M-theory dimensions

Keep these independent:
- E8 lattice depth: unbounded discrete graph traversal in Euclidean R^8.
- 5_21: infinite, locally finite 8D Euclidean honeycomb.
- M-theory: 11D Lorentzian spacetime, with a 10D spatial slice in the flat local model.
- V8: eight normalized semantic coordinates.
- Janus Hydra: five paired semantic transformations.
- UHFE/UDFE: separate formation/dissolution receivers.

The fact that the 5_21 lattice has unbounded graph depth does not imply extra spacetime dimensions. Conversely, the 11D spacetime dimension does not cap the number of lattice shells or recursive graph levels. These are different notions of dimension and depth.

## 5. Status and next validation gates

**Passed in independent local calculation:** root construction, 240-neighbor count, local 4_21 edge count, uniform degree 56, adjacent-center distance, 56 shared neighbors, translational congruence of local incidence.

**Not run:** repository pytest, GitHub Actions, full 5_21 cell/facet incidence enumeration, a large-radius BFS benchmark, the 72 Coxeter-plane Sierpinski seed experiment, 11D supergravity field equations, compactification, or a physical R^8-to-R^10 embedding.

Recommended next steps:
1. Implement a pure, exact-arithmetic five21_neighborhood.py adapter without modifying gosset_421.py or Janus v1.
2. Add tests for 240 nearest neighbors, 56 shared neighbors for adjacent centers, 6,720 local Gosset edges, translation equivariance, and deterministic BFS.
3. Enumerate finite BFS shells and report unique-vertex counts and memory/time scaling.
4. Separately revisit the 72 Coxeter-plane Sierpinski seeds, distinguishing orbit-invariant recursion from projection artifacts.
5. Keep any R^8-to-R^10 embedding as a separately declared geometric adapter; do not call it a compactification absent a physical ansatz.

**Scientific caution:** These are exact lattice/polytope combinatorics. They do not demonstrate an M-theory vacuum, a physical extra-dimensional geometry, or a physical interpretation of Janus pair defects.
