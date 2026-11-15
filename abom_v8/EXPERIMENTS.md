# ABOM-V8 visual experiment inputs

This document preserves the specific construction targets supplied for this milestone. These formulas are visualization hypotheses to encode and test; they are not general physical laws.

## UHFE/UDFE occupancy and boundary

The five-state circular sequence shows complementary area fractions \(N\) and \(1-N\) for occupancy values 0.95, 0.75, 0.50, 0.25 and 0.05. The Fermi occupancy curve is evaluated against reduced energy \(x=(E-\mu)/T\), with

\[
N=\frac{1}{e^x+1},\qquad \delta=2N-1=-\tanh(x/2).
\]

The supplied unit-disk construction uses two semicircle boundary diameters \(d_-=1-\delta\) and \(d_+=1+\delta\), whose sum is 2. The kernel's existing \`fermi_yinyang.py\` implements that exact white/black disk partition, including eye geometry (excluded from the area statement). ABOM-V8 wraps this implementation rather than copying it.

## Focus-radius and eye-area curves

The supplied second chart plots the candidate focal radii

\[
c_+=\frac{N}{\sqrt{2}},\qquad c_-=\frac{1-N}{\sqrt{2}},
\]

for unit-disk radius, and the third chart plots candidate eye-area values \(A_+=N^2\), \(A_-=(1-N)^2\), alongside binary Shannon entropy \(H_2(N)\). These relationships are captured as named helpers in \`occupancy/fermi.py\` and clearly marked as visualization parameterizations. They must not be generalized to all lemniscates without additional derivation.

## Radial scale-shell visual

The radial point-cloud image motivates a separate golden-angle shell generator with configurable shell count, point count, base radius and scale ratio (default \(\phi\)). This is only a 2D visualization layout. It is not an E8 root generator, Gosset \(4_{21}\) construction or quasicrystal cut-and-project map.

## Vector differential operators

The operator reference sheet motivates optional Cartesian finite-difference gradient, divergence, curl and Laplacian diagnostics. They are implemented only for smooth scalar/vector fields sampled on a uniform 3D Cartesian grid. A separate graph-operator contract is required for Menger adjacency graphs; a generalized metric/operator contract is required for Gosset geometry or the eight-coordinate V8 state space.
