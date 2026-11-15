# Integration adapters

ABOM-V8 does not vendor the Fractal Kernel or PANoRAMic.os.

## Fractal Kernel adapter

The kernel owns mathematical primitives and geometry engines. An ABOM adapter should consume stable kernel APIs and return versioned references/provenance. The built-in plug-ins expose Gerono/Bernoulli curves, Fermi occupancy, Cartesian field diagnostics, μ-cube state, V8 trajectory navigation, golden-ratio scaling, radial-shell visualization, Menger mu-cube volume/flux identities and the 13_3 microtubule lattice. The Menger adapter lazily wraps the existing `menger_sponge.py` functions for finite cells, face adjacency and audit output. It returns the kernel's cell/adjacency objects and audit metadata without copying the engine. Gosset/E8 adapter wiring remains an interface boundary pending a stable, tested API.

Candidate capabilities:
- Menger retained-cell graph and its explicitly named graph operators;
- Gosset (4_{21})/E8-associated exact incidence and local-star audit outputs;
- other independently validated kernel primitives.

Do not conflate cubic-grid Menger variants with Gosset (4_{21}) or the E8 root system.

## PANoRAMic.os adapter

PAN is the application/navigation layer. It may use ABOM-V8 state and route abstractions to navigate data, snapshots and views. It should not mutate canonical kernel records or duplicate geometric engines.

## Compatibility rule

Each adapter publishes supported ABOM-V8 schema versions and dependency versions. Integration occurs after contract tests pass; consumers must honor `tau` as the normalized temporal-offset coordinate.