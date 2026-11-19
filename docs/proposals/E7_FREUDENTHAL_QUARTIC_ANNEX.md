# E7 Annex: Exact Freudenthal Quartic Invariant

**Proposal ID:** E7-ANNEX-001  
**Status:** Draft research proposal — implementation not yet authorized by this document  
**Repository:** `SireLuke/pan-fractal-kernel`  
**Owner / attribution:** Lucas Thouvenell (`@SireLuke`)  
**Target:** A separately versioned E7 research annex alongside the Gosset 4_21 / E8 geometry layer

## 1. Purpose

Specify an auditable exact-arithmetic implementation of the E7(7) quartic invariant on declared 56-dimensional charge vectors, beginning with the STU ((2,2,2)) sector and then extending to the Freudenthal triple system over the split exceptional Jordan algebra.

The annex evaluates a mathematical invariant on an explicitly declared representation and charge vector. It does **not** measure an astrophysical black hole, infer charges from observations, or establish a physical model. A mapping from PAN V8 states to E7 charges is out of scope and would require a separately preregistered hypothesis and validation protocol.

## 2. Evidence status and implementation boundary

A prototype report supplied for this proposal states that:
- the STU restriction reproduces Cayley's 2×2×2 hyperdeterminant;
- one declared GHZ-type fixture gives (I_4=1), and one declared W-type fixture gives (I_4=0);
- 200 seeded random integer tensors passed tested (SL(2,\mathbb Z)^3) invariance and quartic homogeneity checks.

These are **reported prototype results, not yet independently reproduced in this repository**. Before treating them as kernel results, the exact source, charge-index ordering, sign convention, normalization, fixtures, random seed, generated inputs, and transformation generators must be committed and independently rerun. No prototype code or result is silently assumed to exist in the kernel.

## 3. Mathematical scope

### 3.1 STU sector

Represent the STU charge sector as an integer tensor
[
a_{ABC}\in\mathbb Z^{2\times2\times2},\qquad A,B,C\in\{0,1\}.
]

Implement Cayley's hyperdeterminant as an explicit integer polynomial. The selected convention must be documented with the complete index-to-charge map and any electric/magnetic sign changes. The quartic invariant convention must be fixed so that the declared fixtures are unambiguous.

Required initial fixtures:
- GHZ-type charge tensor with expected (I_4=+1) under the frozen convention.
- W-type charge tensor with expected (I_4=0) under the frozen convention.
- Zero tensor and signed/permuted variants.
- Hand-calculated small integer examples independently checked by a second implementation or symbolic derivation.

The STU tests must verify:
- Exact equality with the explicit hyperdeterminant polynomial.
- Invariance under generators of each (SL(2,\mathbb Z)) factor, acting on its corresponding tensor index.
- Quartic homogeneity: (I_4(k a)=k^4 I_4(a)) for integer (k).
- Deterministic seeded property tests, with all failing tensors and transformations retained as fixtures.

A finite randomized suite is a regression test, not a proof of invariance. The generator set and algebraic identity must be documented so the group action being tested is precise.

### 3.2 Full 56-dimensional representation

Use the Freudenthal coordinate shape
[
x=(\alpha, A, B, \beta),\qquad
\alpha,\beta\in\mathbb Z,\quad A,B\in J,
]
where (J) is a precisely specified integral form of the **split** exceptional Jordan algebra (J_3(\mathbb O_s)). This gives dimensions (1+27+27+1=56).

The implementation specification must freeze:
- The chosen integral split-octonion model and basis.
- Conjugation, norm, trace, and multiplication conventions.
- The signed structure constants and multiplication table.
- The Jordan product and cubic norm on (J_3(\mathbb O_s)).
- The trace pairing and sharp/adjoint map.
- The Freudenthal quartic formula, including all signs and normalization factors.
- The precise integral charge lattice and closure properties under the selected transformations.

A Fano-plane mnemonic alone is not a sufficient algebra specification. The split real form and integral structure must be explicit; do not substitute the compact division-octonion algebra (\mathbb O) for (\mathbb O_s). The proposed “short multiplication table” is an implementation convenience, not evidence that the algebra has been specified correctly.

### 3.3 E7 root and weight bridge

Construct and record the E7 root subsystem from the kernel's E8 root system using a fixed, declared E8 root and an explicit inner-product convention. Record:
- The selected root and its canonical coordinates.
- The 126 orthogonal E7 roots.
- The 56 weights of the minuscule representation, with the sign/orientation convention used to select them.
- Their mapping to the chosen Freudenthal basis.
- The Weyl generators and their exact integer action on the 56.

Do not infer that a correct E7 root subsystem automatically supplies a correct integral Freudenthal charge basis. The embedding and basis transformation are separate objects and require explicit tests.

## 4. Invariance and consistency tests

### STU gate (E7-01)
- Exact hyperdeterminant equality.
- GHZ/W/zero fixtures.
- (SL(2,\mathbb Z)^3) generator invariance.
- Quartic homogeneity.
- Seeded randomized tests with replayable inputs.

### Algebra gate (E7-02)
- Split-octonion multiplication/conjugation identities.
- Composition/norm identities appropriate to the selected integral model.
- Jordan trace, adjoint, and cubic norm identities.
- Freudenthal quartic hand fixtures and normalization checks.
- Negative tests for invalid/non-integral inputs and unsupported elements.

### Representation gate (E7-03)
- 126-root E7 subsystem cardinality and closure.
- 56-weight cardinality, minuscule weight structure, and Weyl closure.
- Exact integer action matrices for generating Weyl reflections.
- Explicit STU embedding into the 56 and round-trip coordinate checks.

### Quartic gate (E7-04)
- Exact quartic evaluation in Freudenthal coordinates.
- Invariance under each generating Weyl reflection on the 56.
- Invariance under the embedded STU subgroup.
- Homogeneity and selected independent symbolic/small-value checks.
- Reproducible property tests with persisted seeds and counterexamples.

Weyl invariance is a necessary representation-level check, not by itself proof of invariance under the full continuous E7(7) group or the full arithmetic duality group. Claims about (E_{7(7)}(\mathbb Z)) or a physical duality group require the relevant integral group, lattice, and action to be defined and tested separately.

## 5. Certificate format

The annex may emit a canonical, content-addressed **I4 certificate**. Minimum fields:

- Schema name and version.
- Kernel commit and annex implementation version.
- Representation/form identifier (including split-octonion and lattice conventions).
- E7 root-slice identifier and selected E8 root.
- Charge vector in canonical coordinate order.
- Input encoding and canonical serialization version.
- Exact integer (I_4), with no floating-point conversion.
- Sign class: positive, negative, or zero.
- Optional theory/convention-qualified interpretation, clearly separated from the computed invariant.
- Transformations applied and their exact matrices, if applicable.
- Test-suite version, deterministic seed, and test provenance.
- SHA-256 digest of the canonical certificate payload.

The digest establishes byte-level integrity of the serialized payload; it does not establish mathematical correctness, source authenticity, or physical validity. Preserve the full payload alongside the digest.

## 6. Classification and interpretation fences

The sign of (I_4) can distinguish important orbit families in specified supergravity conventions, but sign alone must not be promoted to a complete BPS classification. Any labels such as “large BPS,” “large non-BPS,” or “small” must be conditional on a named theory, real form, charge convention, and cited classification result. The invariant evaluator's primary output remains the exact integer and its sign.

No astrophysical interpretation is emitted by default. No telescope observation becomes an E7 charge vector without an independently justified supergravity dictionary and an explicit data-to-charge model.

Canonical PAN V8 remains
[
V8=(h,R,u,d,\tau,\chi,s,f).
]
These eight coordinates are **not** the 56 E7 charges. No automatic V8-to-E7 mapping, feature extraction, or semantic equivalence is introduced by this annex.

## 7. Proposed milestone sequence

| Milestone | Deliverable | Exit criteria |
|---|---|---|
| E7-01 | STU hyperdeterminant module | Frozen convention, exact fixtures, subgroup generator tests, homogeneity |
| E7-02 | Integral split Albert algebra | Explicit basis and identities; independent checks |
| E7-03 | E7 root/56-weight bridge | Exact 126-root subsystem, 56 weights, Weyl action and embedding |
| E7-04 | Freudenthal quartic | Exact evaluation and Weyl/STU invariance tests |
| E7-05 | I4 certificate | Canonical serialization, SHA-256, provenance, replay |
| E7-06 | STRATA audit | Independent controls, reproducibility, uncertainty/limitations, no overclaim |

The STU gate may proceed independently as a small, reviewable first implementation. Full Freudenthal work is blocked until the integral split-octonion/Jordan conventions and the 56-dimensional representation map are frozen.

## 8. Repository architecture proposal

Keep this as a sibling annex, not code embedded in `gosset_421.py`. Suggested layout, subject to repository conventions:

```text
e7_annex/
  README.md
  conventions.md
  stu_hyperdeterminant.py
  split_octonion.py
  jordan_algebra.py
  freudenthal.py
  e7_representation.py
  certificate.py
  tests/
    test_stu_fixtures.py
    test_stu_invariance.py
    test_split_octonion.py
    test_jordan_identities.py
    test_e7_representation.py
    test_freudenthal_quartic.py
    test_certificate.py
```

The annex may consume the existing E8 root-system implementation through a narrow, read-only adapter. It must not modify canonical Gosset/E8 data, V8 semantics, or existing root construction. Tests should distinguish exact algebraic tests, representation tests, software integration tests, and any later empirical comparisons.

## 9. STRATA and acceptance policy

STRATA review must record:
- Source and license/provenance for any external prototype or reference implementation.
- Frozen conventions and independent derivations.
- Exact reproducibility and retained counterexamples.
- Domain-native mathematical baselines.
- Leakage and shared-implementation risks in cross-checks.
- Explicit “not tested” fields where evidence is absent.

A passing software suite establishes only that the implementation satisfies the tested software contracts. It does not validate a physical theory, an astrophysical interpretation, or a V8-to-E7 correspondence.

## 10. Approval requested

This proposal requests review and authorization for **E7-01 only** as the first implementation milestone. It does not authorize:
- Full Freudenthal implementation before E7-02/E7-03 specifications are accepted.
- Changes to canonical E8/Gosset or V8 modules.
- A V8-to-E7 mapping.
- Astrophysical data ingestion or black-hole measurement claims.
- Production wiring or automatic classification beyond the declared mathematical output.

**Acceptance principle:** two independently specified routes to the same mathematical object should agree; disagreement is retained as a finding and investigated, never silently normalized away.
