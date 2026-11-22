# Provenance (repo filing): kernel port of Lucas's tested Burgers /
# Fermi-sea prototype (2026-11-17, 9/9), prepared by Cosmo (Memory bench)
# and placed at the maintainer's explicit approval, 2026-11-21, as a new
# standalone module. Burgers analogue graded tested; Navier-Stokes
# remains not_tested.

#!/usr/bin/env python3
"""
Burgers in the fractal Fermi sea — kernel port of the tested prototype.

Placement approved by the maintainer (Lucas) on 2026-11-21 as a new
standalone module at repo root, after a show-first staged draft was
presented and verified (see the PR carrying this file).

Provenance: port of the standalone prototype `burgers-fermi-sea.py`
(workspace, 2026-11-17), the agreed first test of the Fermi-sea Navier
programme (pan-map-legend.md §3). The prototype passed 9/9 checks on
2026-11-17 and its results file was reproduced bit-for-bit on an
independent re-run the same day. This port is a translation, not a new
design: the solver, the Cole–Hopf answer key, the forward / backward /
randomised protocol and all nine gated checks are carried over unchanged.
What changes is where the programme's own diagnostics come from:

  * the log_phi shell ladder is no longer hand-rolled — shell edges are
    the kernel's barbershop ruler at base phi, from
    `feynman_barbershop.barbershop_amplitude`, and the front's position
    is reported in the ruler's coordinate via
    `feynman_barbershop.horizontal_coordinate_for_gap`;
  * the occupation bookkeeping is expressed against the kernel's
    `fermi_sea`: each snapshot's measured shell occupations are reported
    with their holes (1 - N) in the FermiSeaFrame shape, and the initial
    condition is checked against the kernel's number-conserving sea at
    T = 0 on the same ladder (the fully condensed reference: all energy
    in the lowest shell). Measured occupations are measurements, not
    equilibrium claims — the sea is the reference frame, not the source
    of the numbers.

Programme (Lucas, 2026-11-17): Navier–Stokes recast as occupation
transport in a fractal Fermi sea — occupancy N vs 1-N, mu-cube flux
Phi = N(1-N) — with the sea and its ceiling tabulated on a golden-ratio
logarithmic scale (log_phi spacing) and read via the unrolled
barbershop. A finite-time blow-up is the occupation front reaching the
ceiling (k -> infinity) in finite time; a BEC is the mirror image
(occupation piling into the lowest state).

The test itself (unchanged from the prototype):
  * inviscid Burgers (nu = 0): u_t + u u_x = 0, u0 = -sin(x) — shock
    forms at t* = 1 at x = 0, exactly computable. The shock is the
    occupation front striking the ceiling at a point.
  * viscous Burgers (nu > 0): shock vs Cole-Hopf smoothness — the exact
    answer key. Viscosity is the sea's damping on the front.
  * Protocol per Lucas: forward / backward / randomised.

STRATA grade: this grades the BURGERS ANALOGUE only (tested, 9/9).
Navier–Stokes itself remains not_tested; the programme stays a
representation proposal.

Run:  python3 burgers_fermi_sea.py
Requires: numpy, plus the kernel modules fermi_sea.py and
feynman_barbershop.py importable alongside (repo root layout).
Writes burgers-fermi-sea-kernel-results.json next to itself.
"""

import json
import math
import os

import numpy as np

try:
    from .feynman_barbershop import (
        barbershop_amplitude,
        horizontal_coordinate_for_gap,
    )
    from .fermi_sea import number_conserving_fermi_sea
except ImportError:  # repo-root flat layout, as in pan_v8_janus_phase.py
    from feynman_barbershop import (
        barbershop_amplitude,
        horizontal_coordinate_for_gap,
    )
    from fermi_sea import number_conserving_fermi_sea

PHI = (1.0 + math.sqrt(5.0)) / 2.0
N = 512                      # grid points, periodic domain [0, 2*pi)
X = np.linspace(0, 2 * np.pi, N, endpoint=False)
K = np.fft.fftfreq(N, d=1.0 / N)          # integer wavenumbers, FFT ordering
K2 = K ** 2
DEALIAS = np.abs(K) <= (N // 3)           # 2/3 rule mask


def spectral_deriv(u_hat):
    return 1j * K * u_hat


def rhs_burgers(u_hat, nu):
    """RHS of Burgers in Fourier space: -u*u_x + nu*u_xx, de-aliased."""
    u = np.fft.ifft(u_hat).real
    ux_hat = spectral_deriv(u_hat)
    ux = np.fft.ifft(ux_hat).real
    nonlinear = np.fft.fft(u * ux)
    nonlinear[~DEALIAS] = 0.0
    out = -nonlinear - nu * K2 * u_hat
    out[~DEALIAS] = 0.0
    return out


def rk4_step(u_hat, dt, nu):
    k1 = rhs_burgers(u_hat, nu)
    k2 = rhs_burgers(u_hat + 0.5 * dt * k1, nu)
    k3 = rhs_burgers(u_hat + 0.5 * dt * k2, nu)
    k4 = rhs_burgers(u_hat + dt * k3, nu)
    out = u_hat + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)
    out[~DEALIAS] = 0.0
    return out


def run_burgers(u0, nu, t_end, dt=0.0005, sample_times=()):
    """Integrate Burgers to t_end. Returns (u(t_end), {t: max|u_x|})."""
    u_hat = np.fft.fft(u0)
    u_hat[~DEALIAS] = 0.0
    samples = {}
    t = 0.0
    targets = sorted(sample_times)
    ti = 0
    while t < t_end - 1e-12:
        step = min(dt, t_end - t)
        while ti < len(targets) and targets[ti] <= t + 1e-12:
            u = np.fft.ifft(u_hat).real
            ux = np.fft.ifft(spectral_deriv(u_hat)).real
            samples[targets[ti]] = float(np.max(np.abs(ux)))
            ti += 1
        u_hat = rk4_step(u_hat, step, nu)
        t += step
    while ti < len(targets):
        u = np.fft.ifft(u_hat).real
        ux = np.fft.ifft(spectral_deriv(u_hat)).real
        samples[targets[ti]] = float(np.max(np.abs(ux)))
        ti += 1
    return np.fft.ifft(u_hat).real, samples


def cole_hopf_exact(u0, nu, t):
    """Exact viscous-Burgers solution via the Hopf integral formula.

    u(x,t) = ∫ ((x-y)/t) K(x-y, y) dy / ∫ K(x-y, y) dy,
    K = exp(-(x-y)^2 / (4 nu t) - (1/2nu) * int_0^y u0),
    evaluated by direct quadrature in log space (logsumexp per row).

    Why quadrature, not the textbook spectral theta: theta = exp(-anti/2nu)
    spans a dynamic range of e^{1/nu} (e^100 at nu=0.01). A Fourier sum of
    ~1e42-magnitude modes cancelling to a theta ~ 1e-43 trough is destroyed
    by rounding noise (~1e-14 absolute against the normalised peak) — theta
    goes negative and u is NaN; two fixes were tried and both failed for
    nu=0.01. The ratio-of-integrals form has the same sharp weight in
    numerator and denominator, so it cancels in the ratio; the logsumexp
    shift keeps every intermediate O(1). Periodic images are negligible
    here (Gaussian width sqrt(4 nu t) <= 0.2 << 2*pi), so the wrapped
    distance is used. (For u0 = -sin(x), anti = cos(x) - 1 is periodic, so
    the wrapped antiderivative is exact.)

    RETAINED FAILURE (1 of 2, kept from the prototype record): the
    textbook spectral Cole–Hopf (theta via FFT) returns NaN at nu = 0.01
    for the reason above. The quadrature form here is the fix; the
    failure is recorded, not erased.
    """
    # antiderivative of u0 anchored at 0, spectrally
    u0_hat = np.fft.fft(u0)
    anti_hat = np.zeros_like(u0_hat, dtype=complex)
    nz = K != 0
    anti_hat[nz] = u0_hat[nz] / (1j * K[nz])
    anti = np.fft.ifft(anti_hat).real
    anti = anti - anti[0]
    d = (X[:, None] - X[None, :] + np.pi) % (2 * np.pi) - np.pi  # wrapped x - y
    log_w = -(d ** 2) / (4.0 * nu * t) - anti[None, :] / (2.0 * nu)
    log_w = log_w - np.max(log_w, axis=1, keepdims=True)
    w = np.exp(log_w)
    num = np.sum((d / t) * w, axis=1)
    den = np.sum(w, axis=1)
    return num / den


# ---- Fermi-sea diagnostics: log_phi shells over wavenumber -----------------
def log_phi_shells(k_max):
    """Shell edges k = phi^j from the kernel barbershop ruler (base phi).

    Edge j is barbershop_amplitude(1, j, 1, phi) = phi^j — the owner-
    defined exponential ruler of feynman_barbershop.py, read at the
    golden base. Returns the edge list, closed by k_max itself.
    """
    edges = [1.0]
    while edges[-1] * PHI < k_max:
        edges.append(barbershop_amplitude(1, float(len(edges)), 1.0, PHI))
    edges.append(float(k_max))
    return edges


def shell_occupation(u):
    """Energy spectrum E(k) = |u_hat_k|^2 binned into log_phi shells.

    Returns list of dicts: shell (k_lo, k_hi), occupation N_j = E_j / E_tot,
    flux proxy Phi_j = N_j (1 - N_j). The top shell is the ceiling.
    """
    u_hat = np.fft.fft(u)
    energy = (np.abs(u_hat) ** 2) / N ** 2
    # fold +/-k (real signal): use |k|
    k_abs = np.abs(K)
    e_tot = float(np.sum(energy))
    edges = log_phi_shells(float(np.max(k_abs)))
    out = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (k_abs >= lo) & (k_abs < hi)
        n_j = float(np.sum(energy[mask])) / e_tot if e_tot > 0 else 0.0
        out.append({"k_lo": lo, "k_hi": hi, "N": n_j, "Phi": n_j * (1.0 - n_j)})
    return out, e_tot


def spectral_front(u, frac=1e-3):
    """Highest wavenumber carrying >= frac of the PEAK spectral energy.

    The occupation front's position: as the shock forms, energy climbs to
    ever-higher k. The ceiling is the grid Nyquist (k=256); the front's
    approach to it is the diagnostic. (The top log_phi shell, k>=199, is
    only reached asymptotically — at t=0.9 the front is at k~10, so the
    top-shell occupation is a lagging indicator and is reported, not gated.)

    RETAINED FAILURE (2 of 2, kept from the prototype record): the first
    ceiling diagnostic (top-shell occupation) read 0.0000 even at t = 0.9
    — the front had only reached k ~ 10, not the k >= 199 top shell.
    k_front here is its replacement; the failure is recorded, not erased.
    """
    u_hat = np.fft.fft(u)
    energy = (np.abs(u_hat) ** 2) / N ** 2
    peak = float(np.max(energy))
    k_abs = np.abs(K)
    mask = energy >= frac * peak
    return int(np.max(k_abs[mask])) if np.any(mask) else 0


def top_shell_fraction(u):
    shells, _ = shell_occupation(u)
    return shells[-1]["N"], shells


def front_coordinate(k_front):
    """The front's position on the unrolled barbershop: log_phi(k_front)."""
    if k_front < 1:
        return 0.0
    return horizontal_coordinate_for_gap(float(k_front), PHI)


def reference_sea(n_shells, filling_fraction):
    """The kernel's number-conserving Fermi sea on the log_phi ladder.

    Mode energies are the shell indices 0..n_shells-1 — the ladder's
    positions in barbershop coordinate (log_phi k), equally spaced once
    unrolled. At T = 0 the sea fills the lowest shells first: the fully
    condensed reference the measured occupations are read against.
    """
    return number_conserving_fermi_sea(
        [float(j) for j in range(n_shells)],
        temperature=0.0,
        filling_fraction=filling_fraction,
    )


def measured_frame(shells):
    """A snapshot's measured occupations in the FermiSeaFrame shape.

    occupations N_j come from the spectrum (measurement); holes are
    1 - N_j; particle number is sum(N_j) = 1 by construction (the
    spectrum is normalised). This is a reporting frame, not an
    equilibrium claim — cf. reference_sea for the kernel sea itself.
    """
    occ = [s["N"] for s in shells]
    return {
        "occupations": occ,
        "holes": [1.0 - n_j for n_j in occ],
        "particle_number": float(sum(occ)),
        "capacity_per_state": 1.0,
        "n_shells": len(occ),
    }


def main():
    results = {"checks": {}}
    u0 = -np.sin(X)

    # --- 1. Inviscid: shock formation, t* = 1 ------------------------------
    print("== 1. Inviscid Burgers, u0 = -sin(x), shock time t* = 1 ==")
    _, grads = run_burgers(u0, nu=0.0, t_end=0.9, sample_times=(0.0, 0.5, 0.9))
    theory = {t: 1.0 / (1.0 - t) for t in (0.0, 0.5, 0.9)}
    for t in (0.0, 0.5, 0.9):
        print(f"  t={t:.1f}  max|u_x| = {grads[t]:8.3f}   theory 1/(1-t) = {theory[t]:8.3f}")
    # Shock-time estimator: near blow-up max|u_x| ~ 1/(t* - t), so
    # t*_est = t + 1/max|u_x|(t) is linear-exact for the -sin(x) profile.
    t_star_est = 0.9 + 1.0 / grads[0.9]
    print(f"  shock-time estimate from t=0.9 sample: t*_est = {t_star_est:.4f} (exact 1.0)")
    results["inviscid_max_grad"] = grads
    results["inviscid_t_star_est"] = t_star_est
    results["checks"]["inviscid_steepening"] = grads[0.9] > 4.0  # theory 10; spectral under-resolves near shock
    results["checks"]["inviscid_t_star_est"] = abs(t_star_est - 1.0) < 0.01

    # --- 2. Viscous vs Cole-Hopf exact answer key ---------------------------
    print("== 2. Viscous Burgers vs Cole-Hopf exact solution ==")
    for nu in (0.1, 0.01):
        u_num, _ = run_burgers(u0, nu=nu, t_end=0.5)
        u_ex = cole_hopf_exact(u0, nu, 0.5)
        err = float(np.max(np.abs(u_num - u_ex)))
        u_num2, grads_v = run_burgers(u0, nu=nu, t_end=1.5, sample_times=(1.5,))
        print(f"  nu={nu:<5} max|u_num - u_ColeHopf| at t=0.5 = {err:.3e}   "
              f"max|u_x| at t=1.5 = {grads_v[1.5]:.3f}")
        print(f"         (nu=0.01 arrests the front at a FINITE slope ~O(1/nu), "
              f"large but not a singularity — damping, not elimination)")
        results[f"viscous_nu_{nu}_colehopf_err"] = err
        results[f"viscous_nu_{nu}_max_grad_t1.5"] = grads_v[1.5]
    results["checks"]["colehopf_nu0.1"] = results["viscous_nu_0.1_colehopf_err"] < 1e-6
    results["checks"]["colehopf_nu0.01"] = results["viscous_nu_0.01_colehopf_err"] < 1e-6
    results["checks"]["viscous_bounded"] = results["viscous_nu_0.1_max_grad_t1.5"] < 6.0

    # --- 3. Backward run (time reversal) ------------------------------------
    print("== 3. Backward run: inviscid forward to t=0.5, then back to t=0 ==")
    u_fwd, _ = run_burgers(u0, nu=0.0, t_end=0.5)
    # backward leg inline with negative dt (run_burgers assumes t_end > 0)
    u_hat = np.fft.fft(u_fwd)
    u_hat[~DEALIAS] = 0.0
    t = 0.5
    while t > 0.0 + 1e-12:
        step = -min(0.0005, t)
        u_hat = rk4_step(u_hat, step, 0.0)
        t += step
    u_back = np.fft.ifft(u_hat).real
    back_err = float(np.max(np.abs(u_back - u0)))
    print(f"  max|u_back(0) - u0| = {back_err:.3e}  (inviscid Burgers is time-reversible)")
    print("  Note: viscous backward integration is NOT run — anti-diffusion "
          "(nu -> -nu) amplifies high-k noise exponentially; that ill-posedness "
          "is itself the honest backward result for the viscous case.")
    results["backward_err"] = back_err
    results["checks"]["backward_recovery"] = back_err < 1e-6

    # --- 4. Randomised initial conditions ------------------------------------
    print("== 4. Randomised: 8 seeds, u0 = -sin(x+p1) + a2 sin(2x+p2) ==")
    # Shock-time estimator (same linear law as §1): t*_est = t + 1/max|u_x|(t),
    # evaluated at the last sample before 0.98*t*. Sharp to ~1% when the
    # sample is close to the shock; a coarse crossing-time bracket would
    # only return the grid point, so it is NOT used.
    rng = np.random.default_rng(20261117)
    ok = 0
    shock_estimates = []
    for seed in range(8):
        p1, p2 = rng.uniform(0, 2 * np.pi, 2)
        a2 = rng.uniform(0.0, 0.3)
        u0r = -np.sin(X + p1) + a2 * np.sin(2 * X + p2)
        # exact shock time for inviscid Burgers: t* = -1 / min(u0')
        u0p = -np.cos(X + p1) + 2 * a2 * np.cos(2 * X + p2)
        t_star = -1.0 / float(np.min(u0p))
        t_last = 0.98 * t_star
        _, g = run_burgers(u0r, nu=0.0, t_end=t_last, sample_times=(t_last,))
        t_est = t_last + 1.0 / g[t_last]
        rel = abs(t_est - t_star) / t_star
        good = rel < 0.05
        ok += int(good)
        shock_estimates.append({"seed": seed, "a2": round(float(a2), 3),
                                "t_star_exact": round(t_star, 3),
                                "t_star_est": round(t_est, 3),
                                "rel_err": round(float(rel), 4)})
        print(f"  seed {seed}: a2={a2:.2f} t*_exact={t_star:.3f} "
              f"t*_est={t_est:.3f} rel_err={rel:.4f}")
    results["randomised"] = shock_estimates
    results["checks"]["randomised_shock_time"] = ok >= 7

    # --- 5. Fermi-sea ceiling diagnostic: log_phi shells ----------------------
    print("== 5. Ceiling diagnostic: occupation in log_phi wavenumber shells ==")
    print("   (shell = [phi^j, phi^(j+1)) from the kernel barbershop ruler; "
          "Phi_j = N_j(1-N_j) is the mu-cube flux proxy; k_front = highest k "
          "carrying >=0.1% of peak energy; x_front = log_phi(k_front))")
    fronts = {}
    front_coords = {}
    for label, nu, t_end in (("inviscid t=0", 0.0, 0.0), ("inviscid t=0.9", 0.0, 0.9),
                             ("viscous nu=0.1 t=1.5", 0.1, 1.5)):
        if t_end == 0.0:
            u = u0
        else:
            u, _ = run_burgers(u0, nu=nu, t_end=t_end)
        top, shells = top_shell_fraction(u)
        kf = spectral_front(u)
        fronts[label] = kf
        front_coords[label] = front_coordinate(kf)
        print(f"  {label:<24} k_front = {kf:3d}   x_front = {front_coords[label]:.3f}   "
              f"top-shell N = {top:.4f}")
        if label == "inviscid t=0.9":
            print("   shells at t=0.9 (k_lo, N, Phi): " +
                  ", ".join(f"[{s['k_lo']:.0f}:{s['N']:.3f}]" for s in shells))
        if label == "inviscid t=0":
            # The initial condition against the kernel sea: u0 = -sin(x)
            # puts all energy in shell 0 — the T = 0 number-conserving sea
            # at filling 1/n_shells on the same ladder must agree exactly.
            frame = measured_frame(shells)
            sea = reference_sea(frame["n_shells"], 1.0 / frame["n_shells"])
            sea_agrees = (
                abs(sea.occupations[0] - frame["occupations"][0]) < 1e-12
                and all(abs(o) < 1e-12 for o in sea.occupations[1:])
                and abs(frame["occupations"][0] - 1.0) < 1e-12
            )
            results["sea_reference_initial"] = {
                "n_shells": frame["n_shells"],
                "sea_occupations": list(sea.occupations),
                "measured_occupations": frame["occupations"],
                "sea_agrees_with_measured": bool(sea_agrees),
            }
            print(f"   kernel sea (T=0, filling 1/{frame['n_shells']}) vs measured "
                  f"initial occupation: agree = {sea_agrees}")
    results["ceiling_k_front"] = fronts
    results["ceiling_x_front"] = front_coords
    results["checks"]["ceiling_climbed_inviscid"] = (
        fronts["inviscid t=0.9"] >= 5 * max(fronts["inviscid t=0"], 1))
    results["checks"]["ceiling_arrested_viscous"] = (
        fronts["viscous nu=0.1 t=1.5"] < fronts["inviscid t=0.9"])

    # --- Verdict ---------------------------------------------------------------
    print("\n== Verdict ==")
    for name, passed in results["checks"].items():
        print(f"  [{'PASS' if passed else 'FAIL'}] {name}")
    results["all_passed"] = bool(all(results["checks"].values()))
    print(f"\nAll checks passed: {results['all_passed']}")
    print("Reading: inviscid shock = occupation front striking the ceiling at a "
          "point (t*=1); viscosity = the sea's damping, front arrested, "
          "Cole-Hopf exact. This grades the BURGERS ANALOGUE only — "
          "Navier-Stokes itself remains not_tested.")

    out_path = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                            "burgers-fermi-sea-kernel-results.json")
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults written to {out_path}")


if __name__ == "__main__":
    main()
