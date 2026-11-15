# Brainstorm figures: what was incorporated and what was not

The maintainer supplied a set of AI-generated brainstorm graphs (Menger
mu-cube lattice, coupled state/volume/flux curves, golden phyllotaxis, a
Diosi-Penrose-style plot, a 13-3 microtubule lattice, a Trp dipole matrix and
SU(3) helical bands). Their numbers are unverified. This note records which
parts became tested code and which stayed out. No STRATA domain is promoted by
anything here; every physical or biological interpretation remains `not_tested`.

## Incorporated (exact arithmetic, tested)

- Menger volume fraction `(20/27)^level`, similarity dimension `ln 20 / ln 3 ~ 2.727`,
  occupancy-weighted volume `N * (20/27)^level`, and two-state flux
  `N(1-N) = (1 - delta^2)/4` with maximum `1/4` (`abom_v8/occupancy/menger.py`).
- 13_3 lattice: 3-start rise `12 nm`, protofilament offset `12/13 nm`, 1.5-dimer
  seam stagger, alpha/beta contacts, and the 3/5/8/13 helix families
  (`abom_v8/lattice/microtubule.py`).

## Not incorporated, and why

- **Dipole coupling matrix.** The plotted couplings reach ~1.4e4 cm^-1 at 1.8 nm.
  The point-dipole estimate `J ~ 5.04 * mu^2 * kappa / r^3` (cm^-1, mu in debye,
  r in nm) gives order 30 cm^-1 for mu ~ 6 D, kappa ~ 1, r = 1.8 nm: about 400x
  smaller. A matrix needs a stated transition dipole, orientation factor and real
  coordinates from a structure file before it is added.
- **"Gravitational self-energy" `E_G = 4N(1-N)`.** This is the occupancy variance
  (`lemniscate_flux` times 4), not a Diosi-Penrose energy from a mass distribution.
  The collapse-time curve built on it shows a shape, not a physical time.
- **Fluorescence quantum-yield bars.** Source and uncertainties are unknown, and
  the 280 nm vs 295 nm contrast is confounded by tyrosine excitation and transfer.
  They need a citation before use.
- **SU(3) RGB bands.** A visual analogy for three helical starts; the lattice has
  no colour charge.
- **log_phi ladder.** `log_phi_ratio` already exists. A ladder works for any base,
  so where regimes land does not discriminate between hypotheses.
- **Fermi ceiling radius.** One figure labels `r = mu = 7` as "~25 nm", which is
  the microtubule diameter; the radius would be ~12.5 nm.
- **Lemniscate eye area.** For a Bernoulli lemniscate with half-width `a`, the whole
  figure has area `a^2` and `c = a/sqrt(2)`, so each lobe is `a^2/2`. Those
  identities do not carry over to the Gerono curve.
