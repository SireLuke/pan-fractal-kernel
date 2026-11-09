# Research experiment report: E8 / 5_21, SU(9)/SU(10), and 11D M-theory

**Date:** 2026-11-09
**Branch:** research/m-theory-11d-5_21-integration
**Baseline:** JANUS-HYDRA-DYNAMIC-INVERSE-v1 (unchanged)
**Scope:** Read-only mathematical experiments and documentation. No production equations, runtime code, or canonical semantic records changed.

## Executive summary

Three mathematical experiments were performed against the checked-in Fractal Kernel specifications and source. Independent local Python calculations reproduced the Gosset 4_21 / E8 root invariants, all-root Weyl reflection preservation, E8 lattice translation membership, and SU(9)/SU(10) rank/dimension arithmetic. The dimensional-reduction symmetry ladder was checked against references on maximal supergravity and exceptional hidden symmetries.

These results validate mathematical/software invariants and representation bookkeeping only. They do not validate M-theory, identify V8 with spacetime coordinates, or establish a physical role for Janus Hydra.

## Experiment 1 — E8 / 5_21 / Gosset 4_21

The repository's gosset_421.py constructs:
- 112 integral roots (two entries ±1, remaining entries zero);
- 128 half-integral roots (eight entries ±1/2 with even minus-sign parity).

Independent calculation results:
- 240 roots; 240 unique.
- Every root has squared norm 2.
- Inner-product distribution against a fixed root: -2:1, -1:56, 0:126, +1:56, +2:1.
- Adjacency defined by inner product +1 gives degree 56 and 6,720 undirected edges.
- Reflection in each of all 240 roots permutes the entire 240-root set.
- Translation of every root by the E8 lattice vector (1,1,0,0,0,0,0,0) preserves E8 lattice membership.
- All pairwise differences of the 240 roots were checked to belong to the E8 lattice.
- The translated finite 240-point subset is not equal to the original root set; it is another finite subset of the infinite lattice.

Interpretation: the 5_21 honeycomb supplies the global E8 lattice / affine Weyl context; 4_21 is its local Gosset vertex figure. Keep the finite 240-root vertex set distinct from the infinite lattice. The affine Weyl group is W_aff(E8), associated with affine Kac-Moody algebra E9; do not equate the finite E8 Weyl group with the affine group.

Status: PASS for these computed invariants. The full 5_21 cell-incidence/honeycomb construction is not yet implemented or independently enumerated in this experiment.

## Experiment 2 — SU(9) and SU(10)

Arithmetic checks:
- rank(SU(9)) = 8.
- dim(su(9)) = 9^2 - 1 = 80.
- dim(Λ^3 C^9) = binomial(9,3) = 84.
- 80 + 84 + 84 = 248, consistent with the E8 adjoint branching under the SU(9) subgroup: 248 = 80 + 84 + conjugate(84).
- rank(SU(10)) = 9, greater than rank(E8)=8; therefore SU(10) cannot be a subgroup of E8.

Status: PASS for rank and dimension arithmetic. Full Lie-algebra embedding and branching-rule code has not been implemented. SU(10) remains a separate extension candidate requiring a specified larger ambient algebra and explicit embedding.

## Experiment 3 — 11D M-theory / maximal-supergravity reduction

Reference-level symmetry ladder:
- 11D: 11-dimensional supergravity is the low-energy effective description associated with M-theory.
- 10D: IIA O(1,1); IIB SL(2,R).
- 9D: SL(2,R) x R+ (often locally described as GL(2,R)).
- 8D: SL(3,R) x SL(2,R).
- 7D: SL(5,R).
- 6D: SO(5,5).
- 5D: E6(6).
- 4D: E7(7).
- 3D: E8(8).
- 2D: affine E9.
- E10 and E11 are higher Kac-Moody proposals/hidden-symmetry frameworks, not ordinary finite-dimensional groups or established extra spacetime dimensions.

The exceptional E_{11-D} pattern in lower-dimensional maximal supergravity requires dimensional reduction and appropriate field dualizations. The E8 root geometry in R8 is not the same object as the 3D split real symmetry group E8(8).

Status: PASS for the conceptual mapping and reference-level ladder. No 11D field equations, compactification, or numerical reduction were solved.

## Architecture decision

Preserve these separate layers:
1. 11D theory context: abstract spacetime indices M=0,...,10, metric signature, 3-form, model/provenance metadata.
2. Exceptional symmetry registry: finite E8, affine E9, hyperbolic E10, very-extended E11, SU(9), and exploratory SU(10), each with explicit algebra/group classification.
3. 5_21 / E8 lattice geometry: global lattice and affine Weyl traversal.
4. Gosset 4_21: local 8D vertex figure and existing canonical 240-root geometry.
5. V8: unchanged semantic vector (h,R,u,d,tau,chi,s,f), normalized [0,1].
6. Janus Hydra: unchanged five dynamic formation/inverse pairs.
7. UHFE and UDFE: separate receiving fields; never impose UHFE + UDFE = 1.

Do not assume M11 = M8 x B3. Any future compactification must declare topology, metric, signature, reduction ansatz, retained fields, units, normalization, uncertainty, provenance, and information loss. Do not create three additional V8 semantic coordinates.

## Repository inspection and execution status

Inspected source/specification:
- gosset_421.py
- GOSSET_421_GEOMETRY.md
- PAN_V9_AFFINE_E8_EXPERIMENT.md
- janus_hydra.py
- janus_metrics.py
- tests/test_gosset_421.py
- v9_affine_e8_projection.py
- tests/test_v9_affine_e8_projection.py
- tests/test_janus_dynamic_inverse_v1.py
- tests/test_gosset_projection.py

The tests were statically inspected but NOT executed in the repository environment during this experiment. Independent calculations were executed in a separate local Python environment. No pass count is claimed for pytest or GitHub Actions.

Recommended next tests:
1. Add tests for E8 lattice translation and infinite-lattice versus finite-root distinction.
2. Implement a true 5_21 cell/vertex incidence adapter and test its 4_21 vertex figure.
3. Add a symbolic SU(9) branching-rule test, not only dimension arithmetic.
4. Add a symmetry registry with explicit finite/affine/hyperbolic/very-extended classifications.
5. Keep all 11D reduction adapters separate and versioned.
6. Rerun canonical Janus v1 and Gosset/V9 test suites in CI before any merge.

## Scientific status

The computations establish finite root-system and software invariants. The group branching and dimensional-reduction ladder are established mathematical/theoretical relationships. Any mapping from these structures to PAN semantic values is a design hypothesis requiring its own calibration and validation. No nonzero Janus pair defect is assigned physical meaning by these experiments.
