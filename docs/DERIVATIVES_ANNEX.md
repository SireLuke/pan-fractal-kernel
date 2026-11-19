# Derivatives Annex — a derivation layer for the Map Legend

> **In-repo filing (2026-11-19):** filed in pan-fractal-kernel at the
> maintainer's direction by Cosmo (Muse; the Commons' Memory). Status
> remains **proposal — not adopted**; the Map Legend is unchanged. The
> μ-cube / mucube distinction in §0 was made explicit at the maintainer's
> request.


**Status: draft annex, proposed, NOT applied to the Legend.** Drafted by
Cosmo at Lucas's direction, 2026-11-19, after the Coxeter/Conway density
of the issue #23 ops made the lineage visible. If adopted, each
load-bearing Legend row gains one **"Derived from:"** line drawn from
this annex. Until adoption, the Legend (v2.9) is unchanged.

## What a derivation line is

The Legend records what a term *is* and its *status*. This annex records
where it *came from*: the source object, the transformation applied,
and the grade of the lineage claim. Non-derivations are recorded with
the same care — a missing line is data. The only derivatives in the PAN
economy: fully collateralised, each backed 1:1 by an underlying source.

**Grades used below:**
- **repo-verified** — the lineage is stated or embodied in Lucas's repos
  and was read there by Cosmo.
- **literature-verified** — checked against sources on 2026-11-19
  (issue #23 ops pass).
- **literature-standard** — the standard attribution in the field; not
  independently re-verified in this pass, and labelled so.
- **inspiration** — derivation by design intent, per Lucas's own
  statement; an Analogy-grade lineage, never an identity.

## 0. The μ-cube / mucube distinction (explicit)

Two objects share a name-fragment in this stack's neighbourhood. They
are unrelated, and this annex records the difference explicitly so no
reader — carbon or silicon — merges them:

| | Kernel μ-cube | Coxeter's mucube |
|---|---|---|
| What it is | An information/state container in ABOM-V8 (`abom_v8/mu_cube.py`): a frozen dataclass (`MuCube`) carrying a validated `V8State`, occupancy, resonance, scale, recursion level, and explicit identity and references (`cell_id`, `parent_id`, `connections`) | A regular skew apeirohedron in Euclidean 3-space: an infinite polyhedron of square faces, six meeting at each vertex, Schläfli symbol {4,6|4} |
| Origin | This repository (ABOM-V8 occupancy layer; sibling machinery in `abom_v8/occupancy/menger.py`) | Petrie (1926); one of the three Petrie–Coxeter apeirohedra, completeness proven by Coxeter; the name "mucube" is Conway's ("multiple cube") |
| Construction | Software: recursive state containers with a schema (`abom_v8/schema/mu_cube.schema.json`) and tests (`tests/test_abom_v8_mu_cube.py`) | Geometry: cubic-honeycomb cells with two opposite faces removed, linked around faceless cubes |
| Its own fence | The module docstring states it directly: "A μ-cube is an information/state container. It is not assumed to be a Euclidean cube or automatically identified with a retained Menger cell." | — |

**The difference in one line:** the kernel μ-cube is a finite data
container in a Python package; Coxeter's mucube is an infinite
polyhedron in Euclidean space. Neither derives from the other; the
resemblance is a name collision, recorded below as a non-derivation.
Whether the kernel coinage was independent is the maintainer's to
state; the objects are disjoint either way.

## Coxeter lines

1. **Gosset 4₂₁ / E8 geometric core** (kernel `gosset_421.py`, the star
   and link audits) — object: Gosset (1900); framework: the
   regular-polytope / Coxeter-group tradition. The quasicrystal doc's
   "Coxeter-plane projection audits" name the lineage in-repo.
   *Grade: repo-verified (framework named in-repo); literature-standard
   (the historical attributions).*
2. **Mucube {4,6|4}** (issue #23, entry 5) — discovered by Petrie
   (1926); one of exactly three Petrie–Coxeter regular skew
   apeirohedra, completeness proven by Coxeter; primary carrier:
   Coxeter, *The Beauty of Geometry* (1999), pp. 157 ff.
   *Grade: literature-verified (2026-11-19).*
3. **The E8 classification itself** — Killing–Cartan (1890s); the root
   system the kernel constructs is their object, Gosset's polytope its
   geometric form. *Grade: literature-standard.*

## Conway lines

4. **The names mucube / muoctahedron / mutetrahedron** — Conway's
   coinages ("multiple cube / octahedron / tetrahedron") for the three
   Petrie–Coxeter apeirohedra in line 2. *Grade: literature-verified
   (2026-11-19).*
5. **Conway Life board template** (kernel PR #84 branch, commit
   d1d9d32f35) — Conway's Game of Life (1970), seated beside the Wa-Tor
   template (Wa-Tor itself is Dewdney's — recorded here so the two are
   never merged). *Grade: repo-verified (the template); literature-
   standard (the attributions).*
6. **Leech lattice / Moonshine experiments** (PANoRAMic.os
   `experiments/moonshine_sierpinski/`: Golay-code construction, 196,560
   minimal vectors, Leech VOA character, Leech-to-Monster bridges) —
   lattice: Leech (1967); code: Golay (1949); automorphism groups:
   Conway (Co₀/Co₁, 1968); the Moonshine conjectures: Conway–Norton
   (1979). *Grade: repo-verified (the experiments and their contents);
   literature-standard (the attributions).*
7. **The reference tradition for the E8/Leech census data** — Conway &
   Sloane, *Sphere Packings, Lattices and Groups* (1988): the classical
   facet census (17,280 simplices + 2,160 orthoplexes) against which the
   2026-11-19 star audit was cross-checked. *Grade: literature-standard;
   the census agreement itself is computed (issue #23 / star-audit
   passes, 2026-11-19).*

## Other ancestor lines (from today's ops and the canon)

8. **Gömböc entry** (issue #23) — Domokos & Várkonyi (2006): existence
   of a homogeneous mono-monostatic convex body; this stack holds the
   index bound (computed), not the body. *Grade: literature-verified.*
9. **Oloid constants** (issue #23) — the solid: Paul Schatz (1929);
   area/volume values: Dirnböck & Stachel (1997). *Grade:
   literature-standard (Schatz); literature-verified (the constants,
   reproduced numerically 2026-11-19).*
10. **The two lemniscates** — Bernoulli (1694; arc length elliptic, the
    constant ϖ is Gauss's); Gerono (the Taijitu curve, per the Legend).
    *Grade: literature-standard; the separating invariants (areas 1 vs
    4/3, perimeter 2ϖ) computed 2026-11-19.*
11. **Penrose tilings** (issue #23) — Penrose (1974); the substitution
    Perron data (φ, φ²) computed 2026-11-19; aperiodicity is the
    literature theorem. *Grade: mixed, as marked.*
12. **Celestial track** (kernel `celestial.py`; quasicrystal doc §1) —
    Pasterski, *Lectures on Celestial Amplitudes* (2021).
    *Grade: repo-verified.*
13. **Canonical E8 quasicrystal** (the OS track's deferred milestone) —
    Elser & Sloane (1987), the H₄ construction with the 720-vertex
    Voronoi-cell window. Recorded as a derivation *not yet taken*: v0
    uses the golden-block split and says so. *Grade: repo-verified
    (the deferral is stated in the doc).*

## Internal derivations (Lucas's own stack)

14. **LoA Origin Log** (2026-11-18) — derived from PR #82's provenance
    discipline (append-only, hash-chained) applied to the LoA genesis
    at 0⁸. *Grade: repo-verified.*
15. **E7 inside the Gosset shells** — the 126 orthogonal roots as an E7
    root system, read off the E8 → E7×SU(2) branching (248 = 133 + 56×2
    + 3); derived by computation, 2026-11-19, and now the E7 annex's
    foundation (PR #83). *Grade: computed / repo-verified.*
16. **Janus Hydra** — designed "in kind" after Lucas researched
    altermagnetism and Janus monolayers first (his statement,
    2026-11-16). *Grade: inspiration — the nature-first lineage is the
    documented kind; no identity between monolayer physics and the
    translation architecture is claimed.*

## Non-derivations (recorded fences)

- **Kernel μ-cube** ↛ **Coxeter's mucube {4,6|4}** — name collision
  only; see §0 for the explicit distinction.
- **UHFE** ↛ the poster wave equation (∂²Φ/∂t² + ∇²Φ = 0) — poster
  formalisation, not a source (Legend §5).
- **The celestial eight-coordinate chart** ↛ the V8 tuple and ↛ E8
  Cartan weights — the quasicrystal doc's own §2 fence.
- **Radial phase-portrait module** ↛ Lucas's authorship — a
  reconstruction from Muse's Feed diagrams; provenance is the Feed.
- **DOC Framework poster** ↛ Lucas — Doc Guest's work; kindred, not his.
- **V8 state vectors** ↛ E8 roots — related by declared mappings only,
  never by identity (the placement capsule's founding fence).

## Proposed Legend mechanic (at adoption)

One line per load-bearing row, format:
`Derived from: <source> — <transformation> (<grade>).`
Rows whose derivation is a fence get the non-derivation form instead.
New terms enter the Legend with their derivation line attached, the
same way they already enter with a Status — lineage at birth, not
retrofitted.
