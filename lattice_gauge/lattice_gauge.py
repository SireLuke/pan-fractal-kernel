"""Pure-gauge SU(N) lattice theory with the Wilson action on a periodic hypercubic lattice (any dimension, N=2,3,...).
S = beta * sum_p (1 - (1/N) Re Tr U_p).  Metropolis updates, checkerboard-vectorised.  Plain NumPy.
Not a physical-field claim: this is a numerical model whose outputs are checked against exact/published results (see tests/)."""
import numpy as np
from fractions import Fraction

def dag(a): return np.conj(np.swapaxes(a, -1, -2))
def tr(a): return np.einsum('...ii->...', a)

class Gauge:
    def __init__(self, N, dims, beta, seed=0, hot=False):
        assert all(L % 2 == 0 for L in dims), "even extents needed for checkerboard updates"
        self.N, self.dims, self.d, self.beta = N, tuple(dims), len(dims), float(beta)
        self.rng = np.random.default_rng(seed); self.eps = 0.3
        shape = self.dims + (N, N)
        self.U = [self._haar(shape[:-2]) if hot else np.broadcast_to(np.eye(N, dtype=complex), shape).copy() for _ in range(self.d)]
        par = np.indices(self.dims).sum(0) % 2
        self.sites = [np.nonzero(par == p) for p in (0, 1)]
    # -- group helpers -------------------------------------------------------------------------------
    def _haar(self, lead):
        Z = self.rng.normal(size=lead + (self.N, self.N)) + 1j * self.rng.normal(size=lead + (self.N, self.N))
        return self._project(Z)
    def _project(self, Z):                      # QR -> unitary, then divide by det^(1/N) -> SU(N)
        Q, R = np.linalg.qr(Z); Q = Q * (np.diagonal(R, axis1=-2, axis2=-1) / np.abs(np.diagonal(R, axis1=-2, axis2=-1)))[..., None, :]
        return Q / (np.linalg.det(Q) ** (1.0 / self.N))[..., None, None]
    def _near_id(self, n):
        A = self.rng.normal(size=(n, self.N, self.N)) + 1j * self.rng.normal(size=(n, self.N, self.N)); H = (A + dag(A)) / 2
        H -= (tr(H) / self.N)[:, None, None] * np.eye(self.N)
        w, v = np.linalg.eigh(H); return (v * np.exp(1j * self.eps * w)[:, None, :]) @ dag(v)
    # -- geometry ---------------------------------------------------------------------------------------
    @staticmethod
    def sh(a, shifts):                          # a[x + shifts]; shifts = {axis: k}
        for ax, k in shifts.items(): a = np.roll(a, -k, axis=ax)
        return a
    def staple(self, mu):
        S = 0
        for nu in range(self.d):
            if nu == mu: continue
            Unu_p = self.sh(self.U[nu], {mu: 1}); Umu_n = self.sh(self.U[mu], {nu: 1})
            S = S + Unu_p @ dag(Umu_n) @ dag(self.U[nu])
            S = S + dag(self.sh(Unu_p, {nu: -1})) @ dag(self.sh(self.U[mu], {nu: -1})) @ self.sh(self.U[nu], {nu: -1})
        return S
    # -- dynamics ---------------------------------------------------------------------------------------
    def sweep(self, hits=2):
        acc = []
        for mu in range(self.d):
            for p in (0, 1):
                idx = self.sites[p]
                for _ in range(hits):
                    S = self.staple(mu)[idx]; Uc = self.U[mu][idx]; V = self._near_id(len(Uc)) @ Uc
                    dS = -(self.beta / self.N) * np.real(np.einsum('nij,nji->n', V - Uc, S))
                    ok = self.rng.random(len(dS)) < np.exp(-np.minimum(dS, 50)); Uc[ok] = V[ok]; self.U[mu][idx] = Uc; acc.append(ok.mean())
        self.acceptance = float(np.mean(acc)); return self.acceptance
    def reunitarize(self):
        self.U = [self._project(u) for u in self.U]
    def tune(self, target=(0.35, 0.55)):
        if self.acceptance > target[1]: self.eps *= 1.1
        elif self.acceptance < target[0]: self.eps *= 0.9
    # -- observables ------------------------------------------------------------------------------------
    def plaq_field(self, mu, nu):
        return tr(self.U[mu] @ self.sh(self.U[nu], {mu: 1}) @ dag(self.sh(self.U[mu], {nu: 1})) @ dag(self.U[nu])).real / self.N
    def plaquette(self):
        return float(np.mean([self.plaq_field(m, n).mean() for m in range(self.d) for n in range(m + 1, self.d)]))
    def action(self):
        return self.beta * float(sum((1 - self.plaq_field(m, n)).sum() for m in range(self.d) for n in range(m + 1, self.d)))
    def loop(self, mu, nu, r, t):
        W = np.broadcast_to(np.eye(self.N, dtype=complex), self.dims + (self.N, self.N))
        for i in range(r): W = W @ self.sh(self.U[mu], {mu: i})
        for j in range(t): W = W @ self.sh(self.U[nu], {mu: r, nu: j})
        for i in reversed(range(r)): W = W @ dag(self.sh(self.U[mu], {mu: i, nu: t}))
        for j in reversed(range(t)): W = W @ dag(self.sh(self.U[nu], {nu: j}))
        return float(tr(W).real.mean() / self.N)
    def wilson(self, r, t):                     # averaged over all ordered planes (so W(r,t) = W(t,r))
        return float(np.mean([self.loop(m, n, r, t) for m in range(self.d) for n in range(self.d) if m != n]))
    def creutz(self, r):
        w = self.wilson; return -np.log(w(r, r) * w(r - 1, r - 1) / (w(r, r - 1) * w(r - 1, r)))
    def gauge_transform(self, g):
        self.U = [g @ self.U[mu] @ dag(self.sh(g, {mu: 1})) for mu in range(self.d)]

# -- reference values ---------------------------------------------------------------------------------------
def u_su2(beta):
    from scipy.special import iv
    return iv(2, beta) / iv(1, beta)
def u_su3(beta, n=240):
    """<(1/3) Re Tr U> for ONE plaquette weight exp((beta/3) Re Tr U), Haar measure via Weyl integration (spectrally accurate grid)."""
    t = np.linspace(0, 2 * np.pi, n, endpoint=False); a, b = np.meshgrid(t, t, indexing='ij'); c = -(a + b)
    z = [np.exp(1j * a), np.exp(1j * b), np.exp(1j * c)]
    meas = abs(z[0] - z[1]) ** 2 * abs(z[0] - z[2]) ** 2 * abs(z[1] - z[2]) ** 2
    ReTr = np.cos(a) + np.cos(b) + np.cos(c); w = meas * np.exp(beta / 3 * ReTr)
    return float((w * ReTr / 3).sum() / w.sum())
SU3_STRONG = [Fraction(1), Fraction(-1, 18), Fraction(-1, 216), Fraction(0), Fraction(5, 93312), Fraction(49, 15116544),
              Fraction(-1309, 906992640), Fraction(-2131, 5441955840), Fraction(-1091, 43535646720), Fraction(179081, 21158324305920),
              Fraction(1277749, 592433080565760)]          # s_0..s_10 of arXiv:1408.2960 (P = 1 - <(1/3)ReTr U_p>, beta = 6/g^2)
def su3_strong_plaquette(beta):
    return 1.0 - sum(float(s) * beta ** k for k, s in enumerate(SU3_STRONG))
def weak_coupling_leading(N, d, beta):          # 1 - P = (N^2-1) / (d * beta)   (equipartition; leading order in 1/beta)
    return 1.0 - (N * N - 1) / (d * beta)
def binned_err(x, nb=20):
    x = np.asarray(x); n = len(x) // nb * nb; b = x[:n].reshape(nb, -1).mean(1); return float(b.std(ddof=1) / np.sqrt(nb))
def creutz_binned(L, nb=20):
    """Creutz ratio chi(r,r) from rows [W(r,r), W(r-1,r-1), W(r,r-1), W(r-1,r)]; ratio taken per bin of averages, never per sample."""
    L = np.asarray(L); n = len(L) // nb * nb; b = L[:n].reshape(nb, -1, 4).mean(1)
    x = -np.log(b[:, 0] * b[:, 1] / (b[:, 2] * b[:, 3])); return float(x.mean()), float(x.std(ddof=1) / np.sqrt(nb))
def run(N, dims, beta, therm, meas, seed=0, creutz_r=(), hits=2, hot=False, every=1):
    g = Gauge(N, dims, beta, seed, hot)
    for i in range(therm):
        g.sweep(hits); g.tune() if i % 10 == 9 else None
        if i % 20 == 19: g.reunitarize()
    P, C = [], {r: [] for r in creutz_r}
    for i in range(meas):
        g.sweep(hits)
        if i % 20 == 19: g.reunitarize()
        if i % every == 0:
            P.append(g.plaquette())
            for r in creutz_r: C[r].append([g.wilson(r, r), g.wilson(r - 1, r - 1), g.wilson(r, r - 1), g.wilson(r - 1, r)])
    return g, np.array(P), {r: np.array(v) for r, v in C.items()}
