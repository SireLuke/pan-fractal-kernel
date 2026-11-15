# Lemniscate transport experiments

Curves are candidate geometries for bidirectional path routing. The initial default is a parameterized **Gerono curve** because its horizontal and vertical scales can be selected independently. The package will compare it with Bernoulli and other lemniscates using the same metrics.

## Gerono

`x(t) = a cos(t)`, `y(t) = b sin(2t)`, for (t\in[0,2\pi]).

- `a > 0`: horizontal half-width.
- `b > 0`: vertical half-height.
- The curve crosses the origin at (t=\pi/2) and (t=3\pi/2).
- The scale ratio `b/a` controls lobe aspect ratio.

There is no invariant sense in which the standard Gerono curve has a larger radius than the standard Bernoulli lemniscate: their parameterizations and scale conventions differ. Compare them after normalizing a shared measure such as bounding-box width, enclosed lobe area, or arc length.

## Bernoulli

Use the implicit polar relation (r^2=c^2\cos(2\theta)) on its real domain as one comparison family. Conversion to Cartesian points and handling of the focal/origin behavior must be tested.

## Comparison metrics

- origin crossing count and location;
- lobe symmetry and aspect ratio;
- sampled arc length and curvature distribution;
- path continuity and tangent behavior;
- numerical stability under resolution changes;
- routing reversibility;
- occupancy conservation along a separately defined transport update.

The normalized comparison harness is available as `abom.transport.experiments.compare_lemniscates`; its resolution sweep reports sampling sensitivity. These are geometry diagnostics only. A plotted curve alone does not establish transport dynamics.