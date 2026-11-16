# STRATA protocol: Fourier curve parameterization experiment

Project attribution: Lucas Thouvenell (@SireLuke).

Status: preregistration template for future runs. No experiment is claimed to
have run by the presence of this document.

## Question

Can two parameterizations of the same closed planar locus produce different
finite Fourier coefficient vectors, and how do truncation order and sampling
density affect reconstruction error?

## Hypotheses

- H1 (parameterization sensitivity): a nontrivial smooth monotone periodic
  reparameterization of a non-circular reference curve preserves its locus
  while changing its Fourier coefficients.
- H2 (truncation): for a fixed sampled parameterized signal and nested
  symmetric mode sets, the least-squares/orthogonal-projection residual on
  the training samples is non-increasing as modes are added.
- H3 (sampling sensitivity): changing sample density or endpoint convention
  can change estimated coefficients and must be reported, not hidden.

## Fixtures and controls

Primary fixture: analytic ellipse with known low-frequency parameterization.
Warped fixture: same ellipse locus under a smooth, strictly increasing
periodic phase warp. Control A: identity phase map. Control B: reversed
traversal. Control C: a translated/scaled ellipse with the same normalized
shape, used to check coordinate normalization. Include a polygonal or
violin-like closed outline only when its source points and parameterization
are retained as immutable inputs.

The phase warp must be checked for monotonicity over a full period before
being accepted. All runs must declare orientation, start point, period,
sampling count, endpoint duplication policy, coordinate units, normalization,
mode convention, and truncation order.

## Metrics

Report separately:
1. coefficient-vector difference under the declared mode ordering;
2. synchronized maximum and RMS pointwise reconstruction errors;
3. errors normalized by the original outline height;
4. a parameterization-invariant shape metric (for example a separately
   specified bidirectional Hausdorff approximation) only in a later stage.

Never interpret synchronized error as a parameterization-invariant shape
distance. Report discretization and truncation contributions separately
where the experiment design permits.

## Leakage and reproducibility

Freeze source samples, protocol version, code revision, parameterization
functions, and seeds before comparison. Use deterministic fixtures first.
For randomized fixtures, derive independent per-run seeds from a recorded
master seed without replacing the base seed or prior evidence. Do not tune
the warp, mode count, or normalization after inspecting the comparison result.

## Evidence classification

- Exact analytic identity: only where established symbolically.
- Software/numerical check: implementation behavior on declared fixtures.
- Reference comparison: agreement with an independently computed reference.
- Research hypothesis: any claim about geometry, dynamics, or physical meaning.

A passing test is not physical validation. Do not infer that Fourier modes
correspond to V8 coordinates, E8 roots, physical harmonics, or a preferred
transport geometry. Any such mapping requires a separate hypothesis,
independent controls, uncertainty analysis, and its own STRATA protocol.

## Lean 4 obligations

Formalization is pending. The first target is a finite-sum specification for
the coefficient map and elementary algebraic properties over an explicitly
chosen scalar field. The numerical Python DFT must not be described as
formally verified until a refinement relation and floating-point error
contract are established. The Lean build must be run and recorded separately.
