# PAN V8 Janus Phase Integration (experimental)

## What this layer couples

`pan_v8_janus_phase.py` connects the existing Janus semantic reader to the eight-channel phase-lock primitives:

1. Validate and project one canonical V8 state through `read_semantics`.
2. Advance eight phase channels using the caller's monotonic timestamp.
3. Compare those phases with a caller-supplied geometric reference phase.
4. Alternate pulse activation: pulse 0 = UHFE, pulse 1 = UDFE, repeating. UHFE pulse polarity is +1; UDFE pulse polarity is -1.
5. Modulate each active semantic channel by `cos(phase_error)`.
6. Compute a per-channel Fermi diagnostic from the explicit mapping `delta_E_i = UDFE_i - UHFE_i`; hole values are `1 - occupancy`.

## Deliberate boundaries

- Timestamps are supplied by the caller. This module does not read an atomic clock or implement a hardware timing adapter.
- The geometric reference phase is supplied by the caller. The module does not infer a Cauchy hypersurface or solve Einstein's constraints.
- The Fermi values are conventional logistic diagnostics over a declared numerical mapping. They do not establish that UHFE/UDFE are physical fermion seas.
- The 8D cross-polytope and the E8 root system remain distinct geometric objects; this module does not identify them.
- This is an experimental integration layer, not a physical field solver or claim of new physics.

## Validation

Run:

```bash
python -m pytest -q tests
```

The integration tests check alternating UHFE/UDFE pulse order and polarity, phase modulation, bounded/complementary Fermi diagnostics, monotonic timestamps, and failure atomicity (invalid input must not consume a pulse or advance stored time). These are software-contract tests; they are not empirical validation of a physical model.
