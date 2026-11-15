# Plug-in and adapter contract

A plug-in is an optional capability with a small, versioned boundary. Implementations must not import concrete PANoRAMic.os application modules.

## Capability descriptor

Every adapter should declare:

- unique `plugin_id` and implementation version;
- supported ABOM-V8 schema versions;
- input and output types;
- required capabilities (if any);
- deterministic or stochastic behavior;
- units and coordinate frame;
- validation/test entry points.

## Geometry adapter

Input: a versioned geometry request and parameters.

Output: a geometry reference plus provenance describing the algorithm, parameterization, resolution/depth and limitations.

The adapter must not copy a kernel implementation into ABOM-V8. It calls or wraps a kernel-owned API where one exists. If no stable kernel API exists, the adapter remains a protocol stub.

## Transport adapter

Input: parameterized curve configuration, parameter interval and sampling policy.

Output: ordered points, tangent/curvature data when supported, and continuity/origin-crossing diagnostics.

Transport is a path/trajectory abstraction. It does not imply physical flow without a separately specified dynamical law.

## Field-diagnostics adapter

Input: scalar or vector field, domain, coordinate frame, discretization and boundary conditions.

Optional outputs: gradient, divergence, curl, Laplacian and associated residual/error data. The protocol must state whether operators are analytic, finite-difference, finite-element or graph-based. Do not mix their definitions silently.

## Occupancy adapter

Input: reduced energy ((E-\mu)/T) or a validated equivalent.

Output: occupation (F), asymmetry (zeta=2F-1), and binary entropy. The (T=0) boundary case must be handled explicitly.

## Failure behavior

- Reject unsupported schema versions.
- Reject dimension/frame mismatches.
- Reject non-finite numerical inputs.
- Never coerce unknown coordinate semantics.
- Keep unavailable optional capabilities explicit rather than returning fabricated values.