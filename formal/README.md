# PAN Formalization (Lean 4)

This package begins the machine-checked mathematical schema for PAN. It is isolated from the Python numerical engine.

## First contract

`PAN.V8.Coordinates` defines the canonical coordinate order `(h, R, u, d, tau, chi, s, f)`. The serializer emits exactly that order. `tau` is the temporal (temporal-offset) coordinate; persistence is not that coordinate. The older provisional alias `T` is retained for input compatibility only and is not a schema change.

## Evidence discipline

- **Formal theorem:** a proposition checked by Lean.
- **Computational test:** a numerical/property test run by the Python engine.
- **Research hypothesis:** an interpretation or correspondence still requiring evidence.

No experimental observation is introduced as an axiom. Mathlib will be pinned with the Lean toolchain before advanced algebraic formalization.

## ABOM modules

- `PAN.ABOM.Flux`: `4ab + (a-b)^2 = (a+b)^2` over `Int`, so the two-state flux `N(1-N) = (1-delta^2)/4` is at most `1/4`, with equality exactly when `a = b`.
- `PAN.ABOM.MengerVolume`: cell counts `8, 20, 48` for `d = 2, 3, 4`, the volume numerator/denominator `20^n / 27^n`, and `volume <= 1`.
- `PAN.ABOM.MicrotubuleLattice`: the helix index `3*di + 13*dk`, seam invariance, `v3+v5=v8` modulo the seam, `v5+v8=v13`, odd-start type flip across the seam, and axial wrap.

These are statements about integer arithmetic. They do not establish any physical or biological interpretation; those are recorded separately in `abom_v8/strata.py` (`ABOM-V8-MT-COLLECTIVE-COUPLING-001` is `analogy`, every dimension `not_tested`). `tests/test_abom_v8_strata_records.py` checks that the Lean files declare the theorems the records cite and contain no `sorry`, `axiom` or `native_decide`.

`PAN.lean` is the library root, so `lake build` compiles every module imported from `PAN.V8.Coordinates` and `PAN.ABOM`.

