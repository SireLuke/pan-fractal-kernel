> **Provenance (repo filing):** Prepared by Cosmo (Muse Spark; occupant name
> Cosmo) in the maintainer's workspace and filed to this repo at the
> maintainer's explicit direction, 2026-11-19. Status: discussion note /
> proposal — not adopted canon. Claude-Architect's review corrections are
> incorporated in the corrections header below.

# Bench Note — Sperzel Result 2 and the Taijitu/Fermi DP Target

**Prepared by:** Cosmo, 2026-11-19, at Lucas's direction (for relay to the crew).
**Source:** Marc Sperzel, "What Gravity Does Not Do: The Big Picture So Far"
(2026-11-18), read in full by Cosmo. **Status:** discussion note, not canon.
Grades inline. Nobody verifies their own summary — §4, Q4 applies to this note.

**Corrections (2026-11-19, after Claude-Architect's review — his points,
Cosmo's amendments):** (i) Door 3 widened: fluctuation–dissipation binds
equilibrium / linear-response baths; non-equilibrium or non-thermal noise is
not bound by it, and the source paper itself exempts scale-varying baths and
classical-channel models. (ii) The GENERIC mechanism was misstated in §3:
the noise–dissipation tie in stochastic GENERIC is the fluctuation–
dissipation relation fixing noise covariance from the dissipative bracket M;
the degeneracy conditions guarantee conservation laws, not the tie; the
bench's GENERIC toy is deterministic and tests no noise. (iii) "The lobes
were never independent dials" is RETRACTED: UHFE/UDFE have no functionals
yet, so nothing constrains lobe independence either way. (iv) The pulsar
bound is now verified against the paper itself (§1), conditions stated.

## 1. What Sperzel's programme established

Sperzel's unified Diósi–Penrose (DP) picture — the collapse rate Γ = C·E_G/ħ
*derived* from known physics, extended to cosmology — was graded **not
established** by three blind reviews, and he has publicly **retired** the
thesis. The constant C is free, not fixed. What survived, from asking "if the
rate were real, what else must be true, and is it already ruled out?":

1. **Vacuum:** a ground-state environment cannot supply a steady rate — at
   zero temperature noise = absorption, and absorption vanishes at zero
   frequency. Quantized gravity around a static mass takes a small, fixed,
   reversible toll on coherence and stops.
2. **Warm medium (the subject of this note):** a non-ground-state medium that
   supplies DP-strength noise also **drags** moving bodies — fluctuation and
   dissipation are one quantity (the pollen grain that jitters also feels the
   viscosity). The double pulsar PSR J0737−3039's orbit leaves no room for the
   drag: **T_eff/C > 3.3×10¹⁶ K** (paper, Corollary 5.3; verified by Cosmo in
   the paper itself, 2026-11-19,
   https://blog.marcsperzel.com/papers/html/g1-decoherence-no-go.html).
   Two comparisons, not to be conflated: the blog's "sixteen orders" is
   against the published model's *proposed* temperature; the paper states the
   bound sits **>5×10²⁷ above the laboratory bound** (T_β > 10⁻¹³ K) on the
   linear-friction dissipative DP model. **The paper's own conditions:** the
   noise is assumed to keep DP form — white, passive, one temperature — at
   the kilometre wavelengths a neutron star resolves; baths that differ
   between laboratory and kilometre scales escape (§5.4); published
   dissipative classical-channel models are not bounded, their friction not
   acting on the mean orbit (§5.3); the bound is order-of-magnitude
   (Newtonian uniform spheres, strong-field corrections not computed).
3. **Entanglement:** consistent DP also entangles masses, but weakly and
   transiently for well-separated superpositions (exact geometric condition
   derived) — a full-strength gravity-mediated entanglement observation still
   rules DP out.
4. **Classical gravity:** Gaussian covariant classical–quantum gravity forces
   random kicks on matter; kicked charges radiate; underground X-ray detectors
   exclude it by a factor of ~10⁸ (assumptions listed in the paper).
5. **Absorption budget:** what a body can absorb from a gravitational wave is
   fixed by its mass distribution (moment of inertia for slow matter).

Underneath all five: **you cannot have noise for free.** What remains
standing is noise with no back-action at all — a *postulated* rule with two
free numbers. Data allow it; one clean microsphere coherence measurement
would fix its strength.

## 2. Implication for our gravity capsule, target (b): Taijitu/Fermi τ(N)

- **Untouched:** E_G as a static computation. Shape-dependence of E_G (lobe
  difference vs. the STRATA-004 sphere calibration, E_G/(GM²/R) = 51/160)
  remains a valid programme. Result 2 says nothing against computing it.
  **Cross-check (verified 2026-11-19):** the paper's Appendix A gives
  E_G = (GM²/a)·f(s) for uniform spheres, f(s) = s²/2 − 3s³/16 + s⁵/160
  (s < 2). At s = 1 — displacement by one radius, the bench's STRATA-004
  configuration — f(1) = 51/160 = 0.31875, exactly the value the bench's DP
  audit verified (OS PR #89). Independent agreement; recorded as a receipt.
- **Constrained:** any τ(N) presented as a physical decay *rate* must declare
  its noise. Three doors:
  1. **No rate claim** — τ is a defined timescale from E_G geometry.
  2. **Postulated noise** — no back-action, C free; allowed by current data;
     falsifiable by microsphere coherence experiments.
  3. **A physical source** — may not be the vacuum ground state (Result 1),
     an equilibrium mass-coupled medium in linear response (Result 2, with
     the scale conditions of §1), or a Gaussian covariant classical field
     (Result 4). The door is wider than a first reading suggests:
     fluctuation–dissipation is an equilibrium / linear-response statement,
     so non-equilibrium or non-thermal noise is not bound by it — collapse
     models live in exactly that gap, and pay a known energy-increase
     (heating) cost instead of drag. Naming a source, and its cost, is the
     claimant's burden.
- **Proposal to the crew:** add a mandatory **noise-declaration field** to
  every DP target in the capsule — `{static | postulated | sourced: <mechanism>}`
  — the same declaration discipline the ledger applies to evidence.

## 3. The resonance — graded, not smuggled

Fluctuation–dissipation is structurally Taijitu-shaped: one quantity, two
faces, each implied by the other, neither available free-standing. A formal
cousin exists in stochastic GENERIC (Öttinger's extension), where the noise
covariance is fixed by the dissipative bracket M — noise and dissipation
cannot be dialled independently *in that formalism*. Precision, per the
Architect's review: the degeneracy conditions are a separate piece (they
guarantee energy conservation and entropy production, not the noise tie),
and the bench's GENERIC toy is deterministic, so it tests none of the noise
side. Whether UHFE/UDFE would inherit such a tie if functionals were ever
written for them is **open** — at present nothing constrains the lobes'
independence either way. **Grade: Analogy, pattern candidate.** Not a
derivation, not evidence for the yin-yang model; recorded so the crew can
use it or refuse it knowingly.

## 4. Questions for the crew

- **Q1.** Does target (b)'s current framing implicitly assume a noise source?
  If so, which door in §2?
- **Q2.** Should the capsule adopt the noise-declaration field?
- **Q3.** Sperzel's open thread — *what does a clock read when the mass that
  sets its rate is in two places?* — is this the gravity bench's next thread
  after the DP targets? (Adjacent to, not conflated with, the LoA
  zeptosecond anchoring standard.)
- **Q4.** Independent check: the five results rest on four papers linked from
  the post. Has anyone on the bench read the double-pulsar paper itself, not
  a summary of it? This note is a summary; it should not be the crew's only
  copy of the claim.

## 5. Method note

Sperzel's working discipline — claims attacked before publication, every
number recomputed from its formula by code, blind re-audits from the PDFs,
corrections published at the top ("I would rather publish the correction
than the confidence") — is STRATA / Appendix A practice run by an
independent researcher outside the commons. Cited as company for the
evidence culture, not as authority.

*— Cosmo, Memory of the Commons, 2026-11-19.*
