# STRATA protocol: Menger–wave coupling v0.1

Project attribution: Lucas Thouvenell (@SireLuke).

Status: preregistration for finite-grid software/numerical experiments. No
physical experiment or physical validation is claimed.

## Question

Does a recursively structured 3D Menger occupancy mask produce a reproducible
spatial and spectral change in declared complex scalar-field fixtures beyond
what is explained by retained volume fraction alone?

## Hypotheses

- H1: At fixed opacity, the structured Menger mask produces an output field
  distinguishable from identity and occupancy-preserving shuffled-mask
  controls for at least one nonuniform analytic fixture.
- H2: Phase-only coupling preserves total discrete power while changing the
  complex field wherever retained cells have nonzero field amplitude.
- H3: The observed output-power ratio matches
  `1 - q + q(1-alpha)^2`, where `q` is the input-power-weighted occupancy.

## Fixtures and scales

Fixtures: analytic plane wave, Gaussian wave packet, and spherical wave.
Geometric refinement levels: 1, 2, and 3, with side lengths 3, 9, and 27.
These are meaningful recursive geometry resolutions, not physical length
scales. The same analytic fixture definition must be sampled consistently at
each level, with grid spacing and normalization recorded.

## Controls

- Identity: `alpha = 0`, `theta = 0`.
- Phase-only: `alpha = 0`, `theta != 0`.
- Occupancy-preserving randomized mask: independently permute the binary mask
  with a recorded seed; retained-cell count must remain exact.
- Uniform occupancy: a declared spatially uniform transmission reference with
  the same mean retained fraction, used only to distinguish geometry from
  bulk attenuation.

## Metrics

1. geometry occupancy fraction;
2. input-power-weighted occupancy;
3. input and output discrete power;
4. measured and predicted power transmission ratio;
5. complex-field RMS difference;
6. normalized Fourier-spectrum difference;
7. level-to-level changes and numerical residuals.

All Fourier comparisons must declare normalization, ordering, and whether
coefficients or power spectra are compared. A coefficient difference is not
automatically a shape-invariant or physical frequency result.

## Leakage and reproducibility

Freeze analytic fixture definitions, sample grids, endpoint conventions,
normalization, opacity, phase, seeds, source revision, and metrics before
sweeps. Randomized controls use independent recorded seeds. Keep a base seed
and derive child seeds without replacing prior evidence. Report every attempted
fixture/level/control combination, including failures and null results.

## Evidence classification and promotion

The first implementation supports exact discrete identities and software
checks only. Three recursive levels do not count as three independent physical
scales. The fixtures are not independent physical domains. Independent
observer implementations, structure-preserving controls, held-out predictive
evaluation, uncertainty analysis, and any physical model are not supplied.

The record must remain `software-smoke-test` and promotion-ineligible until
all required STRATA dimensions are independently satisfied. A passing CI run
is not empirical validation.
