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