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
