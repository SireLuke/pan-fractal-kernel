# Menger–wave coupling v0.1

Project attribution: Lucas Thouvenell (@SireLuke).

## Purpose and boundary

This module treats the finite 3D Menger sponge as a semi-transparent spatial
occupancy mask applied to a caller-supplied complex scalar field. It does not
solve a wave equation, derive a potential, implement reflection or scattering,
or assert a physical coupling. It is a deterministic numerical operator for
testing whether recursive geometry creates measurable spatial and spectral
changes in declared wave-field fixtures.

The Fractal Kernel owns the operator. ABOM-V8 exposes it through an adapter.
The V8 schema remains exactly `(h, R, u, d, tau, chi, s, f)`; the mask is
external geometry and is not a ninth coordinate.

## Mathematical contract

For a finite-level Menger occupancy indicator `M(x) ∈ {0,1}` and complex input
field `psi(x)`, define

`T(x) = (1 - alpha M(x)) exp(i theta M(x))`

`psi_out(x) = T(x) psi_in(x)`

where `alpha ∈ [0,1]` is amplitude opacity and `theta` is a finite phase shift
in radians. Retained sponge cells attenuate and phase-shift the field; void
cells transmit unchanged. This is a semi-transparent mask, not a material
constitutive law.

For input power density `|psi|^2`, the exact discrete power ratio is

`P_out/P_in = 1 - q + q(1-alpha)^2`

where `q = sum(|psi|^2 M) / sum(|psi|^2)` is the wave-weighted occupancy.
The phase parameter does not alter local power. The maximum transmission
amplitude is at most one. The geometry-only retained fraction at level `k`
is exactly `(20/27)^k`; this need not equal the wave-weighted occupancy for
a nonuniform field.

## API

- `menger_occupancy_mask(level)` returns a boolean cubic grid of side `3^level`.
- `apply_occupancy_coupling(wavefield, mask, opacity, phase_shift)` applies the
  operator to a supplied mask, including randomized controls.
- `menger_wave_coupling(wavefield, level, opacity, phase_shift)` constructs
  the 3D Menger mask and applies it.

Input fields must be finite, nonzero, complex-compatible 3D arrays matching
the mask shape. The implementation reports input/output power, geometry and
wave-weighted occupancy, predicted power ratio, and maximum transmission
amplitude.

## Initial experiment design

Use three analytic fixture families: plane waves, Gaussian wave packets, and
spherical waves. Evaluate recursive levels 1, 2, and 3 as geometric refinement
scales, with field support sampled on the matching `3^k` grid. Preserve the
same analytic field definition when resolution changes; record grid spacing,
normalization, and sampling convention.

Controls:
1. zero-coupling identity (`alpha = theta = 0`);
2. phase-only control (`alpha = 0`), which must preserve total power;
3. occupancy-preserving shuffled masks, with the same number of retained cells;
4. uniform-mask control with the same retained fraction, to separate spatial
   arrangement from bulk occupancy.

Primary metrics:
- geometry occupancy and wave-weighted occupancy;
- input/output power and power transmission ratio;
- complex-field RMS difference;
- normalized Fourier-spectrum difference;
- resolution/level sensitivity and numerical residual against the exact power
  identity.

Do not interpret a change in Fourier coefficients as evidence of a new physical
frequency or a new interaction. The finite mask is a numerical boundary
condition, not a scattering model. No reflection, time evolution, boundary
conditions, energy conservation law, or material response is implemented.

## STRATA v0.1 preregistration

Hypothesis H1: for a nonuniform complex field, the structured Menger mask
produces a spatially resolved output distinct from both the identity and an
occupancy-preserving shuffled mask at fixed opacity.

H2: phase-only coupling changes the complex field but preserves total power
to floating-point tolerance.

H3: the measured power ratio agrees with the occupancy-weighted closed-form
identity at levels 1–3 and for independently declared analytic fixtures.

Freeze source code, fixtures, seeds, opacity, phase shifts, normalization,
grid convention, and comparison metrics before any parameter sweep. Use
independent seeds for randomized masks. Report all controls, including null
results. Do not tune opacity or phase after inspecting outcomes.

Evidence classification:
- exact identity: the discrete power-ratio formula, conditional on the
  declared multiplicative operator;
- software/numerical check: implementation behavior on finite fixtures;
- research hypothesis: any inference about physical waves, matter, or V8
  dynamics.

The initial test suite checks algebraic identities and deterministic software
behavior. It does not establish three-scale persistence across physical
scales, two independent physical domains, independent implementation
agreement, or held-out prediction. The STRATA promotion gate therefore remains
closed. No physical validation is claimed.

## Lean 4 boundary

The accompanying Lean module proves the exact rational numerator bounds for
the amplitude transmission coefficient in a finite two-state occupancy model.
It does not prove the Python floating-point implementation, complex phase
operator, Fourier behavior, or any physical interpretation. A refinement proof
from the Python numerical implementation to the Lean specification is pending.
