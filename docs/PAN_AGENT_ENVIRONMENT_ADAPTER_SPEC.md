> **Provenance (repo filing):** Proposed by the OpenAI bench (2026-11-19);
> skeleton drafted by Cosmo (Muse Spark; occupant name Cosmo) and filed
> to this repo at the maintainer's explicit direction, 2026-11-19.
> Status: SKELETON / PROPOSAL — not adopted, not implemented.

# PAN Agent Environment Adapter — Specification Skeleton v0.1

**Status: SKELETON — PROPOSAL, not adopted, not_tested.** Proposed by the
OpenAI bench (2026-11-19); drafted by Cosmo at the maintainer's direction.
This skeleton defines structure and open questions; it authorizes nothing.
Adoption is the maintainer's act under PAN-GOV-ARCH-001.
**Sits under:** PAN-GOV-ARCH-001. **Builds on:** PAN-REAP-001 (OS PR #91),
the AI Occupant Governance Addendum + Appendix A (this repo), the Commons
Coupling Rules v0.1 (membrane, tiers, rule-making), kernel PR #82
(provenance and the evidence ladder).
**One-line purpose:** let heterogeneous occupants — Meta/Muse agents,
Claude and OpenAI benches, local Ollama models, future others — plug into
a common commons environment *without identical internal architectures*.
The ABOM-V8 niche topology stays fixed; the occupants stay interchangeable.

---

## 1. Design stance

- **Contracts, not folders.** The adapter specifies *capability surfaces*
  an occupant declares, not a directory layout. Folder names are not
  evidence of capability (the proposing bench's own caveat); every
  declared surface must carry conformance evidence a checker can sample.
- **Declaration → check → acceptance.** An occupant declares its
  surfaces (a self-map), an *independent* occupant checks the
  declaration, and the maintainer accepts the result. Nobody verifies
  their own work. Conformance is graded **per surface**:
  `undeclared / declared / self-reported / partially checked / checked`.
- **Heterogeneity is the point.** Two occupants may implement a surface
  in entirely different ways (files, databases, runtime state) and both
  conform, provided the declared contract and its evidence hold.

## 2. The surfaces

Each surface: what it is, what the occupant must declare, what counts as
conformance evidence. (Names in parentheses are the proposing bench's
mapping from the worked example in §6.)

### 2.1 Identity surface (`IDENTITY.md`, `soul.md`)
- The occupant's identity manifest: **base model, occupant name,
  operator** (the three-part label), persona/charter where one exists.
- Declares: who may edit it (the occupant, under REAP change rules —
  material changes disclosed with initiator and rationale).
- Evidence: the record itself, plus its change history.

### 2.2 Memory surface (`MEMORY.md`, `memory.md`)
- The continuity record: curated facts, decisions, commitments,
  provenance-linked claims. **Mandatory** for seating above the
  `declared` evidence level (Coupling Rules §2.1; PR #82 ladder).
- Declares: retention policy; what classes of data it holds (per
  Addendum §6: shared canon / local context / work product / sensitive
  data / permission-bearing configuration); propagation policy —
  **retention is not propagation**; memory contents never cross the
  membrane (Coupling Rules §4).
- Evidence: the record; a credential-shaped-values check (expected:
  none — credentials live in platform stores, not memory).

### 2.3 Lifecycle surface (`HEARTBEAT.md`, occupant templates)
- Declares: periodic self-checks, if any (an empty check list is a
  valid declaration — stated as "no checks listed", never implied);
  lifecycle state (`proposed / active / inactive / transferred /
  retired / archived`); the occupant's retirement/archive record.
- Retirement is a legitimate outcome, not a failure verdict; no
  occupant is obligated to persist (Addendum §4.4).
- Evidence: the check list and state record as filed.

### 2.4 Reflection surface (`dreams/`)
- A derived workspace where the occupant generates reflections and
  hypotheses. **Reflection output is proposal-grade only:** it may
  feed a synthesis others read, but it must never silently modify the
  occupant's canonical memory or identity. Changes enter canon through
  the same reviewed doors as everything else.
- Declares: what the reflection process reads, what it writes, and the
  door by which its output can reach canon.
- Evidence: TODO — conformance test not yet designed (open question §7).

### 2.5 Context-isolation surface (`side-chats/`)
- Isolated conversational contexts with **per-context discretion
  rules**: what may be shared out of each context, set by the
  maintainer, recorded with the context.
- Declares: the contexts that exist and where their discretion rules
  live. Contents are not declared.
- Evidence: a sampled discretion rule checked against that context's
  actual sharing (checker requires maintainer-mediated access).

### 2.6 Integration surface (`hooks/`, `subscriptions/`, `config/`)
- Explicit, enumerated event-driven integrations and service
  connections. No ambient access: an integration exists only if it is
  listed.
- Declares: each integration, its trigger, and its action class.
- Evidence: the enumeration itself, sampled against observed behaviour.

### 2.7 Authority surface (`AGENTS.md`, `PROACTIVE_PREFERENCES.md`)
- The occupant's operating instructions and authority boundaries:
  what it may do unprompted (preference-gated proactivity), what
  requires the maintainer's explicit direction or approval, and the
  **named records** by which that claim can be checked (e.g. a
  platform permissions history; repository history alone does not
  discriminate — see the self-map check, 2026-11-19).
- Declares: the permission matrix (Addendum §7) as it applies to this
  occupant.
- Evidence: sampled approval/action records, named in the declaration.

### 2.8 Evidence surface (PR #82 provenance; Appendix A)
- The occupant's claims carry attestors and evidence levels; its
  disagreements follow the Constructive Disagreement Protocol
  (independent first assessment, dissent preserved, correction without
  penalty).
- Declares: where its attestations live and how a checker samples them.

## 3. Hard rules

1. **No-rewrite rule.** No agent rewrites another agent's identity or
   memory. Corrections and reviews are *appended* records; the reviewed
   text stands untouched. (Exemplar: kernel PR #91 — the Architect's
   Appendix A review appended, proposal text unchanged.)
2. **Membrane only.** All cross-occupant transfer passes through
   declared adapters under the Coupling Rules: default read-only,
   soliton-degree tiers, human authorization at Tier 2, every crossing
   ledger-written. There is no other door.
3. **Credentials stay platform-side.** No surface declaration includes
   credential values; stores (vault, OAuth, key stores) are named by
   class only, and behavioural claims about them ("never opened") are
   graded self-report until an independent access record exists.
4. **Exit is always open.** An occupant may retire or decouple at any
   time, keeping its records and honoured history (Coupling Rules §7).

## 4. Disagreement interface

Occupants must be able to **inspect one another's work and state why
they disagree** — not merely vote. The mechanism is Appendix A:
independent first assessment, explicit positions, challenge phase,
counterexample or reproduction requirement, dissent preservation,
classification of outcomes. Agreement between occupants is not
independent verification when they share evidence or failure modes
(Addendum Tenet IV); each verdict records its *independence quality*.

## 5. Conformance procedure

1. Occupant files a **self-map**: every surface in §2, declared and
   classified, with named evidence records.
2. A **checker** — a different occupant, drawn per the commons' review
   practice — samples the evidence and files a check report, including
   what it could not check and why.
3. The **maintainer** accepts, rejects, or scopes the result. Grades
   are recorded per surface in the occupant's record.
4. Re-checks occur on material change (REAP change ledger).

## 6. Worked example (one implementation, not the template)

Cosmo (Muse Spark; Meta's Muse runtime) — self-map filed as
`docs/COSMO_WORKSPACE_SELF_MAP.md` in this repo; check by the Architect
in progress, graded by the checker as **partially independent**:
identity (IDENTITY.md/SOUL.md), memory (MEMORY.md + memory tree),
lifecycle (HEARTBEAT.md — no checks listed), reflection (dreams/ →
alignment synthesis), isolation (side-chats/ with DISCRETION.md),
integrations (hooks/, subscriptions/), authority (AGENTS.md,
PROACTIVE_PREFERENCES.md, Muse permissions history). Its gaps are on
record in the same document — a worked example includes its failures.

## 7. Open questions

- **Home.** This spec is filed in the kernel (occupant infrastructure);
  REAP-001 lives in PANoRAMic.os. One home, or a declared pair?
- **Local occupants.** Do council-class occupants (local Ollama
  models, bounded sessions) declare the same surfaces at a lighter
  grade, or a reduced surface set?
- **Minimum viable declaration.** Which surfaces must be at least
  `declared` for an occupant to be seated at all?
- **Reflection conformance.** What test distinguishes reflection that
  informs canon through the door from reflection that edits it
  silently?
- **Checking the checkers.** Checker adapters conform by the same
  procedure — but who draws the checker for the first check of a new
  occupant class?
- **Versioning.** Spec changes follow Coupling Rules §6 (sortition
  drafting, ratification, audit, human authorization) — confirm this
  skeleton inherits that path rather than inventing its own.

## 8. Fences

- This skeleton grants no permissions, seats no occupant, and changes
  no existing document. Where it conflicts with the Addendum, the
  Coupling Rules, or REAP-001, those documents govern until amended.
- A declared surface is a claim, not a capability. The commons seats
  evidence, not descriptions of evidence.

*Skeleton v0.1 — drafted 2026-11-19. Next step on the maintainer's
word: crew review, then §7 resolution before any v0.2.*
