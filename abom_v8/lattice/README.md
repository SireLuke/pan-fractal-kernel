# Microtubule 13_3 lattice geometry

`MicrotubuleLattice` is pure lattice arithmetic for the 13-protofilament, 3-start
B-lattice. It makes no physical, biological or quantum claim, and nothing here is
evidence for any hypothesis.

## Model

Sites are integer pairs `(i, k)`: protofilament index `i` (angle `2*pi*i/13`) and
monomer index `k`. Axial position is `z = monomer_nm * (k + start*i/13)`.
Going once around the cylinder (`i -> i + 13`) lands on the same site as
`k -> k + start`, so the lattice is `Z^2` modulo the seam vector `(13, -3)`.

| Quantity | Value (nominal parameters) |
| --- | --- |
| Rise of the 3-start helix per turn | `3 * 4.0 nm = 12.0 nm` |
| Axial offset between neighbouring protofilaments | `12/13 nm ~ 0.923 nm` |
| Seam stagger | `1.5` dimer repeats (`3` is odd, so alpha meets beta) |
| Pitch angle at the nominal 10 nm centreline radius | `~10.8 deg` |

Nominal values (monomer 4.0 nm, dimer 8.0 nm, radius 10.0 nm) are literature-typical
parameters, not measurements made here. Override them on construction.

## Helix families

A step `(di, dk)` generates a family with start number `S = |3*di + 13*dk|`.
Canonical (shortest-lateral) vectors:

| S | step | relative handedness |
| --- | --- | --- |
| 3 | `(1, 0)` | `+1` (reference) |
| 5 | `(6, -1)` | `+1` |
| 8 | `(-6, 2)` | `-1` |
| 13 | `(0, 1)` | `0` (straight) |

`v3 + v5 = v8` (modulo the seam vector) and `v5 + v8 = v13` hold exactly, and
3, 5, 8, 13 are consecutive Fibonacci numbers. That is an identity of these
integers (`13 = 5 + 8`, `8 = 5 + 3`). The 5- and 8-start helices are long paths,
not nearest-neighbour bonds, so the pattern is not a structural claim about
tubulin. Handedness flips with the representative chosen modulo the seam vector
(`(7, -1)` and `(-6, 2)` are the same family), so any handedness label needs a
stated convention. `canonical_helix` fixes one.

## Not included

Subunit coordinates from a structure file, dipole couplings and any
superradiance rate are not modelled here. See
`../experiments/brainstorm_figures.md` for why.
