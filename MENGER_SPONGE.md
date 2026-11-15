# Menger sponge in d dimensions: exact audit and spectral dimension

`menger_sponge.py` builds finite-level d-dimensional Menger sponges as face-adjacency graphs on the integer grid
`{0, ..., 3^k - 1}^d`. A cell is kept when, at every base-3 digit position, at most one coordinate has digit 1.
Each subdivision keeps `N_d = 2^d + d*2^(d-1)` of the `3^d` sub-cells, so d = 2 is the Sierpinski carpet and d = 3 the
Menger sponge. This is a finite-graph computation. It makes no physical claim and no claim about the V8 manifold.

## Exact results (all asserted in `tests/test_menger_sponge.py`)

| d | cells kept per level | similarity dimension ln(N_d)/ln 3 |
|---|---|---|
| 2 (carpet) | 8 of 9 | 1.8928 |
| 3 (Menger) | 20 of 27 | 2.7268 |
| 4 | 48 of 81 | 3.5237 |
| 8 | 1280 of 6561 | 6.5124 |
| 10 | 6144 of 59049 | 7.9402 |

- Cell counts equal `N_d^level` exactly; the graph is connected; occupied-box counts at every scale equal
  `N_d^(level-j)`, so the box-counting slope reproduces the similarity dimension to 1e-9.
- Level 1, d = 3 matches a hand count: 20 cells, 24 edges, 12 cells of degree 2 and 8 of degree 3. Level 1, d = 2 is an
  8-cycle.

## Spectral dimension (an estimate, not an exact result)

`spectral_dimension` fits `p_t(x,x) ~ t^(-d_s/2)` for the lazy random walk on the graph, averaged over random start
cells. It depends on the fit window and is valid only while the walk has not yet saturated on the finite graph.

**Validation:** on the Sierpinski gasket (exact `d_s = 2 ln3 / ln5 = 1.3652`, same graph construction as the stage
audit in PANoRAMic.os `experiments/moonshine_sierpinski`) the estimator gives 1.34 to 1.38 at stage 8, inside
the tolerance asserted in the tests.

**Results, run once (not asserted except the carpet):**

| Graph | cells | d_s estimate | note |
|---|---|---|---|
| Carpet, level 5 | 32,768 | 1.82 to 1.83 | stable across windows (asserted in 1.6 to 1.89) |
| Menger sponge, level 4 | 160,000 | 2.3 to 2.4 | local slopes 2.29 to 2.43; fits over four windows 2.36 to 2.39 |
| Menger sponge, level 3 | 8,000 | 2.24 down to 1.82 | **not reliable**: drifts with window because the walk saturates |

In each case d_s is below the similarity dimension (1.89 and 2.73), as is usual for fractals. Reproduce the sponge number
with `python menger_sponge.py --d 3 --level 4 --spectral --steps 1200`. A literature comparison for the carpet and sponge
values has not been done.

## Relation to existing repository work
- The Sierpinski gasket reference graph follows the PANoRAMic.os stage audit. The Sierpinski IFS on projected Gosset faces
  (`DEEP_GEOMETRY_EXPERIMENTS_2026-11-09.md`, section 4) is a different construction (a planar IFS, not a graph) and is
  not used here.
- Du Val's constrained R^10 model of E8 (`du_val_e8.py`) is a lattice, not a fractal. The d = 8 and d = 10 sponges here
  are fractal subsets of a cubic grid and have no stated relation to it.
