# STRATA protocol: torque-free intermediate-axis instability

Project attribution: Lucas Thouvenell (@SireLuke).

Status: protocol only; no physical measurement is claimed.

## Hypotheses

H1: For 0 < I1 < I2 < I3 and nonzero intermediate spin Omega, the linearized
transverse subsystem has a positive real growth exponent.

H2: Pure rotations about the smallest and largest principal axes are linearly
stable to small transverse perturbations.

H3: Energy, angular-momentum magnitude and inertial-frame angular-momentum
vector are conserved by the exact torque-free equations. Numerical drift
decreases under time-step refinement for the declared integrator and fixture.

## Controls and measurements

Use matched inertia ratios and normalized perturbation amplitudes, both
perturbation signs, and stable-axis controls. Repeat at dt, dt/2 and dt/4
with fixed initial conditions and duration. Record body angular velocity,
attitude, energy, body/inertial angular momentum, invariant drift, perturbation
envelope and flip events.

Define a flip event operationally before analysis (for example, crossing a
specified body-axis orientation threshold relative to inertial angular
momentum). Visual impression alone is not a measurement.

## Evidence levels

1. Symbolic identities from Euler's equations.
2. Unit tests on fixed fixtures.
3. Numerical convergence under step refinement.
4. Independent solver comparison.
5. Physical validation with measured inertia and calibrated orientation data.

Do not promote evidence between levels. Earth-specific claims require a
separate inertia tensor and geophysical model.

## Lean 4

Formal proof obligations are listed in TORQUE_FREE_RIGID_BODY.md. Formalization
is pending until a Lean module and successful build are present.
