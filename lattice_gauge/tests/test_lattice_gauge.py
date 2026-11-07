import itertools, sys, pathlib; sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))
import numpy as np
from lattice_gauge import *
RNG = np.random.default_rng(11)
def close(a, b, tol, msg): assert abs(a - b) <= tol, f"{msg}: {a} vs {b} (tol {tol})"

def test_group_closure_after_updates():
    for N in (2, 3):
        g, _, _ = run(N, (4, 4, 4), 2.0, 20, 5, seed=1, hot=True); g.reunitarize()
        for u in g.U:
            assert np.allclose(u @ dag(u), np.eye(N), atol=1e-10) and np.allclose(np.linalg.det(u), 1, atol=1e-10)

def test_local_dS_equals_full_action_change():
    for N in (2, 3):
        g = Gauge(N, (4, 4, 4), 1.7, seed=2, hot=True)
        for _ in range(40):
            mu = int(g.rng.integers(g.d)); x = tuple(int(g.rng.integers(L)) for L in g.dims)
            S = g.staple(mu)[x]; old = g.U[mu][x].copy(); new = g._project(g.rng.normal(size=(N, N)) + 1j * g.rng.normal(size=(N, N)))
            dS_local = -(g.beta / N) * np.real(np.trace((new - old) @ S)); a0 = g.action(); g.U[mu][x] = new; dS_full = g.action() - a0; g.U[mu][x] = old
            close(dS_local, dS_full, 1e-9, f"SU({N}) local vs full dS")

def test_gauge_invariance():
    for N in (2, 3):
        g = Gauge(N, (4, 4, 4), 2.0, seed=3, hot=True); p0, w0, l0 = g.plaquette(), g.wilson(2, 2), np.trace(g.U[0][0, 0, 0]).real
        g.gauge_transform(g._haar(g.dims))
        close(g.plaquette(), p0, 1e-10, "plaquette"); close(g.wilson(2, 2), w0, 1e-10, "2x2 loop")
        assert abs(np.trace(g.U[0][0, 0, 0]).real - l0) > 1e-6, "a single link must NOT be gauge invariant"

def test_hot_and_cold_starts_agree():
    for N, beta in ((2, 2.0), (3, 5.5)):
        pa = run(N, (4, 4, 4, 4), beta, 300, 800, seed=5, hot=False)[1]; pb = run(N, (4, 4, 4, 4), beta, 300, 800, seed=6, hot=True)[1]
        close(pa.mean(), pb.mean(), 5 * np.hypot(binned_err(pa), binned_err(pb)) + 1e-3, f"SU({N}) hot/cold")

def test_exact_2d_plaquette_and_creutz_ratio():
    for N, beta, uex in ((2, 2.0, u_su2(2.0)), (3, 8.0, u_su3(8.0))):
        g, P, C = run(N, (16, 16), beta, 200, 1200, seed=7, creutz_r=(2,), hits=3)
        close(P.mean(), uex, 5 * binned_err(P) + 1e-3, f"SU({N}) 2D plaquette"); cm, ce = creutz_binned(C[2]); close(cm, -np.log(uex), 5 * ce + 0.02, f"SU({N}) 2D Creutz")

def test_su3_weyl_measure_is_normalised():
    t = np.linspace(0, 2 * np.pi, 240, endpoint=False); a, b = np.meshgrid(t, t, indexing='ij'); c = -(a + b)
    z = [np.exp(1j * a), np.exp(1j * b), np.exp(1j * c)]
    close((abs(z[0] - z[1]) ** 2 * abs(z[0] - z[2]) ** 2 * abs(z[1] - z[2]) ** 2).mean() / 6, 1.0, 1e-9, "Weyl measure normalisation")

def test_su3_4d_strong_coupling_series():             # published series, arXiv:1408.2960
    for beta in (0.5, 1.0, 1.5):
        g, P, _ = run(3, (4, 4, 4, 4), beta, 100, 400, seed=8, hits=2)
        close(P.mean(), su3_strong_plaquette(beta), 5 * binned_err(P) + 2e-4, f"SU(3) 4D strong coupling beta={beta}")

def test_su2_4d_strong_coupling_leading_order():      # next correction is O(u^5) (~1e-5 here)
    for beta in (0.3, 0.6):
        g, P, _ = run(2, (4, 4, 4, 4), beta, 100, 600, seed=9)
        close(P.mean(), u_su2(beta), 5 * binned_err(P) + 5e-4, f"SU(2) 4D strong coupling beta={beta}")

def test_weak_coupling_equipartition():                # 1-P -> (N^2-1)/(d beta); first correction O(1/beta^2) so allow 10%
    for N, dims, beta in ((2, (4, 4, 4), 20.0), (2, (4, 4, 4, 4), 20.0), (3, (4, 4, 4, 4), 40.0)):
        g, P, _ = run(N, dims, beta, 150, 200, seed=10)
        lead = (N * N - 1) / (len(dims) * beta); assert abs((1 - P.mean()) / lead - 1) < 0.10, (N, dims, (1 - P.mean()) / lead)

if __name__ == "__main__":
    fails = 0
    for n, f in sorted(globals().items()):
        if n.startswith("test_"):
            try: f(); print("ok   ", n)
            except AssertionError as e: fails += 1; print("FAIL ", n, e)
    print("FAILS", fails); sys.exit(1 if fails else 0)
