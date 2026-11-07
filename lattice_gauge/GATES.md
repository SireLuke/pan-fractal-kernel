# NAHT-LG-001 release gates: what CI checks and what it cannot

| Gate | Automated here? | How |
|---|---|---|
| Conformance suite against exact / published values | Yes | `tests/test_lattice_gauge.py` (9 checks) |
| Core independent of PAN | Yes | `tests/test_core_independence.py` (import allow-list: numpy, scipy, stdlib) |
| DCO sign-off | Yes (PRs) | workflow step checks `Signed-off-by:` on each commit |
| Licence choice (AGPL-3.0 candidate) | **No** | pending counsel review; I am not a lawyer |
| Patent-review gate | **No** | human/legal process |
| NAHT-SAFE-001 covenant (separate from licence) | **No** | human/legal process |
| Not pushed to main | Partly | workflow ignores `main` pushes; branch protection must be set in GitHub settings |

A green CI run means the numerics match their references. It is not certification and not a legal clearance.
