# Direct Gosset 4-Clique and Vertex-Figure Antipode Audit

**Status:** Isolated exact combinatorial research experiment.

## Why the 28 exceptional pairs matter

For a chosen E8 root alpha, the 56 neighboring roots beta (alpha dot beta = 1
in unscaled coordinates) project into the hyperplane perpendicular to alpha
as beta - alpha/2. These are the 56 vertices of the corresponding Gosset
vertex figure.

The local graph has 28 pairs with zero common neighbors. The audit now checks
that each such pair is exactly (beta, alpha - beta). Their projected vectors
are negatives:

    (alpha - beta) - alpha/2 = -(beta - alpha/2).

Thus the 56 projected points split into 28 antipodal pairs. The pairing is
an involution with no fixed points, and it is exactly the exceptional
zero-common-neighbor matching. This is a precise geometric interpretation
inside the root-space vertex figure, not a physical interpretation.

## Direct global 4-clique enumeration

The local-star calculation previously implied 241,920 global 4-cliques:
each local triangle is a 4-clique containing its base vertex, and every
global 4-clique is counted at four vertices.

This experiment independently enumerates all 4-cliques using ordered
common-neighbor intersections in the 240-vertex, 56-regular root graph.
It checks:

- exactly 241,920 distinct four-vertex cliques;
- all six pairs in each clique are Gosset edges;
- all 6,720 global edges occur in exactly 216 four-cliques;
- every global vertex belongs to exactly 4,032 four-cliques;
- vertex incidences agree with the local-star triangle count.

No full Weyl-group enumeration or floating-point arithmetic is used.

## Reproduction

    python -m pytest -q tests/test_gosset_global_4cliques.py
    PYTHONPATH=. python experiments/gosset_global_4clique_audit.py

## Boundaries

This validates finite graph incidence and the antipodal geometry of the
vertex figure under the specified E8 root model. It is not a Lean proof,
physical validation, or evidence that the same structure maps to Janus Hydra
or PAN V8 semantics.
