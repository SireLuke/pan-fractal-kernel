# Model provenance STRATA protocol (ABOM-V8-PROVENANCE-001)

**Status:** preregistered scope for a software-only module. Project attribution: Lucas Thouvenell (@SireLuke).

## Claim under test

In `abom_v8/routing`:

1. A placement digest is tamper-evident: changing the model id, the coordinates or
   any recorded evidence field makes `Provenance.verify` fail.
2. Evidence gates are monotone: raising an occupant's evidence level never makes it
   ineligible for a niche or task it previously met.
3. Each level's requirements (sources, distinct attesters) are enforced at creation.
4. Every successful seat and vacate is appended to a hash-chained ledger in the same
   shape for every model, and a failed seat or rejected placement appends nothing.

## Evidence

| Dimension | Status | Basis |
|---|---|---|
| formal_verification | pass | `formal/PAN/ABOM/Provenance.lean` (gate order and list append only) |
| two_representations | pass | Python SHA-256 chain and exact Lean statements over Nat and lists |
| three_meaningful_scales | not_tested | evidence levels are ordered categories, not scales |
| two_independent_domains | not_tested | one software construction |
| observer_implementation_checks | not_tested | no independent implementation |
| randomized_control | not_tested | deterministic claims |
| structure_preserving_control | not_tested | not preregistered |
| held_out_predictive_evaluation | not_tested | no predictive claim |

Evidence level: `software-smoke-test`. Promotion-ineligible.

## Evidence boundary

- A valid digest shows a record is unaltered, not that the benchmarks were honest.
- Attester names are caller-asserted; there are no signatures or identity checks.
- The hash chain detects edits to a copied ledger. A holder of the whole ledger can
  recompute it, so the head hash must be anchored outside the ledger.
- Lean does not cover SHA-256 or chain integrity.
- Placement evidence levels are not STRATA claim levels.
- NAHT channels remain an unassigned parameter block on each occupant.

## Reproduce

```
python -m pytest -q tests/test_abom_v8_routing_provenance.py tests/test_abom_v8_strata_records.py
```
