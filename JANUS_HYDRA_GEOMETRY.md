# Janus Hydra geometric language

**Status:** PAN V8 research specification. These are computational geometric mappings and metaphors, not claims of a new physical field theory.

## Canonical domain

\[
V_8=(h,R,u,d,\tau,\chi,s,f)
\]

The coordinates are Harmonic Coherence, Recursive Depth, Constructive Polarity, Decoherence, Temporal Persistence, Chirality/Orientation, Information Density, and Forcing/Fractal Forcing Index.

The geometry remains the **whole** 8D cross-polytope:

\[
\mathcal H_8=\{q\in\mathbb R^8:\sum_{i=1}^8|q_i|\leq1\},\qquad
\rho_0(n)=\frac{1}{\sum_i|n_i|}
\]

for unit direction n. The origin is the shared waist/reference point. UHFE and UDFE are distinct, independently evolving fields over the same complete domain. Do not split the polytope into formation and dissolution halves.

## Five UHFE heads and inverse UDFE language

| UHFE head | V8 projection | Geometric meaning | UDFE inverse language |
|---|---|---|---|
| Bubble | (h,R,u) | constructive expansion / transition envelope | AntiBubble / Cavitation |
| Honeycomb | (τ,s) | persistent information packing / tessellation | InverseHoneycomb / vacancies |
| SpiderWeb | (f,h,R) | recursive forcing network / boundary connectivity | InverseSpiderWeb / RadialVoid |
| ChiralDNA | (χ,τ,R) | oriented, persistent recursive helix | ChiralVoid |
| CompoundEye | (s,h,d) | multi-aperture sampling and coherence/decoherence contrast | DiscreteSingularDots / InverseCompoundEye |

Baseline scalar projections:

\[
B=(h+R+u)/3,\quad H=(\tau+s)/2,\quad W=(f+h+R)/3
\]
\[
C=(\chi+\tau+R)/3,\quad E=(s+h+d)/3.
\]

The default normalized complement is \(\mathcal C(x)=1-x\), so \(\mathcal C(\mathcal C(x))=x\). The reference inverse scores are:

\[
B^-=(d+(1-u)+(1-h))/3
\]
\[
H^-=((1-\tau)+(1-s))/2,\quad
W^-=((1-f)+(1-h)+(1-R))/3
\]
\[
C^-=((1-\chi)+(1-\tau)+(1-R))/3
\]
\[
E^-=((1-s)+(1-h)+d)/3.
\]

The d term is deliberately retained in AntiBubble and inverse CompoundEye as a dissolution-side signal, following the project's semantic mapping. This is a design choice, not a mathematical necessity; preserve it as a versioned rule.

## Independent fields and interference

Define independent histories \(U_H(n,t)\) and \(U_D(n,t)\), with separately configurable amplitudes, frequencies, phases, and spatial profiles. Do not force \(U_D=1-U_H\). A centered interaction is:

\[
I(n,t)=(U_H-\bar U_H)(U_D-\bar U_D).
\]

One candidate boundary law is:

\[
\rho(n,t)=\rho_0(n)\exp[g(t)+\lambda_H\delta U_H(n,t)
-\lambda_D\delta U_D(n,t)+\lambda_{HD}I(n,t)].
\]

This guarantees positive radius for finite inputs. It is a proposed shape-evolution rule, not a law derived from physics.

## Octadial channels and orientation

The eight V8 coordinate axes are the eight named channels; they are not the 256 sign orthants of \(\mathbb R^8\). For a nonzero direction n:

\[
w_i(n)=\frac{n_i^2}{\sum_j n_j^2}.
\]

These weights are sign-symmetric. Chirality must therefore enter through a separately specified orientation-sensitive operator using χ or signed directional terms.

Golden-angle phase offsets may be scheduled with:

\[
\theta_G=2\pi/\phi^2,\quad \phi=(1+\sqrt5)/2,\quad
\varphi_i=i\theta_G.
\]

This is a phase-scheduling heuristic, not an 8D rotation group.

## Kernel invariants

1. Both fields cover the same complete 8D domain; no half-polytope assignment.
2. q=0 remains the shared reference point.
3. Radial boundary remains positive for finite model inputs.
4. Complement is involutive on normalized values.
5. Every inverse head retains pairing and operator provenance.
6. UHFE and UDFE can have different histories and parameters.
7. V8 coordinate order is preserved: (h,R,u,d,τ,χ,s,f).
8. Report invalid inputs and numerical convergence; never silently clamp raw values.

## Separation from JOBF

The fractal kernel owns V8 projections, geometric vocabulary, inverse mappings, and invariants. JOBF owns time evolution, independent field histories, interference, radial deformation, and diagnostics. E8 roots or other symmetry layers must be added separately with an explicit map into V8; they are not implicitly implemented here.
