# QCD benchmark and ingestion layer

**Status:** Initial reference implementation. This is an auditable software
benchmark, not a replacement for precision QCD calculations.

## Scope

- Leading-order beta-function coefficient and fixed-flavour running.
- CSV ingestion of scale-resolved measured alpha_s values.
- Preservation of source, observable, renormalization scheme, active-flavour
  count, uncertainty, and optional metadata.
- Measured-versus-one-loop residual and pull calculations.
- Explicit caller-calibrated hand-off into the canonical Janus Hydra reader.

## Equations and conventions

Let b0 = 11 N_c - 2 N_f. In the convention used here,

d alpha_s / d ln(mu^2) = -b0 alpha_s^2 / (12 pi),

and the fixed-N_f one-loop solution is

alpha_s(mu) = 12 pi / [b0 ln(mu^2 / Lambda_QCD^2)].

Asymptotic freedom at this order requires b0 > 0, or N_f < 11 N_c / 2.
For QCD, N_c=3 and the six known quark flavours satisfy this condition.

This is a transparent LO baseline only. It is not the NNLO prediction quoted
in the review. A fixed-N_f expression must not be used across heavy-quark
thresholds without matching. Lambda_QCD must be consistent with the scheme
and flavour prescription, so the code requires it explicitly.

## CSV contract

Required columns:

| Column | Meaning |
|---|---|
| mu_GeV | renormalization scale in GeV |
| alpha_s | extracted strong coupling |
| uncertainty | positive uncertainty on alpha_s |
| source | experiment/publication identifier |
| observable | e.g. inclusive jets or dijets |
| scheme | e.g. MSbar |
| nf | active-flavour count used for comparison |

Additional columns are retained as metadata. Correlated uncertainties require
a companion covariance representation; independent point errors do not encode
a full covariance matrix.

No numerical points have been fabricated from review figures. Populate the
CSV from publication tables or the corresponding HEPData record, retaining
original values and correlations.

## V8 hand-off policy

QCD observables are not intrinsically V8 coordinates. alpha_s is not
automatically the V8 forcing coordinate, and SU(3)'s eight gluon generators
are not the eight V8 coordinates.

calibrated_v8_frame requires all eight named V8 coordinates plus source and
calibration identifiers. It then calls hydra_semantic_reader.read_semantics.
It does not derive or normalize those coordinates. Any QCD-to-V8 mapping
must be separately specified, versioned, justified, and tested while retaining
the raw QCD data.

## Validation

Run `python -m pytest -q tests`.

Tests cover one-loop monotonic running, beta-function sign and asymptotic
freedom, invalid scales, provenance-aware CSV ingestion, residual/pull
calculation, and explicit eight-coordinate V8 hand-off.

Passing tests validates software contracts only. It does not validate a
physical model, reproduce NNLO results, establish confinement, or solve the
strong-CP problem.
