# PAN V9 affine-E8 projection experiment

**Status:** Experimental software/view layer. Not a new physical dimension, gauge theory, or fluid solver.

## Scope and architecture boundaries

- Canonical geometry remains Gosset 4_21: the 240 E8 roots in R^8.
- The affine E8 Weyl group is W(E8) semidirect E8-lattice translations. A lattice translation maps the full E8 lattice to itself; it does not map the finite 240-root subset onto itself.
- V9 is represented experimentally as (V8, xi), with xi in [0,1] controlling a continuous orthogonal display-frame family.
- xi is not asserted to be a ninth Euclidean root coordinate or an affine null-root coordinate.
- Janus Hydra remains the semantic translator. UHFE and UDFE remain separate formation and dissolution outputs.
- V8 order remains (h, R, u, d, tau, chi, s, f). No geometry-view operation mutates V8 or semantic records.

## Implemented view construction

The existing Gosset projection primitives (ProjectionFrame, project_points,
and source-root indexing) are reused by v9_affine_e8_projection.py.

A deterministic Q(xi) in SO(8) is constructed from four coordinate-plane
rotations. Q(0)=I. A view frame is P(xi)=P0 Q(xi), where P0 is the existing
coordinate projection. Full 8D frames are lossless and reversible; lower
dimensional views remain lossy and report residuals. Original E8 root
coordinates and indices are retained.

The continuous Q(xi) family is not generally an E8 lattice automorphism.
Only discrete Weyl/lattice operations carry that exact symmetry claim.
Reverse traversal uses Q(xi)^T and deterministic recomputation from xi.

## Affine lattice translation

The module checks the standard E8 lattice description: integer coordinates
with even coordinate sum, or half-integer coordinates with even coordinate
sum. Translation by a lattice vector preserves lattice membership and all
pairwise differences. The finite root set is translated to another finite
subset of the full lattice; it is not claimed to remain the same root set.

Center-and-RMS normalization separately removes common translation and
positive scale from a point cloud. This is a shape-normalization convention,
not a Weyl-group action.

## Janus v1 compatibility gate

JANUS-HYDRA-DYNAMIC-INVERSE-v1 is the canonical semantic baseline. All five
inverse heads include dissolution density d, and the reader has separate
formation and inverse support maps. The five pair defects are regression
tested. V9 view traversal is not connected to, and cannot modify, the V8
semantic input.

## Separate SU(9) and transport research

SU(9) has 80 Lie-algebra generators. The standard block embedding contains
su(8) (63 generators), with the complement decomposing as 1 + 8 + 8bar.
This is a representation-theoretic decomposition, not proof that the 17
additional generators encode xi or arise from affine E8.

A nine-spatial-dimensional incompressible Navier-Stokes model would require
its own domain, units, boundary conditions, forcing, energy estimates, and
regularity analysis. It is not implemented here. No EDDE stability or
singularity-prevention claim is made.

## Validation

Run:

    python -m pytest -q tests/test_v9_affine_e8_projection.py tests/test_janus_dynamic_inverse_v1.py tests/test_gosset_projection.py tests/test_system_integration.py

Passing tests establish software invariants only, not physical significance.
