# Gosset Projection Engine

**Status:** Experimental view/projection infrastructure. The canonical geometry
remains the Gosset 4_21 polytope, represented by the 240 E8 roots in R^8.

## Separation of source geometry and rendered views

The engine never replaces the source root set with a 4D, 3D, or 2D object.
Every projected vertex retains its canonical root index and original 8D
coordinates. The 6,720 Gosset edges are defined in the original E8 space
(`alpha dot beta = 1`) and exported as root-index pairs. Do not infer new
adjacency from projected screen coordinates: projection can make distinct
vertices overlap or create misleading apparent crossings.

## Projection mathematics

A projection frame is a matrix A whose rows are orthonormal:

`A A^T = I_k`, with `A: R^n -> R^k`.

For row-major point x, the projected point is `y = x A^T`. The canonical
least-squares lift is `x_hat = y A`; the residual
`||x - x_hat||_2` measures discarded information. A projection is marked
lossless for an individual point only when this residual is within tolerance.
A full-rank 8D identity frame is exactly reversible; dimension-reducing
projections are generally lossy. No inverse is claimed where information has
been discarded.

## Default view ladder

The deterministic default chain is:

- 8D: canonical E8/Gosset coordinates (identity)
- 4D: retain coordinates 0..3
- 3D: retain coordinates 0..2 of the 4D view
- 2D: retain coordinates 0..1 of the 3D view

These coordinate views are intentionally simple and reproducible. They are
not claimed to be uniquely privileged by E8 symmetry or to be the most
informative visual orientation. Arbitrary orthonormal frames can be supplied
for rotated views. Future work can add named Weyl-aligned, PCA, or optimized
view frames without changing canonical source coordinates.

## Semantic and identity boundaries

- V8 channel order remains `(h, R, u, d, tau, chi, s, f)`.
- Eight V8 channels are not the 240 E8 roots and are not projection axes.
- Projection metadata does not mutate V8State, UHFE/UDFE head values, or
  paired semantic records.
- Root identity and E8 adjacency remain attached to the source-space data.
- The 8D cross-polytope remains a separate comparison geometry, not the
  source for this projection engine.

## Validation

Run `python -m pytest -q tests/test_gosset_projection.py`.

Tests cover frame orthonormality, coordinate and rotated projections,
reconstruction error, lossless identity transforms, the 8D->4D->3D->2D
ladder, root identity, canonical adjacency indexing, and stable V8 labels.
Passing tests validates this software transform contract, not a physical
interpretation of E8 or PAN V8.

See `VIEW_LADDER_SCHEMA.md` for the schema that unifies this ladder with the seeded 3D view and
adds finite 5_21 / affine-E8 patches.
