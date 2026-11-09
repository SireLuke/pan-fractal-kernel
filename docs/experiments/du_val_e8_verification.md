# Du Val R10 realization: independent E8 check

Coxeter describes the 5_21 lattice in ten Euclidean coordinates, constrained by two zero-sum equations. Its ten coordinates therefore occupy an eight-dimensional subspace. The relevant passage identifies the minimal points at distance (5\sqrt{2}) as the 240 vertices of Gosset 4_21; the table on the following page supplies explicit Du Val coordinate examples ([Coxeter, *Regular and Semi-Regular Polytopes III*, §3.8, pp. 38–39](https://roice3.org/ruen/Regular_and_Semi-Regular_Polytopes_III.pdf), printed pages 38–39).

The PDF text layer mangles some congruence symbols. The common-residue interpretation used in `du_val_e8.py` is checked against the table examples: for example, `(4,-1,-1,-1,-1; 2,2,2,-3,-3)` has zero block sums, the first five entries share residue 4 modulo 5, and twice each of the final five entries also has residue 4 modulo 5. This check supports the congruence implementation, while a high-resolution glyph inspection remains useful before building a general-purpose coordinate parser.

## Exact reduction

Write the independent coordinates as
`y=(x1,x2,x3,x4,x6,x7,x8,x9)`. The congruence condition gives
`y = c(1,1,1,1,3,3,3,3) + 5z`, with integer `c` and `z`; the remaining coordinates are fixed by the two zero-sum equations. The coordinate-lattice determinant is `5^7`. The induced Gram matrix is block diagonal with blocks `I4 + J4`; its determinant is `25), so the Euclidean covolume before scaling is `5^8). Scaling coordinates by `1/5` gives covolume 1.

The bounded exact enumeration only needs four free integers per five-coordinate block. Since the norm cutoff is 50, each coordinate lies in `[-7,7]`; the fifth coordinate is the negative sum of the first four. Pairing the two blocks by their shared residue gives:

- minimum nonzero squared norm: 50 before scaling, 2 after scaling;
- exactly 240 minimal vectors;
- inner-product distribution for a fixed scaled minimal vector: `{-2: 1, -1: 56, 0: 126, 1: 56, 2: 1}`;
- all 240 root reflections preserve the 240-vector set.

This verifies the minimal-vector E8 root system in the eight-dimensional constrained subspace. The module is a bounded verifier for minimal vectors, not a full enumerator of every point in the infinite 5_21 lattice.
