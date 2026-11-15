# Occupancy model

For (T>0), define the Fermi-Dirac occupancy

`F(E)=1/(\exp((E-\mu)/T)+1)`.

Let `x=(E-mu)/T`. Then:

- `F=1/(exp(x)+1)`;
- `zeta=2F-1`;
- binary Shannon entropy (H_2(F)=-F\log_2 F-(1-F)\log_2(1-F)).

At (E=\mu), (F=1/2) and binary entropy is 1 bit, its maximum. At finite positive temperature this does not prove maximum spatial connectivity, accessibility or transport efficiency; those require separate graph/path metrics.

The (T=0) limit is a step function with a boundary convention at (E=\mu); implementations must not evaluate the finite-temperature expression by division by zero.

For the project's UHFE/UDFE vocabulary, document the mapping from occupied and unoccupied measures explicitly. The terms do not, by themselves, prescribe an equation of motion.

## Menger mu-cube volume and flux

`menger.py` adds exact helper identities (no physical claim):

- `menger_volume_fraction(level, d)` is `(N_d / 3^d)^level` (`20/27` per level for `d = 3`);
- `menger_hausdorff_dimension(d)` is `ln N_d / ln 3` (`~2.727` for `d = 3`);
- `mu_cube_volume(n, level, d)` is `n * menger_volume_fraction(level, d)`, an occupancy-weighted volume definition used for visualization;
- `lemniscate_flux(n)` is `n(1-n) = (1 - delta^2)/4`, peaking at `1/4` for `n = 1/2`.

The flux is the Bernoulli variance of a two-state occupancy, not a measured flow or a gravitational self-energy. Cell counts come from the kernel's `menger_sponge.py`, imported lazily.

