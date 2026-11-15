# PAN Formalization (Lean 4)

This package begins the machine-checked mathematical schema for PAN. It is isolated from the Python numerical engine.

## First contract

`PAN.V8.Coordinates` defines the canonical coordinate order `(h, R, u, d, tau, chi, s, f)`. The serializer emits exactly that order. `tau` remains persistence; it is not silently renamed to `T`.

## Evidence discipline

- **Formal theorem:** a proposition checked by Lean.
- **Computational test:** a numerical/property test run by the Python engine.
- **Research hypothesis:** an interpretation or correspondence still requiring evidence.

No experimental observation is introduced as an axiom. Mathlib will be pinned with the Lean toolchain before advanced algebraic formalization.
