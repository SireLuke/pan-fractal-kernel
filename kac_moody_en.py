"""Exact Kac-Moody / Coxeter checks for the E_n series (E8 finite, E9 affine, E10 hyperbolic, E11 very extended).

Independent of the PANoRAMic.os E10 experiments: integer Cartan matrices, congruence-diagonalisation
inertia, hyperbolicity by subdiagram classification, and bounded real-root growth. Pure standard library.
Nothing here asserts a physical meaning for any dimension.

Labelling (Bourbaki-style): chain 1-3-4-...-n, with node 2 attached to node 4. n=9 is affine E8,
n=10 is hyperbolic, n=11 very extended.
"""
from __future__ import annotations

from fractions import Fraction
from itertools import combinations

try:
    from . import five21_neighborhood as nb
except ImportError:
    import five21_neighborhood as nb


def edges_en(n: int):
    if n < 3: raise ValueError("n >= 3")
    e = [(1, 3)]
    if n >= 4:
        e += [(i, i + 1) for i in range(3, n)] + [(2, 4)]
    return e


def cartan_en(n: int):
    A = [[2 if i == j else 0 for j in range(n)] for i in range(n)]
    for a, b in edges_en(n):
        A[a - 1][b - 1] = A[b - 1][a - 1] = -1
    return A


def sub_cartan(A, keep):
    return [[A[i][j] for j in keep] for i in keep]


def inertia_det(A):
    """(positive, negative, zero, det) of a symmetric rational matrix by exact congruence diagonalisation."""
    M = [[Fraction(x) for x in row] for row in A]
    n = len(M)
    diag, det_sign_factor = [], Fraction(1)
    idx = list(range(n))
    while idx:
        piv = next((i for i in idx if M[i][i] != 0), None)
        if piv is None:
            pair = next(((i, j) for i in idx for j in idx if i < j and M[i][j] != 0), None)
            if pair is None:
                diag += [Fraction(0)] * len(idx); break
            i, j = pair                                  # row/col i += row/col j (congruence, det-preserving)
            for k in range(n): M[i][k] += M[j][k]
            for k in range(n): M[k][i] += M[k][j]
            continue
        d = M[piv][piv]; diag.append(d)
        for i in idx:
            if i != piv and M[i][piv] != 0:
                f = M[i][piv] / d
                for k in range(n): M[i][k] -= f * M[piv][k]
                for k in range(n): M[k][i] -= f * M[k][piv]
        idx.remove(piv)
    det = Fraction(1)
    for d in diag: det *= d
    return (sum(d > 0 for d in diag), sum(d < 0 for d in diag), sum(d == 0 for d in diag), det)


def kernel_vector(A):
    """Primitive positive integer kernel vector of a singular symmetric integer matrix with 1-dim kernel."""
    n = len(A)
    M = [[Fraction(x) for x in row] for row in A]
    pivcols, r = [], 0
    for c in range(n):
        p = next((i for i in range(r, n) if M[i][c] != 0), None)
        if p is None: continue
        M[r], M[p] = M[p], M[r]
        M[r] = [x / M[r][c] for x in M[r]]
        for i in range(n):
            if i != r and M[i][c] != 0:
                f = M[i][c]; M[i] = [x - f * y for x, y in zip(M[i], M[r])]
        pivcols.append(c); r += 1
    free = [c for c in range(n) if c not in pivcols]
    if len(free) != 1: raise ValueError(f"kernel dimension {len(free)}, expected 1")
    f = free[0]
    v = [Fraction(0)] * n; v[f] = Fraction(1)
    for row, c in enumerate(pivcols): v[c] = -M[row][f]
    from math import gcd
    den = 1
    for x in v: den = den * x.denominator // gcd(den, x.denominator)
    iv = [int(x * den) for x in v]
    g = 0
    for x in iv: g = gcd(g, abs(x))
    iv = [x // g for x in iv]
    return [x if iv[0] >= 0 else -x for x in iv] if iv[0] != 0 else iv


def connected(nodes, edges):
    nodes = set(nodes); seen = set(); stack = [next(iter(nodes))]
    while stack:
        v = stack.pop()
        if v in seen: continue
        seen.add(v)
        stack += [b if a == v else a for a, b in edges if v in (a, b) and a in nodes and b in nodes]
    return seen == nodes


def classify(A):
    p, m, z, _ = inertia_det(A)
    n = len(A)
    if p == n: return "finite"
    if m == 0 and z == 1 and p == n - 1: return "affine"       # connected, PSD, corank 1
    return "indefinite"


def delete_node_classes(n: int):
    """Class of the Dynkin diagram with each node deleted (Coxeter-simplex vertex types)."""
    A = cartan_en(n)
    return {k + 1: classify(sub_cartan(A, [i for i in range(n) if i != k])) for k in range(n)}


def is_hyperbolic(n: int) -> bool:
    """Kac-Moody hyperbolic: indefinite, and every proper connected subdiagram is finite or affine."""
    A = cartan_en(n); E = edges_en(n)
    if classify(A) != "indefinite": return False
    for k in range(1, n):
        for keep in combinations(range(n), k):
            if connected([i + 1 for i in keep], E) and classify(sub_cartan(A, keep)) == "indefinite":
                return False
    return True


def root_growth(n: int, depth: int):
    """Cumulative distinct real roots (simple-root integer coordinates) within `depth` reflections of a simple root."""
    A = cartan_en(n)
    simple = {tuple(int(i == j) for i in range(n)) for j in range(n)}
    roots, frontier, counts = set(simple), set(simple), [len(simple)]
    for _ in range(depth):
        nxt = set()
        for b in frontier:
            for i in range(n):
                c = sum(A[i][j] * b[j] for j in range(n))
                r = list(b); r[i] -= c; r = tuple(r)
                if r not in roots: roots.add(r); nxt.add(r)
        frontier = nxt; counts.append(len(roots))
    norms = {sum(b[i] * A[i][j] * b[j] for i in range(n) for j in range(n)) for b in roots}
    assert norms == {2}
    return counts


# ---------------------------------------------------------------- E9 <-> affine reflections on the E8 lattice
# Bourbaki E8 simple roots, doubled coordinates (2x): a1 = 1/2(e1+e8-e2-...-e7), a2 = e1+e2, a_k = e_{k-1}-e_{k-2}.
E8_SIMPLE2 = [
    (1, -1, -1, -1, -1, -1, -1, 1),
    (2, 2, 0, 0, 0, 0, 0, 0),
    (-2, 2, 0, 0, 0, 0, 0, 0),
    (0, -2, 2, 0, 0, 0, 0, 0),
    (0, 0, -2, 2, 0, 0, 0, 0),
    (0, 0, 0, -2, 2, 0, 0, 0),
    (0, 0, 0, 0, -2, 2, 0, 0),
    (0, 0, 0, 0, 0, -2, 2, 0),
]
THETA2 = (0, 0, 0, 0, 0, 0, 2, 2)          # highest root e7 + e8


def dot2(u, v):
    """Inner product of x=u/2 and y=v/2 (exact: dot4/4)."""
    s = sum(a * b for a, b in zip(u, v)); assert s % 4 == 0
    return s // 4


def e9_simple_roots_as_affine():
    """Level-0 part and delta-coefficient of each E9 simple root: a_i = (a_i, 0), a_9 = (-theta, 1)."""
    return [(a, 0) for a in E8_SIMPLE2] + [(tuple(-t for t in THETA2), 1)]


def weight_reflection(x2, alpha2, n):
    """Reflect the level-1 weight Lambda0 + x in the real root alpha + n*delta (alpha a root, norm 2).

    <Lambda0 + x, (alpha + n delta)^vee> = x.alpha + n  =>  x' = x - (x.alpha + n) alpha.
    """
    c = dot2(x2, alpha2) + n
    return tuple(a - c * b for a, b in zip(x2, alpha2))


def affine_reflection_via_roots(x2, alpha2, k):
    """five21_neighborhood.affine_reflection but implemented through the Kac-Moody root alpha - k*delta."""
    return weight_reflection(x2, alpha2, -k)


# ---------------------------------------------------------------- E10 root lattice = E8 (+) U (explicit isometry)
def e10_basis_change():
    """Integer matrix B (rows = new basis in simple-root coordinates) with B A B^T = E8 (+) U, det B = +-1.

    New basis: a_1..a_8, delta = sum(marks_i a_i) + a_9 (null, orthogonal to a_1..a_8), f = -a_10 - delta
    (null, f.delta = 1, f.a_i = 0 for i <= 8). Node numbering as cartan_en(10).
    """
    marks = [2, 3, 4, 6, 5, 4, 3, 2, 1]
    rows = [[int(i == j) for j in range(10)] for i in range(8)]
    delta = marks + [0]
    f = [-d for d in delta]; f[9] -= 1
    return rows + [delta, f]


def gram_of(B, A):
    n = len(A)
    return [[sum(B[i][a] * A[a][b] * B[j][b] for a in range(n) for b in range(n)) for j in range(len(B))] for i in range(len(B))]


# ---------------------------------------------------------------- root multiplicities (Peterson) + denominator check
def _bilinear(A, u, v):
    n = len(A)
    return sum(u[i] * A[i][j] * v[j] for i in range(n) for j in range(n) if u[i] and v[j])


def positive_real_roots(n: int, max_height: int):
    """All positive real roots of height <= max_height, by the exact rule beta = s_i(gamma), gamma lower, (gamma|a_i) < 0."""
    A = cartan_en(n)
    by_h = {1: [tuple(int(i == j) for j in range(n)) for i in range(n)]}
    seen = set(by_h[1])
    for h in range(2, max_height + 1):
        cur = []
        for g in by_h.get(h - 1, []) if False else [r for hh in range(1, h) for r in by_h.get(hh, [])]:
            for i in range(n):
                ip = sum(A[i][j] * g[j] for j in range(n))
                if ip < 0 and sum(g) - ip == h:
                    r = list(g); r[i] -= ip; r = tuple(r)
                    if r not in seen: seen.add(r); cur.append(r)
        by_h[h] = cur
    return seen


def peterson_multiplicities(n: int, max_height: int):
    """Multiplicities of all positive roots of E_n up to `max_height` (simple-root integer coordinates).

    Peterson: (b|b-2rho) c(b) = sum_{b'+b''=b} (b'|b'') c(b') c(b''),  c(b) = sum_{k>=1} mult(b/k)/k,
    with (b|2rho) = 2 ht(b) (simply laced). The coefficient vanishes at k*beta for a real root beta of height k,
    so real roots (mult 1) and their multiples (c = 1/k) are seeded directly; the recursion decides the rest.
    Exact Fractions; only nonzero c are stored.
    """
    from math import gcd
    A = cartan_en(n)
    real = positive_real_roots(n, max_height)
    c = {}
    by_h = {h: [] for h in range(1, max_height + 1)}
    for r in real:
        for k in range(1, max_height // sum(r) + 1):
            v = tuple(k * x for x in r)
            c[v] = Fraction(1, k); by_h[sum(v)].append(v)
    real_multiples = set(c)
    mult = {r: 1 for r in real}
    for h in range(2, max_height + 1):
        acc = {}
        for h1 in range(1, h // 2 + 1):
            for b1 in by_h[h1]:
                for b2 in by_h[h - h1]:
                    ip = _bilinear(A, b1, b2)
                    if ip == 0: continue
                    b = tuple(x + y for x, y in zip(b1, b2))
                    if b in real_multiples: continue
                    acc[b] = acc.get(b, 0) + ip * c[b1] * c[b2] * (2 if h1 < h - h1 else 1)
        for b, total in acc.items():
            if total == 0: continue
            coef = _bilinear(A, b, b) - 2 * h
            if coef == 0: raise ArithmeticError(f"nonzero Peterson sum with zero coefficient at {b}")
            cb = Fraction(total) / coef
            c[b] = cb; by_h[h].append(b)
            g = 0
            for x in b: g = gcd(g, x)
            m = cb
            for k in range(2, g + 1):
                if g % k == 0:
                    m -= Fraction(mult.get(tuple(x // k for x in b), 0), k)
            if m.denominator != 1 or m < 0: raise ArithmeticError(f"non-integer/negative multiplicity {m} at {b}")
            if m != 0: mult[b] = int(m)
    return {b: m for b, m in mult.items() if m}


def weyl_denominator_terms(n: int, max_height: int):
    """{mu: sign} for sum_w sign(w) e^{w rho - rho} = sum sign * x^{rho - w rho}, truncated at height <= max_height."""
    A = cartan_en(n)
    start = tuple([0] * n)
    terms = {start: 1}
    frontier = [start]
    while frontier:
        nxt = []
        for mu in frontier:
            for i in range(n):
                cc = 1 - sum(A[j][i] * mu[j] for j in range(n))        # <w rho, alpha_i^vee>
                if cc > 0 and sum(mu) + cc <= max_height:
                    new = list(mu); new[i] += cc; new = tuple(new)
                    if new not in terms:
                        terms[new] = -terms[mu]; nxt.append(new)
        frontier = nxt
    return {m: s for m, s in terms.items()}


def denominator_identity_holds(n: int, max_height: int, mult=None) -> bool:
    """Check prod_{b>0} (1 - x^b)^{mult(b)} == sum_w sign(w) x^{rho-w rho} through height max_height."""
    from math import comb
    mult = peterson_multiplicities(n, max_height) if mult is None else mult
    series = {tuple([0] * n): 1}
    for b, m in sorted(mult.items(), key=lambda kv: sum(kv[0])):
        hb = sum(b)
        new = dict(series)
        for k in range(1, max_height // hb + 1):
            coef = (-1) ** k * comb(m, k)
            if coef == 0: continue
            sh = tuple(k * x for x in b)
            for mono, v in series.items():
                if sum(mono) + k * hb <= max_height:
                    key = tuple(x + y for x, y in zip(mono, sh))
                    new[key] = new.get(key, 0) + coef * v
        series = {k: v for k, v in new.items() if v}
    rhs = {k: v for k, v in weyl_denominator_terms(n, max_height).items()}
    return series == rhs
