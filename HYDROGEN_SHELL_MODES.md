# Hydrogen eigenstates on the 3D view of E8 / 5_21 shells

**Status:** isolated research module; exact reference functions plus one exact structural result and one empirical comparison.
**Branch:** `research/hydrogen-shell-modes` · **Date:** 2026-11-10
**Changes:** adds `hydrogen_shell_modes.py`, `run_hydrogen_shell_experiment.py`, `tests/test_hydrogen_shell_modes.py`, a focused workflow, and this note. No existing module, V8 value, Janus Hydra equation, or UHFE/UDFE behaviour is modified.

## Question

Does the Euclidean-shell structure of the 5_21 patch, seen through the View Ladder's 3D stage, carry hydrogen-like (radial index × angular harmonic) structure, or is any resemblance an artifact of the projection?

## Results

### 1. Exact: shells give an isotropic solid-harmonic Gram matrix in every 3D view
Shells n = 1, 2, 3 (240, 2160, 6720 vectors) are spherical 7-designs on S^7. For any orthonormal 3 x 8 frame P, the real solid harmonics S_lm(Px) (l <= 2) are harmonic polynomials in x, so the shell mean of S_lm S_l'm' equals its S^7 average: diagonal, with entries E[rho^(2l)]/(4 pi), E[rho^(2k)] = B(k+3/2, 5/2)/B(3/2, 5/2) (e.g. E[rho^2] = 3/8).

Measured max deviation over seeds 421, 7, 73: **2.5e-16, 7.4e-16, 8.0e-16** (shells 1, 2, 3). Random iid points on S^7 with the same N give about 1e-3 to 4e-3. Radial moments E[rho^(2k)] are exact for k <= 3 and visibly break at k = 4 (degree 8), confirming the design boundary.

This restates, for the 3D view, the 7-design property already noted in `VIEW_LADDER_SCHEMA.md`. It is a property of the lattice shells, not of hydrogen.

### 2. Empirical: hydrogen cross-(l, m) overlap beats a shuffled-direction null at small scale only
States n <= 3 (14 states). Statistic: the largest normalised |<psi_a|psi_b>| between states with different (l, m), using equal point weights. Null: identical radii, random directions (40 trials). `length_scale` is a0 per unit of the unit-sphere-normalised 3D coordinate and is an explicit free parameter.

| Shell | Scale 2 | Scale 6 | Scale 12 |
|---|---|---|---|
| 1 (240 pts) | 0.0085 vs null 0.149 | 0.044 vs 0.146 | 0.106 vs 0.227 |
| 2 (2160) | 0.0014 vs 0.058 | 0.0096 vs 0.052 | 0.029 vs 0.072 |
| 3 (6720) | 0.0009 vs 0.029 | 0.0071 vs 0.027 | 0.031 vs 0.037 (27% of nulls are lower) |

The advantage is large when the radial functions are smooth over the sampled radius range and shrinks as the scale grows. That is what the design boundary predicts: psi_nlm is not a polynomial, so exact orthogonality holds only through degree 7, and large scales probe higher effective degree. The scale is not derived from the geometry; choosing it to be physical is open.

## What this does not show

- It does **not** show E8 or the golden ratio is special: any good spherical design gives result 1, and result 2 is explained by design strength.
- The radial coordinate in the 3D view is the projected radius, spread continuously inside each shell; it is not an independent radial quantum number. Radial *nodes* are not recovered from the point cloud here; only exact node positions of the reference functions are tested.
- Hydrogen's angular part lives on S^2; the shells are designs on S^7. The 3D view is a display transform.
- No identification of V8 coordinates, UHFE/UDFE, or Janus Hydra with hydrogen is made. Passing tests is a software and exact-arithmetic result.

## Verification performed

- Reference functions: normalisation to 1e-9, node counts n-l-1 by sign changes, nodes at r = 2 (2s), 6 (3p), 12 (4d), 3(3 +/- sqrt 3)/2 (3s), Y_20 cone at 54.7356 degrees, Y_lm orthonormality by Gauss-Legendre quadrature.
- Structural result across three frames and three shells, with iid null and the degree-8 breakdown.
- Cross-overlap comparison against a 20-trial null in the tests (the runner uses 40).
- Reproduce: `python run_hydrogen_shell_experiment.py docs/experiments/hydrogen_shell_modes_results.json`; `python -m pytest -q tests/test_hydrogen_shell_modes.py`.

## Suggested next steps

1. Derive a physical `length_scale` from a stated rule instead of sweeping it.
2. Test shell 4 (17,280 points) once the depth engine exposes it, and check whether the scale at which the advantage vanishes moves with design strength.
3. Add a node-recovery test on the cloud itself (nodal-domain counts with a declared neighbourhood graph and null).
4. Obtain independent review before treating any of this beyond a software and numerical result.
