# PAN V8 Fractal Kernel — observational and GRMHD ingestion

The data adapters now **feed source-derived V8 proxy vectors into JOBF**, rather than merely running JOBF independently of the source data.

## Gaia DR3 ingestion

```bash
python -m pip install numpy matplotlib
python ingest_gaia_v8.py --rows 256 --output gaia_v8_jobf_test.csv
```

The script queries the ESA Gaia Archive TAP service and retains source IDs and raw observables in the output. It maps RUWE, parallax S/N, proper motion, astrometric excess noise, scan count, proper-motion angle, and flux S/N into the ordered V8 vector. These are explicitly provisional engineering proxies, not direct measurements of the conceptual V8 coordinates.

## GRMHD ingestion

```bash
python -m pip install numpy matplotlib h5py
python ingest_grmhd_v8.py --max-cells 50000 --output grmhd_v8_jobf_test.csv
```

By default this downloads one public HARM-format snapshot from the Illinois v3 GRMHD library: SANE, dimensionless spin a*=+0.5, 288x128x128. The dump is roughly 144 MB and remains local; do not commit the raw binary to Git. Use --input for another compatible dump and --primitive-key if its 4D primitive dataset is not auto-detected.

The adapter expects the conventional HARM primitive ordering (rho, uu, u1, u2, u3, B1, B2, B3). It samples cells and retains primitive values alongside their V8 proxies. This first pass uses one snapshot, so tau is explicitly neutral (0.5); a time-series extension should ingest multiple ordered snapshots and derive temporal persistence from actual inter-snapshot change.

## V8-to-JOBF coupling

Each source row/cell becomes a normalized vector in canonical order:

`(h, R, u, d, tau, chi, s, f)`.

The adapter injects that vector into the JOBF v0.2 engine, disables synthetic V8 oscillation for that input state, recomputes UHFE/UDFE head baselines from the input, and records the breathing boundary and interference diagnostics. The UHFE and UDFE remain distinct fields over the same complete 8D cross-polytope.

## Important scientific boundary

These pipelines are integration experiments. Gaia measurements and GRMHD primitive variables are not semantically identical, and their proxy mappings are not validated physical definitions of V8. Keep Gaia and GRMHD outputs in separate files and compare them only after calibration and explicit unit/feature documentation. A successful positive-boundary check validates a numerical invariant, not a physical theory.

## Data provenance

- Gaia DR3: ESA Gaia Archive TAP, table `gaiadr3.gaia_source`.
- GRMHD: Illinois Simulation Data Products, v3 ideal GRMHD simulation library. The selected sample is one SANE model at a*=+0.5; the broader release spans MAD/SANE and five black-hole spins.
- The GRMHD dump is retrieved on demand, not stored in this repository.

References:
- https://gea.esac.esa.int/archive/documentation/
- https://thz.astro.illinois.edu/v3_grmhd.html
- https://doi.org/10.3847/1538-4365/adaea6
