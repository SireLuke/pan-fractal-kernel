# Torque-free rigid-body dynamics: tennis-racket theorem

Project attribution: Lucas Thouvenell (@SireLuke).

## Equations

For principal moments 0 < I1 < I2 < I3, torque-free Euler equations in the
body frame are:

    I1 w1_dot = (I2-I3) w2 w3
    I2 w2_dot = (I3-I1) w3 w1
    I3 w3_dot = (I1-I2) w1 w2

The engine also integrates body-to-inertial attitude with unit quaternions.
The inertial angular-momentum vector can therefore be checked while body-frame
components change.

## Stability

Pure rotations about I1 and I3 are linearly stable; rotation about I2 is
linearly unstable. The intermediate-axis perturbation growth exponent is

    sigma = |Omega| sqrt(((I2-I1)(I3-I2))/(I1 I3)).

A visible flip sequence depends on inertia ratios, energy, angular momentum,
initial perturbation and observation frame. The ideal equations do not imply
that the body literally pauses or settles after each half-turn.

## Numerical method and validation

rigid_body_dynamics.py uses fourth-order Runge-Kutta integration for angular
velocity and quaternion attitude, normalizing the quaternion after each step.
Exact torque-free motion conserves kinetic energy, angular-momentum magnitude,
and the inertial angular-momentum vector. The discretized RK4 solver only
conserves these approximately; step refinement is required.

Tests cover principal-axis equilibria, the linear growth rate, invariant drift,
stable-axis controls and quaternion normalization. They do not validate a
specific racket, phone, spacecraft or Earth. Physical prediction requires a
measured inertia tensor, initial state and uncertainty budget.

## Lean 4 roadmap

Formalization is pending. Candidate exact lemmas: conservation of
1/2 sum(I_i w_i^2) and sum(I_i^2 w_i^2) under the symbolic Euler vector field,
and positivity of the intermediate-axis linearized growth exponent when
0 < I1 < I2 < I3. Proving these equations does not formally verify the
floating-point RK4 implementation.
