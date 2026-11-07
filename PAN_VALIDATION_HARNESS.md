# PAN Validation Harness

**Status:** Initial unified validation contract. This document separates implemented checks from planned validation work.

The harness is an open-source software-validation system for the PAN V8 research kernel. It validates implementation behavior against explicit mathematical, geometric, numerical, interface, and reference-data contracts. A passing suite is not evidence that PAN V8 is a physical theory or that an observational proxy is a direct measurement of a V8 coordinate.

## Validation layers

| Layer | Scope | Primary evidence |
|---|---|---|
| L0 — Static/import | Python syntax, imports, dependency boundaries | CI collection and import checks |
| L1 — Unit mathematics | V8 normalization, complement involution, phase and Fermi functions, SU(2) algebra, QCD reference equations | Deterministic unit tests |
| L2 — Geometry | E8 root count/norm, Gosset adjacency, Weyl reflections, projections, radial boundaries | Exact invariants and numerical tolerances |
| L3 — Semantic architecture | UHFE/UDFE head vocabulary, inverse pairing, eight-channel projections, canonical reader | Semantic contract tests |
| L4 — Coupled dynamics | Janus alternating pulses, phase lock, JOBF evolution, finite positive radial boundary | State-transition and integration tests |
| L5 — Data adapters | Gaia/GRMHD/QCD input schemas, calibration declarations, units, provenance, missing-data behavior | Offline fixtures plus opt-in live-data checks |
| L6 — System integration | Geometry swap isolation, reader-to-JOBF path, projection identity, SU(2) transport composition | Cross-subsystem tests |
| L7 — Robustness/performance | Seeded randomized inputs, boundary cases, regression envelopes, runtime/memory benchmarks | Reproducible stress and benchmark jobs |

## Existing suite map

Run all currently implemented tests:

```bash
python -m pytest -q tests
```

- `tests/test_pan_v8_phase_lock.py`: phase, Fermi occupancy, golden-ratio branches, 8D plane rotation, metadata validation.
- `tests/test_pan_v8_janus_phase.py`: alternating UHFE/UDFE pulses, phase alignment, occupancy/hole complements, transactional state updates.
- `tests/test_jobf_v0_2.py`: V8 validation, semantic reader, head pairing, geometry adapters, JOBF boundary.
- `tests/test_gosset_421.py`: 240 E8 roots, root norm, 56 neighbors, 6,720 edges, Weyl reflections, support/radial reference checks.
- `tests/test_gosset_projection.py`: 8D-to-lower-dimensional projection, reconstruction error, source-index identity, canonical adjacency.
- `tests/test_naht_topology_su2.py`: Y/Delta junction geometry and SU(2) quaternion/matrix representation.
- `tests/test_qcd_benchmark.py`: one-loop QCD reference equations, CSV provenance, explicit calibration-gated V8 handoff.
- `tests/test_system_integration.py`: reader-to-JOBF path, geometry isolation, Gosset projection identity, deterministic ingestion bridge, robust scaling, SU(2) transport composition.

## Evidence labels

Every result should be reported under one of these labels:

1. **PASS — exact invariant:** exact count, identity, schema, or algebraic property.
2. **PASS — numerical tolerance:** floating-point result within a declared tolerance.
3. **PASS — reference agreement:** comparison against a named external/analytic reference with version, units, and uncertainty.
4. **PASS — software integration:** modules exchange valid data and preserve interface contracts.
5. **EXPLORATORY — behavior observed:** a simulation or visualization behaved as configured; no physical inference follows.
6. **NOT RUN / BLOCKED:** unavailable dependency, external data, hardware, or benchmark environment.
7. **FAIL:** reproducible contract violation, including test name, seed, inputs, expected result, observed result, and commit.

Never collapse these categories into one generic “validated” claim.

## Reproducibility requirements

- Record commit SHA, Python version, dependency versions, operating system, test command, random seed, and elapsed time for benchmark runs.
- Keep deterministic unit and integration tests offline. Live Gaia, GRMHD, and external QCD data retrieval belongs in separately marked opt-in jobs with cached fixtures and source provenance.
- Use fixed seeds in CI. Stress jobs may use rotating seeds, but must print and persist the failing seed.
- Numerical tolerances must be explicit and justified by the algorithm; do not loosen a tolerance solely to make a failing test green.
- Keep raw observations, calibrated proxies, and derived V8/JOBF outputs in separate fields. Never overwrite source measurements with normalized coordinates.
- Preserve failure history. A fix is not complete until the corrected commit has a green run and the test reproducing the prior failure remains in the suite.

## Planned expansions

The following are harness work items, not claims that they are already implemented:

- Property-based testing for valid/invalid V8 states and SU(2) composition.
- Randomized orthant and forward/backward evolution tests with deterministic seed capture.
- Cauchy-data contracts and explicit initial/boundary-condition fixtures.
- Time-reversal and reversible-step checks where the underlying operator is mathematically reversible; label dissipative steps separately.
- NAHT three-channel transport fixtures and later SU(3) adapter contract tests, keeping SU(2), SU(3), QCD color, and V8 channels distinct.
- QCD reference tables with threshold/matching conventions and uncertainty propagation.
- Gaia/GRMHD offline golden fixtures, calibration versioning, unit checks, and provenance assertions.
- Warp/GRMHD/black-hole and other exploratory cases only where a defined reference solution or measurable invariant exists; otherwise classify as exploratory.
- Performance baselines for Gosset facet construction, vectorized ray intersections, JOBF throughput, and memory use.

## Interpretation boundary

The Gosset 4_21 / E8 root polytope remains the primary geometric target. The 8D cross-polytope is a comparison adapter, not a substitute. The harness must enforce that JOBF always uses Gosset 4_21 as its production radial boundary. The H8 cross-polytope may be evaluated independently for comparison, but it cannot be injected as a JOBF boundary. Tests also verify that H8 comparison calculations do not mutate V8 state or UHFE/UDFE semantic records.

Physics and geometry are complementary but not interchangeable: geometric structure, physical dynamics, numerical implementation, and empirical calibration require separate validation paths.
