# Differential-operator diagnostics

This module defines optional diagnostics, not a mandatory geometry representation.

For a smooth scalar field (g) on Euclidean coordinates:

- gradient: (\nabla g), a vector field;
- Laplacian: (\nabla^2 g=\nabla\cdot\nabla g), a scalar field.

For a smooth vector field (V):

- divergence: (\nabla\cdot V), a scalar field;
- curl: (\nabla\times V), a vector field in three dimensions.

The familiar formulas in Cartesian 3D are not automatically valid on arbitrary graphs, fractals, non-Euclidean manifolds or the eight-coordinate state space. An adapter must specify its domain, metric, coordinate chart, discretization and boundary conditions.

## Candidate uses in ABOM-V8

- Gradient: local direction of fastest increase of a scalar occupancy/entropy field, where a differentiable field is defined.
- Divergence: local source/sink diagnostic for a declared vector transport field.
- Curl: local circulation/rotation diagnostic in a declared 3D chart or with a separately defined generalized operator.
- Laplacian: scalar-field diffusion/curvature diagnostic for a declared operator and metric.

For Menger graphs, define graph operators (e.g. graph Laplacian) separately. Do not call a graph Laplacian the Euclidean differential Laplacian without qualification.

## Minimum report

Record operator definition, discretization, boundary conditions, mesh/graph identity, convergence study and residual/error estimate.