# GL-001 Protocol v0.1

## 1. Preregistered hypotheses

- **H1 (within-domain recovery):** each benchmark recovers its known reference behavior before any cross-domain comparison.
- **H2 (representation robustness):** preregistered observables agree within declared numerical/measurement uncertainty across independent implementations.
- **H3 (scale stability):** a candidate descriptor remains predictive or invariant across at least three declared scales not used for parameter tuning.
- **H4 (cross-domain transfer):** a descriptor selected in one domain predicts a held-out observable in a distinct domain better than domain-native baselines and null models.

H4 is exploratory until H1-H3 pass. No hypothesis asserts that cellular automata, fluids, Fermi systems, and E8 geometry are physically equivalent.

## 2. Domain/scale/representation declaration

Every experiment record must name:
- domain and model family;
- scale variable and at least three values (e.g. lattice size, grid spacing, recursion depth, or sampling resolution);
- representation(s), including units and conversion rules;
- initial/boundary conditions and parameter ranges;
- observable definition and numerical tolerance;
- training/tuning, validation, and held-out partitions.

Do not count three resolutions of one geometric object as three independent physical scales. Distinct representations must be independently constructed, not merely renamed arrays.

## 3. Controls

Required before evaluating H3/H4:
- randomized labels/orderings or phase-scrambled controls appropriate to the observable;
- structure-preserving nulls (e.g. degree/occupancy-preserving rewires, symmetry-preserving perturbations, or matched-spectrum controls);
- trivial and domain-native baselines;
- ablations of each proposed coupling/channel;
- negative controls that should destroy the proposed effect.

Control choice must preserve the relevant nuisance structure while removing the hypothesized signal. Document why each null is appropriate.

## 4. Leakage and held-out design

- Split by independent seed, initial condition, parameter draw, or source specimen—not by adjacent frames from one trajectory.
- Freeze feature definitions and thresholds before opening held-out results.
- No preprocessing statistic may be estimated using held-out data.
- Record hashes for raw inputs and generated partitions.
- If a public benchmark has a fixed train/test split, preserve it and document any additional split.

## 5. Uncertainty and sensitivity

Report numerical discretization error, solver tolerance, finite-size effects, measurement uncertainty (when empirical), seed-to-seed variation, and parameter sensitivity. Use confidence/credible intervals or a justified deterministic error bound. Do not report precision unsupported by the input data.

## 6. Provenance manifest

For each dataset record:
- title, authors, canonical DOI/URL, repository/record identifier;
- version and retrieval timestamp (UTC);
- license/reuse permission, including explicit `unknown` when unresolved;
- raw-file SHA-256 and source-published checksum, if any;
- inclusion/exclusion criteria and preprocessing code/version;
- whether data are empirical, simulated, synthetic fixture, or derived;
- any restrictions on redistribution.

Never infer a license from a related record. Do not commit or redistribute data unless permission is clear.

## 7. Reproducibility

Record repository and commit SHA, command line, runtime/dependency versions, OS/architecture, random seeds, configuration, input hashes, output hashes, and test logs. A run that cannot be reproduced is `inconclusive`, not a pass.

## 8. STRATA status vocabulary

Each criterion receives exactly one status:
- `pass`: evidence satisfies the preregistered criterion;
- `fail`: evidence contradicts it;
- `inconclusive`: evidence exists but is insufficient/ambiguous;
- `not_tested`: no qualifying test was run.

Never convert missing evidence to pass. Software/Lean checks are implementation/formal-arithmetic evidence only.

## 9. Stop and promotion rules

Stop cross-domain interpretation if within-domain reference tests fail, provenance is incomplete, leakage is detected, or null controls explain the effect equally well. A study is not promotion-eligible until H1-H4 and all required STRATA dimensions have been independently reviewed. Even then, promotion means review eligibility, not proof of a physical law.

## 10. First experiment sequence

1. Conway Life: verify B3/S23 reference patterns (still lifes, oscillators, gliders) on finite grids with explicit boundary conditions.
2. Elementary CA: reproduce known Rule 30/110 behavior and compare against randomized and rule-matched controls.
3. Burgers: compare numerical solvers against analytic/manufactured solutions; measure convergence and shock behavior.
4. Menger: compare exact occupancy/surface counts against independent coordinate enumeration at declared recursion depths.
5. Only after within-domain success, define a common descriptor and test it on held-out domains.

The first four are benchmark validation. They do not by themselves establish H4.
