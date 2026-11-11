# Parameter-free length scale for hydrogen on E8 / 5_21 shell views

**Status:** pre-registered comparison; result is **negative** for the hydrogen-matched rules.
**Branch:** `research/hydrogen-shell-scale-rule` · **Date:** 2026-11-10
**Builds on:** `HYDROGEN_SHELL_MODES.md` (#38). **Changes:** adds `hydrogen_shell_scale.py`, a runner, tests, results JSON, and this note. No existing module, V8 value, Janus Hydra equation, or UHFE/UDFE behaviour is modified.

## Why

`HYDROGEN_SHELL_MODES.md` found that the cross-(l, m) overlap of hydrogen states on a projected shell beats a shuffled-direction null at small `length_scale` and loses the advantage as the scale grows, but the scale was a swept parameter. This note fixes the scale by rules written down before the run and tests the same statistic.

## Pre-registered rules and criterion

Shell n (norm^2 = 2n) is tied to principal quantum number n. With rho = |p| for the unit-normalised 3D view p:

| Rule | Scale s_n (a0 per unit) | Hydrogen input |
|---|---|---|
| `mean_radius` | 1.5 n^2 / mean(rho) | match mean radius to <r> of the ns state |
| `max_radius` | 2 n^2 / max(rho) | match outer edge to the classical l = 0 turning radius |
| `lattice_unit` | sqrt(2n) | none: one raw lattice unit = 1 a0 |

Statistic: the largest |overlap| between states with different (l, m), over states with n' <= n. Null: same radii, random directions, 200 trials. Criterion fixed in advance: E8 value < 0.25 x null minimum. Undefined for shell 1 (one state).

## Results

| Rule | Shell | Scale | E8 | Null min | Ratio | Passes |
|---|---|---|---|---|---|---|
| mean_radius | 2 | 10.30 | 0.0176 | 0.0199 | 0.88 | no |
| mean_radius | 3 | 23.20 | 0.0659 | 0.0406 | 1.62 | no |
| max_radius | 2 | 8.14 | 0.0113 | 0.0141 | 0.80 | no |
| max_radius | 3 | 18.26 | 0.0479 | 0.0303 | 1.58 | no |
| lattice_unit | 2 | 2.00 | 0.00051 | 0.0093 | 0.055 | yes |
| lattice_unit | 3 | 2.45 | 0.0012 | 0.0181 | 0.066 | yes |

## Interpretation

- **When the scale is set from hydrogen, the advantage disappears.** At the radii that actually span the wavefunctions (up to about 2n^2 a0), the E8 cloud is no better than shuffled directions at shell 2 and worse at shell 3. This is consistent with the design-strength explanation: psi_nlm over that range is far from a degree <= 7 polynomial, so the exactness of the 7-design no longer helps.
- **The earlier advantage was a small-scale effect.** The `lattice_unit` rule passes, but it samples only the inner 2 to 2.5 a0 where the states are smooth, and it uses no hydrogen input. It does not support hydrogen structure in the geometry.
- Under the stated criterion the hydrogen-matched hypothesis is **not supported**. The exact result of `HYDROGEN_SHELL_MODES.md` (isotropic solid-harmonic Gram on every shell) is unaffected.

## Units bookkeeping (not a claim)

For reference, `physical_bookkeeping` converts a scale to metres and Planck lengths using the kernel's spectroscopy constants, CODATA a0 = 5.29177210544e-11 m, and G = 6.67430e-11. For `mean_radius` at shell 2, one raw lattice unit is 4.07 a0 = 2.15e-10 m = 1.33e25 Planck lengths. This is a unit conversion only; it asserts no minimum length, no discretisation, and no physical size for the lattice. `halpha_check()` confirms the kernel's Rydberg wavelength (656.47 nm) equals h c / (E3 - E2) from Bohr levels to machine precision. Finite-proton-mass corrections to a0 are ignored.

## Limits

- Equal point weights are used; hydrogen's radial orthogonality assumes volume weighting, so only different-(l, m) pairs are scored.
- One view seed (421) and one statistic. Other views and a node-recovery test are not yet run.
- Fermi-sea occupation weighting and the UHFE Planck constants were considered; neither enters the statistic, so only the Planck length is used (bookkeeping).

## Reproduce

`python run_hydrogen_shell_scale_experiment.py docs/experiments/hydrogen_shell_scale_rule_results.json` and `python -m pytest -q tests/test_hydrogen_shell_scale.py`.
