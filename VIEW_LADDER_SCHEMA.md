# View-ladder schema (`view-ladder-v1`) and the 5_21 / affine-E8 ("E9") ladder

A **view ladder** is an ordered set of orthonormal views of one source point set, from the full
8D space down to 4D, 3D and 2D. It merges two things that existed separately: the 8D→4D→3D→2D
chain in `gosset_projection.py` and the seeded 3D view in `gosset_3d_simulation.py`.

## Schema

`ViewLadder.to_schema()` returns a JSON document (`validate_schema` checks it):

- `source`: geometry name, ambient dimension, point count, `id_kind`, `ids_sha256`, notes.
- `stages[]` (strictly decreasing dimension): `frame_matrix` (k×N, orthonormal, **taken from the source
  space**), `nested_in_previous`, `max_residual_vs_source`, `rms_residual_vs_source`,
  `energy_retained_fraction`, `lossless`.
- `schema_sha256` over the rest of the document.

Residuals are measured against the original 8D points, never against the previous stage. Non-nested
frames are allowed but flagged, not hidden. Source coordinates and ids are never mutated.

## Ladders provided

| Builder | Source | 3D stage |
|---|---|---|
| `gosset_coordinate_ladder()` | 240 E8 roots | leading coordinates (identical to `project_gosset_chain`) |
| `gosset_seeded_ladder(seed)` | 240 E8 roots | the seeded view used by `gosset_3d_simulation` (same RNG recipe; pinned by a test); 2D = its first 2 rows; 4D and 8D extend it by seeded Gram-Schmidt |
| `five21_neighborhood.five21_ladder(max_shell, kind, seed)` | finite patch of the 5_21 vertex set (E8 lattice): origin + Euclidean shells | same two kinds as above |

`gosset_3d_simulation` metadata now embeds the seeded ladder as `view_ladder`.

## 5_21 / "E9"

"E9" here means **affine E8** (E8^(1)), the Coxeter group [3^{5,2,1}] of the 5_21 honeycomb, whose
vertex set is the E8 lattice and whose vertex figure is the Gosset 4_21. It is not the hyperbolic E10.
`five21_neighborhood.py` works in doubled integer coordinates (v = 2x) so half-integers are exact:

- lattice membership, 240 neighbours, Euclidean shells n ≤ 3 (sizes 1, 240, 2160, 6720 = E8 theta series);
- affine reflections `x → x − (x·α − k)α`, exact, verified as lattice-preserving involutions
  (k = 0 is the finite Weyl group; k = 1 sends the origin to α).

## What this does not claim

- The honeycomb is infinite; a patch is a finite sample. Nothing here describes global cell/facet incidence.
- Views are display transforms. The coordinate choices are conventions, not privileged by E8 symmetry.
- Because the 240 roots form a spherical 7-design, **any** k-frame retains exactly k/8 of their energy
  (tested). So `energy_retained_fraction` is the same for every view of the roots and does **not** rank
  views; use `max_residual_vs_source` per point or a task-specific metric to compare them. For a
  patch that includes more shells this isotropy need not hold per frame.
- The V8 channels (h,R,u,d,τ,χ,s,f) are not view axes and are untouched.
