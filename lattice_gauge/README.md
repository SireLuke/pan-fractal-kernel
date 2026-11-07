# lattice_gauge: SU(2)/SU(3) Wilson lattice gauge toy, any dimension

Periodic hypercubic lattice, Wilson action, checkerboard Metropolis, NumPy only (+SciPy for Bessel references).
Run `python tests/test_lattice_gauge.py` (about 2.5 min) and `python tests/test_core_independence.py`.

## What is checked (all pass)
- group closure, local dS = full dS in 3D, gauge invariance (loops yes, single links no), hot/cold agreement
- 2D periodic exact: SU(2) I2/I1; SU(3) via Weyl integration (my own numerics); Creutz ratio = -ln(u)
- 4D SU(3) strong coupling vs the published series (arXiv:1408.2960): plaquette within errors at beta=0.5, 1.0, 1.5
- 4D SU(2) strong-coupling leading term; weak-coupling equipartition 1-P -> (N^2-1)/(d beta) within 10%

## Production runs (8^4 / 12^3; 200 therm + 400 meas sweeps; production_results.json)
SU(3) 4D beta=6.0: P = 0.5937 +/- 0.0005. Recalled literature value is about 0.594; NOT verified against a fetched source.
No published SU(2) 4D numbers were sourced; those points are sanity-checked only against the limits above.

## Limits
Toy model. 20-bin blocking errors, autocorrelation not estimated, single volume (no finite-size or continuum extrapolation),
strong-coupling series is truncated and only meaningful at small beta. Not a physical-QCD claim. See GATES.md.
