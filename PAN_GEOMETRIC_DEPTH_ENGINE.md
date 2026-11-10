# PAN Geometric Depth Engine v1

**Status:** isolated research implementation; bounded exact-arithmetic BFS.  
**Geometry:** E8 lattice vertex graph of the infinite 5_21 honeycomb.  
**Canonical boundary object:** Gosset 4_21 remains the 240-vertex local vertex figure.

## Purpose

The engine explores finite neighborhoods of an unbounded geometric structure. It imposes no maximum geometric depth; each run has an explicit computational depth and/or vertex budget.

## Three distinct depth concepts

1. **Graph depth** d_G(p,q): shortest number of nearest-root transitions, each adding one of the 240 E8 roots.
2. **Euclidean radius** ||p-q||²: metric distance in canonical E8 Euclidean space.
3. **View depth**: selected representation/projection level, such as 8D → 4D → 3D → 2D.

Graph depth and Euclidean radius are not interchangeable. View depth is a representation choice, not a geometric distance.

## Exact coordinate representation

The implementation uses doubled integer coordinates v=2x. Integral and half-integral E8 coordinates are represented without floating-point accumulation. The 240 transitions come from the existing canonical five21_neighborhood.ROOTS2.

## v1 API

- explore(max_depth, origin=..., max_vertices=..., track_paths=False)
- DepthRun: immutable run summary and completed shells.
- DepthShell: shell size, cumulative count, Euclidean norm-squared histogram, deterministic SHA-256.
- path_to(vertex): optional shortest root-index path when track_paths=True.
- run_to_dict(run): JSON-ready stable report.

If the vertex budget would be exceeded, the engine discards the incomplete next shell. It never reports a partial shell as complete. Parent-path retention is optional because it increases memory.

## Baseline reference values

| Graph depth | New vertices | Cumulative |
|---:|---:|---:|
| 0 | 1 | 1 |
| 1 | 240 | 241 |
| 2 | 9,120 | 9,361 |
| 3 | 121,680 | 131,041 |
| 4 | 864,960 | 996,001 |

CI pins depths 0–3 to exercise a nontrivial frontier while keeping execution bounded. Depth 4 remains a benchmark target, not a CI assumption. The depth-4 digest from the exploratory run must be compared only after matching this engine's canonical serialization.

## View Ladder integration boundary

Existing five21_neighborhood.five21_ladder builds views from **Euclidean norm shells**, not graph-distance shells. v1 does not relabel those points as graph shells. A later adapter may pass a completed graph-depth run into view_ladder.build_ladder, with explicit source ordering, projection provenance, and schema-hash tests.

## PAN architecture boundaries

- The engine explores the 8D E8 lattice underlying 5_21; it does not change Gosset 4_21.
- It does not alter V8=(h,R,u,d,τ,χ,s,f), normalization, or channel meanings.
- It does not alter Janus Hydra's five dynamic inverse pairs or JANUS-HYDRA-DYNAMIC-INVERSE-v1.
- It does not implement UHFE or UDFE; those remain separate receivers.
- A view/projection is not a physical compactification; no M-theory mapping is claimed.

## Reproducibility and next research tasks

1. Run python -m pytest -q tests/test_pan_geometric_depth.py tests/test_view_ladder.py tests/test_du_val_e8.py.
2. Benchmark depths 3 and 4 with memory measurement and exact environment capture.
3. Add a graph-shell-to-view-ladder adapter with source-index provenance.
4. Convert the Coxeter-plane face equilateral test and 72-orbit classification into a standalone exact-arithmetic experiment, including an independent implementation.
5. Verify the Du Val congruence transcription against a high-resolution scan of Coxeter (1988) before using it in a production converter.
6. Obtain independent mathematical review before manuscript submission.

No physical law, new particle model, or experimental prediction is claimed.
