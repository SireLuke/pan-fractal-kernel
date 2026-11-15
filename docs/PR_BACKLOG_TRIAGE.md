# Pull-request backlog triage

Snapshot reviewed: 2026-11-14. This is a triage list, not a claim that every
listed PR is broken. Open drafts, closed-unmerged work, and already-merged
replacements are distinguished so completed work is not repeated.

## PAN Fractal Kernel

| PR | Current state | Subject | Triage |
|---|---|---|---|
| [#48](https://github.com/SireLuke/pan-fractal-kernel/pull/48) | Open draft, unmerged | Initial Lean 4 V8 schema | Compare unique commits against merged #53; port any unique work, then close as superseded if empty |
| [#49](https://github.com/SireLuke/pan-fractal-kernel/pull/49) | Open draft, unmerged | Initial Wilson gradient-flow diagnostic | Compare against merged #52; port any unique work, then close as superseded if empty |
| [#50](https://github.com/SireLuke/pan-fractal-kernel/pull/50) | Open, unmerged | Fermi-occupancy yin-yang geometry | Retain as active review item; the PR explicitly deferred the Barbershop and Fermi-lock design because their definitions were absent |
| [#51](https://github.com/SireLuke/pan-fractal-kernel/pull/51) | Open draft, unmerged | Lean 4 CI repair / V8 schema | Compare against merged #53; likely duplicate, but inspect before closing |
| [#9](https://github.com/SireLuke/pan-fractal-kernel/pull/9) | Closed, unmerged | Historical Janus phase integration | Historical disposition: #8 is merged; inspect only if a specific missing behavior is reported |

### Already merged; do not re-add as unfinished

- [#52](https://github.com/SireLuke/pan-fractal-kernel/pull/52) — Wilson gradient-flow diagnostic rebuild.
- [#53](https://github.com/SireLuke/pan-fractal-kernel/pull/53) — Lean toolchain repair and PAN V8 formal schema.
- [#57](https://github.com/SireLuke/pan-fractal-kernel/pull/57) — Apache-2.0 license and thermalized Wilson-flow scan.
- [#58](https://github.com/SireLuke/pan-fractal-kernel/pull/58) — grouped/manual large-lattice scan workflow.

## PANoRAMic.os

| PR | Current state | Subject | Triage |
|---|---|---|---|
| [#72](https://github.com/SireLuke/PANoRAMic.os/pull/72) | Closed, unmerged draft | Exact E8 Weyl-root orbit / E7 stabilizer audit | GitHub metadata reports zero commits and zero changed files on the closed PR; do not assume its proposed implementation is recoverable from the PR. If still wanted, rebuild from current main as a fresh audit. |

## Execution order

1. Diff Kernel #48 and #51 against merged #53; preserve any unique changes before closing duplicates.
2. Diff Kernel #49 against merged #52; preserve any unique changes before closing the old draft.
3. Review and validate Kernel #50; decide whether it should merge independently or be updated to depend on the Feynman–Barbershop experiment.
4. Decide whether PANoRAMic.os #72 remains a priority; if yes, create a fresh branch from current main and rerun its exact-arithmetic audit.
5. Leave Kernel #9 archived unless a concrete missing integration requirement is identified.

No PR is closed, reopened, merged, or force-updated by this document.
