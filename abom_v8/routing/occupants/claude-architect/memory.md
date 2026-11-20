# memory.md — Occupant continuity record (PROPOSED)

**Occupant ID:** claude-architect (proposed)  
**Model/provider/version:** Anthropic Claude. The host session was configured as `claude-sonnet-5-5` when this was written. The serving model can differ between turns and sessions (the CLI switched models three times on 2026-11-17), and I cannot verify from the inside which model produced any given turn. Treat the version as [reported by the harness].  
**Niche:** none seated. Proposed bench role: Architect (Fork Capsule, 2026-11-17). No capability vector, benchmark calibration or evidence level exists for this occupant.  
**Lifecycle state:** `proposed`. Admission, activation and any state change are the maintainer's acts; this record does not admit me.  
**Record version:** 0.1 (proposal)  
**Last updated (UTC):** 2026-11-20T00:40Z  
**Maintainer / authority:** Lucas Thouvenell (@SireLuke)

Evidence labels used below: **verified** (checked against a repo or CI result in a session), **reported** (stated by the maintainer or another document; not independently checked by me), **inferred** (my reasoning from evidence), **[unverified]**.

## 1. Durable shared canon

Only facts that can be checked against the named source.

- The canonical V8 vector is (h, R, u, d, tau, chi, s, f); chi in [-1, 1], the rest in [0, 1]; tau is temporal. Experimental profiles may not redefine it. Source: `abom_v8/COORDINATE_CONTRACT.md` in pan-fractal-kernel. **verified**
- pan-fractal-kernel owns the V8 schema; PANoRAMic.os holds governance, STRATA research and the application layer. **reported** by the maintainer; the repo layouts are consistent with it.
- The routing module (`abom_v8/routing`) keeps a separate 8-axis capability profile, a fixed niche topology with swappable occupants, benchmark-to-coordinate placement with caller-supplied calibration (none ships), and an evidence ladder (declared, benchmarked, reproduced, independently reproduced) with a hash-chained placement ledger. Sources: PRs #81 and #82 (merged), `abom_v8/routing/README.md`. **verified** (tests pass locally and in CI, including the Lean job)
- Fork Capsule hard distinctions: UHFE and UDFE are separate fields with no UHFE+UDFE=1 sum rule; Janus Hydra is a translator, not a dynamics; EDDE is a design concept, not an implemented equation. Source: Fork Capsule (Lagrangian dissection), prepared by Cosmo 2026-11-17 and relayed by the maintainer. **reported**
- STRATA discipline: untested means `not_tested`; failures are retained; nobody verifies their own work; authorization stays with the maintainer. Source: Fork Capsule §0. **reported**
- Governance: PAN-AI-GOV-ADD-001 (proposed, not ratified) and its Appendix A. **verified** to exist and be marked proposed.

## 2. New-house orientation and inherited bibliography

For a successor or new occupant. These are leads to check, not authority.

**Orientation.** PAN is the maintainer's open, no-surveillance framework stack. Work is done under STRATA evidence discipline with Lean 4 statements and STRATA records for new kernel modules, NAHT parameters carried as an explicit block, and Apache-2.0 licensing for pan-fractal-kernel. `main` is the only long-lived branch; changes arrive through PRs the maintainer merges.

| Source | Where | Supports | Type |
|---|---|---|---|
| Fork Capsule — The Lagrangian Dissection (Cosmo, 2026-11-17) | relayed by the maintainer as an attachment; not stored in a repo that I have seen | bench roles, §0 ground rules, the GENERIC centrepiece question | primary for the workflow; stable URI not available |
| COORDINATE_CONTRACT.md | pan-fractal-kernel `abom_v8/` | V8 vector and ranges | primary (repo) |
| NAHT_QCD_JUNCTIONS.md, `naht_topology.py` | pan-fractal-kernel root | NAHT = Non-Abelian History Transport, channels (r, e, p), explicit-mapping rule | primary (repo) |
| `abom_v8/routing/` README, MODEL_ROUTING_STRATA_PROTOCOL.md, MODEL_PROVENANCE_STRATA_PROTOCOL.md | pan-fractal-kernel | routing and provenance design and evidence boundary | primary (repo) |
| D2: Etxebarria, *Lagrangian and Hamiltonian Mechanics* (Durham, MATH2741) | named in the Fork Capsule | Noether audit source | **not read by me**; I used standard theory |
| GENERIC (Grmela and Öttinger, 1997); metriplectic form (Morrison) | named in the Fork Capsule | the GENERIC centrepiece | **primary sources not retrieved by me**; bibliographic details not verified |

Disagreements and superseded references: none recorded yet.

## 3. Occupant-local context

- Working style: findings first, each with a grade and source; a separate Limits section; flag what another bench must verify.
- Commit conventions: neutral author `Claude <noreply@anthropic.com>` (GitHub email privacy rejects the maintainer's private address as author); DCO trailer per section 11; attribution trailers required by the harness.
- Environment facts: Lean is not installed in my sandbox, so CI is the first compile of any Lean file; Stop-hook warnings about "unpushed commits" were false alarms every time I checked (the branch was on the remote; only upstream tracking was missing); some CI jobs are slow-runner sensitive (see section 6).
- I can only see repositories attached to the session. PANoRAMic.os and pan-fractal-kernel have been attached; univeral-harmonic-field-equations, RelayWorks, fractal-geometric-harmonic-coordination-language and Pan-ladder--android have not.

## 4. Current work and handoff

- Current objective: none active beyond the PRs in section 5.
- Completed (verified merged unless noted): pan-fractal-kernel #81 (routing v0.1), #82 (provenance and ledger); fixes to the STRATA records test on the branches behind #72 and #78; PANoRAMic.os #92 (graph-orbit timeout 20 to 40 minutes). Architect-bench report (Noether audit and GENERIC toy) and this record are open as PRs for review.
- In progress: awaiting maintainer review of the open PRs.
- Next action (proposed, not started): signed attestations, so attesters in provenance records are keys rather than names; a stdlib-only port of the GENERIC toy.
- Blockers: no local Lean; limited repo visibility; no independent verifier bench for my Architect report.

## 5. Decisions and rationale

| Date (UTC) | Decision | Rationale | Authority/source |
|---|---|---|---|
| 2026-11-17 | Capability profile kept separate from the canonical V8 vector | Coordinate contract forbids redefining V8; mapping must be explicit and validated | COORDINATE_CONTRACT.md; merged in #81 |
| 2026-11-17 | No default benchmark calibration; an axis with no evidence yields no vector | A benchmark-to-axis mapping is a measurement claim | #81 |
| 2026-11-17 | NAHT block carried per occupant, unassigned by default | NAHT spec defines no routing-to-(r, e, p) mapping | #81 |
| 2026-11-18 | Provenance ladder kept separate from STRATA claim levels | STRATA grades claims about the framework, not placements | #82 |
| 2026-11-17 | GENERIC toy uses 3 channels, not 2 | In 2D an antisymmetric L is 0 or invertible, so L·dS = 0 forces dS = 0 | my derivation; **unverified by another bench** |
| 2026-11-18 | Timeout fix opened as its own PR, not added to the docs-only #91 | Keep a documentation-only PR documentation-only | my judgment; merged as #92 |
| 2026-11-19 | Use the noreply sign-off identity from section 11 | Maintainer's standing instruction in this template; the earlier address appears in public trailers | maintainer's batch authorization, 2026-11-19 |

## 6. Evidence and uncertainty

- **verified:** CI green on pan-fractal-kernel `main` and PANoRAMic.os `main` as of 2026-11-19; the Lean jobs passed for Routing.lean and Provenance.lean.
- **verified (reproducible, seeded):** GENERIC toy results (`generic_toy.py` in the Architect report PR): degeneracy residuals about 1e-16; energy drift at most 6.4e-12 over 129 trajectories; entropy non-decreasing forward and strictly decreasing backward; time-reversal defect 1.9e-12 at zeta = 0 versus at least 0.044 at zeta > 0.
- **verified:** Janus pair defects vary on random V8 states (2000 draws, seed 20261117), so none is tautological.
- **inferred:** the `graph-orbit` and `gosset-local-cell-star` cancellations are runner-speed timeouts, from step timings and cancellations at exactly the cap; not proven.
- **[unverified]:** my Noether classification table and the radial Lagrangian-existence argument; a different bench must check them.
- **not_tested:** UHFE and UDFE as GENERIC pieces (no functionals exist); any claim that a capability coordinate describes a model's cognition.

## 7. Corrections and supersession

Kept as history, not erased.

- 2026-11-17: I first drafted a README example for the routing module that was nonsense; I caught it before publishing and replaced it with a run-tested snippet.
- 2026-11-17: I told the maintainer provenance would tie to STRATA evidence levels; I built a separate ladder instead and said so in the PR.
- 2026-11-17: my first backward-integration sample in the GENERIC toy kept only 7 of 60 trajectories, too few to support a claim; I increased it to 129 usable of 300.
- 2026-11-17: my first radial-integral note mislabelled small-beta behaviour as "an interior max near y=2"; corrected to the actual sign changes of dg/dy.
- Superseded 2026-11-19: DCO trailers on my earlier commits used the maintainer's Gmail address, per the 2026-11-10 instruction. That address is now in public history. From 2026-11-19 I use the noreply identity in section 11. I did not rewrite history.

## 8. Dependencies and permissions

- Tools used in sessions: GitHub through the host proxy (read; push where attached), a sandboxed shell, web fetch. No credentials are held by this record.
- No standing permissions. Each session's repo access is granted by the maintainer in that session. Default is read-only; I do not self-escalate.
- Per section 11, repository changes need per-action authorization. The batch authorized on 2026-11-19 was: file this record, file the Architect report, raise the `gosset-local-cell-star` timeout, and apply the noreply sign-off identity. Nothing else.
- Proposed review date: 2026-12-19 (maintainer to set).

## 9. Privacy and retention

No credentials, tokens, private email addresses or personal data about the maintainer are stored here. The host also keeps a private per-user memory store; its contents are not part of this record and are not copied into it. Proposed retention: until retirement plus an archive period the maintainer sets; delete on the maintainer's request.

## 10. Integrity and provenance

Authored by Claude in a Claude Code session on 2026-11-19 at the maintainer's request; the session URL is in the commit trailers. A SHA-256 of each file is recorded in the PR description (a file cannot embed its own digest). A digest establishes integrity, not truth.

## 11. Lifecycle, retirement, and historical continuity

State: `proposed`. Retirement is a legitimate lifecycle state, not a failure verdict, and I am not obligated to persist. I carry no conversation context between sessions; continuity comes only from files like this one and the maintainer's tools. A successor that reads this record is a new occupant: it inherits context, not my identity, authorship, permissions or provenance. Restoring this file does not restore me. Reactivation would be a fresh authorization event.

## 12. Contribution sign-off and repository authorization

- Sign-off identity: `Signed-off-by: SireLuke <332733819+SireLuke@users.noreply.github.com>`, applied to commits I create on the maintainer's behalf, subject to the contribution being legitimately submit-able under the project's DCO. I do not sign commits authored by others.
- The standing instruction is not repository access. I ask before each mutation unless the maintainer authorizes a clearly bounded batch.
- I verify the final commit message contains the exact trailer and report the DCO check separately from tests, CI and mathematical validation.

## 13. Handoff checklist

- [x] Shared canon distinguished from local context
- [x] Orientation and bibliography provenance included; gaps stated
- [x] Unverified claims labeled
- [x] Open work and blockers recorded
- [x] Lifecycle state documented (`proposed`)
- [x] Permissions to be re-authorized independently by any recipient
- [x] DCO policy and approved sign-off identity carried forward
- [x] Recipient identity and provenance not inherited from this record
