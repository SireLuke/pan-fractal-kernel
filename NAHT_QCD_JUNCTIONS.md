# PAN Non-Abelian History Transport (NAHT)
## QCD-inspired junction topology: Y and Delta network models

**Status:** Research specification / proposed Fractal Kernel subsystem  
**Scope:** Geometric and computational analogy informed by non-Abelian gauge theory and lattice-QCD results. This document does not claim that NAHT is QCD, that PAN variables are color charges, or that the proposed transport model is a physical gauge theory.

## 1. Purpose

NAHT extends the scalar retained-history proposal into a path-dependent, matrix-valued transport layer. Its central design question is whether a system can retain distinguishable history when multiple channels interact, merge at a junction, and subsequently separate—even when a scalar summary makes different histories appear identical.

The QCD three-quark system supplies a useful external geometric benchmark. SU(3) lattice-QCD studies compare a pairwise Delta-law parameterization with a Y-law parameterization in which three flux tubes meet at a junction. Large-separation ground-state results commonly support Y-shaped flux organization, while short-distance behavior and the transition between descriptions require care. NAHT borrows the network-comparison problem, not QCD's microscopic dynamics.

## 2. Keep the spaces distinct

| Object | Meaning | Space |
|---|---|---|
| QCD color | Fundamental SU(3) gauge degrees of freedom | Internal color space |
| QCD flux-tube geometry | Spatial distribution of gauge-field observables | Physical space / lattice |
| NAHT channels | PAN engineering decomposition of retained history | Three-channel state space |
| PAN V8 | Canonical semantic state | R^8, ordered (h, R, u, d, tau, chi, s, f) |
| Gosset 4_21 | Primary shared E8-root geometry | R^8 |

The eight Gell-Mann generators of su(3) are not the eight V8 coordinates. The three NAHT channels are not the three quark colors. Any mapping between these spaces must be explicit, versioned, and independently validated.

## 3. Three-channel history state

Define the proposed NAHT history state

\[
\mathbf q(\ell)=
\begin{pmatrix}q_r(\ell)\\q_e(\ell)\\q_p(\ell)\end{pmatrix},
\qquad \mathbf q\in\mathbb R^3.
\]

Engineering labels:
- **r — relational:** orientation and relationships among participating entities;
- **e — environmental:** embedding, boundary conditions, and external context;
- **p — phase/path:** ordered phase or wave-geometry history.

These are proposed PAN channels, not standard QCD observables. Store units, normalization, source provenance, and calibration version wherever applicable.

A minimal transport law is

\[
\frac{d\mathbf q}{d\ell}
=\omega(\ell)\hat{\mathbf n}(\ell)\times\mathbf q
+\mathbf C(\mathbf q,\varepsilon,\ell),
\]

where \ell is a declared path parameter, \omega is a rotation rate in that parameterization, \hat n is a unit rotation axis, \varepsilon is a strain/disturbance descriptor, and C is the explicit coupling/forcing term.

The rotational term is perpendicular to q, so

\[
\frac{d}{d\ell}\|\mathbf q\|^2=2\mathbf q\cdot\mathbf C.
\]

The norm is conserved only when q dot C = 0. Do not assume it is invariant unless the implemented coupling guarantees it. A selective-strain experiment may perturb only q_e; a global-strain experiment must perturb all channels. The target is **strain tolerance and history distinguishability**, not blanket strain immunity.

## 4. Non-Abelian transport layer

Represent the internal transport connection using Hermitian SU(3) generators T^a = lambda^a/2:

\[
\mathcal A_\mu(x)=A_\mu^a(x)T^a,\qquad a=1,\ldots,8.
\]

With this convention, define the path transporter

\[
W[\Gamma]=\mathcal P\exp\left(ig\int_\Gamma\mathcal A_\mu\,dx^\mu\right).
\]

Path ordering is essential: for noncommuting connection components, the order of traversed segments can change the transporter. The corresponding curvature convention is

\[
\mathcal F_{\mu\nu}
=\partial_\mu\mathcal A_\nu-\partial_\nu\mathcal A_\mu
-ig[\mathcal A_\mu,\mathcal A_\nu].
\]

The sign follows the Hermitian-generator and positive-ig transporter convention above. If code uses anti-Hermitian generators or a different transporter sign, change the curvature convention consistently.

### 4.1 Mapping PAN channels into the connection

A mapping

\[
\Psi:(q_r,q_e,q_p,\text{context})\longrightarrow\mathfrak{su}(3)
\]

is required before the three PAN channels can drive an SU(3)-valued connection. This mapping is not canonical and must not be inferred from the number of SU(3) generators. Document the generator coefficients, units and coupling normalization, transformation law, context/strain dependence, injectivity over the tested domain, calibration data, and version. Until then, the three-channel state and SU(3) connection are coupled design layers, not an already-constructed physical gauge model.

### 4.2 Gauge-aware comparison

An open Wilson line transforms at its endpoints; its matrix entries are not independently gauge-invariant observables. Compare open-path transporters only after specifying a common endpoint frame or valid parallel-transport alignment.

For a closed loop, the Wilson-loop trace is gauge invariant:

\[
\mathcal W(\Gamma)=\operatorname{Tr}W[\Gamma].
\]

For two closed-loop transporters based at the same point and represented in a common frame, relative holonomy can be studied through eigenvalues of W_A dagger W_B. If those eigenvalues are exp(i theta_m), define an eigenangle comparison with an explicit branch/wrapping convention. Do not use a raw matrix logarithm without documenting branch ambiguity.

The scalar Tr(F_munu F^munu) is gauge invariant, but in Lorentzian signature it is not generally a positive-definite norm. A positive diagnostic requires a declared metric/signature or suitable Euclideanized quantity.

## 5. Baryonic network geometries as NAHT test topologies

For three source positions x_1, x_2, x_3, define two competing network models.

### 5.1 Y-junction model

The Y model connects each source to a common junction y. Its minimal total length is

\[
L_Y=\min_{\mathbf y}\sum_{i=1}^{3}\|\mathbf x_i-\mathbf y\|.
\]

For a non-degenerate triangle whose angles are all below 120 degrees, the minimizing junction is the Fermat/Steiner point, with three arms meeting at 120 degrees. If one triangle angle is at least 120 degrees, the minimizing junction lies at that vertex; do not force a three-arm 120-degree junction in that case.

A long-distance baryonic string ansatz is

\[
V_Y=V_{\mathrm{Coulomb}}+\sigma L_Y+\mu_Y,
\]

where sigma is a string-tension parameter and mu_Y an offset. This is a model form; fitted coefficients and corrections depend on lattice setup and conventions.

### 5.2 Delta model

The Delta model uses pairwise source separations:

\[
L_\Delta^{\mathrm{pair}}=\frac12(r_{12}+r_{23}+r_{31}),
\qquad r_{ij}=\|\mathbf x_i-\mathbf x_j\|,
\]

with an ansatz

\[
V_\Delta=V_{\mathrm{Coulomb}}+\sigma L_\Delta^{\mathrm{pair}}+\mu_\Delta.
\]

The factor one-half is a common convention when comparing the pairwise sum with a mesonic string-tension normalization; record the convention rather than treating it as universal.

Y and Delta are competing effective descriptions of the three-source potential/flux organization. Avoid saying Delta is universally the literal short-distance flux-tube topology and Y universally takes over at one sharp distance. Lattice results are geometry- and setup-dependent; the transition is not a universal hard switch. At sufficiently short distances, Coulombic contributions and the breakdown of a thin-string picture matter.

### 5.3 Proposed NAHT interpretation

- **Y topology:** three independently tracked history channels converge on a shared junction state, undergo a junction update, and continue along outgoing paths.
- **Delta topology:** each channel pair exchanges history directly, creating a closed three-edge interaction cycle without a distinguished central junction.
- **Hybrid topology:** permit both junction and pairwise couplings, with weights calibrated against declared synthetic or empirical tasks.

A junction is a computational interaction node in NAHT. Do not assign it QCD quantum numbers or claim it is physically equivalent to the QCD baryonic junction.

## 6. Flux profiles, squeezing, and internal modes

Lattice-QCD studies investigate spatial distributions of color-field observables and flux-tube profiles. The dual-superconductor / dual-Meissner picture is an influential confinement mechanism model: in that picture, monopole-current behavior is associated with collimation of color-electric flux. It is inaccurate to state that gluon self-attraction alone is a complete derivation of flux squeezing.

For a PAN network, introduce a separately measured transverse profile rather than assuming an exponential form:

\[
\rho_\perp(r;\ell)=\text{measured or simulated transverse density profile}.
\]

An exponential candidate,

\[
\rho_\perp(r;\ell)=\rho_0(\ell)e^{-r/\xi(\ell)},
\]

may be fitted if supported by data. Record residuals and compare alternatives; do not hard-code it as a universal QCD law.

Excited flux configurations can be studied through transverse modes and junction fluctuations. Candidate NAHT analogues include transverse channel perturbations, phase winding along a path, junction displacement/relaxation, and braid/ordering signatures in noncommuting path composition.

Helical or braided patterns are **optional hypotheses to test**, not a generic property of every QCD flux tube. A visually helical state does not by itself establish non-Abelian topology; specify the gauge-covariant observable and boundary conditions.

## 7. Relationship to PAN V8, Janus Hydra, Chronos, and E8

NAHT is an auxiliary transport module. It does not redefine canonical V8:

\[
V8=(h,R,u,d,\tau,\chi,s,f).
\]

It does not replace the Janus Hydra semantic reader, mutate canonical V8 records, or change the primary Gosset 4_21 geometry.

Recommended separation:
1. **V8 / Janus Hydra:** validated semantic state and UHFE/UDFE interpretation.
2. **NAHT channel state:** three-channel retained-history representation with explicit provenance.
3. **SU(3)-like transport adapter:** optional matrix-valued path transport, enabled only after Psi and gauge conventions are specified.
4. **Chronos:** temporal/state-transition bookkeeping; history transport may provide an input feature but does not define Chronos occupancy dynamics.
5. **Gosset 4_21:** E8-root geometry remains the primary R^8 domain. Any embedding/projection of NAHT observables into R^8 must be explicit and preserve the distinction between internal SU(3) and external E8 coordinate spaces.

No identification is made between the 240 E8 roots, eight SU(3) generators, three NAHT channels, or three baryonic sources.

## 8. Validation plan

| Test | Setup | Required check |
|---|---|---|
| Scalar-cancellation baseline | Distinct histories with same scalar summary | Demonstrate scalar aliasing |
| Selective strain | Perturb only q_e | Determine whether q_r and q_p retain distinguishable information |
| Global strain | Couple strain into all channels | Quantify loss of distinguishability; do not assume invariance |
| Norm accounting | Evaluate transport ODE | Verify d(norm q squared)/d ell = 2 q dot C |
| Path-order test | Compose two noncommuting segments in both orders | Confirm order dependence |
| Gauge covariance | Apply local frame transformation | Verify endpoint transformation of open transporters |
| Wilson-loop invariance | Transform a closed loop | Verify loop-trace invariance within tolerance |
| Junction geometry | Symmetric/asymmetric source triangles | Recover 120-degree junction when applicable and vertex solution for angle >=120 degrees |
| Y-vs-Delta comparison | Sweep triangle shape and scale | Compare objective values without a universal switch distance |
| Profile fitting | Generate or ingest transverse profiles | Compare exponential and alternative fits |
| UHFE/UDFE coupling | Run formation and inverse semantic inputs | Preserve independent histories and inverse-head vocabulary |
| E8 integration | Project declared observables into Gosset adapter | Confirm no mutation of roots or canonical V8 records |
| Blind validation | Freeze mapping and parameters before held-out cases | Report performance without refitting |

Record numerical thresholds, random seeds, units, and tolerances. Passing software tests validates implementation contracts, not QCD, confinement, or a new physical theory.

## 9. Suggested implementation sequence

1. Add pure-Python naht_state.py for validated three-channel state, units, and provenance.
2. Add naht_topology.py for Y, Delta, and hybrid network objective functions.
3. Add naht_transport.py for ordered segment composition and a separated transport backend.
4. Add gauge-covariance tests before exposing an SU(3) connection API.
5. Add profile/mode analysis only after reference data or synthetic ground truth is available.
6. Integrate read-only outputs with Janus Hydra / JOBF; do not alter canonical V8 input semantics.
7. Add Chronos and Gosset adapters behind explicit interfaces and versioned mappings.

## 10. References

1. Ph. de Forcrand and O. Jahn, *The baryon static potential from lattice QCD*, arXiv:hep-ph/0502039 (2005): https://arxiv.org/abs/hep-ph/0502039
2. T. T. Takahashi et al., *Detailed analysis of the three-quark potential in SU(3) lattice QCD*, Phys. Rev. D 65, 114509 (2002): https://doi.org/10.1103/PhysRevD.65.114509
3. H. Suganuma et al., *Study of quark confinement in baryons with lattice QCD*, Nucl. Phys. B Proc. Suppl. 141 (2005), 92–98: https://doi.org/10.1016/j.nuclphysbps.2004.12.015
4. M. Pfeuffer, G. S. Bali, and M. Panero, *Fluctuations of the baryonic flux-tube junction from effective string theory*, Phys. Rev. D 79, 025022 (2009): https://doi.org/10.1103/PhysRevD.79.025022
5. *Baryonic flux in quenched and two-flavor dynamical QCD after Abelian projection*, Phys. Rev. D 70, 054506 (2004): https://doi.org/10.1103/PhysRevD.70.054506
6. *Gluon flux-tube distribution and linear confinement in baryons*, Phys. Rev. D 76, 114512 (2007): https://doi.org/10.1103/PhysRevD.76.114512

---
*NAHT is a proposed PAN computational architecture inspired by non-Abelian transport and baryonic network geometry. All cross-domain mappings remain hypotheses until explicitly defined and validated.*
