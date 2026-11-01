# PAN V8 Dynamic Phase-Locking Layer (experimental)

Status: **experimental scaffold; not merged into the physical runtime**.

## Purpose

This branch adds a small, dependency-light numerical contract for the next PAN V8 milestone:

- the canonical eight-coordinate state `(h, R, u, d, tau, chi, s, f)`;
- eight phase channels advanced using externally supplied timestamps;
- phase errors relative to a selected geometric reference phase and per-channel offsets;
- explicit rotation in a selected 2D plane of an 8D coordinate representation;
- the 16 signed unit vertices of the 8D cross-polytope (hyperoctahedron);
- separate positive-`phi` and negative-`1/phi` scaling branches;
- bounded Fermi occupation and complementary hole occupancy;
- an Abazith glyph/audio metadata interface for later measured-acoustic integration.

## Clock and temporal semantics

The module does **not** read an atomic clock. A caller supplies monotonic timestamps, allowing a future clock adapter to be tested independently. Phase advancement uses
`phase_next = wrap(phase_now + omega * (t_next - t_now))`.

A 90-degree rotation is represented by an explicit `angle=pi/2` supplied to `rotate_8d_plane`; it is not assumed to occur at every clock tick. The rotation plane must be specified. Phase offsets are likewise explicit per channel.

A saved `V8State` plus timestamp can be treated as initial data on a computational time slice. This is **not** a claim to construct a general-relativistic Cauchy hypersurface or solve Einstein's constraint equations; that requires a spacetime metric, induced spatial metric, extrinsic curvature, constraints, and boundary/gauge choices.

## Geometry and E8 distinction

The 8D hyperoctahedron/cross-polytope has vertices `±e_i`, hence 16 vertices. It is not the E8 root system. E8 has 240 roots; any future coupling must be represented as a separate, explicit transformation or projection with its own tests.

## Fermi and golden-ratio semantics

For energy units with `k_B = 1`, the module implements the Fermi-Dirac occupation
`n(E) = 1 / (exp((E-mu)/T) + 1)`, with a stable logistic evaluation and a zero-temperature limit. Hole occupancy is defined as `1 - n(E)`. This is a conventional occupancy complement, not proof that UHFE/UDFE are physical fermion seas.

The golden branches are `phi*x` and `-(x/phi)`. The second is a sign-reversed reciprocal scaling, **not** the algebraic inverse of the first.

## Abazith interface

`AbazithGlyph` stores element/register/glyph identifiers, optional pronunciation and documented meaning, and optional measured acoustic features. It deliberately does not assign frequencies or physical meanings to glyphs by assumption. Future work should load source metadata and real recordings, then test acoustic features independently before any V8 calibration.

## Validation

Run:

```bash
python -m pytest -q tests/test_pan_v8_phase_lock.py
```

The tests check state shape and finite values, monotonic timestamp handling, phase wrapping, rotation norm preservation, cross-polytope vertex count, golden-branch definitions, Fermi bounds/complementarity, and glyph metadata validation.

These are software-contract tests. They do not establish new physics or demonstrate that the proposed layers are physically coupled.
