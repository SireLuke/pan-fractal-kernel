# Fourier Curve Analysis (finite sampled contract)

Project attribution: Lucas Thouvenell (@SireLuke).

## Purpose

`fourier_curve.py` implements a finite complex Fourier reconstruction of a
sampled planar closed curve. The input is a parameterized path
`z(t) = x(t) + i y(t)`, not an unordered point cloud. The discrete coefficients
are computed from equally spaced samples over one period, with the endpoint
not duplicated. A truncation to modes `-K..K` produces a finite approximation.

## Critical distinction: locus versus parameterization

A geometric outline is the image set traced by the curve. A parameterization
also specifies which point is visited at each value of `t`. A monotone
periodic reparameterization can preserve the same locus while changing the
Fourier coefficients, because the coefficients describe the time/parameter
signal. Therefore:

- coefficient equality is not a test of geometric-shape equality;
- synchronized pointwise reconstruction error depends on parameterization;
- the reported normalized error is max/RMS synchronized error divided by the
  input outline's vertical extent;
- this report is not a Hausdorff distance or a parameterization-invariant
  geometric error.

The reported violin figure of 0.32% is a claim about that Reel's particular
outline, sampling, parameterization, and error definition. It is not a
universal accuracy guarantee and is not reproduced by this generic engine.

## API and numerical contract

`FourierCurve.fit(samples, harmonics=K)` accepts finite planar samples,
uses modes `-K..K`, and requires at least `2K+1` samples. The input must
cover one period without repeating the endpoint. `evaluate(t)` evaluates the
truncated series at normalized parameter `t`. `error_report(samples)`
returns maximum and RMS synchronized errors, plus their fractions of outline
height.

The implementation is a deterministic direct DFT reference routine. Its
cost is O(NK) to fit and O(K) per evaluation; it is intended as a transparent
baseline, not a high-performance FFT backend. Frequencies use the convention
`exp(+2π i k t)` in reconstruction and the conjugate negative sign in
coefficient extraction.

## Validation plan

1. Exact low-mode fixtures (circle/ellipse) establish coefficient and
   reconstruction conventions.
2. Increasing truncation order is tested on fixed samples.
3. A monotone time warp of an ellipse checks that the locus can remain the
   same while coefficients change.
4. STRATA comparisons must keep parameterization, sampling density, endpoint
   convention, normalization, and truncation order explicit. Shape-only
   comparisons require a separate parameterization-invariant metric.
5. Report numerical error and sampling/discretization error separately.
   Do not label a passing software test as physical validation.

## Future extensions (separate contracts)

- Fourier series for real scalar signals and finite generalized harmonic sums
  remain distinct from this complex curve representation.
- Arc-length reparameterization and parameterization-invariant shape distance
  should be separate utilities, never silently applied during fitting.
- Windowing, adaptive sampling, FFT acceleration, uncertainty propagation,
  and graph/Gosset spectral modes require independent tests and protocols.
- Lean 4 formalization should begin with exact finite-sum identities and
  periodicity/linearity contracts; floating-point DFT implementation claims
  require a separately stated numerical refinement argument.

This is a Fractal Kernel mathematical primitive. ABOM-V8 and PANoRAMic.os may
consume it through adapters; they must not fork or duplicate the implementation.
