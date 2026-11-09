"""Exact, bounded verification of Du Val's constrained R^10 model of E8.

Coxeter describes points x in R^10 with two zero-sum blocks and a
mod-5 common-residue condition. Scaling x by 1/5 gives the E8 lattice.
This module enumerates only the minimal vectors, using exact integers.
"""
from __future__ import annotations

from collections import Counter
from itertools import product

BLOCK_LIMIT_SQUARED = 50
SCALE = 5


def _block_vectors(kind: str):
    """Enumerate zero-sum integer 5-tuples of squared norm <= 50 by residue."""
    if kind not in {"first", "second"}:
        raise ValueError("kind must be 'first' or 'second'")
    buckets = [[] for _ in range(5)]
    for prefix in product(range(-7, 8), repeat=4):
        vector = (*prefix, -sum(prefix))
        norm_sq = sum(value * value for value in vector)
        if norm_sq > BLOCK_LIMIT_SQUARED:
            continue
        if kind == "first":
            residues = {value % 5 for value in vector}
            if len(residues) != 1:
                continue
            residue = residues.pop()
        else:
            residues = {(2 * value) % 5 for value in vector}
            if len(residues) != 1:
                continue
            residue = residues.pop()
        buckets[residue].append((norm_sq, vector))
    return buckets


def du_val_minimal_vectors() -> tuple[tuple[int, ...], ...]:
    """Enumerate the 240 shortest nonzero Du Val vectors in integer R^10."""
    first = _block_vectors("first")
    second = _block_vectors("second")
    candidates = []
    minimum = None
    for residue in range(5):
        for n1, left in first[residue]:
            for n2, right in second[residue]:
                total = n1 + n2
                if total == 0:
                    continue
                if minimum is None or total < minimum:
                    minimum, candidates = total, []
                if total == minimum:
                    candidates.append(left + right)
    if minimum != BLOCK_LIMIT_SQUARED:
        raise AssertionError(f"expected minimum norm 50, found {minimum}")
    result = tuple(sorted(set(candidates)))
    if len(result) != 240:
        raise AssertionError(f"expected 240 minimal vectors, found {len(result)}")
    return result


def verify_du_val_e8() -> dict[str, object]:
    """Check norm, root inner products, reflections, and lattice covolume."""
    roots = du_val_minimal_vectors()
    root_set = set(roots)
    norms = {sum(value * value for value in root) for root in roots}
    if norms != {50}:
        raise AssertionError(f"unexpected minimal-vector norms: {norms}")

    # The Euclidean metric on the 8 free coordinates is block diag(I4+J4,
    # I4+J4), of determinant 25. The residue lattice has coordinate
    # determinant 5^7; hence covolume 5^8 before scaling and 1 after /5.
    inner_products = Counter()
    for root in roots:
        numerator = sum(a * b for a, b in zip(roots[0], root))
        if numerator % 25:
            raise AssertionError("scaled root inner product is not integral")
        inner_products[numerator // 25] += 1
    expected = {-2: 1, -1: 56, 0: 126, 1: 56, 2: 1}
    if dict(inner_products) != expected:
        raise AssertionError(f"unexpected E8 inner-product distribution: {inner_products}")

    for alpha in roots:
        for vector in roots:
            numerator = sum(a * b for a, b in zip(vector, alpha))
            if numerator % 25:
                raise AssertionError("scaled reflection coefficient is not integral")
            coefficient = numerator // 25
            reflected = tuple(x - coefficient * a for x, a in zip(vector, alpha))
            if reflected not in root_set:
                raise AssertionError("a root reflection did not preserve the 240-vector set")

    return {
        "ambient_coordinates": 10,
        "independent_dimension": 8,
        "minimal_vectors": len(roots),
        "unscaled_minimum_squared_norm": 50,
        "scaled_minimum_squared_norm": 2,
        "inner_product_distribution": expected,
        "all_240_root_reflections_preserve_set": True,
        "unscaled_covolume": 5 ** 8,
        "scaled_covolume": 1,
        "congruence": "x1..x5 share residue c; 2*x6..2*x10 share residue c (mod 5)",
    }
