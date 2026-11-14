# Gosset 4_21 Local Vertex-Star and Incidence Audit

**Status:** Isolated exact combinatorial audit; no production wiring.

## Method

The canonical E8 roots are represented in doubled integer coordinates
X = 2x. A pair of roots is adjacent in the Gosset 1-skeleton exactly when
X dot Y = 4. For each of the 240 possible base vertices, the local vertex
star is constructed as the induced graph on the 56 roots X satisfying
base dot X = 4.

All pair tests, degree counts, common-neighbor counts, graph distances, and
triangle counts use exact integer arithmetic. The audit does not use SciPy,
floating-point tolerances, GPU computation, or enumeration of the full Weyl
group.

## Local invariants

For every base vertex, the induced 56-vertex graph must have:

- 756 edges and degree 27 at every vertex;
- 756 adjacent pairs with 16 common neighbors each;
- 756 nonadjacent pairs with 10 common neighbors each;
- 28 nonadjacent pairs with zero common neighbors;
- the 28 zero-common-neighbor pairs form a perfect matching;
- distance distribution (1, 27, 27, 1) from every local vertex;
- 4,032 triangles in the local graph;
- exactly 216 local triangles through each local vertex.

The perfect matching is a graph-theoretic exceptional-pair relation. This
audit does not assign it a physical or semantic interpretation.

## Global incidence derivation

A triangle in the local star of base vertex v corresponds to a 4-clique
containing v in the global Gosset graph. Each global 4-clique is counted once
at each of its four vertices. Therefore:

    number of global 4-cliques = 240 * 4,032 / 4 = 241,920.

Each global 4-clique contains six edges. The implied number of 4-cliques
incident to each global edge is:

    241,920 * 6 / 6,720 = 216.

The experiment checks that these local-to-global incidence totals balance.
This is a derived incidence count from the exact root graph, not a separate
enumeration of every global 4-clique.

## Reproduction

    python -m pytest -q tests/test_gosset_local_star.py
    PYTHONPATH=. python experiments/gosset_local_star_audit.py

The CI workflow runs both commands and stores the JSON report as an artifact.

## Scope and limitations

Passing establishes the stated finite graph invariants for the current
canonical E8 root construction. It does not prove a geometric realization
beyond the specified root-polytope model, formalize the result in Lean, or
validate a physical interpretation. The local star is treated as an induced
subgraph of the 1-skeleton; no assumptions are made about PAN V8 semantics.
