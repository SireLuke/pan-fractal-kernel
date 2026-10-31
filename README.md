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

The QCD layer is a benchmark/reference adapter. It does not equate SU(3)
colour degrees of freedom with V8 coordinates, and it does not infer V8
coordinates from alpha_s. Raw observables and provenance remain explicit.

Run tests with `python -m pytest -q tests`.
