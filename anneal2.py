"""TEAM anneal: generic free-alphabet annealer with word+quadgram scoring and restart-convergence test.

Model: x_i = (CAinv[C_i] - s*K_i) mod 26 ; P_i = PA[x_i]   (Quagmire IV generalised; Beaufort = reversed CA)
Keystream modes:
  0 periodic        K_i = k[i % p]
  1 fixed           K_i = ks[i]  (Gromark digits etc.; only alphabets free)
  2 PT-autokey/PA   K_i = k[i] (i<L) else x_{i-L}          (key letter indexed in PT alphabet)
  3 PT-autokey/CA   K_i = k[i] (i<L) else CAinv[P_{i-L}]   (key letter indexed in CT alphabet)
  4 CT-autokey/CA   K_i = k[i] (i<L) else CAinv[C_{i-L}]
  5 CT-autokey/PA   K_i = k[i] (i<L) else PAinv[C_{i-L}]
Objective: sum quadgram log10 + WW * word-Viterbi log10 - 25 * crib mismatches.
Convergence: pairwise agreement of restart plaintexts on non-crib positions (chance ~0.07).
"""
import numpy as np
from numba import njit, prange
from k4lib import CT, CRIB_POS, load_quadgrams, AZ
from wordscore import get_trie, wseg_nb

QG = load_quadgrams()
CTA = np.array([ord(c) - 65 for c in CT], dtype=np.int64)
CRIB = np.full(97, -1, dtype=np.int64)
for _i, _c in CRIB_POS.items():
    CRIB[_i] = ord(_c) - 65
CHILD, VAL, _ = get_trie()
NONCRIB = np.array([i for i in range(97) if CRIB[i] < 0])


@njit(cache=True)
def decrypt(PA, CAinv, k, mode, p, s, ks, cta, pt, xs):
    n = cta.shape[0]
    PAinv = np.empty(26, dtype=np.int64)
    for i in range(26):
        PAinv[PA[i]] = i
    for i in range(n):
        if mode == 0:
            K = k[i % p]
        elif mode == 1:
            K = ks[i]
        elif i < p:
            K = k[i]
        elif mode == 2:
            K = xs[i - p]
        elif mode == 3:
            K = CAinv[pt[i - p]]
        elif mode == 4:
            K = CAinv[cta[i - p]]
        else:
            K = PAinv[cta[i - p]]
        x = (CAinv[cta[i]] - s * K) % 26
        xs[i] = x
        pt[i] = PA[x]


@njit(cache=True)
def repair(PA, CAinv, k, mode, p, s, ks, cta, crib, pt, xs):
    """Force PA[x_i] = crib letter at crib positions (x independent of PA for modes 0,1,2,4).
    Returns number of conflicts (crib letters that could not be placed)."""
    decrypt(PA, CAinv, k, mode, p, s, ks, cta, pt, xs)
    n = cta.shape[0]
    owner = np.full(26, -1, dtype=np.int64)  # x slot -> pinned letter
    conf = 0
    for i in range(n):
        c = crib[i]
        if c < 0:
            continue
        x = xs[i]
        if owner[x] >= 0:
            if owner[x] != c:
                conf += 1
            continue
        # where is letter c now?
        j = 0
        for t in range(26):
            if PA[t] == c:
                j = t
        if j != x and owner[j] >= 0:
            conf += 1  # c already pinned at another slot
            continue
        PA[j] = PA[x]; PA[x] = c
        owner[x] = c
    return conf


@njit(cache=True)
def score(PA, CAinv, k, mode, p, s, ks, cta, crib, QG, child, val, ww, pt, xs):
    if mode == 0 or mode == 1 or mode == 2 or mode == 4:
        repair(PA, CAinv, k, mode, p, s, ks, cta, crib, pt, xs)
    decrypt(PA, CAinv, k, mode, p, s, ks, cta, pt, xs)
    n = cta.shape[0]
    pen = 0
    for i in range(n):
        if crib[i] >= 0 and crib[i] != pt[i]:
            pen += 1
    q = 0.0
    for i in range(n - 3):
        q += QG[((pt[i] * 26 + pt[i + 1]) * 26 + pt[i + 2]) * 26 + pt[i + 3]]
    w = 0.0
    if ww > 0:
        w, _c = wseg_nb(pt, child, val, -7.0)
    return q + ww * w - 25.0 * pen, pen, q / (n - 3), w / n


@njit(cache=True)
def anneal(mode, p, s, ks, cta, crib, QG, child, val, ww, iters, seed, T0):
    np.random.seed(seed)
    PA = np.random.permutation(26)
    CAinv = np.random.permutation(26)
    nk = max(p, 1)
    k = np.random.randint(0, 26, nk)
    n = cta.shape[0]
    pt = np.empty(n, dtype=np.int64); xs = np.empty(n, dtype=np.int64)
    cur, pen, q, w = score(PA, CAinv, k, mode, p, s, ks, cta, crib, QG, child, val, ww, pt, xs)
    best = cur
    bPA = PA.copy(); bCA = CAinv.copy(); bk = k.copy()
    nmv = 2 if mode == 1 else 3
    sPA = PA.copy()
    ncyc = 4
    cyc = iters // ncyc
    for it in range(iters):
        if it > 0 and it % cyc == 0:  # reheat from best state at reduced temperature
            PA[:] = bPA; CAinv[:] = bCA; k[:] = bk
            cur, pen, q, w = score(PA, CAinv, k, mode, p, s, ks, cta, crib, QG, child, val, ww, pt, xs)
        T = T0 * (0.6 if it >= cyc else 1.0) * (1.0 - (it % cyc) / cyc) + 0.05
        mv = np.random.randint(0, nmv)
        a = 0; b = 0; old = 0
        sPA[:] = PA
        if mv == 0:
            a = np.random.randint(0, 26); b = np.random.randint(0, 26)
            PA[a], PA[b] = PA[b], PA[a]
        elif mv == 1:
            a = np.random.randint(0, 26); b = np.random.randint(0, 26)
            CAinv[a], CAinv[b] = CAinv[b], CAinv[a]
        else:
            a = np.random.randint(0, nk); old = k[a]; k[a] = np.random.randint(0, 26)
        new, npen, nq, nw = score(PA, CAinv, k, mode, p, s, ks, cta, crib, QG, child, val, ww, pt, xs)
        if new >= cur or np.random.random() < np.exp((new - cur) / T):
            cur = new
            if cur > best:
                best = cur
                bPA[:] = PA; bCA[:] = CAinv; bk[:] = k
        else:
            PA[:] = sPA
            if mv == 1:
                CAinv[a], CAinv[b] = CAinv[b], CAinv[a]
            elif mv == 2:
                k[a] = old
    best, pen, q, w = score(bPA, bCA, bk, mode, p, s, ks, cta, crib, QG, child, val, ww, pt, xs)
    return best, pen, q, w, pt.copy()


@njit(parallel=True, cache=True)
def multi(mode, p, s, ks, cta, crib, QG, child, val, ww, iters, restarts, base_seed, T0,
          r_best, r_pen, r_q, r_w, r_pt):
    for r in prange(restarts):
        b, pen, q, w, pt = anneal(mode, p, s, ks, cta, crib, QG, child, val, ww, iters, base_seed + r, T0)
        r_best[r] = b; r_pen[r] = pen; r_q[r] = q; r_w[r] = w; r_pt[r] = pt


def run(mode, p, cta=CTA, s=1, ks=None, ww=1.0, iters=1_000_000, restarts=8, seed=1, T0=None, crib=CRIB):
    if ks is None:
        ks = np.zeros(97, dtype=np.int64)
    if T0 is None:
        T0 = 8.0 * (1 + ww * 0.5)
    rb = np.zeros(restarts); rp = np.zeros(restarts, dtype=np.int64); rq = np.zeros(restarts)
    rw = np.zeros(restarts); rpt = np.zeros((restarts, 97), dtype=np.int64)
    multi(mode, p, s, np.asarray(ks, dtype=np.int64), cta, crib, QG, CHILD, VAL, ww, iters, restarts,
          seed, T0, rb, rp, rq, rw, rpt)
    return rb, rp, rq, rw, rpt


def convergence(rpt, rb, rp, top=None):
    """Pairwise non-crib agreement among crib-clean restarts. Returns (best-vs-others mean, max pair, n clean)."""
    ok = [i for i in np.argsort(-rb) if rp[i] == 0]
    if top:
        ok = ok[:top]
    if len(ok) < 2:
        return 0.0, 0.0, len(ok)
    A = rpt[ok][:, NONCRIB]
    m = (A[:, None, :] == A[None, :, :]).mean(axis=2)
    iu = np.triu_indices(len(ok), 1)
    return float(m[0, 1:].mean()), float(m[iu].max()), len(ok)


def txt(a):
    return "".join(AZ[int(x)] for x in a)
