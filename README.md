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
