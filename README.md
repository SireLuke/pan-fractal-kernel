# PAN Fractal Kernel

An open computational research kernel for the PAN V8 coordinate model.

## Architecture

`hydra_semantic_reader.py` is the canonical semantic gateway:
validated V8 input -> Janus Hydra UHFE/UDFE head interpretation -> paired
semantic record -> eight-channel V8 projections -> JOBF.

- `janus_hydra.py`: normalized V8 state and Janus formation/inverse semantics.
- `hydra_semantic_reader.py`: canonical input validation, pairing, and projection.
- `jobf_v0_2.py`: time evolution, interference, and radial boundary evaluation.
- `v8_ingest_common.py`: shared observational/GRMHD ingestion bridge.
- `QCD_BENCHMARK.md`: QCD running-coupling reference and ingestion contract.
- `qcd_reference.py`: transparent fixed-flavour one-loop QCD calculations.
- `qcd_ingest.py`: provenance-aware alpha_s CSV loader and explicit V8 hand-off.
- `JANUS_HYDRA_GEOMETRY.md`: architecture and validation contract.
- `NAHT_QCD_JUNCTIONS.md`: proposed Non-Abelian History Transport (NAHT) design, including three-channel history, SU(2)/SU(3) transport roles, and Y/Delta baryonic network test topologies.
- `naht_topology.py`: Y-Steiner and Delta half-perimeter geometric measures for three-source configurations.
- `naht_su2.py`: unit-quaternion SU(2) composition, inverse, trace, and 2x2 matrix representation.
- `tests/test_naht_topology_su2.py`: deterministic junction-geometry and SU(2) algebra tests.

The QCD layer is a benchmark/reference adapter. It does not equate SU(3)
colour degrees of freedom with V8 coordinates, and it does not infer V8
coordinates from alpha_s. Raw observables and provenance remain explicit.

NAHT is a separate proposed history-transport layer. Its three PAN channels
are not the three QCD colors or the eight SU(3) generators. QCD junction
geometry is used as a comparative network benchmark, not as evidence that
PAN models QCD.

Run tests with `python -m pytest -q tests`.

- `transition_algebra.py`: typed PAN transition operators, append-only event history, versioned UBP fingerprint, and conditional identity/no-reset checks.
- `pan_transition_benchmarks.py`: quasi-star lifecycle integration fixture and reversed-path altermagnetic history-sensitivity proxy.
- `tests/test_transition_algebra.py` and `tests/test_pan_transition_benchmarks.py`: operator-contract, lifecycle, history, and endpoint-null-model tests.

The quasi-star lifecycle uses synthetic normalized V8 coordinates and is a
software integration benchmark, not a stellar-evolution solver. The
altermagnetic path-order benchmark uses an explicitly phenomenological
history-coupling knob; its endpoint-only null model must erase path-order
differences. Neither benchmark establishes a new physical interaction.

## Spectroscopy reference layer

- `spectroscopy.py`: unit-explicit foundational calculations for photon
  energy/frequency/wavelength, spectroscopic wavenumber, Beer-Lambert
  absorbance/transmittance, diatomic reduced mass and harmonic vibrational
  wavenumber, NMR Larmor frequency and chemical shift, hydrogen-like Rydberg
  transitions, and transition-specific Moseley scaling.
- `tests/test_spectroscopy.py`: dimensional/conversion consistency,
  Beer-Lambert round trips, reduced-mass and vibrational checks, proton NMR,
  Balmer-alpha reference, Moseley scaling, and invalid-input coverage.

This layer computes reference observables; it does not force measurements
into V8 coordinates or claim that the Gosset 4_21 geometry predicts spectra.
Instrument metadata, calibration, uncertainty, and raw measured spectra
belong in a later provenance/ingestion adapter. The harmonic oscillator,
Rydberg, and Moseley relations are model/reference equations with stated
domains and approximations, not universal high-precision line solvers.

## Spectral provenance and Janus history

- `spectral_provenance.py`: immutable, schema-versioned spectral observation
  records with raw measurements, explicit unit labels, derived values,
  uncertainty, instrument metadata, calibration, acquisition timestamp, and
  source provenance.
- `SpectralObservation.digest`: deterministic SHA-256 content fingerprint of
  the complete canonical observation. The digest is an index, not a
  replacement for the retained record.
- `SpectralObservation.to_janus_pair()` and
  `append_spectral_janus()`: append paired UHFE/UDFE history events that
  reference the same canonical observation bytes and digest. The channel
  labels distinguish processing paths; they do not alter or negate measured
  data.
- `tests/test_spectral_provenance.py`: raw-data retention, stable content
  identity, paired evidence equality, append-only history, duplicate-event
  rejection, and invalid-record coverage.

Spectral ingestion is deliberately separate from V8 projection. No spectral
quantity is silently assigned to a V8 coordinate. A later, separately
validated adapter may compute explicit features or model projections while
retaining the raw observation and its provenance unchanged.

## Spectral feature bridge

- `spectral_feature_bridge.py`: caller-declared feature extraction from raw
  or derived observation fields using scalar, mean, min, max, or RMS reducers.
- `FeatureSpec` requires an explicit source, key, unit label, and reducer;
  modality names never trigger hidden feature selection.
  Raw-feature unit labels are checked against the observation's declared units.
- `project_features_to_v8()`: opt-in linear mapping into all eight canonical
  V8 coordinates. Every coordinate requires an explicit mapping, with optional
  explicit offsets. No implicit clipping, normalization, or coordinate
  semantics are introduced.
- `V8Projection` retains the observation ID/digest, feature-vector digest,
  and canonical mapping record including feature units.
- `tests/test_spectral_feature_bridge.py`: extraction, reducer behavior,
  mapping reproducibility, unit/mapping provenance, and invalid-input tests.

Feature values retain their declared units. Mapping coefficients therefore
carry the inverse or otherwise appropriate units needed to produce the
intended coordinate scale; the bridge does not perform dimensional analysis
or claim a physically privileged feature-to-V8 mapping. Establishing and
validating domain-specific mappings remains a separate research task.

## Spectral uncertainty propagation

The spectral feature bridge can carry explicitly declared standard
uncertainties from raw observations into extracted features. Sequence reducers
use first-order propagation under an independent-sample assumption; extrema
use the selected sample's uncertainty as a local approximation, and RMS
uncertainty is rejected at the all-zero nondifferentiable point.

Linear V8 projection propagates feature covariance as
`C_V8 = W C_feature W^T`. A supplied covariance matrix must be complete,
symmetric, and positive semidefinite. Its diagonal is checked against any
feature-level standard uncertainties supplied during extraction. If only
individual standard uncertainties are available, the caller must explicitly
opt into an independent-feature assumption; the bridge never silently assumes
zero correlation. The resulting coordinate standard uncertainties and full
coordinate covariance are retained alongside the mapping provenance.

These are first-order uncertainty estimates for a declared linear map, not
automatic confidence intervals or a claim that the chosen V8 mapping is
physically privileged.

## Spectral sensitivity harness

- `spectral_sensitivity.py`: one-factor-at-a-time finite-difference sweeps,
  seeded Gaussian Monte Carlo using a supplied feature covariance or an
  explicitly authorized independent-feature approximation, and forward /
  reverse floating-point accumulation-order checks.
- Reports retain observation, feature-vector, and mapping digests; baseline
  V8 state; perturbation scales; Monte Carlo seed; coordinate means, standard
  deviations, and empirical quantiles; and declared assumptions.
- `tests/test_spectral_sensitivity.py`: analytic linear-map derivatives,
  seeded reproducibility, covariance handling, provenance, and invalid-input
  checks.

The Monte Carlo summaries are empirical summaries of a caller-specified
Gaussian uncertainty model, not automatic confidence intervals or claims
about the physical distribution of measurements. Forward/reverse evaluation
tests numerical accumulation-order sensitivity; it is not a physical
time-reversal test. The bridge remains an explicit model projection, not a
physical law.

## PAN experimental comparison engine

- `pan_experimental_comparison.py`: immutable, content-addressed comparison
  reports for normalized V8 states, extracted spectral feature vectors,
  UHFE/UDFE semantic projections, and already-aligned state trajectories.
- V8 comparisons report signed coordinate deltas and L1, L2, L-infinity,
  RMS, and explicitly weighted L2 distances.
- Spectral comparisons require exact feature-name and unit-label agreement.
  Combined standard uncertainties are computed only when independence of
  the two observations is explicitly authorized; otherwise they remain
  uncomputed rather than assuming zero correlation.
- Janus comparisons keep UHFE and UDFE channel distances separate and report
  changes in each paired head's formation-minus-inverse gap.
- Path comparisons require equal-length, already-aligned trajectories. They
  report per-step distances, maximum and cumulative step divergence, and
  endpoint divergence. No interpolation or resampling is implicit.
- `tests/test_pan_experimental_comparison.py`: metric contracts, uncertainty
  policy, unit mismatch rejection, Janus pairing, aligned paths, provenance
  digests, and invalid-input checks.

These baseline distances are transparent diagnostics over normalized model
coordinates, not universal physical metrics. The Gosset 4_21 / E8 comparison
interface remains intentionally unimplemented pending a separately specified
and validated geometric metric adapter. No Euclidean V8 distance is presented
as an E8 invariant or as evidence of physical correspondence.
