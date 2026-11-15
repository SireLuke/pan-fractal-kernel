# PAN Fractal Kernel

An open computational research kernel for the PAN V8 coordinate model.

## Quick start

Requires Python 3.11+ (CI uses 3.11; also run on 3.13). Pure Python on NumPy, SciPy and matplotlib, with no GPU or compiled code of its own. Only Linux is exercised in CI.

```bash
git clone https://github.com/SireLuke/pan-fractal-kernel
cd pan-fractal-kernel
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
python -m pip install -r requirements-dev.txt       # runtime only: requirements.txt
python -m pytest -q tests                           # about 2 min
```

Smoke test, run from the repository root:

```python
from hydra_semantic_reader import read_semantics
from view_ladder import gosset_seeded_ladder, validate_schema

# V8 order: h, R, u, d, tau, chi, s, f -- every value normalized to [0, 1]
frame = read_semantics([0.5, 0.5, 0.5, 0.5, 0.5, 0.0, 0.5, 0.5])
print(frame.uhfe_heads, frame.udfe_heads)

ladder = gosset_seeded_ladder()          # 8D -> 4D -> 3D -> 2D views of the 240 E8 roots
validate_schema(ladder.to_schema())
```

V8 coordinates: `h` coherence, `R` recursion, `u` construction, `d` decoherence,
`tau` temporal offset, `chi` chirality, `s` information density, `f` forcing. The
provisional input alias `T` maps to `tau`; persistence is not the `tau` coordinate.

Modules live at the repository root and import each other by name, so run scripts and
tests from the root. Longer suites are run directly: `python lattice_gauge/tests/test_lattice_gauge.py`
(about 2.5 min). Each experiment has a `run_*.py` entry point and a matching CI workflow in
`.github/workflows/`, which is the reference for exact arguments.

## Module map

Everything below is a software result unless a document says otherwise; see the evidence
notes in each layer's own document.

| Layer | Modules | Documents |
|---|---|---|
| V8 core and Janus Hydra | `janus_hydra`, `hydra_semantic_reader`, `janus_metrics`, `jobf_v0_2`, `geometry_adapter`, `cauchy_janus`, `feynman_barbershop` | `JANUS_HYDRA_GEOMETRY.md`, `docs/FEYNMAN_BARBERSHOP_V8.md` |
| Phase layers (experimental) | `pan_v8_phase_lock`, `pan_v8_janus_phase`, `fermi_sea`, `fermi_yinyang` | `PAN_V8_DYNAMIC_PHASE_LAYER.md`, `PAN_V8_JANUS_PHASE_INTEGRATION.md` |
| Gosset 4_21 / E8 geometry | `gosset_421`, `gosset_projection`, `menger_sponge`, `gosset_3d_simulation`, `gosset_local_star`, `gosset_global_4cliques`, `e8_bounded_symmetry`, `du_val_e8`, `kac_moody_en` | `GOSSET_421_GEOMETRY.md`, `GOSSET_PROJECTION_ENGINE.md`, `MENGER_SPONGE.md`, `DEEP_GEOMETRY_EXPERIMENTS_2026-11-09.md` |
| 5_21 / affine E8 and view ladders | `five21_neighborhood`, `five21_star`, `view_ladder`, `v9_affine_e8_projection`, `pan_geometric_depth` | `VIEW_LADDER_SCHEMA.md`, `FIVE21_NEIGHBORHOOD_EXPERIMENT.md`, `PAN_V9_AFFINE_E8_EXPERIMENT.md`, `PAN_GEOMETRIC_DEPTH_ENGINE.md`, `M_THEORY_11D_5_21_INTEGRATION.md`, `M_THEORY_11D_5_21_EXPERIMENT_REPORT.md` |
| Hydrogen on shell views | `hydrogen_shell_modes`, `hydrogen_shell_scale`, `hydrogen_node_recovery`, `run_hydrogen_*_experiment` | `HYDROGEN_SHELL_MODES.md`, `HYDROGEN_SHELL_SCALE_RULE.md`, `HYDROGEN_NODE_RECOVERY.md` |
| Lattice gauge and QCD benchmarks | `lattice_gauge/`, `yang_mills_v8_gosset`, `run_yang_mills_v8_gosset`, `run_wilson_flow_sector_scan`, `qcd_reference`, `qcd_ingest` | `lattice_gauge/README.md`, `QCD_BENCHMARK.md`, `NAHT_QCD_JUNCTIONS.md` |
| History and transitions | `transition_algebra`, `pan_transition_benchmarks`, `naht_topology`, `naht_su2` | `NAHT_QCD_JUNCTIONS.md` |
| Observational ingestion | `ingest_gaia_v8`, `ingest_grmhd_v8`, `v8_ingest_common`, `spectroscopy`, `spectral_provenance`, `spectral_feature_bridge`, `spectral_sensitivity` | `DATA_INGESTION.md` |
| Comparison and validation | `pan_experimental_comparison`, `pan_sandbox_metrics`, `tests/`, `formal/` (Lean 4) | `PAN_VALIDATION_HARNESS.md`, `formal/README.md` |

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


## Lightly weighted sandbox comparison diagnostics

- `pan_sandbox_metrics.py` provides an optional secondary evidence layer for
  selected PAN sandbox outputs. Metrics are compared only when their names,
  units, direction, protocol ID, evidence class, role, and declared weight
  match exactly.
- Synthetic exploratory results receive an evidence factor of 0.25;
  software/numerical checks 0.50; and reference comparisons 0.75. These are
  conservative engineering policy weights, not empirically fitted
  probabilities or scientific confidence levels.
- Relative metric differences are bounded to [-1, 1] before aggregation so
  raw units or large magnitudes cannot dominate. Context-only diagnostics
  (including backward amplification, dissipative contraction, historical
  replay failures, and configured Fermi filling) are retained but excluded
  from the score.
- `blend_primary_and_sandbox_score()` caps the secondary contribution at
  10%; the default is 10%, leaving at least 90% of the blend to the caller's
  primary score. The helper requires both scores to be on a declared [0, 1]
  higher-is-better scale.
- `historical_sandbox_reference_profile()` records selected historical
  sandbox figures with protocol labels and provenance notes. They are not
  treated as fresh observations or automatically comparable with a new run.
- `tests/test_pan_sandbox_metrics.py` covers contract matching, evidence
  weighting, context-only exclusions, score cap, and provenance digests.

This layer is optional and cannot override primary experimental evidence,
exact validation gates, or external reference agreement. A green software
test remains a software result, not empirical validation of a physical claim.

## ABOM-V8 modular manifold/navigation layer (experimental)

- `abom_v8/` contains separately versioned V8 and μ-cube state contracts,
  past/current/future trajectory navigation, a version-aware plug-in registry,
  built-in Gerono/Bernoulli/Fermi/Cartesian/Menger/scale/radial adapters,
  configurable transport curves, dimensionless φ scaling and field diagnostics,
  exact Menger μ-cube volume/flux identities and a combinatorial 13_3
  microtubule lattice geometry (pure arithmetic, no physical claims).
- The canonical coordinate order is `(h, R, u, d, tau, chi, s, f)`, normalized
  to `[0, 1]`; `tau` is the temporal-offset coordinate and provisional `T`
  maps to `tau`.
- ABOM-V8 reuses the kernel's existing `fermi_yinyang.py` geometry rather than
  forking it. Kernel mathematical engines remain kernel-owned; ABOM adapters
  expose plug-in boundaries rather than duplicating those implementations.
- Cartesian gradient/divergence/curl/Laplacian routines apply only to smooth
  fields on a uniform 3D Cartesian grid. They are not Menger graph, Gosset,
  or general 8D manifold operators.
- Gerono is the initial configurable lemniscate candidate. Bernoulli is
  implemented as a comparison candidate; neither is asserted as the final
  transport geometry. The radial shell generator is visualization-only and
  is not an E8 or quasicrystal construction.
- Tests: `tests/test_abom_v8_*.py`. This package is an experimental software
  layer, not a physical-validation claim and not yet wired into PANoRAMic.os.

Project attribution: Lucas Thouvenell (`@SireLuke`).

## License

Licensed under the Apache License, Version 2.0. See `LICENSE` and `NOTICE`.
