# Node recovery: does the projected shell cloud reproduce hydrogen's nodal-domain counts?

**Status:** pre-registered comparison; result is **negative** (E8 is not distinguishable from the shuffled-direction null).
**Branch:** `research/hydrogen-node-recovery` (stacked on `research/hydrogen-shell-scale-rule`) · **Date:** 2026-11-10
**Changes:** adds `hydrogen_node_recovery.py`, a runner, tests, results JSON, this note. No existing module, V8 value, Janus Hydra equation, or UHFE/UDFE behaviour is modified.

## Question

`HYDROGEN_SHELL_SCALE_RULE.md` left open whether the cloud itself shows hydrogen's radial and angular nodes. Here the sign structure of psi_nlm is counted on the projected shell cloud.

## Ground truth and procedure

A real orbital restricted to radius r_max has (1 + radial nodes below r_max) x A(l, m) strong nodal domains, with A(l, 0) = l + 1 and A(l, m != 0) = 2|m|(l - |m| + 1). Domains are counted as connected components of the positive and negative sets in a symmetrised 10-nearest-neighbour graph; points with |psi| < 5% of max are excluded and components under 0.5% of N are ignored. A state is unscored if a radial node lies in 0.8 to 1.0 of r_max.

**Pre-registered criterion:** E8 exact-recovery rate must exceed the 95th percentile of 100 direction-shuffled nulls (same radii, random directions) and be at least 0.5.
**Pilot:** view seeds 7 and 73 were used to check the procedure runs and to see the dynamic range; the evaluation seed 421 was not touched beforehand. Scale rules are those of the previous note.

## Results (seed 421, k = 10)

| Rule | Shell | Scored | E8 recovery | Null mean | Null p95 | Passes |
|---|---|---|---|---|---|---|
| lattice_unit | 2 | 5 | 1.00 | 1.00 | 1.00 | no |
| lattice_unit | 3 | 13 | 0.92 | 0.94 | 1.00 | no |
| mean_radius | 2 | 5 | 1.00 | 1.00 | 1.00 | no |
| mean_radius | 3 | 14 | 0.79 | 0.78 | 0.86 | no |

Sensitivity to k = 6 and 16 and a low-N stress (random subsets of 120, 240, 480 points) give the same picture: E8 and null track each other within noise in every row. The misses are specific states (for example 3s and 3d, m = 1) where a nodal region is thinly sampled.

## Interpretation

- **No criterion is met.** The cloud does recover most nodal counts, but a cloud with identical radii and random directions recovers them equally well. Recovery here is set by sampling density, the radial distribution, and where nodes fall relative to r_max, not by the lattice directions.
- **Caveat on the null:** it keeps the E8 radial profile (the ball-like (1 - rho^2)^(3/2) distribution from projecting S^7). So the test does not say the radial profile is unimportant, only that directions add nothing beyond it. A uniform-in-ball null was not run.
- Combined with the earlier notes: the exact 7-design result stands, the hydrogen-matched scale does not show a geometric advantage, and node recovery does not either.

## Non-claims

No V8, Janus Hydra, or UHFE/UDFE mapping onto hydrogen. A recovery rate is a numerical result on a finite point cloud under declared filters (k, amplitude threshold, minimum component size); other choices could change individual rows. One view seed was evaluated.

## Reproduce

`python run_hydrogen_node_recovery_experiment.py docs/experiments/hydrogen_node_recovery_results.json`; `python -m pytest -q tests/test_hydrogen_node_recovery.py`.
