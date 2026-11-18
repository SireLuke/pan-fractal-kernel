# Model routing STRATA protocol (ABOM-V8-MODEL-ROUTING-001)

**Status:** preregistered scope for a software-only module. Project attribution: Lucas Thouvenell (@SireLuke).

## Claim under test

Capability placement and routing in `abom_v8/routing` are deterministic and
model-agnostic:

1. The per-axis capability distance is a metric (identity, symmetry, triangle inequality).
2. Seating a model in an occupied niche leaves the set of occupied niches unchanged.
3. The routing choice depends only on capability vectors, declared minimums and
   context size, never on model or vendor names.
4. The niche set is fixed at construction and unaffected by seat, replace or vacate.

## Evidence

| Dimension | Status | Basis |
|---|---|---|
| formal_verification | pass | `formal/PAN/ABOM/Routing.lean` (integer model; items 1 and 2 only) |
| two_representations | pass | float Python implementation and exact Lean statements over Nat |
| three_meaningful_scales | not_tested | capability axes are normalised descriptors, not scales |
| two_independent_domains | not_tested | one software construction |
| observer_implementation_checks | not_tested | no independent implementation |
| randomized_control | not_tested | deterministic claims; random-vector metric checks are regression tests |
| structure_preserving_control | not_tested | not preregistered |
| held_out_predictive_evaluation | not_tested | no predictive claim |

Evidence level: `software-smoke-test`. Promotion-ineligible. Keep it that way
until independent controls, held-out evaluation and the other required
dimensions are met.

## Evidence boundary

- No claim that a capability coordinate describes a model's cognition, or that a
  benchmark score measures an axis. Calibration is caller-supplied and versioned; none ships.
- The capability profile is not the canonical V8 vector; no mapping is claimed.
- NAHT channels `(r, e, p)` are an unassigned parameter block; no routing-to-NAHT
  mapping is claimed (see `NAHT_QCD_JUNCTIONS.md`).
- Lean does not cover the floating-point router, benchmark placement or transports.
- Ollama is one transport; nothing here depends on it.

## Reproduce

```
python -m pytest -q tests/test_abom_v8_model_routing.py tests/test_abom_v8_strata_records.py
```
