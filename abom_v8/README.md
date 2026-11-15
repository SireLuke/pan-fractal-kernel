# ABOM-V8 (experimental package, v0.1)

ABOM-V8 is a modular manifold/navigation layer. It is deliberately separate from the Fractal Kernel's mathematical primitives and from PANoRAMic.os application orchestration.

## Design boundary

- **Fractal Kernel** owns reusable mathematics and geometry (for example finite Menger graph construction and independently audited mathematical engines).
- **ABOM-V8** owns the V8 state contract, manifold adapters, coordinate-aware navigation, and plug-in interfaces.
- **PANoRAMic.os** consumes ABOM-V8 through adapters; it does not own or duplicate the kernel's mathematical implementations.
- **Transport curves and differential diagnostics** are replaceable plug-ins. Gerono is the initial lemniscatic transport experiment, not a universal choice.
- This package is experimental and has no production wiring or physical-validation claim.

## Canonical V8 coordinates

The ordered coordinate contract is:

`(h, R, u, d, tau, chi, s, f)`

The package preserves the established ordering and labels. It does not reinterpret coordinates. The package matches the kernel's current contract: `tau` is the temporal offset and provisional `T` maps to `tau`. See [COORDINATE_CONTRACT.md](COORDINATE_CONTRACT.md).

## Modules

- `schema/`: versioned V8 state and μ-cube contracts.
- `strata.py` and `STRATA_PLAN.md`: evidence records aligned to the authoritative PANoRAMic.os STRATA protocol; untested dimensions remain explicit.
- `formal/` at repository root: Lean 4 contracts for exact finite state and occupancy properties.
- `state.py` and `mu_cube.py`: normalized V8 vectors and recursive state containers with occupancy, entropy, resonance, scale, links and parent identity.
- `trajectory.py`: immutable past/current/future snapshot navigation.
- `harmonics.py`: φ-power shells and dimensionless logarithmic scale ratios.
- `transport/`: curve protocol and parameterized Gerono, Bernoulli and other candidate families.
- `diagnostics/`: optional scalar/vector differential-operator interface.
- `occupancy/`: Fermi-Dirac occupancy and binary entropy helpers.
- `adapters/`: version-aware plug-in registry plus built-in curve, occupancy, field-diagnostic, μ-cube, trajectory, golden-scale, radial-shell and lazy Menger adapters; PAN navigation remains an adapter boundary.
- `experiments/`: isolated visual/geometry/occupancy experiments.

Each layer may be used independently. Importing the base state/navigation API does not load the Menger graph engine or impose a geometry backend; Fermi geometry and Menger adjacency are loaded only when their optional adapters/helpers are used.

## Principles

1. Explicit schemas and versioned adapters; no silent coordinate migration.
2. Optional capabilities with declared interfaces and capability discovery.
3. Pure mathematical functions where possible; deterministic tests.
4. Experimental comparisons remain separate from production wiring.
5. Occupancy conservation, curve continuity and topology claims require tests.
6. Binary entropy maximum at occupancy 1/2 is not, by itself, proof of maximum graph connectivity or accessibility.

## Status

The first implementation pass includes typed V8 and μ-cube state contracts, past/current/future snapshot navigation, built-in plug-ins, Fermi/entropy helpers, Gerono and Bernoulli curve samplers, dimensionless φ scaling, 3D Cartesian field diagnostics, a Menger graph adapter, a radial-shell visualization generator, and dedicated unit tests. CI is pending. PANoRAMic.os production wiring, Gosset/E8 adapter integration, graph-generalized differential operators and physical transport dynamics remain future milestones.