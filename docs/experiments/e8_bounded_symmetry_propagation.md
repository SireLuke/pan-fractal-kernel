# Bounded E8 Symmetry Propagation

**Status:** Isolated computational research experiment. No production wiring.

## Purpose

This experiment adapts the useful part of the nested-reference analogy from
42.zip: represent repeated structure through shared generators and references,
not duplicated payloads. It does **not** reproduce archive nesting, exploit
overlapping ZIP headers, or perform uncontrolled decompression.

The E8/Gosset object is a finite graph. Its 240 vertices are generated from
eight simple-root reflections, and its 6,720 undirected edges are derived from
exact integer inner products. The full Weyl group is not enumerated.

## Exact coordinate contract

Use doubled coordinates X = 2*x. The 240 roots then have integer
coordinates and squared norm 8:

- 112 integer-coordinate roots: exactly two entries are +/-2, with the
  remaining six entries zero.
- 128 half-integer roots: all entries are +/-1, with an even number of
  negative entries.

The eight stored simple-root generators have a Gram matrix with diagonal 8
and off-diagonal entries 0 or -4, with seven -4 entries above the diagonal.
For a simple root A, the exact reflection is

    X' = X - (dot(X, A) / 4) * A.

The divisibility check is performed before integer division. No floating-point
tolerance is used in this propagation module.

## Bounded propagation

Breadth-first orbit construction uses explicit limits:

| Resource | Hard maximum |
|---|---:|
| Unique roots | 240 |
| Reflection generators | 8 |
| Generator applications | 1,920 |
| Search depth | 64 |
| Gosset edges | 6,720 |
| Cached neighborhoods | 240 |

The default run reaches all 240 roots in 1,920 generator applications. A
request exceeding its declared node, depth, transition, or edge budget raises
TraversalBudgetExceeded rather than returning a silently truncated graph.

## Graph representations

- **explicit:** materializes roots, all 6,720 edges, and adjacency lists.
- **implicit:** retains the seed and generators; regenerates the finite orbit for
  each requested neighborhood and does not retain an expanded orbit or edge
  list on the graph instance.
- **cached:** retains the orbit and a bounded LRU of requested neighborhoods.

The implicit mode is a reference implementation of on-demand expansion, not a
claim that the Python runtime has zero temporary memory use. The three modes
are tested for identical roots, edges, and neighborhoods.

## Exact graph criteria

For doubled roots X and Y, Gosset adjacency is dot(X, Y) = 4
(equivalent to the original inner product being 1). The audit requires:

- 240 unique roots, matching the existing gosset_421.E8_ROOTS enumeration;
- root-family split 112 + 128 and scaled squared norm 8;
- 8 simple-reflection generators and exact E8 Gram structure;
- 6,720 undirected edges and degree 56 at every vertex;
- agreement between explicit, implicit, and cached graph views;
- explicit failures when a traversal or cache budget is exceeded.

## Run

    python -m pytest -q tests/test_e8_bounded_symmetry.py
    python experiments/e8_bounded_symmetry_audit.py

The workflow uses only Python's standard library plus pytest. This is an exact
finite combinatorial/software audit, not a Lean proof, physical validation, or
proof that any PAN semantic coordinate corresponds to an E8 root.

## Deliberate boundaries

No 16-way branching factor is assumed to be geometrically intrinsic. A
four-dimensional 16-cell has 8 vertices, not 16. The 128 half-integer roots
are parity-constrained sign vectors, not an unrestricted hypercube.
Weyl reflections are used as generators; the 696,729,600-element Weyl group is
never expanded. No archive bomb, overlapping ZIP structure, unbounded
recursion, GPU requirement, V8 change, Janus Hydra mapping, or production
dependency is introduced.
